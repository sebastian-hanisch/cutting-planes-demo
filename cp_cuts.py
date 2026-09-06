"""Greedy-Trennungsheuristik: findet aus der aktuellen fraktionalen LP-Lösung eine
verletzte, minimale Deckung (cover) - oder gibt ehrlich auf, wenn sie keine findet.

Eine Deckung ist eine Teilmenge C von Paketen mit sum(weights in C) > Kapazität - es
können also nie alle Pakete aus C gleichzeitig gewählt werden. Die daraus folgende
Ungleichung sum_{i in C} x_i <= |C| - 1 ist für JEDE zulässige 0/1-Lösung gültig,
schneidet aber die aktuelle fraktionale LP-Lösung nur ab, wenn diese sie verletzt
(sum_{i in C} x_i* > |C| - 1).

Diese Trennungsheuristik ist bewusst einfach (greedy statt exakt) - Cover-Separation
ist selbst ein kombinatorisches Optimierungsproblem, dessen exakte Lösung so teuer wie
das Ursprungsproblem sein kann. Dass sie nicht jeden existierenden Schnitt findet, ist
diese Demo eigene, ehrliche Schwäche."""

from cp_constants import EPS


def find_violated_cover(instance, x, existing_covers, eps=EPS):
    n = instance.n_items
    order = sorted(range(n), key=lambda i: x[i], reverse=True)

    cover = []
    total_weight = 0
    for i in order:
        if x[i] <= eps:
            break
        cover.append(i)
        total_weight += instance.weights[i]
        if total_weight > instance.capacity:
            break

    if total_weight <= instance.capacity:
        return None  # aus den von der LP "gewollten" Paketen lässt sich keine Deckung bauen

    cover_set = set(cover)
    for i in sorted(cover, key=lambda i: x[i]):  # am wenigsten gewollt zuerst entfernen
        if i not in cover_set:
            continue
        trial = cover_set - {i}
        trial_weight = sum(instance.weights[j] for j in trial)
        if trial_weight > instance.capacity:  # bleibt ohne i eine Deckung -> i war redundant
            cover_set = trial

    cover_final = tuple(sorted(cover_set))
    violation = sum(x[i] for i in cover_final) - (len(cover_final) - 1)
    if violation <= eps or cover_final in existing_covers:
        return None
    return cover_final
