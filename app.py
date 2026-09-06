"""
Schnittebenen am Rucksackproblem – interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Drittes Stück der "Konzepte"-Reihe, Exakte-Suche-Linie: dasselbe 0/1-Rucksackproblem
wie branch-bound-demo, aber ein dritter Mechanismus - die LP-Relaxierung selbst wird
iterativ verschärft (Schnittebenen/Cover-Cuts), statt einen Suchbaum zu verzweigen
oder eine Tabelle zu füllen. Vorläufer für ein späteres branch-cut-demo, das dieses
Stück mit branch-bound-demo kombiniert.

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import cp_constants as C
from cp_bruteforce import solve_bruteforce
from cp_evaluation import stats_up_to_iteration
from cp_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from cp_scenario import generate_instance
from cp_solver import solve_cutting_planes
from cp_visualization import build_bound_chart, build_solution_chart

st.set_page_config(page_title="Schnittebenen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _compute_solve(n_items, capacity_fraction, correlation, seed):
    instance = generate_instance(n_items, capacity_fraction, correlation, seed)
    result = solve_cutting_planes(instance)
    true_optimum, _true_selection = solve_bruteforce(instance)
    return instance, result, true_optimum


st.title("✂️ Schnittebenen am Rucksackproblem")
st.markdown(
    """
Wieder dasselbe 0/1-Rucksackproblem wie in den ersten beiden Stücken dieser Reihe -
aber ein dritter, komplett anderer Ansatz: **Schnittebenen** verzweigen keinen
Suchbaum und füllen keine Tabelle, sondern verschärfen die LP-Relaxierung selbst,
Schritt für Schritt, bis entweder eine ganzzahlige (und damit bewiesen optimale)
Lösung herauskommt - oder die Methode ehrlich zugibt, dass sie allein nicht
weiterkommt. Genau **wie** das funktioniert, erklärt der aufgeklappte Abschnitt
direkt darunter - bevor weiter unten die Iterationen live dazu laufen.
"""
)
st.caption(
    "Anders als die Fall-Demos im Portfolio, die an einem Anwendungsfall mehrere Verfahren "
    "vergleichen, zeigt diese Demo - wie branch-bound-demo und dynamic-programming-demo, die "
    "ersten beiden Stücke der Exakte-Suche-Linie - **ein** Verfahren an einem wachsenden "
    "Beispiel. Diesmal kein vollständiger Kontrast: dieses Stück ist der **Vorläufer** für ein "
    "künftiges Branch-&-Cut-Stück, das Schnitte mit dem Verzweigen aus branch-bound-demo "
    "kombiniert, sobald die Schnitte hier allein nicht mehr ausreichen."
)

with st.expander("So funktionieren Schnittebenen", expanded=True):
    st.markdown(
        r"""
Die LP-Relaxierung (Bruchteile statt nur ganz/gar nicht) liefert eine optimistische
obere Schranke - aber meist eine fraktionale Lösung, kein gültiges Ganzzahl-Ergebnis.
Eine **Deckung** (cover) ist eine Teilmenge $C$ von Paketen, deren Gewichte zusammen
das Limit überschreiten - es können also nie alle Pakete aus $C$ gleichzeitig gewählt
werden. Daraus folgt eine Ungleichung, die **jede** zulässige Lösung erfüllt:

> *"Von den Paketen in dieser Deckung darf höchstens eines weniger gewählt werden,
> als die Deckung Pakete hat."*

Verletzt die aktuelle fraktionale Lösung diese Ungleichung, schneidet sie sie ab -
ohne eine einzige zulässige Ganzzahl-Lösung zu verlieren, daher "Schnittebene". Das
Verfahren wiederholt drei Schritte:

1. **LP lösen** (Kapazität + alle bisherigen Schnitte).
2. **Ganzzahlig?** Dann fertig - eine ganzzahlige Lösung einer gültig verschärften
   Relaxierung ist automatisch die bewiesene Ganzzahl-Optimallösung.
