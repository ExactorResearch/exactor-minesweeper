"""
Unit tests for Minesweeper Board core engine.
"""

import pytest
from exactor_minesweeper.core.board import MinesweeperBoard, Difficulty, CellState


def test_board_initialization():
    board = MinesweeperBoard(difficulty=Difficulty.BEGINNER, seed=42)
    assert board.width == 8
    assert board.height == 8
    assert board.num_mines == 10
    assert not board.is_over
    assert not board.is_victory
    assert board.move_count == 0


def test_first_click_safety():
    """First clicked cell must NEVER be a mine."""
    for seed in range(10):
        board = MinesweeperBoard(difficulty=Difficulty.BEGINNER, seed=seed)
        status, revealed = board.reveal(3, 3)
        assert status in ("OK", "WIN")
        assert not board.mines_grid[3][3]
        assert board.revealed_grid[3][3]


def test_flag_toggling():
    board = MinesweeperBoard(difficulty=Difficulty.BEGINNER, seed=42)
    assert not board.flagged_grid[2][2]
    
    # Flag
    assert board.toggle_flag(2, 2)
    assert board.flagged_grid[2][2]
    
    # Cannot reveal flagged cell directly
    status, _ = board.reveal(2, 2)
    assert status == "FLAGGED"
    assert not board.revealed_grid[2][2]

    # Unflag
    assert not board.toggle_flag(2, 2)
    assert not board.flagged_grid[2][2]


def test_clue_numbers_accuracy():
    board = MinesweeperBoard(difficulty=Difficulty.BEGINNER, seed=123)
    board.reveal(0, 0)
    
    for r in range(board.height):
        for c in range(board.width):
            if not board.mines_grid[r][c]:
                actual_adj_mines = sum(
                    1 for nr, nc in board.get_neighbors(r, c)
                    if board.mines_grid[nr][nc]
                )
                assert board.clues_grid[r][c] == actual_adj_mines
