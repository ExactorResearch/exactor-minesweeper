"""
Quick 1-Click Benchmark Runner: Exactor-Accelerator vs Pure JEV
"""

import sys
import os

# Ensure exactor_minesweeper and exactor-jev are accessible in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "exactor-jev")))

from exactor_minesweeper.cli import main

if __name__ == "__main__":
    # Default to running benchmark
    if len(sys.argv) == 1:
        sys.argv.append("--benchmark")
    main()