3. **Sonst**: eine verletzte Deckung suchen und als neuen Schnitt hinzufügen - weiter
   bei Schritt 1.

Im Diagramm weiter unten sehen Sie pro Iteration die aktuelle fraktionale Lösung (die
gerade gefundene Deckung farblich hervorgehoben) sowie, wie die Schranke mit jedem
Schnitt fällt. **Wichtig, und cutting-planes-demos eigene ehrliche Schwäche**: die
Suche nach einer verletzten Deckung ist selbst eine Heuristik, keine erschöpfende
Suche - sie findet nicht garantiert jeden existierenden Schnitt. Bricht sie ergebnislos
ab, bevor die Lösung ganzzahlig ist, bleibt eine Lücke zum wahren Optimum offen. Genau
das motiviert **Branch & Cut**: branchen (wie in branch-bound-demo), sobald die
Schnitte ausgehen.
        """
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
PRESET_HELP = {
    "Kleine Instanz (ein Schnitt reicht zum Optimum)": "5 Pakete - ein einziger Schnitt macht die LP-Lösung ganzzahlig, das bewiesene Optimum steht sofort fest.",
    "Schnitte allein reichen nicht (Branch & Cut nötig)": "Nur 4 Pakete, trotzdem findet die Trennungsheuristik keinen Schnitt mehr, bevor eine deutliche Lücke zum wahren Optimum bleibt.",
    "Viele kleine Schnitte (Bound nähert sich nur an)": "9 Pakete - mehrere, zunehmend kleinere Schnitte nähern die Schranke stark an, ohne sie ganz zu schließen.",
}
preset_cols = st.columns(len(C.PRESETS))
for i, name in enumerate(C.PRESETS.keys()):
    with preset_cols[i]:
        st.button(name, use_container_width=True, on_click=apply_preset, args=(name,), help=PRESET_HELP[name])

st.caption(
    "🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, "
    "um ein Szenario zu teilen."
)

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_items = st.slider("Anzahl Pakete", *bounds("n_items_slider"), key="n_items_slider")
    capacity_fraction = st.slider(
        "Gewichtslimit (Anteil der Gesamtmenge)", *bounds("capacity_fraction_slider"), key="capacity_fraction_slider"
    )
    correlation = st.slider(
        "Korrelation Wert/Gewicht", *bounds("correlation_slider"), key="correlation_slider",
        help="0 = Wert unabhängig vom Gewicht. 1 = wertvolle Pakete sind auch die schweren "
        "(Branch & Bounds Härtefall - siehe branch-bound-demo). Ob Schnitte allein bis zum "
        "Optimum reichen, hängt kaum systematisch an diesem Regler - probieren Sie verschiedene "
        "Seeds bei gleicher Korrelation aus.",
    )
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)

    st.button(
        "🎲 Neue Instanz generieren",
        use_container_width=True,
        on_click=randomize_seed,
        help="Würfelt einen neuen Zufalls-Seed für Paketgewichte und -werte.",
    )

sync_query_params(n_items, capacity_fraction, correlation, seed)

scenario_key = (int(n_items), capacity_fraction, correlation, int(seed))

with st.spinner("Löse die LP-Relaxierung iterativ..."):
    instance, result, true_optimum = _compute_solve(*scenario_key)

if "cp_step" not in st.session_state or st.session_state.get("cp_step_owner") != scenario_key:
    st.session_state["cp_step"] = len(result.iterations) - 1
    st.session_state["cp_step_owner"] = scenario_key

st.markdown("## 🎯 Die Schnittebenen in Aktion")

max_step = len(result.iterations) - 1
step_col, play_col = st.columns([5, 1])
with step_col:
    if max_step == 0:
        step = 0
        st.caption("Kein einziger Schnitt nötig oder möglich - kein Regler nötig.")
    else:
        step = st.slider(
            "Iteration", 0, max_step, key="cp_step",
            help="Ein Schritt = eine gelöste LP-Relaxierung, inklusive aller bis dahin "
            "hinzugefügten Schnitte.",
        )
with play_col:
    auto_play = st.button("▶️ Abspielen", use_container_width=True)

solution_slot = st.empty()
bound_slot = st.empty()


def _render(current_step):
    solution_slot.plotly_chart(
        build_solution_chart(instance, result, current_step),
        use_container_width=True, key=f"solution_{current_step}",
    )
    bound_slot.plotly_chart(
        build_bound_chart(result, true_optimum, current_step),
        use_container_width=True, key=f"bound_{current_step}",
    )


if auto_play:
    for s in range(max_step + 1):
        _render(s)
        time.sleep(0.4)
    step = max_step
else:
    _render(step)

live = stats_up_to_iteration(result, step)
lm1, lm2, lm3, lm4 = st.columns(4)
lm1.metric("Iteration", f"{live['iteration']} / {max_step}")
lm2.metric(
    "Schnitte bisher angewendet", f"{live['cuts_so_far']:,}",
    help="Jeder Schnitt ist eine zusätzliche Restriktion, die die LP-Relaxierung verschärft.",
)
lm3.metric(
    "Aktuelle LP-Schranke", f"{live['bound']:.2f}",
    help="Fällt mit jedem hinzugefügten Schnitt (oder bleibt gleich) - nie steigend.",
)
lm4.metric(
    "Ganzzahlig?", "Ja ✅" if live["is_integral"] else "Nein",
    help="Ja bedeutet: bewiesenes Optimum gefunden. Nein: die aktuelle LP-Lösung hat noch "
    "mindestens ein fraktionales Paket.",
)

if result.reached_integral:
    st.success(
        f"✅ Bewiesenes Optimum gefunden: **{result.best_value}** - nach {len(result.cuts)} "
        f"Schnitt(en) wurde die LP-Relaxierung ganzzahlig, keine Verzweigung nötig."
    )
else:
    gap = result.iterations[-1].bound - true_optimum
    st.warning(
        f"⚠️ Abbruch ohne bewiesenes Optimum: nach {len(result.cuts)} Schnitt(en) findet die "
        f"Trennungsheuristik keine weitere verletzte Deckung mehr, obwohl die LP-Lösung noch "
        f"fraktional ist. Verbleibende Lücke zur (per Bruteforce ermittelten) wahren "
        f"Optimallösung **{true_optimum}**: **{gap:.2f}** ({gap / true_optimum * 100:.1f}%). "
        f"Genau hier würde Branch & Cut ansetzen und auf dieser Schranke weiter verzweigen."
    )

st.markdown("---")

st.subheader("📐 Wie viele Schnitte braucht es wirklich?")
st.markdown(
    """
