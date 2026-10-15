"""
graph_data.py - every predefined example lives here.

Each example = vertex positions (for drawing) + an edge list (a multigraph).
`expected` is what Euler's theorem should say; the unit tests check it.
"""
import math
from dataclasses import dataclass


@dataclass
class Example:
    key: str
    category: str       # which sidebar group it belongs to
    title: str
    description: str
    positions: dict     # vertex -> (x, y)
    edges: list         # [(u, v), ...]  parallel edges allowed
    expected: str       # "circuit" | "path" | "none"
    landmarks: dict = None   # optional vertex -> real-world meaning

    @property
    def nodes(self):
        return list(self.positions)


def circle(names, r=1.4, start=90):
    n = len(names)
    return {nm: (r * math.cos(math.radians(start + 360 * i / n)),
                 r * math.sin(math.radians(start + 360 * i / n)))
            for i, nm in enumerate(names)}


def complete(names):
    return [(a, b) for i, a in enumerate(names) for b in names[i + 1:]]


# ---- Königsberg: A = Kneiphof island, B = north bank, C = south bank, D = east island
KB_POS = {"A": (-1.5, 0), "B": (0, 1.5), "C": (0, -1.5), "D": (1.7, 0)}
KB_EDGES = [("A", "B"), ("A", "B"), ("A", "C"), ("A", "C"),
            ("A", "D"), ("B", "D"), ("C", "D")]
KB_LAND = {"A": "Kneiphof island", "B": "North bank",
           "C": "South bank", "D": "East island (Lomse)"}

