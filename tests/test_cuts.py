from itertools import product

from cp_scenario import generate_instance
from cp_solver import solve_cutting_planes


def test_every_found_cover_actually_exceeds_capacity():
    for seed in range(20):
        instance = generate_instance(n_items=8, capacity_fraction=0.5, correlation=seed % 5 / 4, seed=seed)
        result = solve_cutting_planes(instance)
        for cover in result.cuts:
            weight = sum(instance.weights[i] for i in cover)
            assert weight > instance.capacity, f"seed={seed} cover={cover}"


def test_every_found_cover_is_minimal():
    # Entfernen jedes einzelnen Pakets aus einer gefundenen Deckung muss sie wieder
    # zulässig machen (sum weights <= capacity) - sonst wäre sie nicht minimal.
    for seed in range(20):
        instance = generate_instance(n_items=8, capacity_fraction=0.5, correlation=seed % 5 / 4, seed=seed)
        result = solve_cutting_planes(instance)
        for cover in result.cuts:
            for i in cover:
                reduced_weight = sum(instance.weights[j] for j in cover if j != i)
                assert reduced_weight <= instance.capacity, f"seed={seed} cover={cover} item={i}"


def test_every_feasible_selection_satisfies_every_found_cut():
    # Cover-Ungleichungen müssen für JEDE zulässige 0/1-Lösung gelten, nicht nur für
    # die Optimallösung - kleine Instanz, damit vollständige Enumeration praktikabel ist.
    for seed in range(10):
        instance = generate_instance(n_items=7, capacity_fraction=0.5, correlation=0.3, seed=seed)
        result = solve_cutting_planes(instance)
        for selection in product([False, True], repeat=instance.n_items):
            weight = sum(w for w, take in zip(instance.weights, selection) if take)
            if weight > instance.capacity:
                continue
            for cover in result.cuts:
                count_selected = sum(1 for i in cover if selection[i])
                assert count_selected <= len(cover) - 1, f"seed={seed} cover={cover} selection={selection}"


def test_no_cover_is_added_twice():
    for seed in range(20):
        instance = generate_instance(n_items=9, capacity_fraction=0.5, correlation=0.6, seed=seed)
        result = solve_cutting_planes(instance)
        assert len(result.cuts) == len(set(result.cuts))
