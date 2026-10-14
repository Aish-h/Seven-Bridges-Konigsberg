import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from euler import analyze, degrees
from graph_data import EXAMPLES, BY_KEY


def test_original_degrees():
    e = BY_KEY["original"]
    assert degrees(e.nodes, e.edges) == {"A": 5, "B": 3, "C": 3, "D": 3}
    assert len(e.edges) == 7


def test_original_has_no_path():
    e = BY_KEY["original"]
    a = analyze(e.nodes, e.edges)
    assert a.kind == "none" and len(a.odd_vertices) == 4


@pytest.mark.parametrize("ex", EXAMPLES, ids=lambda e: e.key)
def test_expected_result(ex):
    assert analyze(ex.nodes, ex.edges).kind == ex.expected


@pytest.mark.parametrize("ex", EXAMPLES, ids=lambda e: e.key)
def test_trail_is_valid(ex):
    a = analyze(ex.nodes, ex.edges)
    if a.kind == "none":
        assert a.trail_edges == []
        return
    # uses every edge exactly once ...
    assert sorted(a.trail_edges) == list(range(len(ex.edges)))
    # ... and consecutive vertices really are joined by the edge claimed
    for i, eid in enumerate(a.trail_edges):
        u, v = ex.edges[eid]
        assert {a.trail_vertices[i], a.trail_vertices[i + 1]} == {u, v}
    if a.kind == "circuit":
        assert a.trail_vertices[0] == a.trail_vertices[-1]
    else:
        assert {a.trail_vertices[0], a.trail_vertices[-1]} == set(a.odd_vertices)


def test_handshake_lemma():
    for ex in EXAMPLES:
        a = analyze(ex.nodes, ex.edges)
        assert a.total_degree == 2 * len(ex.edges)
        assert len(a.odd_vertices) % 2 == 0
