"""
Interactive Terminal CLI for Exactor Minesweeper & Quick Benchmarking.
"""

import argparse
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
from exactor_minesweeper.core.board import MinesweeperBoard, Difficulty
from exactor_minesweeper.agents.exactor_agent import ExactorAcceleratorAgent
from exactor_minesweeper.agents.jev_pure_agent import JevPureAgent
from exactor_minesweeper.agents.heuristic_agent import HeuristicAgent
from exactor_minesweeper.benchmark.runner import BenchmarkRunner
from exactor_minesweeper.benchmark.reporter import BenchmarkReporter


def print_cli_board(board: MinesweeperBoard):
    grid = board.get_visible_grid()
    print("\n   " + " ".join(f"{c:2d}" for c in range(board.width)))
    print("  +" + "--" * board.width + "-+")
    for r in range(board.height):
        row_str = []
        for c in range(board.width):
            val = grid[r][c]
            if val == -1:
                row_str.append(" .")
            elif val == -2:
                row_str.append(" F")
            elif val == 0:
                row_str.append("  ")
            else:
                row_str.append(f" {val}")
        print(f"{r:2d}|" + "".join(row_str) + " |")
    print("  +" + "--" * board.width + "-+\n")


def play_cli():
    print("=========================================================")
    print("   EXACTOR MINESWEEPER: Interactive CLI Game")
    print("=========================================================")
    board = MinesweeperBoard(difficulty=Difficulty.BEGINNER)
    print_cli_board(board)

    while not board.is_over:
        cmd = input("Enter move (e.g., 'r 3 4' to reveal, 'f 3 4' to flag, 'ai' for Exactor move, 'q' to quit): ").strip()
        if not cmd:
            continue
        if cmd.lower() == 'q':
            print("Game terminated.")
            break
        elif cmd.lower() == 'ai':
            agent = ExactorAcceleratorAgent()
            action = agent.select_action(board)
            print(f"🤖 Exactor Action: {action.action_type.value} at ({action.row}, {action.col}) | Latency: {action.metadata.get('latency_ms', 0):.4f} ms")
            print(f"   Reasoning: {action.explanation}")
            if action.action_type.value == "REVEAL":
                status, _ = board.reveal(action.row, action.col)
            else:
                board.set_flag(action.row, action.col, True)
            print_cli_board(board)
        else:
            parts = cmd.split()
            if len(parts) == 3:
                act, r_str, c_str = parts[0].lower(), parts[1], parts[2]
                try:
                    r, c = int(r_str), int(c_str)
                    if act == 'r':
                        status, _ = board.reveal(r, c)
                    elif act == 'f':
                        board.toggle_flag(r, c)
                    print_cli_board(board)
                except ValueError:
                    print("Invalid coordinates.")
            else:
                print("Format: 'r <row> <col>' or 'f <row> <col>' or 'ai'")

    if board.is_victory:
        print("🏆 VICTORY! All mines cleared!")
    elif board.is_over:
        print("💥 BOOM! Game Over.")


def main():
    parser = argparse.ArgumentParser(description="Exactor Minesweeper CLI & Benchmark Tool")
    parser.add_argument("--benchmark", action="store_true", help="Run automated comparative benchmark")
    parser.add_argument("--games", type=int, default=25, help="Number of test games for benchmark")
    parser.add_argument("--difficulty", type=str, default="beginner", choices=["beginner", "intermediate", "expert"])
    parser.add_argument("--export-md", type=str, default="benchmark_report.md", help="Path to export markdown report")
    parser.add_argument("--export-json", type=str, default="benchmark_results.json", help="Path to export JSON metrics")
    parser.add_argument("--play", action="store_true", help="Start interactive CLI game")

    args = parser.parse_args()

    if args.benchmark or not args.play:
        diff = Difficulty(args.difficulty)
        print(f"\n🚀 Running automated benchmark ({args.games} boards, difficulty: {args.difficulty.upper()})...\n")
        runner = BenchmarkRunner(difficulty=diff)
        result = runner.run_benchmark(num_games=args.games)

        BenchmarkReporter.print_terminal_summary(result)
        BenchmarkReporter.export_json(result, file_path=args.export_json)

        md_content = BenchmarkReporter.to_markdown(result)
        with open(args.export_md, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"📄 Markdown report saved to: {args.export_md}")
        print(f"📊 JSON results saved to: {args.export_json}\n")
    else:
        play_cli()


if __name__ == "__main__":
    main()
