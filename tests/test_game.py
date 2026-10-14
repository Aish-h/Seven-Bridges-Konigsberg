import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from game import Game, longest_trail
from graph_data import BY_KEY
from euler import analyze


def test_manual_walk_on_pentagon():
    g = Game(BY_KEY["circuit_c5"])
    g.start("A")
    for v in "BCDEA":
        g.move(g.free_edges(to=v)[0])
    assert g.won and g.is_circuit


def test_dead_end_detected():
    g = Game(BY_KEY["path_p5"])
    g.start("C")
    g.move(g.free_edges(to="B")[0])
    g.move(g.free_edges(to="A")[0])
    assert g.dead_end and not g.won


def test_visit_order_and_undo():
    g = Game(BY_KEY["original"])
    g.start("A")
    g.move(g.free_edges(to="B")[0])
    g.move(g.free_edges(to="A")[0])
    assert g.visit_order() == {"A": [1, 3], "B": [2]}
    g.undo(); g.undo(); g.undo()
    assert not g.started


def test_parallel_bridges_are_distinct():
    g = Game(BY_KEY["original"])
    g.start("A")
    assert len(g.free_edges(to="B")) == 2
    g.move(g.free_edges(to="B")[0])
    g.move(g.free_edges(to="A")[0])     # come back over the OTHER A-B bridge
    assert g.free_edges(to="B") == []


def test_original_best_walk_is_6_of_7():
    assert len(longest_trail(BY_KEY["original"])) == 6


def test_auto_solution_wins():
    for key in ("path_house", "circuit_k5", "path_kb_plus1"):
        ex = BY_KEY[key]; a = analyze(ex.nodes, ex.edges)
        g = Game(ex); g.start(a.trail_vertices[0])
        for eid in a.trail_edges:
            g.move(eid)
        assert g.won
