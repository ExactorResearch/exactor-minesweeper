"""
Base class and data contracts for Minesweeper AI agents.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass
from exactor_minesweeper.core.board import MinesweeperBoard


class ActionType(str, Enum):
    REVEAL = "REVEAL"
    FLAG = "FLAG"
    UNFLAG = "UNFLAG"


@dataclass
class AgentAction:
    action_type: ActionType
    row: int
    col: int
    confidence: float
    is_guess: bool
    explanation: str
    metadata: Dict[str, Any]


@dataclass
class ActionResult:
    status: str
    action: AgentAction
    latency_ms: float
    is_game_over: bool
    is_victory: bool


class BaseMinesweeperAgent(ABC):
    """Abstract interface for all Minesweeper playing agents."""

    def __init__(self, name: str):
        self.name = name
        self.total_moves: int = 0
        self.total_guesses: int = 0
        self.total_deterministic_moves: int = 0
        self.total_latency_ms: float = 0.0
        self.api_calls_count: int = 0

    @abstractmethod
    def select_action(self, board: MinesweeperBoard) -> AgentAction:
        """Analyze visible board state and return the next recommended action."""
        pass

    def reset_metrics(self) -> None:
        """Reset agent telemetry metrics for a new game."""
        self.total_moves = 0
        self.total_guesses = 0
        self.total_deterministic_moves = 0
        self.total_latency_ms = 0.0
        self.api_calls_count = 0
