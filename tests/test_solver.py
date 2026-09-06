import pytest

from cp_bruteforce import solve_bruteforce
from cp_constants import PRESETS
from cp_scenario import KnapsackInstance, generate_instance
from cp_solver import solve_cutting_planes


def _greedy_fractional_bound(instance):
    """Unabhängig nachgerechnete LP-Relaxierungs-Schranke (reine Kapazitäts-
    restriktion, kein Schnitt) - dieselbe Formel wie branch-bound-demo/bb_bound.py,
    hier neu geschrieben statt importiert (eigenständiges Repo)."""
    order = sorted(range(instance.n_items), key=lambda i: instance.values[i] / instance.weights[i], reverse=True)
    bound = 0.0
    capacity = instance.capacity
    for idx in order:
        w, v = instance.weights[idx], instance.values[idx]
        if w <= capacity:
            capacity -= w
            bound += v
        else:
            bound += v * (capacity / w)
            break
    return bound


def test_iteration_zero_matches_the_plain_lp_relaxation_bound():
    for seed in range(15):
        instance = generate_instance(n_items=8, capacity_fraction=0.5, correlation=seed % 5 / 4, seed=seed)
        result = solve_cutting_planes(instance)
        expected = _greedy_fractional_bound(instance)
        assert result.iterations[0].bound == pytest.approx(expected, abs=1e-6), f"seed={seed}"


def test_bound_is_never_increasing_across_iterations():
    for seed in range(20):
        instance = generate_instance(n_items=9, capacity_fraction=0.5, correlation=0.4, seed=seed)
        result = solve_cutting_planes(instance)
        bounds = [it.bound for it in result.iterations]
        for a, b in zip(bounds, bounds[1:]):
            assert b <= a + 1e-9


def test_reached_integral_matches_bruteforce_optimum():
    for seed in range(30):
        instance = generate_instance(n_items=8, capacity_fraction=0.5, correlation=seed % 5 / 4, seed=seed)
        result = solve_cutting_planes(instance)
        if not result.reached_integral:
            continue
        true_best, _ = solve_bruteforce(instance)
        assert result.best_value == true_best, f"seed={seed}"
        weight = sum(w for w, take in zip(instance.weights, result.best_selection) if take)
        assert weight <= instance.capacity


def test_final_bound_never_undercuts_the_true_optimum():
    # Jede gültige Schnittebene lässt das Optimum unberührt - die LP-Schranke darf
    # es also niemals unterschreiten, egal ob ganzzahlig erreicht wird oder nicht.
    for seed in range(20):
        instance = generate_instance(n_items=8, capacity_fraction=0.5, correlation=seed % 5 / 4, seed=seed)
        result = solve_cutting_planes(instance)
        true_best, _ = solve_bruteforce(instance)
        assert result.iterations[-1].bound >= true_best - 1e-6, f"seed={seed}"


def test_matches_hand_computed_tiny_instance():
    instance = KnapsackInstance(weights=(2, 3, 4, 5), values=(3, 4, 5, 6), capacity=5, correlation=0.0)
    result = solve_cutting_planes(instance)
    true_best, _ = solve_bruteforce(instance)
    assert true_best == 7
    if result.reached_integral:
        assert result.best_value == 7


def test_max_iterations_cap_is_honored():
    instance = generate_instance(n_items=12, capacity_fraction=0.5, correlation=0.5, seed=1)
    result = solve_cutting_planes(instance, max_iterations=3)
    assert len(result.iterations) <= 3


@pytest.mark.parametrize("name", list(PRESETS.keys()))
def test_presets_behave_as_documented(name):
    preset = PRESETS[name]
    instance = generate_instance(**preset)
    result = solve_cutting_planes(instance)
    if name == "Kleine Instanz (ein Schnitt reicht zum Optimum)":
        assert result.reached_integral
        assert len(result.cuts) == 1
    elif name == "Schnitte allein reichen nicht (Branch & Cut nötig)":
        assert not result.reached_integral
    elif name == "Viele kleine Schnitte (Bound nähert sich nur an)":
        assert len(result.cuts) >= 5
