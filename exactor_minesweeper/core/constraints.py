"""
Constraint Satisfaction & Exact Boolean SAT Engine for Minesweeper.
Extracts linear equations, performs subset resolution, and computes exact combinatorial probabilities.
"""

from typing import List, Tuple, Set, Dict, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import itertools


@dataclass(frozen=True)
class Constraint:
    """Represents equation: sum(variables) == target, where variables in {0, 1}."""
    variables: frozenset[Tuple[int, int]]
    target: int

    def __post_init__(self):
        if not isinstance(self.variables, frozenset):
            object.__setattr__(self, 'variables', frozenset(self.variables))


class ExactSATReduction:
    """
    Direct deterministic Boolean reduction:
    - Single-cell saturation & zero bounds
    - Pairwise subset difference deduction
    - Overlap min-max bounds
    """

    @staticmethod
    def simplify_constraints(
        constraints: List[Constraint],
    ) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]], List[Constraint]]:
        """
        Iteratively simplifies constraints using exact boolean subset algebra.
        Returns:
            guaranteed_safe: set of (r, c) coordinates that are 100% SAFE
            guaranteed_mines: set of (r, c) coordinates that are 100% MINES
            residual_constraints: simplified active constraints
        """
        safe_cells: Set[Tuple[int, int]] = set()
        mine_cells: Set[Tuple[int, int]] = set()

        active = [c for c in constraints if len(c.variables) > 0]
        changed = True

        while changed:
            changed = False
            new_active: List[Constraint] = []
            seen_constraints: Set[Tuple[frozenset[Tuple[int, int]], int]] = set()

            for c in active:
                # Remove already identified safe and mine variables
                vars_left = set(c.variables) - safe_cells
                target_left = c.target

                # For every known mine in this constraint, decrement target
                known_mines_in_c = vars_left.intersection(mine_cells)
                if known_mines_in_c:
                    vars_left -= known_mines_in_c
                    target_left -= len(known_mines_in_c)
                    changed = True

                if len(vars_left) == 0:
                    continue

                # Rule 1: Target is 0 -> All variables are SAFE
                if target_left == 0:
                    for var in vars_left:
                        if var not in safe_cells:
                            safe_cells.add(var)
                            changed = True
                    continue

                # Rule 2: Target equals variable count -> All variables are MINES
                if target_left == len(vars_left):
                    for var in vars_left:
                        if var not in mine_cells:
                            mine_cells.add(var)
                            changed = True
                    continue

                # Rule 3: Target out of bounds (invalid branch)
                if target_left < 0 or target_left > len(vars_left):
                    continue

                c_tuple = (frozenset(vars_left), target_left)
                if c_tuple not in seen_constraints:
                    seen_constraints.add(c_tuple)
                    new_active.append(Constraint(frozenset(vars_left), target_left))

            # Pairwise subset resolution: if V1 subset of V2 => (V2 \ V1) = (T2 - T1)
            derived: List[Constraint] = []
            for i in range(len(new_active)):
                c1 = new_active[i]
                for j in range(len(new_active)):
                    if i == j:
                        continue
                    c2 = new_active[j]
                    if c1.variables.issubset(c2.variables):
                        diff_vars = c2.variables - c1.variables
                        diff_target = c2.target - c1.target
                        if len(diff_vars) > 0 and 0 <= diff_target <= len(diff_vars):
                            diff_tuple = (frozenset(diff_vars), diff_target)
                            if diff_tuple not in seen_constraints:
                                seen_constraints.add(diff_tuple)
                                derived.append(Constraint(frozenset(diff_vars), diff_target))
                                changed = True

            active = new_active + derived

        return safe_cells, mine_cells, active


