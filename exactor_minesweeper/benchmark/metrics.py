"""
Benchmark Metrics and Telemetry Models.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import numpy as np


@dataclass
class SingleGameRecord:
    game_id: int
    seed: int
    difficulty: str
    won: bool
    total_moves: int
    deterministic_moves: int
    guesses_made: int
    total_latency_ms: float
    avg_latency_per_move_ms: float
    p95_latency_ms: float
    api_calls: int
    exploded_at: Optional[Any] = None


@dataclass
class AgentBenchmarkMetrics:
    agent_name: str
    total_games: int
    wins: int
    losses: int
    win_rate_pct: float
    avg_moves_per_game: float
    deterministic_move_ratio_pct: float
    avg_latency_per_move_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    total_time_seconds: float
    total_api_calls: int
    avg_api_calls_per_game: float
    deterministic_accuracy_pct: float
    speedup_vs_baseline: float = 1.0
    game_records: List[SingleGameRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "total_games": self.total_games,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate_pct": round(self.win_rate_pct, 2),
            "avg_moves_per_game": round(self.avg_moves_per_game, 2),
            "deterministic_move_ratio_pct": round(self.deterministic_move_ratio_pct, 2),
            "avg_latency_per_move_ms": round(self.avg_latency_per_move_ms, 4),
            "p50_latency_ms": round(self.p50_latency_ms, 4),
            "p95_latency_ms": round(self.p95_latency_ms, 4),
            "p99_latency_ms": round(self.p99_latency_ms, 4),
            "total_time_seconds": round(self.total_time_seconds, 3),
            "total_api_calls": self.total_api_calls,
            "avg_api_calls_per_game": round(self.avg_api_calls_per_game, 1),
            "deterministic_accuracy_pct": round(self.deterministic_accuracy_pct, 2),
            "speedup_vs_baseline": round(self.speedup_vs_baseline, 1),
        }


@dataclass
class BenchmarkResult:
    timestamp: str
    difficulty: str
    num_games: int
    metrics_by_agent: Dict[str, AgentBenchmarkMetrics]
    comparative_summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "difficulty": self.difficulty,
            "num_games": self.num_games,
            "metrics": {name: m.to_dict() for name, m in self.metrics_by_agent.items()},
            "summary": self.comparative_summary,
        }