EXAMPLES = [
    # ------------------------------------------------------------ ORIGINAL
    Example("original", "Original problem", "The Seven Bridges of Königsberg",
            "Four land masses (A-D) joined by seven bridges. Can you cross every "
            "bridge exactly once? Euler proved in 1736 that you cannot.",
            KB_POS, KB_EDGES, "none", KB_LAND),

    # ------------------------------------------------------------ 0 ODD
    Example("circuit_k5", "0 odd vertices (Eulerian circuit)", "Complete graph K5",
            "Five vertices, each joined to every other. All degrees are 4.",
            circle(list("ABCDE")), complete(list("ABCDE")), "circuit"),
    Example("circuit_c5", "0 odd vertices (Eulerian circuit)", "Pentagon cycle C5",
            "The simplest circuit: walk around the pentagon. All degrees are 2.",
            circle(list("ABCDE")), [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "A")],
            "circuit"),
    Example("circuit_bowtie", "0 odd vertices (Eulerian circuit)", "Bowtie (two triangles)",
            "Two triangles sharing the centre vertex C (degree 4); the rest have degree 2.",
            {"A": (-2, 1), "B": (-2, -1), "C": (0, 0), "D": (2, 1), "E": (2, -1)},
            [("A", "B"), ("B", "C"), ("C", "A"), ("C", "D"), ("D", "E"), ("E", "C")], "circuit"),
    Example("circuit_kb_fixed", "0 odd vertices (Eulerian circuit)",
            "Königsberg + 2 new bridges (B-C and A-D)",
            "Add a bridge B-C and a second bridge A-D. Degrees become A=6, B=4, C=4, "
            "D=4 - all even - so the city would have a perfect tour!",
            KB_POS, KB_EDGES + [("B", "C"), ("A", "D")], "circuit", KB_LAND),
    Example("trap_disconnected", "0 odd vertices (Eulerian circuit)",
            "Trap: two separate triangles (all even, but disconnected)",
            "Every degree is 2, yet there is NO Euler circuit because the graph is "
            "disconnected. Shows that the degree rule alone is not enough.",
            {"A": (-3, 1), "B": (-1.5, -1), "C": (-4.5, -1), "D": (1.5, 1), "E": (3, -1), "F": (0, -1)},
            [("A", "B"), ("B", "C"), ("C", "A"), ("D", "E"), ("E", "F"), ("F", "D")], "none"),

    # ------------------------------------------------------------ 2 ODD
    Example("path_kb_plus1", "2 odd vertices (Eulerian path)", "Königsberg + 1 new bridge (B-C)",
            "Build one extra bridge between the north and south banks. Now only A (5) "
            "and D (3) are odd, so a walk exists - it must start at A or D.",
            KB_POS, KB_EDGES + [("B", "C")], "path", KB_LAND),
    Example("path_house", "2 odd vertices (Eulerian path)", "The house",
            "A square with a roof. Only the two bottom corners A and B have odd degree (3).",
            {"A": (0, 0), "B": (2, 0), "C": (2, 2), "D": (0, 2), "E": (1, 3.2)},
            [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("A", "E"), ("B", "E")], "path"),
    Example("path_envelope", "2 odd vertices (Eulerian path)", "The envelope (classic puzzle)",
            "The 'draw it without lifting your pen' envelope. Odd vertices: A and B.",
            {"A": (0, 0), "B": (2, 0), "C": (2, 2), "D": (0, 2), "E": (1, 3.2)},
            [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("A", "C"), ("B", "D"),
             ("C", "E"), ("D", "E")], "path"),
    Example("path_p5", "2 odd vertices (Eulerian path)", "Path graph P5",
            "A straight line of 4 edges. The two end points are the odd vertices.",
            {"A": (-3, 0), "B": (-1.5, 0), "C": (0, 0), "D": (1.5, 0), "E": (3, 0)},
            [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")], "path"),

    # ------------------------------------------------------------ 4 ODD
    Example("none_k4", "4 odd vertices (no Eulerian path)", "Complete graph K4",
            "Four vertices, every pair joined. All four have degree 3 (odd).",
            {"A": (-1.5, 1.5), "B": (1.5, 1.5), "C": (1.5, -1.5), "D": (-1.5, -1.5)},
            complete(list("ABCD")), "none"),
    Example("none_star", "4 odd vertices (no Eulerian path)", "Star with 4 leaves",
            "Centre O has degree 4 (even); the four leaves have degree 1 (odd).",
            {"O": (0, 0), "A": (-2, 1.5), "B": (2, 1.5), "C": (2, -1.5), "D": (-2, -1.5)},
            [("O", "A"), ("O", "B"), ("O", "C"), ("O", "D")], "none"),
    Example("none_chain", "4 odd vertices (no Eulerian path)", "Island chain with a doubled bridge",
            "A multigraph: islands A-B-C-D in a row, with TWO bridges between B and C. "
            "Degrees are A=1, B=3, C=3, D=1 - four odd vertices.",
            {"A": (-3, 0), "B": (-1, 0), "C": (1, 0), "D": (3, 0)},
            [("A", "B"), ("B", "C"), ("B", "C"), ("C", "D")], "none"),

    # ------------------------------------------------------------ BONUS
    Example("bonus_k33", "Bonus (6+ odd vertices)", "Utility graph K3,3",
            "Three houses, three utilities. All six vertices have degree 3 - six odd vertices.",
            {"H1": (-2, 1.5), "H2": (-2, 0), "H3": (-2, -1.5),
             "U1": (2, 1.5), "U2": (2, 0), "U3": (2, -1.5)},
            [(h, u) for h in ("H1", "H2", "H3") for u in ("U1", "U2", "U3")], "none"),
    Example("bonus_cube", "Bonus (6+ odd vertices)", "Cube graph Q3",
            "The 8 corners of a cube. Every vertex has degree 3 - eight odd vertices.",
            {"A": (-1.6, 1.2), "B": (0.8, 1.2), "C": (0.8, -1.2), "D": (-1.6, -1.2),
             "E": (-0.8, 2.0), "F": (1.6, 2.0), "G": (1.6, -0.4), "H": (-0.8, -0.4)},
            [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"),
             ("E", "F"), ("F", "G"), ("G", "H"), ("H", "E"),
             ("A", "E"), ("B", "F"), ("C", "G"), ("D", "H")], "none"),
]

BY_KEY = {e.key: e for e in EXAMPLES}
CATEGORIES = list(dict.fromkeys(e.category for e in EXAMPLES))
