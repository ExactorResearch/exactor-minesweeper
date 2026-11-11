# Exactor Minesweeper

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](#license)
[![Powered by](https://img.shields.io/badge/Engine-Exactor%20Accelerator-orange.svg)](https://github.com/ExactorResearch/exactor-accelerator)
[![Latency](https://img.shields.io/badge/Fast--Path-~0.45ms-brightgreen.svg)](#benchmarks)
[![Win Rate](https://img.shields.io/badge/Win%20Rate-96%25-brightgreen.svg)](#benchmarks)
[![Live Demo](https://img.shields.io/badge/Demo-Interactive%20App-purple.svg)](https://minesweeper.exactor.ai)

**Exactor Minesweeper** is an interactive demonstration and empirical evaluation arena showcasing **Exactor Accelerator** in a real-time constraint environment.

It isolates the core System 1 vs. System 2 trade-off: **deterministic board states are resolved locally by exact combinatorial deduction in sub-millisecond time with zero API cost, and only genuinely ambiguous states are delegated to a cloud oracle (TypeSafe Jev).**

---

## 🌐 Live Interactive Demo

Test the live interactive solver in your browser:  
👉 **[Launch Minesweeper Live](https://minesweeper.exactor.ai)**

* Experience the real-time split-screen duel: **Exactor Hybrid vs. Pure JEV (LLM/RLCD)**.
* Watch deterministic frontier tiles resolve locally in sub-millisecond time without burning cloud tokens.
* Inspect the dual output on every move: **Board Action (`REVEAL` / `FLAG`) + Algebraic Subset Proof**.

> **Honest note on the "Pure JEV" baseline:** the agent sends each decision to the live TypeSafe Jev API when `JEV_API_KEY` is configured. Without a key it falls back to a *clearly labeled* local simulation (`simulated_llm: true` in move metadata) — simulated numbers are not real LLM measurements.

---

## The Challenge with AI in Minesweeper

Minesweeper is an NP-complete constraint satisfaction game where a single arithmetic counting error triggers instantaneous loss.

| Metric / Dimension | 🤖 Pure JEV (Solo LLM/RLCD, live API) | 📜 Standard Heuristic (1st Order) | ⚡ Exactor Accelerator (Neuro-Symbolic) | Advantage / Delta |
| :--- | :---: | :---: | :---: | :---: |
| **Avg Latency per Move** | `792.27 ms` | `0.14 ms` | **`0.45 ms` (Fast-Path Local)** | **~1,760x Faster** |
| **Board Win Rate (%)** | `0.0%` (25 beginner games) | `72.0%` | **`96.0%`** | **+96 pts** |
| **Deterministic Move Ratio** | `100%` (every move is an API call) | `95.2%` | **`97.6%`** | local algebraic deduction |
| **API Calls per Game** | `3.7 calls` | `0.0 calls` | **`0.0 calls`** | **100% Token Elimination** |
| **Explainability** | Opaque text generation | Hardcoded logic | **Exact Boolean Algebraic Proof** | **Full Causal Audit Trail** |

*Measured live against `api.typesafe.ai` (`JEV_API_KEY` required): 25 beginner games per agent, identical seeds. The Exactor ~0.45 ms/move includes Python-level board handling — the Boolean subset evaluation itself is a fraction of that. Without a key, the Jev agent falls back to a labeled simulation (`simulated_llm: true`); simulated runs are not real LLM measurements.*

---

## Architecture: How It Works

Exactor couples local algebraic subset deduction with calibrated cognitive fallback:

```text
[ Visible Minesweeper Board ]
               │
               ▼
 [ 1. Frontier Constraint Extraction ] ─── (Σ x_i = k - F)
               │
               ▼
 ┌────────────────────────────────────────────────────────┐
 │ 2. Exactor Fast-Path (In-Memory Algebraic Reduction)   │
 │    - Evaluates Subset Overlaps (V_B \ V_A = T_B - T_A) │
 └───────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
 [ Deterministic Tile (95%+) ]     [ Underdetermined 50/50 State ]
        │                                 │
        ▼                                 ▼
 [ Instant Action + Proof ]        [ Oracle Escalation (Jev / LLM) ]
 (REVEAL / FLAG in ~0.5 ms)        (Calibrated Minimum Risk Score)
                                          │
                                          ▼
                                   [ SQLite WAL Ledger ]
                                          │
                                          ▼
                                   [ Hot Engram Consolidation ]
```

### The Dual Output (Glass Box)
For every move, Exactor Minesweeper outputs both the board coordinates and the formal mathematical proof:

```json
{
  "move_id": "move_17",
  "action": "REVEAL",
  "coords": [2, 4],
  "latency_ms": 0.287,
  "execution_path": "FAST_PATH_ALGEBRAIC_SUBSET",
  "causal_proof": "SubsetResolution: Frontier(2,3) ⊂ Frontier(2,5) -> RemainingCount == 0 -> Coords(2,4) IS_SAFE",
  "oracle_consulted": false
}
```

---

## Quickstart

### Prerequisites
* Python 3.9+
* pip

### Installation & Launching Local Web Arena (Port 8000)

```bash
git clone https://github.com/ExactorResearch/exactor-minesweeper.git
cd exactor-minesweeper
pip install -r requirements.txt

# Optional: live Jev oracle for the "Pure JEV" baseline and ambiguous-state escalation
export JEV_API_KEY="your-typesafe-key"

# Launch interactive web arena
python run_web.py
```

Once running, access the local arena at **`http://localhost:8000`**.
* 💣 **Interactive Board**: Play manually or trigger automated step-by-step AI moves with live visual proof highlights.
* ⚔️ **Live Multi-Agent Duel**: Side-by-side race comparing Exactor against Pure JEV on identical board seeds.
* 📊 **Monte Carlo Benchmarks**: Evaluate latency, win rates, and token consumption across Beginner (8x8), Intermediate (16x16), and Expert (30x16) boards.

---

## CLI Usage & Benchmarks

### Play Step via CLI
```bash
python run_cli.py --difficulty beginner --step
```

### Run Monte Carlo Benchmark Suite
```bash
python run_benchmark.py
```

### Run Unit Tests
```bash
python -m pytest -v
```

---

## Project Structure

```text
exactor-minesweeper/
├── exactor_minesweeper/
│   ├── solver.py            # Algebraic subset reduction & probabilistic solver
│   ├── board.py             # Board state management, mine generation, and validation
│   ├── web/                 # Interactive web dashboard & API server (Port 8000)
│   └── duel.py              # Multi-agent visual duel runner
├── run_web.py               # Launch web arena
├── run_cli.py               # Command-line solver interface
├── run_benchmark.py         # Monte Carlo benchmark runner
└── README.md
```

---

## Integration in Python

```python
from exactor_minesweeper.solver import ExactorMinesweeperSolver
from exactor_minesweeper.board import MinesweeperBoard

board = MinesweeperBoard(rows=8, cols=8, num_mines=10)
board.reveal_cell(0, 0)

solver = ExactorMinesweeperSolver()

# Fast-Path local algebraic move (~0.5 ms incl. board handling)
move = solver.get_next_move(board)
print(f"Action: {move.action} at ({move.row}, {move.col}) | Proof: {move.causal_proof}")
```

---

## 📅 Enterprise Evaluation & Demo Scheduling

Explore how Exactor Accelerator combines deterministic algebraic reduction with Bayesian/LLM fallback:

- **Schedule a 15-Min Architecture Review:** [Book Directly on Cal.com](https://cal.com/exactor-tech)
- **Submit Workload Requirements:** [Open Tally / Typeform Assessment](https://tally.so/r/w2xD4P)
- **Direct Commercial Inquiries:** [`contact@exactor.tech`](mailto:contact@exactor.tech)

---

## License

Dual-licensed under [MIT](LICENSE).

