"""Kennzahlen aus einem CuttingPlaneResult."""


def n_cuts(result):
    return len(result.cuts)


def bound_gap(result, true_optimum):
    """Verbleibender Abstand zwischen der zuletzt erreichten LP-Schranke und dem
    wahren (z. B. per Bruteforce ermittelten) Optimum - 0, sobald ganzzahlig
    erreicht wurde."""
    return result.iterations[-1].bound - true_optimum


def stats_up_to_iteration(result, step):
    """Kennzahlen für den Stand nach `step` Iterationen (0-indiziert, wie
    result.iterations) - treibt die Schritt-für-Schritt-Ansicht in der App."""
    it = result.iterations[step]
    return {
        "iteration": step,
        "bound": it.bound,
        "is_integral": it.is_integral,
        "cover": it.cover,
        "violation": it.violation,
        "cuts_so_far": step,  # Iteration 0 hat noch keinen Schnitt angewendet
    }