class BoardConstraintSystem:
    """
    Extracts all active frontier constraints and solves them using
    Fast-Path boolean reduction and Exact Component SAT enumeration.
    """

    def __init__(self, board_visible: List[List[int]], width: int, height: int):
        self.grid = board_visible
        self.width = width
        self.height = height
        self.constraints: List[Constraint] = []
        self._build_constraints()

    def _get_neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        neighbors = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    neighbors.append((nr, nc))
        return neighbors

    def _build_constraints(self) -> None:
        """Scan visible grid and build equations for all clue cells."""
        for r in range(self.height):
            for c in range(self.width):
                clue = self.grid[r][c]
                if clue > 0:
                    hidden_vars: List[Tuple[int, int]] = []
                    flag_count = 0
                    for nr, nc in self._get_neighbors(r, c):
                        val = self.grid[nr][nc]
                        if val == -1:  # Hidden unflagged
                            hidden_vars.append((nr, nc))
                        elif val == -2:  # Flagged
                            flag_count += 1
                    
                    effective_target = clue - flag_count
                    if hidden_vars and effective_target >= 0:
                        self.constraints.append(
                            Constraint(frozenset(hidden_vars), effective_target)
                        )

    def solve_fast_path(self) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Sub-millisecond algebraic deduction.
        Returns guaranteed safe cells and guaranteed mine cells.
        """
        safe, mines, _ = ExactSATReduction.simplify_constraints(self.constraints)
        return safe, mines

    def solve_full_combinatorial(
        self,
        max_component_size: int = 12,
    ) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]], Dict[Tuple[int, int], float]]:
        """
        Full Neuro-Symbolic Exact SAT solver.
        1. Fast-Path Boolean algebraic reduction
        2. Connected Component partition
        3. Exact binary solution space enumeration for calibrated marginal probabilities
        Returns:
            guaranteed_safe: Set of coordinates with P(Mine) = 0.0
            guaranteed_mines: Set of coordinates with P(Mine) = 1.0
            probabilities: Dict mapping (r, c) to P(Mine) in [0.0, 1.0]
        """
        safe_cells, mine_cells, residual = ExactSATReduction.simplify_constraints(self.constraints)
        
        # If all frontier variables were resolved by Fast Path, return immediately!
        probabilities: Dict[Tuple[int, int], float] = {}
        for s in safe_cells:
            probabilities[s] = 0.0
        for m in mine_cells:
            probabilities[m] = 1.0

        if not residual:
            return safe_cells, mine_cells, probabilities

        # Partition residual constraints into independent connected components
        components = self._partition_into_components(residual)

        for comp_vars, comp_constraints in components:
            comp_list = list(comp_vars)
            n_vars = len(comp_list)

            # For tractable components, do exact binary assignment enumeration
            if n_vars <= max_component_size:
                var_to_idx = {var: i for i, var in enumerate(comp_list)}
                valid_solutions_count = 0
                mine_counts = [0] * n_vars

                for assignment in itertools.product([0, 1], repeat=n_vars):
                    # Check if assignment satisfies all constraints in this component
                    is_valid = True
                    for c in comp_constraints:
                        current_sum = sum(assignment[var_to_idx[v]] for v in c.variables)
                        if current_sum != c.target:
                            is_valid = False
                            break
                    
                    if is_valid:
                        valid_solutions_count += 1
                        for i in range(n_vars):
                            if assignment[i] == 1:
                                mine_counts[i] += 1

                if valid_solutions_count > 0:
                    for i, var in enumerate(comp_list):
                        prob = mine_counts[i] / valid_solutions_count
                        probabilities[var] = prob
                        if prob == 0.0:
                            safe_cells.add(var)
                        elif prob == 1.0:
                            mine_cells.add(var)
            else:
                # For very large components, approximate via constraint relaxation / uniform prior
                for c in comp_constraints:
                    c_prob = c.target / len(c.variables)
                    for v in c.variables:
                        if v not in probabilities:
                            probabilities[v] = c_prob
                        else:
                            probabilities[v] = (probabilities[v] + c_prob) / 2.0

        return safe_cells, mine_cells, probabilities

    def _partition_into_components(
        self,
        constraints: List[Constraint],
    ) -> List[Tuple[Set[Tuple[int, int]], List[Constraint]]]:
        """Disjoint set clustering of constraints and variables."""
        if not constraints:
            return []

        all_vars = set().union(*(c.variables for c in constraints))
        adj: Dict[Tuple[int, int], Set[Tuple[int, int]]] = defaultdict(set)

        for c in constraints:
            var_list = list(c.variables)
            for i in range(len(var_list)):
                for j in range(i + 1, len(var_list)):
                    adj[var_list[i]].add(var_list[j])
                    adj[var_list[j]].add(var_list[i])

        visited: Set[Tuple[int, int]] = set()
        components: List[Tuple[Set[Tuple[int, int]], List[Constraint]]] = []

        for v in all_vars:
            if v not in visited:
                comp_vars: Set[Tuple[int, int]] = set()
                queue = [v]
                visited.add(v)
                comp_vars.add(v)

                while queue:
                    curr = queue.pop(0)
                    for neighbor in adj[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            comp_vars.add(neighbor)
                            queue.append(neighbor)

                comp_constraints = [
                    c for c in constraints if c.variables.issubset(comp_vars)
                ]
                components.append((comp_vars, comp_constraints))

        return components
