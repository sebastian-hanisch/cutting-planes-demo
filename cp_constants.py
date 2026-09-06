"""Defaults, slider bounds und Presets für die Schnittebenen-Demo."""

DEFAULT_N_ITEMS = 6
DEFAULT_CAPACITY_FRACTION = 0.5
DEFAULT_CORRELATION = 0.0
DEFAULT_SEED = 7

N_ITEMS_MIN, N_ITEMS_MAX = 3, 18
CAPACITY_FRACTION_MIN, CAPACITY_FRACTION_MAX = 0.2, 0.8
CORRELATION_MIN, CORRELATION_MAX = 0.0, 1.0

WEIGHT_RANGE = (5, 30)
VALUE_BASE_RANGE = (5, 30)
VALUE_NOISE_RANGE = (-8, 8)

# Numerische Toleranz für Ganzzahligkeits- und Verletzungs-Checks (LP-Lösungen sind
# nie exakt 0/1, sondern nur bis auf Gleitkomma-Rauschen).
EPS = 1e-6

# Sicherheitsgrenze: mehr Iterationen als das deutet darauf hin, dass die
# Trennungsheuristik nie aufgeben, aber auch nie ganzzahlig werden wird - in der
# Praxis konvergieren oder scheitern alle Presets weit darunter.
MAX_CUT_ITERATIONS = 30

PRESETS = {
    "Kleine Instanz (ein Schnitt reicht zum Optimum)": {
        "n_items": 5, "capacity_fraction": 0.5, "correlation": 0.0, "seed": 6,
    },
    "Schnitte allein reichen nicht (Branch & Cut nötig)": {
        "n_items": 4, "capacity_fraction": 0.5, "correlation": 0.0, "seed": 4,
    },
    "Viele kleine Schnitte (Bound nähert sich nur an)": {
        "n_items": 9, "capacity_fraction": 0.5, "correlation": 0.5, "seed": 5,
    },
}
