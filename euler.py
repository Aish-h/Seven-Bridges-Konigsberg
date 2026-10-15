"""
euler.py - the mathematics layer (no GUI code here).

A graph is described by a list of edges [(u, v), ...].  Parallel edges are
allowed (they are what makes it a *multigraph*), which is exactly what the
Seven Bridges problem needs: two bridges can join the same pair of land masses.
"""
import random
from collections import deque
from dataclasses import dataclass, field


@dataclass
class Analysis:
    degrees: dict            # vertex -> degree
    odd_vertices: list       # vertices whose degree is odd
    connected: bool          # are all edges in ONE connected piece?
    kind: str                # "circuit" | "path" | "none"
    reason: str              # human-readable explanation
    total_degree: int = 0    # sum of degrees (always 2 * number of edges)
    trail_vertices: list = field(default_factory=list)  # e.g. ["B","A","C",...]
    trail_edges: list = field(default_factory=list)     # edge ids in walking order


def degrees(nodes, edges):
    """Degree of each vertex = number of edge-ends touching it (loop counts 2)."""
    deg = {n: 0 for n in nodes}
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    return deg


def is_connected(nodes, edges):
    """True if every vertex that has at least one edge lies in one component."""
    deg = degrees(nodes, edges)
    active = [n for n in nodes if deg[n] > 0]
    if not active:
        return True
    adj = {n: set() for n in nodes}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    seen, queue = {active[0]}, deque([active[0]])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                queue.append(y)
    return all(n in seen for n in active)


def hierholzer(nodes, edges, start, rng=None):
    """
    Hierholzer's algorithm: builds an Euler trail in O(E).
    Returns (vertex_sequence, edge_id_sequence).
    Only call it when an Euler trail is known to exist.
    Pass rng (a random.Random) to shuffle the edge order -> a different valid trail each call.
    """
    adj = {n: [] for n in nodes}
    for i, (u, v) in enumerate(edges):
        adj[u].append((i, v))
        adj[v].append((i, u))
    if rng is not None:
        for lst in adj.values():
            rng.shuffle(lst)
    used = set()
    stack = [(start, None)]          # (vertex, edge used to arrive here)
    out = []
    while stack:
        v, _ = stack[-1]
        while adj[v] and adj[v][-1][0] in used:   # discard already-used edges
            adj[v].pop()
        if adj[v]:
            eid, w = adj[v].pop()
            used.add(eid)
            stack.append((w, eid))
        else:
            out.append(stack.pop())
    out.reverse()
    return [p[0] for p in out], [p[1] for p in out[1:]]


def analyze(nodes, edges):
    """Apply Euler's theorem and, if a trail exists, actually construct it."""
    nodes = list(nodes)
    deg = degrees(nodes, edges)
    odd = [n for n in nodes if deg[n] % 2 == 1]
    conn = is_connected(nodes, edges)
    total = sum(deg.values())

    if not conn:
        return Analysis(deg, odd, conn, "none",
                        "The edges are split into separate pieces. One continuous "
                        "walk can never jump between pieces, so no Eulerian path "
                        "or circuit exists - even though the degree condition "
                        "may look fine.", total)
    if len(odd) > 2:
        return Analysis(deg, odd, conn, "none",
                        f"{len(odd)} vertices have odd degree ({', '.join(odd)}). "
                        "In any walk, every vertex that is passed through in the "
                        "middle uses edges in pairs (one in, one out), so it must "
                        "have even degree. Only the START and the END of the walk "
                        f"may be odd - at most 2 vertices. Here there are "
                        f"{len(odd)}, so an Eulerian path is impossible.", total)
    if len(odd) == 2:
        start = odd[0]
        tv, te = hierholzer(nodes, edges, start)
        return Analysis(deg, odd, conn, "path",
                        f"Exactly two vertices ({odd[0]} and {odd[1]}) have odd "
                        "degree and the graph is connected, so an Eulerian PATH "
                        f"exists. It must start at {odd[0]} and end at {odd[1]} "
                        "(or the reverse).", total, tv, te)
    start = next(n for n in nodes if deg[n] > 0) if edges else nodes[0]
    tv, te = hierholzer(nodes, edges, start)
    return Analysis(deg, odd, conn, "circuit",
                    "Every vertex has even degree and the graph is connected, so "
                    "an Eulerian CIRCUIT exists: you can start anywhere and "
                    "return to the same place after using every edge exactly once.",
                    total, tv, te)


def random_trail(nodes, edges, rng=random, avoid=None, tries=40):
    """
    A RANDOM Eulerian trail: random legal start vertex + random edge order.
      * 2 odd vertices -> starts at one of the two odd vertices (either one)
      * 0 odd vertices -> starts at any vertex that has a bridge
    `avoid` = the (vertices, edges) signature of the previous trail; we retry so that
    two animations in a row are different (when the graph has more than one trail).
    Returns (vertex_sequence, edge_id_sequence) or ([], []) if no Euler trail exists.
    """
    a = analyze(nodes, edges)
    if a.kind == "none":
        return [], []
    starts = a.odd_vertices if a.kind == "path" else [n for n in nodes if a.degrees[n] > 0]
    result = None
    for _ in range(tries):
        tv, te = hierholzer(list(nodes), edges, rng.choice(starts), rng)
        result = (tv, te)
        if avoid is None or (tuple(tv), tuple(te)) != avoid:
            break
    return result