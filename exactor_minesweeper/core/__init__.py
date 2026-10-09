"""
Core game mechanics and constraint systems for Minesweeper.
"""

from exactor_minesweeper.core.board import MinesweeperBoard, Difficulty
from exactor_minesweeper.core.constraints import Constraint, ExactSATReduction, BoardConstraintSystem

__all__ = [
    "MinesweeperBoard",
    "Difficulty",
    "Constraint",
    "ExactSATReduction",
    "BoardConstraintSystem",
]
