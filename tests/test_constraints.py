"""
Unit tests for Constraint SAT Solver and Boolean Reduction.
"""

import pytest
from exactor_minesweeper.core.constraints import Constraint, ExactSATReduction, BoardConstraintSystem


def test_rule_1_saturation():
    """If target == len(vars), all variables are guaranteed MINES."""
    c = Constraint(frozenset([(0, 1), (0, 2)]), 2)
    safe, mines, _ = ExactSATReduction.simplify_constraints([c])
    assert len(safe) == 0
    assert mines == {(0, 1), (0, 2)}


def test_rule_2_zero_effective():
    """If target == 0, all variables are guaranteed SAFE."""
    c = Constraint(frozenset([(1, 1), (1, 2), (1, 3)]), 0)
    safe, mines, _ = ExactSATReduction.simplify_constraints([c])
    assert safe == {(1, 1), (1, 2), (1, 3)}
    assert len(mines) == 0


def test_rule_3_subset_difference():
    """
    C1: (A, B) = 1
    C2: (A, B, C) = 1
    Derived: C = 0 (Safe!)
    """
    c1 = Constraint(frozenset([(0, 0), (0, 1)]), 1)
    c2 = Constraint(frozenset([(0, 0), (0, 1), (0, 2)]), 1)
    safe, mines, residual = ExactSATReduction.simplify_constraints([c1, c2])
    assert (0, 2) in safe


def test_component_sat_probabilities():
    """
    C1: (A, B) = 1
    No subset relation.
    Both A and B should have marginal P(Mine) = 0.5.
    """
    grid = [
        [1, -1],
        [-1, -1]
    ]
    # (0, 0) has clue 1 touching (0, 1) and (1, 0) and (1, 1)
    cs = BoardConstraintSystem(grid, width=2, height=2)
    safe, mines, probs = cs.solve_full_combinatorial()
    assert (0, 1) in probs
    assert probs[(0, 1)] == pytest.approx(1/3, 0.01)
