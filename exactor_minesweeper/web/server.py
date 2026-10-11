"""
FastAPI Server for Interactive Minesweeper Game & Real-Time AI Duel Visualizer.
"""

import os
import time
import random
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from exactor_minesweeper.core.board import MinesweeperBoard, Difficulty
from exactor_minesweeper.agents.exactor_agent import ExactorAcceleratorAgent
from exactor_minesweeper.agents.jev_pure_agent import JevPureAgent
from exactor_minesweeper.agents.heuristic_agent import HeuristicAgent
from exactor_minesweeper.agents.base import ActionType
from exactor_minesweeper.benchmark.runner import BenchmarkRunner

app = FastAPI(title="Exactor Minesweeper AI Arena", version="1.0.0")

# Static assets mount
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

# In-memory session state
sessions: Dict[str, Dict[str, Any]] = {}
agents_pool = {
    "exactor": ExactorAcceleratorAgent(),
    "jev": JevPureAgent(),
    "heuristic": HeuristicAgent(),
}


class NewGameRequest(BaseModel):
    session_id: str = "default"
    difficulty: str = "beginner"
    width: Optional[int] = None
    height: Optional[int] = None
    mines: Optional[int] = None
    seed: Optional[int] = None


class UserActionRequest(BaseModel):
    session_id: str = "default"
    action_type: str  # "REVEAL" | "FLAG" | "UNFLAG"
    row: int
    col: int


class AIStepRequest(BaseModel):
    session_id: str = "default"
    agent_type: str = "exactor"  # "exactor" | "jev" | "heuristic"


class DuelStepRequest(BaseModel):
    session_id: str = "default"


class BenchmarkRequest(BaseModel):
    num_games: int = 15
    difficulty: str = "beginner"


class ContactLeadRequest(BaseModel):
    name: str
    email: str
    company_role: str
    use_case: str


@app.post("/api/contact")
async def register_contact_lead(lead: ContactLeadRequest):
    return {
        "status": "success",
        "message": "Lead received. Forwarding to contact@exactor.tech",
        "lead": {
            "name": lead.name,
            "email": lead.email,
            "company_role": lead.company_role,
            "use_case": lead.use_case,
        },
        "target_email": "contact@exactor.tech",
        "booking_url": "https://cal.com/exactor-tech",
    }



@app.get("/")
async def get_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Exactor Minesweeper Arena Running</h1>")


@app.post("/api/game/new")
async def new_game(req: NewGameRequest):
    diff = Difficulty(req.difficulty.lower()) if req.difficulty.lower() in [d.value for d in Difficulty] else Difficulty.BEGINNER
    seed = req.seed or random.randint(1000, 999999)

    board_main = MinesweeperBoard(
        width=req.width or 8,
        height=req.height or 8,
        num_mines=req.mines or 10,
        difficulty=diff,
        seed=seed,
    )
    # Duel boards
    board_exactor = board_main.clone()
    board_jev = board_main.clone()

    sessions[req.session_id] = {
        "board_main": board_main,
        "board_exactor": board_exactor,
        "board_jev": board_jev,
        "seed": seed,
        "difficulty": diff.value,
        "history": [],
        "duel_stats": {
            "exactor": {"moves": 0, "latency_ms": 0.0, "won": False, "lost": False, "api_calls": 0},
            "jev": {"moves": 0, "latency_ms": 0.0, "won": False, "lost": False, "api_calls": 0},
        }
    }

    return {
        "status": "CREATED",
        "session_id": req.session_id,
        "seed": seed,
        "board": board_main.to_dict(),
        "duel_boards": {
            "exactor": board_exactor.to_dict(),
            "jev": board_jev.to_dict(),
        }
    }


