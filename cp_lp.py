"""Dünner Wrapper um scipy.optimize.linprog - löst die LP-Relaxierung des
Rucksackproblems plus beliebig viele zusätzliche Schnittebenen-Ungleichungen.

Sobald mehr als die reine Kapazitätsrestriktion aktiv ist, reicht die einfache
Greedy-Bruchteilsrechnung (wie in branch-bound-demo/bb_bound.py) nicht mehr - das ist
dann ein echtes lineares Programm mit mehreren Restriktionen, für das ein
allgemeiner LP-Solver nötig ist, genau wie in echten MIP-Solvern (CPLEX, Gurobi)."""

from scipy.optimize import linprog


def solve_lp(instance, cuts):
    """cuts: Liste bereits hinzugefügter Deckungen (jede eine Tupel-Menge von
    Paket-Indizes) - jede erzeugt eine Restriktion sum_{i in cover} x_i <= |cover|-1."""
    n = instance.n_items
    c = [-v for v in instance.values]  # linprog minimiert, wir wollen maximieren
    a_ub = [list(instance.weights)]
    b_ub = [float(instance.capacity)]
    for cover in cuts:
        row = [1.0 if i in cover else 0.0 for i in range(n)]
        a_ub.append(row)
        b_ub.append(float(len(cover) - 1))

    result = linprog(c, A_ub=a_ub, b_ub=b_ub, bounds=[(0, 1)] * n, method="highs")
    if not result.success:
        raise RuntimeError(f"LP-Relaxierung nicht lösbar: {result.message}")

    x = tuple(float(xi) for xi in result.x)
    bound = float(sum(v * xi for v, xi in zip(instance.values, x)))
    return x, bound
