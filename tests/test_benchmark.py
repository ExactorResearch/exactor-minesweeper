"""
Unit tests for Benchmark Suite and Metrics calculation.
"""

import pytest
from exactor_minesweeper.core.board import Difficulty
from exactor_minesweeper.agents.exactor_agent import ExactorAcceleratorAgent
from exactor_minesweeper.agents.heuristic_agent import HeuristicAgent
from exactor_minesweeper.benchmark.runner import BenchmarkRunner
from exactor_minesweeper.benchmark.reporter import BenchmarkReporter


def test_benchmark_runner_execution():
    agents = [
        ExactorAcceleratorAgent(),
        HeuristicAgent(),
    ]
    runner = BenchmarkRunner(agents=agents, difficulty=Difficulty.BEGINNER)
    result = runner.run_benchmark(num_games=3, start_seed=100)

    assert result.num_games == 3
    assert "Exactor-Accelerator (Neuro-Symbolic)" in result.metrics_by_agent
    assert "Standard Heuristic (1st Order)" in result.metrics_by_agent

    exactor_metrics = result.metrics_by_agent["Exactor-Accelerator (Neuro-Symbolic)"]
    assert exactor_metrics.total_games == 3
    assert exactor_metrics.avg_latency_per_move_ms >= 0.0

    # Test markdown report generation
    md = BenchmarkReporter.to_markdown(result)
    assert "# 🚀 Benchmark Comparative Report" in md
