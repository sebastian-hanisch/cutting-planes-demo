# Schnittebenen am Rucksackproblem – Streamlit-Demo

Drittes Stück der "Konzepte"-Reihe für die Website "Sebastian Hanisch – Operations
Research und Machine Learning", **Exakte-Suche-Linie**: dasselbe 0/1-Rucksackproblem
wie [branch-bound-demo](../branch-bound-demo) und
[dynamic-programming-demo](../dynamic-programming-demo), aber ein dritter Mechanismus
- die LP-Relaxierung selbst wird iterativ verschärft (Schnittebenen/Cover-Cuts),
statt einen Suchbaum zu verzweigen oder eine Tabelle zu füllen. Kein vollständiger
Kontrast wie `dynamic-programming-demo`, sondern ein **Vorläufer**: dieses Stück
bereitet ein künftiges `branch-cut-demo` vor, das Schnitte mit dem Verzweigen aus
`branch-bound-demo` kombiniert.

## Der Mechanismus

Eine **Deckung** (cover) ist eine Teilmenge $C$ von Paketen, deren Gewichte zusammen
das Limit überschreiten - es können also nie alle Pakete aus $C$ gleichzeitig gewählt
werden. Das liefert eine für jede zulässige Lösung gültige Ungleichung
$\sum_{i \in C} x_i \le |C| - 1$. Verletzt die aktuelle LP-Lösung diese Ungleichung,
wird sie als Schnitt hinzugefügt, die LP neu gelöst, wiederholt bis entweder die
Lösung ganzzahlig ist (bewiesenes Optimum) oder keine verletzte Deckung mehr gefunden
wird.

**Warum Cover-Cuts statt Gomory-Schnitte**: Gomory-Schnitte sind allgemeiner (auf
jedes ganzzahlige lineare Programm anwendbar, nicht nur Rucksackprobleme), aber
algebraisch aus den Bruchteilen der Simplex-Tableau-Zeilen hergeleitet - das würde den
anschaulichen Stil dieser Reihe verlassen. Cover-Cuts lassen sich dagegen direkt aus
dem Problem selbst ablesen ("diese Pakete passen nicht alle gleichzeitig hinein") -
diese geringere Allgemeinheit ist die bewusst in Kauf genommene eigene Schwäche dieses
Stücks.

## Die ehrliche eigene Schwäche

Die **Trennungsheuristik** (Greedy-Konstruktion + Minimalisierung einer Deckung aus
der aktuellen fraktionalen Lösung) ist keine erschöpfende Suche - Cover-Separation
(die exakte Version: finde die am stärksten verletzte Deckung) ist selbst NP-schwer.
Empirisch (siehe Presets) erreichen Schnitte allein nur bei einer Minderheit der
Instanzen tatsächlich ein bewiesenes Optimum - meist bleibt eine Lücke offen, auch bei
sehr kleinen, unkorrelierten Instanzen. Das ist keine Fehlfunktion, sondern der
realistische Zustand reiner Schnittebenenverfahren und der direkte Grund, warum echte
Solver (CPLEX, Gurobi) Schnitte immer mit Branching kombinieren (Branch & Cut), nie
mit Schnitten allein.

## Neue Abhängigkeit: scipy

Sobald mehr als eine Restriktion aktiv ist, ist das kein reines Bruchteils-Rucksack-
Problem mehr, sondern ein echtes lineares Programm - `cp_lp.py` löst es über
`scipy.optimize.linprog` (HiGHS-Solver). Erste externe LP-Bibliothek im Portfolio,
ehrlicher als eine selbstgebaute Mini-Simplex-Nachbildung.

## Verifikation

- **Cover-Gültigkeit**: jede gefundene Deckung wiegt tatsächlich mehr als die
  Kapazität; jede zulässige (nicht nur die optimale) 0/1-Lösung erfüllt jeden
  gefundenen Schnitt (vollständige Enumeration bei kleinen Instanzen).
- **Minimalitäts-Invariante**: Entfernen jedes einzelnen Pakets aus einer gefundenen
  Deckung macht sie wieder zulässig.
- **Bound-Monotonie**: die LP-Schranke ist über die Iterationen nie steigend.
- **LP-Cross-Check**: die Schranke ohne Schnitte (Iteration 0) muss exakt der
  unabhängig nachgerechneten Greedy-Bruchteils-Formel aus branch-bound-demo
  entsprechen.
- **Bruteforce-Cross-Check**: wird Ganzzahligkeit erreicht, muss das Ergebnis exakt
  der vollständigen Enumeration entsprechen (bis $n=18$ mit $2^{18}$ noch trivial
  schnell, kein separater Referenzlöser nötig).
- **Sicherheitsgrenzen-Test**: `MAX_CUT_ITERATIONS` wird zuverlässig eingehalten.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Hauptablauf: Presets, Einstellungen, Iterations-Animation, Lücken-Vergleich, Formulierungs-Expander |
| `cp_constants.py` | Defaults, Regler-Grenzen, Sicherheitsgrenzen, `PRESETS` |
| `cp_presets.py` | `SettingSpec`/`SETTING_SPECS`, Permalink-Logik, Presets, Zufalls-Seed-Button |
| `cp_scenario.py` | Zufällige Rucksack-Instanzen mit einstellbarer Korrelation |
| `cp_lp.py` | LP-Solver-Wrapper (scipy.optimize.linprog) |
| `cp_cuts.py` | Greedy-Trennungsheuristik (verletzte, minimale Deckung finden) |
| `cp_solver.py` | Hauptschleife: LP lösen → ganzzahlig? → sonst Schnitt suchen und hinzufügen |
| `cp_bruteforce.py` | Unabhängige Referenzlösung (vollständige Enumeration) |
| `cp_evaluation.py` | Kennzahlen je Iteration |
| `cp_visualization.py` | LP-Lösungs-Balken (mit Cover-Hervorhebung) und Schranken-Konvergenz (Plotly) |
| `tests/` | Cover-Gültigkeit, Minimalität, Bound-Monotonie, LP- und Bruteforce-Cross-Check, Sicherheitsgrenzen |

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

Teil des [Operations-Research-Demo-Portfolios](https://sebastianhanisch.net/demos.html) von
[Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning.
Interesse an einer maßgeschneiderten Lösung? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html).
