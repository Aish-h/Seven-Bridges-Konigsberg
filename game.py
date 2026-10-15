"""
game.py - the rules of the walking game (no GUI code).

A "move" is (edge_id, from_vertex, to_vertex).  The player starts on a vertex and
must cross every edge exactly once.
"""


class Game:
    def __init__(self, example):
        self.ex = example
        self.reset()

    def reset(self):
        self.current = None      # vertex the walker stands on (None = not started)
        self.moves = []          # [(eid, frm, to), ...] in the order crossed

    # ------------------------------------------------------------------ queries
    @property
    def used(self):
        return {m[0] for m in self.moves}

    @property
    def remaining(self):
        return len(self.ex.edges) - len(self.moves)

    @property
    def started(self):
        return self.current is not None

    def free_edges(self, to=None):
        """Unused edges leaving the current vertex (optionally only towards `to`)."""
        if self.current is None:
            return []
        out = []
        for eid, (u, v) in enumerate(self.ex.edges):
            if eid in self.used or self.current not in (u, v):
                continue
            other = v if u == self.current else u
            if to is None or other == to:
                out.append(eid)
        return out

    def other_end(self, eid, frm):
        u, v = self.ex.edges[eid]
        return v if u == frm else u

    @property
    def won(self):
        return self.started and self.remaining == 0

    @property
    def dead_end(self):
        return self.started and self.remaining > 0 and not self.free_edges()

    @property
    def is_circuit(self):
        return self.won and self.moves[0][1] == self.moves[-1][2]

    def visit_order(self):
        """{vertex: [1, 4, ...]} - the order in which each vertex was visited."""
        order = {}
        if not self.started:
            return order
        seq = [self.moves[0][1] if self.moves else self.current] + [m[2] for m in self.moves]
        for i, v in enumerate(seq, 1):
            order.setdefault(v, []).append(i)
        return order

    # ------------------------------------------------------------------ actions
    def start(self, vertex):
        self.moves = []
        self.current = vertex

    def move(self, eid):
        if self.current is None or eid in self.used:
            raise ValueError("illegal move")
        u, v = self.ex.edges[eid]
        if self.current not in (u, v):
            raise ValueError("edge not at current vertex")
        to = self.other_end(eid, self.current)
        self.moves.append((eid, self.current, to))
        self.current = to

    def undo(self):
        if self.moves:
            _, frm, _ = self.moves.pop()
            self.current = frm
        else:
            self.current = None


def longest_trail(example):
    """
    Best-effort walk for graphs with NO Euler trail: the longest sequence of
    distinct edges (found by backtracking).  Used by the 'Auto-solve' demo to show
    how every attempt gets stuck.
    """
    edges = example.edges
    adj = {n: [] for n in example.nodes}
    for i, (u, v) in enumerate(edges):
        adj[u].append((i, v))
        adj[v].append((i, u))
    best = []

    def dfs(v, used, trail):
        nonlocal best
        if len(trail) > len(best):
            best = list(trail)
        if len(best) == len(edges):
            return
        for eid, w in adj[v]:
            if eid not in used:
                used.add(eid)
                trail.append((eid, v, w))
                dfs(w, used, trail)
                trail.pop()
                used.discard(eid)
                if len(best) == len(edges):
                    return

    for s in example.nodes:
        dfs(s, set(), [])
    return best


def random_longest_trail(example, rng=None, avoid=None, cap=4000):
    """
    For graphs with NO Euler trail: pick a RANDOM one of the longest possible walks
    (so each animation shows a different best attempt, from a different start).
    `avoid` = the previous result, so two animations in a row differ.
    """
    import random as _random
    rng = rng or _random
    edges = example.edges
    adj = {n: [] for n in example.nodes}
    for i, (u, v) in enumerate(edges):
        adj[u].append((i, v))
        adj[v].append((i, u))
    best_len, found = 0, []

    def dfs(v, used, trail):
        nonlocal best_len, found
        n = len(trail)
        if n > best_len:
            best_len, found = n, [tuple(trail)]
        elif n == best_len and n and len(found) < cap:
            found.append(tuple(trail))
        for eid, w in adj[v]:
            if eid not in used:
                used.add(eid)
                trail.append((eid, v, w))
                dfs(w, used, trail)
                trail.pop()
                used.discard(eid)

    for s in example.nodes:
        dfs(s, set(), [])
    pool = [t for t in found if len(t) == best_len]
    if avoid is not None and len(pool) > 1:
        pool = [t for t in pool if t != tuple(avoid)] or pool
    return list(rng.choice(pool)) if pool else []