Live für Ihre aktuelle Instanz: wie viel schließt der erste Schnitt bereits, wie viel
bleibt am Ende offen?
"""
)

first_bound = result.iterations[0].bound
final_bound = result.iterations[-1].bound
gc1, gc2, gc3 = st.columns(3)
gc1.metric(
    "LP-Schranke ohne Schnitte", f"{first_bound:.2f}",
    help="Die reine LP-Relaxierung, wie in branch-bound-demo als Bound verwendet - noch bevor "
    "ein einziger Schnitt hinzukam.",
)
gc2.metric(
    f"LP-Schranke nach {len(result.cuts)} Schnitt(en)", f"{final_bound:.2f}",
    delta=f"{final_bound - first_bound:.2f}", delta_color="inverse",
    help="Wie stark alle gefundenen Schnitte zusammen die Schranke verschärft haben.",
)
gc3.metric(
    "Wahres Optimum (Bruteforce)", true_optimum,
    help="Unabhängig ermittelt (vollständige Enumeration) - der Maßstab, an dem sich die "
    "Schnitte messen lassen müssen.",
)

closed_fraction = (first_bound - final_bound) / (first_bound - true_optimum) if first_bound > true_optimum else 1.0
remaining_relative_gap = (final_bound - true_optimum) / true_optimum if true_optimum else 0.0

if result.reached_integral:
    st.success(
        f"✅ Die Schnitte haben die komplette Lücke geschlossen ({first_bound:.2f} → "
        f"{final_bound:.2f} = {true_optimum}) - kein Branchen nötig."
    )
elif remaining_relative_gap <= 0.02:
    st.info(
        f"ℹ️ Die Schnitte haben **{closed_fraction * 100:.0f}%** der ursprünglichen Lücke "
        f"geschlossen und liegen jetzt nur noch **{remaining_relative_gap * 100:.1f}%** über dem "
        f"wahren Optimum. Eine so scharfe Restschranke braucht Branch & Cut typischerweise nur "
        f"noch mit sehr wenig zusätzlicher Verzweigung zu schließen."
    )
else:
    st.info(
        f"ℹ️ Die Schnitte haben **{closed_fraction * 100:.0f}%** der ursprünglichen Lücke "
        f"geschlossen, aber es bleiben noch **{remaining_relative_gap * 100:.1f}%** über dem "
        f"wahren Optimum - reines Branch & Bound bräuchte ab dieser (noch recht lockeren) "
        f"Schranke weiterhin relevante Verzweigungsarbeit."
    )

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**0/1-Rucksackproblem** (identisch zu branch-bound-demo): gegeben $n$ Pakete mit
Gewichten $w_i$ und Werten $v_i$ sowie ein Gewichtslimit $W$, wähle eine Teilmenge, die
den Gesamtwert maximiert, ohne $W$ zu überschreiten.

**Deckung (cover)**: eine Teilmenge $C \subseteq \{1,\dots,n\}$ mit
$\sum_{i \in C} w_i > W$. Da niemals alle Pakete aus $C$ gleichzeitig gewählt werden
können, ist die **Cover-Ungleichung**

$$
\sum_{i \in C} x_i \le |C| - 1
$$

für jede zulässige 0/1-Lösung gültig - eine gültige Schnittebene. Sie schneidet die
aktuelle LP-Lösung $x^*$ genau dann ab, wenn $\sum_{i \in C} x_i^* > |C| - 1$
(**verletzt**).

**Trennungsheuristik** (aus $x^*$ eine verletzte, minimale Deckung konstruieren):
Pakete absteigend nach $x_i^*$ greedy aufnehmen, bis die Gewichtssumme $W$
überschreitet, dann Pakete aufsteigend nach $x_i^*$ probeweise entfernen, solange die
Restmenge weiterhin eine Deckung bleibt (minimal). Das ist eine Heuristik, keine
erschöpfende Suche - **Cover-Separation** (die exakte Version: finde die am stärksten
verletzte Deckung) ist selbst NP-schwer.

**LP-Solver**: sobald mehr als die Kapazitätsrestriktion aktiv ist, reicht die
einfache Greedy-Bruchrechnung aus branch-bound-demo nicht mehr - `cp_lp.py` löst das
allgemeine lineare Programm über `scipy.optimize.linprog` (HiGHS-Solver).

**Gomory-Schnitte** (nicht hier verwendet, zum Vergleich): allgemeiner anwendbar auf
jedes ganzzahlige lineare Programm, nicht nur Rucksackprobleme - hergeleitet aus den
Bruchteilen der Simplex-Tableau-Zeilen der aktuellen LP-Lösung. Mathematisch
eleganter und allgemeiner, aber algebraisch weit weniger anschaulich als
Cover-Ungleichungen, deren Bedeutung ("diese Pakete passen nicht alle gleichzeitig
hinein") sich direkt aus dem Problem selbst ablesen lässt.

Implementiert in `cp_lp.py` (LP-Solver-Wrapper), `cp_cuts.py`
(Trennungsheuristik) und `cp_solver.py` (Hauptschleife).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