@app.post("/api/game/action")
async def user_action(req: UserActionRequest):
    sess = sessions.get(req.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found. Create a game first.")

    board: MinesweeperBoard = sess["board_main"]
    if req.action_type == "REVEAL":
        status, revealed = board.reveal(req.row, req.col)
    elif req.action_type == "FLAG":
        board.set_flag(req.row, req.col, True)
        status = "FLAGGED"
        revealed = []
    elif req.action_type == "UNFLAG":
        board.set_flag(req.row, req.col, False)
        status = "UNFLAGGED"
        revealed = []
    else:
        raise HTTPException(status_code=400, detail="Invalid action type")

    return {
        "status": status,
        "board": board.to_dict(),
        "revealed": revealed,
    }


@app.post("/api/game/ai-step")
async def ai_step(req: AIStepRequest):
    sess = sessions.get(req.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    board: MinesweeperBoard = sess["board_main"]
    if board.is_over:
        return {"status": "GAME_OVER", "board": board.to_dict()}

    agent = agents_pool.get(req.agent_type.lower(), agents_pool["exactor"])
    action = agent.select_action(board)

    if action.action_type == ActionType.REVEAL:
        status, revealed = board.reveal(action.row, action.col)
    elif action.action_type == ActionType.FLAG:
        board.set_flag(action.row, action.col, True)
        status = "FLAGGED"
        revealed = []
    else:
        board.set_flag(action.row, action.col, False)
        status = "UNFLAGGED"
        revealed = []

    return {
        "status": status,
        "action": {
            "type": action.action_type.value,
            "row": action.row,
            "col": action.col,
            "confidence": action.confidence,
            "is_guess": action.is_guess,
            "explanation": action.explanation,
            "metadata": action.metadata,
        },
        "board": board.to_dict(),
        "revealed": revealed,
    }


@app.post("/api/game/duel-step")
async def duel_step(req: DuelStepRequest):
    """Advance one step on both Exactor and JEV boards simultaneously for live visual race."""
    sess = sessions.get(req.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    b_ex: MinesweeperBoard = sess["board_exactor"]
    b_jv: MinesweeperBoard = sess["board_jev"]
    stats = sess["duel_stats"]

    res_exactor = None
    if not b_ex.is_over:
        t0 = time.perf_counter()
        act_ex = agents_pool["exactor"].select_action(b_ex)
        lat_ex = (time.perf_counter() - t0) * 1000.0
        stats["exactor"]["moves"] += 1
        stats["exactor"]["latency_ms"] += lat_ex

        if act_ex.action_type == ActionType.REVEAL:
            st, rev = b_ex.reveal(act_ex.row, act_ex.col)
        else:
            b_ex.set_flag(act_ex.row, act_ex.col, True)
            st, rev = "FLAGGED", []

        stats["exactor"]["won"] = b_ex.is_victory
        stats["exactor"]["lost"] = b_ex.is_over and not b_ex.is_victory

        res_exactor = {
            "action": act_ex.action_type.value,
            "row": act_ex.row,
            "col": act_ex.col,
            "confidence": act_ex.confidence,
            "is_guess": act_ex.is_guess,
            "explanation": act_ex.explanation,
            "status": st,
            "latency_ms": round(lat_ex, 4),
        }

    res_jev = None
    if not b_jv.is_over:
        t0 = time.perf_counter()
        act_jv = agents_pool["jev"].select_action(b_jv)
        lat_jv = (time.perf_counter() - t0) * 1000.0
        stats["jev"]["moves"] += 1
        stats["jev"]["latency_ms"] += lat_jv
        stats["jev"]["api_calls"] += 1

        if act_jv.action_type == ActionType.REVEAL:
            st, rev = b_jv.reveal(act_jv.row, act_jv.col)
        else:
            b_jv.set_flag(act_jv.row, act_jv.col, True)
            st, rev = "FLAGGED", []

        stats["jev"]["won"] = b_jv.is_victory
        stats["jev"]["lost"] = b_jv.is_over and not b_jv.is_victory

        res_jev = {
            "action": act_jv.action_type.value,
            "row": act_jv.row,
            "col": act_jv.col,
            "confidence": act_jv.confidence,
            "is_guess": act_jv.is_guess,
            "explanation": act_jv.explanation,
            "status": st,
            "latency_ms": round(lat_jv, 4),
        }

    return {
        "exactor": {
            "board": b_ex.to_dict(),
            "step": res_exactor,
            "stats": stats["exactor"],
        },
        "jev": {
            "board": b_jv.to_dict(),
            "step": res_jev,
            "stats": stats["jev"],
        },
        "is_duel_finished": b_ex.is_over and b_jv.is_over,
    }


@app.post("/api/benchmark/run")
async def run_benchmark_endpoint(req: BenchmarkRequest):
    diff = Difficulty(req.difficulty.lower()) if req.difficulty.lower() in [d.value for d in Difficulty] else Difficulty.BEGINNER
    runner = BenchmarkRunner(difficulty=diff)
    result = runner.run_benchmark(num_games=req.num_games)
    return result.to_dict()


# Mount static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def start_server(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)
