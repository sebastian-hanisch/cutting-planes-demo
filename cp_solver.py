"""Iteratives Schnittebenenverfahren: LP lösen -> ganzzahlig? fertig. Sonst: verletzte
Deckung suchen, als Schnitt hinzufügen, von vorn. Bricht ehrlich ohne bewiesenes
Optimum ab, wenn die Trennungsheuristik keinen verletzten Schnitt mehr findet - siehe
cp_cuts.py für die Begründung, warum das keine Fehlfunktion, sondern das eigentliche
Thema dieser Demo ist."""

from dataclasses import dataclass

from cp_constants import EPS, MAX_CUT_ITERATIONS
from cp_cuts import find_violated_cover
from cp_lp import solve_lp


@dataclass(frozen=True)
class Iteration:
    x: tuple
    bound: float
    is_integral: bool
    cover: object  # Tupel von Paket-Indizes, oder None
    violation: float


@dataclass
class CuttingPlaneResult:
    iterations: tuple
    cuts: tuple
    reached_integral: bool
    best_value: object  # int, oder None falls nicht ganzzahlig erreicht
    best_selection: object  # Tupel[bool], oder None


def _is_integral(x, eps=EPS):
    return all(min(xi, 1.0 - xi) <= eps for xi in x)


def solve_cutting_planes(instance, max_iterations=MAX_CUT_ITERATIONS):
    cuts = []
    iterations = []

    for _ in range(max_iterations):
        x, bound = solve_lp(instance, cuts)

        if _is_integral(x):
            iterations.append(Iteration(x, bound, True, None, 0.0))
            break

        cover = find_violated_cover(instance, x, set(cuts))
        if cover is None:
            iterations.append(Iteration(x, bound, False, None, 0.0))
            break

        violation = sum(x[i] for i in cover) - (len(cover) - 1)
        iterations.append(Iteration(x, bound, False, cover, violation))
        cuts.append(cover)

    last = iterations[-1]
    if last.is_integral:
        best_selection = tuple(round(xi) == 1 for xi in last.x)
        best_value = sum(v for v, take in zip(instance.values, best_selection) if take)
    else:
        best_selection = None
        best_value = None

    return CuttingPlaneResult(
        iterations=tuple(iterations),
        cuts=tuple(cuts),
        reached_integral=last.is_integral,
        best_value=best_value,
        best_selection=best_selection,
    )
