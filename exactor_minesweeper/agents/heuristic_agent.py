"""
Heuristic and Random Baseline Agents for benchmark comparison.
"""

import random
import time
from exactor_minesweeper.agents.base import BaseMinesweeperAgent, AgentAction, ActionType
from exactor_minesweeper.core.board import MinesweeperBoard


class HeuristicAgent(BaseMinesweeperAgent):
    """Simple 1st-order rule solver (Single-clue zero and saturation only, no subset reduction)."""

    def __init__(self, name: str = "Standard Heuristic (1st Order)"):
        super().__init__(name=name)

    def select_action(self, board: MinesweeperBoard) -> AgentAction:
        t0 = time.perf_counter()
        self.total_moves += 1

        unrevealed = board.get_unrevealed_coords()
        if not unrevealed:
            return AgentAction(ActionType.REVEAL, 0, 0, 1.0, False, "Terminal state", {"latency_ms": 0.0})

        # 1. Opening move
        if board.move_count == 0 or all(all(not r for r in row) for row in board.revealed_grid):
            lat = (time.perf_counter() - t0) * 1000.0
            self.total_latency_ms += lat
            return AgentAction(
                ActionType.REVEAL,
                board.height // 2,
                board.width // 2,
                1.0,
                False,
                "Center opening",
                {"latency_ms": lat},
            )

        # 2. Check each revealed clue independently
        for r in range(board.height):
            for c in range(board.width):
                if board.revealed_grid[r][c] and board.clues_grid[r][c] > 0:
                    clue = board.clues_grid[r][c]
                    hidden = []
                    flags = 0
                    for nr, nc in board.get_neighbors(r, c):
                        if board.flagged_grid[nr][nc]:
                            flags += 1
                        elif not board.revealed_grid[nr][nc]:
                            hidden.append((nr, nc))

                    eff_clue = clue - flags
                    if hidden and eff_clue == 0:
                        # Reveal safe cell
                        lat = (time.perf_counter() - t0) * 1000.0
                        self.total_latency_ms += lat
                        self.total_deterministic_moves += 1
                        return AgentAction(
                            ActionType.REVEAL,
                            hidden[0][0],
                            hidden[0][1],
                            1.0,
                            False,
                            f"Heuristic 0-effective clue at ({r}, {c})",
                            {"latency_ms": lat},
                        )

                    if hidden and eff_clue == len(hidden):
                        # Flag mine
                        lat = (time.perf_counter() - t0) * 1000.0
                        self.total_latency_ms += lat
                        self.total_deterministic_moves += 1
                        return AgentAction(
                            ActionType.FLAG,
                            hidden[0][0],
                            hidden[0][1],
                            1.0,
                            False,
                            f"Heuristic saturated clue at ({r}, {c})",
                            {"latency_ms": lat},
                        )

        # 3. Random guess
        self.total_guesses += 1
        frontier_hidden, _ = board.get_frontier()
        choice = random.choice(frontier_hidden) if frontier_hidden else random.choice(unrevealed)
        lat = (time.perf_counter() - t0) * 1000.0
        self.total_latency_ms += lat
        return AgentAction(
            ActionType.REVEAL,
            choice[0],
            choice[1],
            0.5,
            True,
            "Heuristic fallback random guess",
            {"latency_ms": lat},
        )


class RandomAgent(BaseMinesweeperAgent):
    """Pure random picker baseline."""

    def __init__(self, name: str = "Random Baseline"):
        super().__init__(name=name)

    def select_action(self, board: MinesweeperBoard) -> AgentAction:
        t0 = time.perf_counter()
        self.total_moves += 1
        self.total_guesses += 1

        unrevealed = board.get_unrevealed_coords()
        if not unrevealed:
            return AgentAction(ActionType.REVEAL, 0, 0, 0.0, True, "Terminal", {"latency_ms": 0.0})

        choice = random.choice(unrevealed)
        lat = (time.perf_counter() - t0) * 1000.0
        self.total_latency_ms += lat
        return AgentAction(
            ActionType.REVEAL,
            choice[0],
            choice[1],
            0.1,
            True,
            "Uniform random selection",
            {"latency_ms": lat},
        )
