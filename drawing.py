"""
drawing.py - draws a multigraph with matplotlib.

Parallel edges (two bridges between the same pair of land masses) are drawn as
curves bending in opposite directions so you can see both of them.
"""
from collections import defaultdict
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from matplotlib import colormaps

from euler import degrees

ODD_COLOR = "#e4572e"    # odd-degree vertices
EVEN_COLOR = "#2a9d8f"   # even-degree vertices
STUCK_COLOR = "#d00000"  # "not possible" highlight (stuck vertex, unreachable bridges)


def edge_geometry(example):
    """{edge_id: (a, b, rad)} - the curvature each (parallel) edge is drawn with."""
    names = list(example.positions)
    index = {n: i for i, n in enumerate(names)}
    groups = defaultdict(list)
    for eid, (u, v) in enumerate(example.edges):
        groups[tuple(sorted((u, v), key=index.get))].append(eid)
    geo = {}
    for (a, b), ids in groups.items():
        for j, eid in enumerate(ids):
            geo[eid] = (a, b, (j - (len(ids) - 1) / 2) * 0.5)
    return geo


def point_on_edge(example, eid, frm, t):
    """(x, y) of a walker that has travelled fraction t (0..1) of edge `eid`, starting at `frm`."""
    a, b, rad = edge_geometry(example)[eid]
    if frm == b and frm != a:        # walking the edge backwards
        t = 1 - t
    (x1, y1), (x2, y2) = example.positions[a], example.positions[b]
    cx = (x1 + x2) / 2 + rad * (y2 - y1)
    cy = (y1 + y2) / 2 - rad * (x2 - x1)
    return ((1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2,
            (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2)


def draw_graph(example, order=None, current=None, figsize=(6.6, 5.2),
               walker=None, stuck=None):
    """
    order   : optional {edge_id: step_number}. Edges in it are drawn bold and
              coloured by step; all other edges are faded. None = plain view.
    current : optional vertex to ring in gold (where the walker is standing).
    walker  : optional (x, y) - draws a gold dot there (used by the animation).
    stuck   : optional vertex where the walk got stuck. It is ringed in red and
              every bridge not yet crossed is drawn in red = "can never be used".
    """
    pos, edges = example.positions, example.edges
    names = list(pos)
    index = {n: i for i, n in enumerate(names)}
    deg = degrees(names, edges)

    fig = Figure(figsize=figsize)
    ax = fig.subplots()

    # group parallel edges so each gets its own curvature
    groups = defaultdict(list)
    for eid, (u, v) in enumerate(edges):
        groups[tuple(sorted((u, v), key=index.get))].append(eid)

    cmap = colormaps["plasma"]
    total = max(len(edges), 1)

    for (a, b), ids in groups.items():
        (x1, y1), (x2, y2) = pos[a], pos[b]
        for j, eid in enumerate(ids):
            rad = (j - (len(ids) - 1) / 2) * 0.5
            if order is None:
                color, lw, ls = "#555555", 2.6, "-"
            elif eid in order:
                color, lw, ls = cmap(0.05 + 0.8 * order[eid] / total), 4.2, "-"
            elif stuck is not None:
                color, lw, ls = STUCK_COLOR, 2.6, "--"
            else:
                color, lw, ls = "#cfcfcf", 2.0, "--"
            ax.add_patch(FancyArrowPatch(
                (x1, y1), (x2, y2), connectionstyle=f"arc3,rad={rad}",
                arrowstyle="-", shrinkA=19, shrinkB=19, lw=lw, color=color,
                linestyle=ls, zorder=1))
            # label sits 35% along the curve (not at the middle) so labels of
            # edges that cross at a vertex-free point do not overlap
            cx = (x1 + x2) / 2 + rad * (y2 - y1)      # quadratic Bezier control point
            cy = (y1 + y2) / 2 - rad * (x2 - x1)
            t = 0.35
            mx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2
            my = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2
            if order is None:
                label, tc = str(eid + 1), "#333333"
            elif eid in order:
                label, tc = str(order[eid]), color
            else:
                continue
            ax.text(mx, my, label, ha="center", va="center", fontsize=10,
                    fontweight="bold", color=tc, zorder=2,
                    bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=tc, lw=1))

    xs = [pos[n][0] for n in names]
    ys = [pos[n][1] for n in names]
    ax.scatter(xs, ys, s=1300, c=[ODD_COLOR if deg[n] % 2 else EVEN_COLOR for n in names],
               edgecolors="black", linewidths=1.5, zorder=3)
    if current is not None:
        ax.scatter([pos[current][0]], [pos[current][1]], s=2300, facecolors="none",
                   edgecolors="#f4b400", linewidths=4, zorder=4)
    if stuck is not None:
        ax.scatter([pos[stuck][0]], [pos[stuck][1]], s=2300, facecolors="none",
                   edgecolors=STUCK_COLOR, linewidths=5, zorder=4)
        ax.text(pos[stuck][0], pos[stuck][1] + 0.42, "STUCK!", ha="center", va="bottom",
                fontsize=12, fontweight="bold", color=STUCK_COLOR, zorder=6)
    for n in names:
        ax.text(pos[n][0], pos[n][1], n, ha="center", va="center", color="white",
                fontsize=13, fontweight="bold", zorder=5)
        ax.text(pos[n][0], pos[n][1] - 0.33, f"deg {deg[n]}", ha="center", va="top",
                fontsize=9, color="#222222", zorder=5)

    if walker is not None:
        ax.scatter([walker[0]], [walker[1]], s=330, c="#f4b400", edgecolors="black",
                   linewidths=2, zorder=7)

    ax.set_xlim(min(xs) - 0.8, max(xs) + 0.8)
    ax.set_ylim(min(ys) - 1.0, max(ys) + 0.8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.legend(handles=[
        Line2D([], [], marker="o", ls="", color=ODD_COLOR, markersize=11, label="odd degree"),
        Line2D([], [], marker="o", ls="", color=EVEN_COLOR, markersize=11, label="even degree")],
        loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout()
    return fig