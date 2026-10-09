"""
Unit tests for ExactorAcceleratorAgent.
"""

import pytest
from exactor_minesweeper.core.board import MinesweeperBoard, Difficulty
from exactor_minesweeper.agents.exactor_agent import ExactorAcceleratorAgent
from exactor_minesweeper.agents.base import ActionType


def test_exactor_opening_move():
    agent = ExactorAcceleratorAgent()
    board = MinesweeperBoard(difficulty=Difficulty.BEGINNER, seed=42)
    action = agent.select_action(board)
    
    assert action.action_type == ActionType.REVEAL
    assert (action.row, action.col) == (board.height // 2, board.width // 2)
    assert not action.is_guess


def test_exactor_deterministic_moves():
    agent = ExactorAcceleratorAgent()
    board = MinesweeperBoard(difficulty=Difficulty.BEGINNER, seed=999)
    board.reveal(board.height // 2, board.width // 2)

    while not board.is_over and board.move_count < 25:
        action = agent.select_action(board)
        assert action.action_type in (ActionType.REVEAL, ActionType.FLAG)
        assert 0.0 <= action.confidence <= 1.0
        
        if action.action_type == ActionType.REVEAL:
            board.reveal(action.row, action.col)
        else:
            board.set_flag(action.row, action.col, True)
