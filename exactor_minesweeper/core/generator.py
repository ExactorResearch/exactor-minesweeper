"""
Dataset Generator for Minesweeper Boolean Rule Mining & Invariant Extraction.
Generates tabular data representing cell frontier contexts and ground-truth mine status.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from exactor_minesweeper.core.board import MinesweeperBoard, Difficulty
from exactor_minesweeper.core.constraints import BoardConstraintSystem


class MinesweeperDataGenerator:
    """Generates synthetic tabular datasets of Minesweeper frontier states for rule learning."""

    @staticmethod
    def generate_training_data(
        num_games: int = 50,
        difficulty: Difficulty = Difficulty.BEGINNER,
        seed: int = 42,
    ) -> pd.DataFrame:
        """
        Plays simulated games to harvest frontier cell features and labels.
        """
        rows: List[Dict[str, Any]] = []
        rng = np.random.default_rng(seed)

        for g_idx in range(num_games):
            board = MinesweeperBoard(difficulty=difficulty, seed=int(rng.integers(1, 100000)))
            # Perform safe first click in the center
            init_r, init_c = board.height // 2, board.width // 2
            board.reveal(init_r, init_c)

            # Advance game state with partial reveals
            steps = 0
            while not board.is_over and steps < 30:
                steps += 1
                cs = BoardConstraintSystem(board.get_visible_grid(), board.width, board.height)
                safe_cells, mine_cells, probs = cs.solve_full_combinatorial()

                frontier_hidden, frontier_clues = board.get_frontier()
                if not frontier_hidden:
                    break

                # Extract features for all frontier cells
                for (r, c) in frontier_hidden:
                    ground_truth_is_mine = 1 if board.mines_grid[r][c] else 0
                    
                    # Compute neighborhood metrics
                    adj_clues = []
                    adj_eff_clues = []
                    adj_hidden_counts = []
                    for nr, nc in board.get_neighbors(r, c):
                        if board.revealed_grid[nr][nc] and board.clues_grid[nr][nc] > 0:
                            clue = board.clues_grid[nr][nc]
                            flags = sum(1 for nnr, nnc in board.get_neighbors(nr, nc) if board.flagged_grid[nnr][nnc])
                            hiddens = sum(1 for nnr, nnc in board.get_neighbors(nr, nc) if not board.revealed_grid[nnr][nnc] and not board.flagged_grid[nnr][nnc])
                            adj_clues.append(clue)
                            adj_eff_clues.append(clue - flags)
                            adj_hidden_counts.append(hiddens)

                    if not adj_clues:
                        continue

                    min_eff = min(adj_eff_clues)
                    max_eff = max(adj_eff_clues)
                    min_hiddens = min(adj_hidden_counts)
                    
                    # Boolean predicates
                    has_zero_eff = 1 if min_eff == 0 else 0
                    has_saturated = 1 if any(eff == hc for eff, hc in zip(adj_eff_clues, adj_hidden_counts)) else 0
                    min_diff = min(hc - eff for eff, hc in zip(adj_eff_clues, adj_hidden_counts))

                    rows.append({
                        "adj_clue_count": len(adj_clues),
                        "min_effective_clue": min_eff,
                        "max_effective_clue": max_eff,
                        "min_hidden_neighbors": min_hiddens,
                        "has_zero_effective_clue": has_zero_eff,
                        "has_saturated_clue": has_saturated,
                        "min_slack": min_diff,
                        "is_corner": 1 if (r in (0, board.height - 1) and c in (0, board.width - 1)) else 0,
                        "is_border": 1 if (r in (0, board.height - 1) or c in (0, board.width - 1)) else 0,
                        "is_mine": ground_truth_is_mine,
                    })

                # Make next move
                if safe_cells:
                    # Reveal all safe cells
                    for sr, sc in list(safe_cells)[:3]:
                        board.reveal(sr, sc)
                elif mine_cells:
                    # Flag all mine cells
                    for mr, mc in list(mine_cells)[:3]:
                        board.set_flag(mr, mc, True)
                else:
                    # Guess lowest prob cell
                    best_cell = min(probs.keys(), key=lambda k: probs[k]) if probs else frontier_hidden[0]
                    board.reveal(best_cell[0], best_cell[1])

        df = pd.DataFrame(rows)
        # Drop duplicates for clean boolean invariant mining
        df = df.drop_duplicates().reset_index(drop=True)
        return df
