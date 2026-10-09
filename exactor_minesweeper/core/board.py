"""
Minesweeper Board Implementation with Standard Rules and Safe First-Click Mechanics.
"""

import random
import copy
from enum import Enum
from typing import List, Tuple, Set, Dict, Optional, Any


class Difficulty(str, Enum):
    BEGINNER = "beginner"       # 8x8, 10 mines
    INTERMEDIATE = "intermediate" # 16x16, 40 mines
    EXPERT = "expert"           # 30x16, 99 mines
    CUSTOM = "custom"


DIFFICULTY_PRESETS = {
    Difficulty.BEGINNER: {"width": 8, "height": 8, "mines": 10},
    Difficulty.INTERMEDIATE: {"width": 16, "height": 16, "mines": 40},
    Difficulty.EXPERT: {"width": 30, "height": 16, "mines": 99},
}


class CellState:
    HIDDEN = -1
    FLAGGED = -2


class MinesweeperBoard:
    """
    Standard Minesweeper board simulation engine.
    Supports first-click safety, flood-fill cascading, deterministic query APIs,
    and state serialization for AI solvers.
    """

    def __init__(
        self,
        width: int = 8,
        height: int = 8,
        num_mines: int = 10,
        seed: Optional[int] = None,
        difficulty: Optional[Difficulty] = None,
    ):
        if difficulty and difficulty in DIFFICULTY_PRESETS:
            cfg = DIFFICULTY_PRESETS[difficulty]
            self.width = cfg["width"]
            self.height = cfg["height"]
            self.num_mines = cfg["mines"]
            self.difficulty = difficulty
        else:
            self.width = max(3, width)
            self.height = max(3, height)
            self.num_mines = min(num_mines, (self.width * self.height) - 1)
            self.difficulty = Difficulty.CUSTOM

        self.seed = seed
        self.rng = random.Random(seed)

        # Internal state grids
        self.mines_grid: List[List[bool]] = [[False] * self.width for _ in range(self.height)]
        self.revealed_grid: List[List[bool]] = [[False] * self.width for _ in range(self.height)]
        self.flagged_grid: List[List[bool]] = [[False] * self.width for _ in range(self.height)]
        self.clues_grid: List[List[int]] = [[0] * self.width for _ in range(self.height)]

        self.mines_placed: bool = False
        self.is_over: bool = False
        self.is_victory: bool = False
        self.exploded_at: Optional[Tuple[int, int]] = None
        self.move_count: int = 0
        self.first_click_pos: Optional[Tuple[int, int]] = None

    def _place_mines(self, safe_r: int, safe_c: int) -> None:
        """Place mines avoiding the first clicked cell and its immediate neighbors."""
        safe_zone = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = safe_r + dr, safe_c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    safe_zone.add((nr, nc))

        all_coords = [
            (r, c)
            for r in range(self.height)
            for c in range(self.width)
            if (r, c) not in safe_zone
        ]

        if len(all_coords) < self.num_mines:
            # Fallback if board is very dense
            all_coords = [
                (r, c)
                for r in range(self.height)
                for c in range(self.width)
                if (r, c) != (safe_r, safe_c)
            ]

        mine_coords = self.rng.sample(all_coords, min(self.num_mines, len(all_coords)))
        for r, c in mine_coords:
            self.mines_grid[r][c] = True

        # Calculate clue numbers
        for r in range(self.height):
            for c in range(self.width):
                if not self.mines_grid[r][c]:
                    count = 0
                    for nr, nc in self.get_neighbors(r, c):
                        if self.mines_grid[nr][nc]:
                            count += 1
                    self.clues_grid[r][c] = count
                else:
                    self.clues_grid[r][c] = -1

        self.mines_placed = True

    def get_neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Return valid 8-neighborhood coordinate pairs for (r, c)."""
        neighbors = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    neighbors.append((nr, nc))
        return neighbors

    def reveal(self, r: int, c: int) -> Tuple[str, List[Tuple[int, int]]]:
        """
        Reveal cell at (r, c).
        Returns:
            status: "OK", "BOOM", "WIN", "ALREADY_REVEALED", "FLAGGED"
            revealed_cells: List of (r, c) coordinates revealed during this action (including cascade).
        """
        if self.is_over:
            return "GAME_OVER", []

        if not (0 <= r < self.height and 0 <= c < self.width):
            return "OUT_OF_BOUNDS", []

        if self.flagged_grid[r][c]:
            return "FLAGGED", []

        if self.revealed_grid[r][c]:
            return "ALREADY_REVEALED", []

        self.move_count += 1

        if not self.mines_placed:
            self.first_click_pos = (r, c)
            self._place_mines(r, c)

        if self.mines_grid[r][c]:
            self.revealed_grid[r][c] = True
            self.is_over = True
            self.is_victory = False
            self.exploded_at = (r, c)
            return "BOOM", [(r, c)]

        # Perform BFS flood-fill for 0-clue propagation
        revealed_now: List[Tuple[int, int]] = []
        queue = [(r, c)]
        self.revealed_grid[r][c] = True
        revealed_now.append((r, c))

        while queue:
            curr_r, curr_c = queue.pop(0)
            if self.clues_grid[curr_r][curr_c] == 0:
                for nr, nc in self.get_neighbors(curr_r, curr_c):
                    if not self.revealed_grid[nr][nc] and not self.flagged_grid[nr][nc]:
                        self.revealed_grid[nr][nc] = True
                        revealed_now.append((nr, nc))
                        if self.clues_grid[nr][nc] == 0:
                            queue.append((nr, nc))

        # Check win condition
        if self.check_victory():
            self.is_over = True
            self.is_victory = True
            return "WIN", revealed_now

        return "OK", revealed_now

    def toggle_flag(self, r: int, c: int) -> bool:
        """Toggle flag status on cell (r, c). Returns new flag state."""
        if self.is_over or not (0 <= r < self.height and 0 <= c < self.width):
            return False
        if self.revealed_grid[r][c]:
            return False

        self.flagged_grid[r][c] = not self.flagged_grid[r][c]
        return self.flagged_grid[r][c]

    def set_flag(self, r: int, c: int, state: bool = True) -> bool:
        """Set specific flag status."""
        if self.is_over or not (0 <= r < self.height and 0 <= c < self.width):
            return False
        if self.revealed_grid[r][c]:
            return False
        self.flagged_grid[r][c] = state
        if self.check_victory():
            self.is_over = True
            self.is_victory = True
        return True

    def check_victory(self) -> bool:
        """True if all non-mine cells are revealed."""
        for r in range(self.height):
            for c in range(self.width):
                if not self.mines_grid[r][c] and not self.revealed_grid[r][c]:
                    return False
        return True

    def get_visible_grid(self) -> List[List[int]]:
        """
        Returns grid as visible to a player / AI agent:
        -1: Hidden
        -2: Flagged
        0-8: Revealed clue count
        """
        visible = [[CellState.HIDDEN] * self.width for _ in range(self.height)]
        for r in range(self.height):
            for c in range(self.width):
                if self.flagged_grid[r][c]:
                    visible[r][c] = CellState.FLAGGED
                elif self.revealed_grid[r][c]:
                    visible[r][c] = self.clues_grid[r][c]
                else:
                    visible[r][c] = CellState.HIDDEN
        return visible

    def get_unrevealed_coords(self) -> List[Tuple[int, int]]:
        """Returns all unrevealed, unflagged coordinates."""
        return [
            (r, c)
            for r in range(self.height)
            for c in range(self.width)
            if not self.revealed_grid[r][c] and not self.flagged_grid[r][c]
        ]

    def get_frontier(self) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Returns:
            frontier_hidden: list of hidden, unflagged cells adjacent to at least one revealed clue.
            frontier_clues: list of revealed clue cells that have at least one unrevealed neighbor.
        """
        frontier_hidden: Set[Tuple[int, int]] = set()
        frontier_clues: Set[Tuple[int, int]] = set()

        for r in range(self.height):
            for c in range(self.width):
                if self.revealed_grid[r][c] and self.clues_grid[r][c] > 0:
                    unrevealed_neighbors = [
                        (nr, nc)
                        for nr, nc in self.get_neighbors(r, c)
                        if not self.revealed_grid[nr][nc] and not self.flagged_grid[nr][nc]
                    ]
                    if unrevealed_neighbors:
                        frontier_clues.add((r, c))
                        frontier_hidden.update(unrevealed_neighbors)

        return list(frontier_hidden), list(frontier_clues)

    def remaining_mines_estimate(self) -> int:
        """Estimated mines remaining based on total mines minus placed flags."""
        flag_count = sum(sum(1 for f in row if f) for row in self.flagged_grid)
        return max(0, self.num_mines - flag_count)

    def clone(self) -> "MinesweeperBoard":
        """Returns an exact independent deep-copy clone of the board."""
        return copy.deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize board state for Web API / Frontend / Logs."""
        return {
            "width": self.width,
            "height": self.height,
            "num_mines": self.num_mines,
            "difficulty": self.difficulty.value if hasattr(self.difficulty, "value") else str(self.difficulty),
            "is_over": self.is_over,
            "is_victory": self.is_victory,
            "move_count": self.move_count,
            "exploded_at": self.exploded_at,
            "visible_grid": self.get_visible_grid(),
            "flags_placed": sum(sum(1 for f in row if f) for row in self.flagged_grid),
            "cells_revealed": sum(sum(1 for r in row if r) for row in self.revealed_grid),
            "total_cells": self.width * self.height,
        }
