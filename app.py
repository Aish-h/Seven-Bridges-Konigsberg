"""
app.py - Streamlit front end.   Run with:   streamlit run app.py
"""
import time

import pandas as pd
import streamlit as st

from drawing import draw_graph, point_on_edge
from euler import analyze
from game import longest_trail
from graph_data import BY_KEY, CATEGORIES, EXAMPLES

st.set_page_config(page_title="Seven Bridges of Königsberg", page_icon="🌉", layout="wide")

# ------------------------------------------------------------------ sidebar
st.sidebar.title("Choose a graph")
category = st.sidebar.radio("Category", CATEGORIES)
choices = [e for e in EXAMPLES if e.category == category]
example_key = st.sidebar.selectbox("Example", [e.key for e in choices],
                                   format_func=lambda k: BY_KEY[k].title)
example = BY_KEY[example_key]
st.sidebar.caption("The result is computed automatically as soon as you pick a graph.")

analysis = analyze(example.nodes, example.edges)

st.title("🌉 Seven Bridges of Königsberg - Eulerian paths")
st.caption("A multigraph has an Eulerian path **iff** at most two vertices have odd degree "
           "(and all edges lie in one connected piece).")

tab_analysis, tab_play, tab_theory = st.tabs(["📊 Analysis", "🎮 Play the game", "📖 Theory & proof"])


def verdict_banner():
    if analysis.kind == "circuit":
        st.success("✅ Eulerian CIRCUIT exists (starts and ends at the same vertex).")
    elif analysis.kind == "path":
        st.success("✅ Eulerian PATH exists (starts and ends at different vertices).")
    else:
        st.error("❌ NO Eulerian path or circuit exists.")


# ------------------------------------------------------------------ animation
SPEEDS = {"Slow": 0.22, "Normal": 0.09, "Fast": 0.02}   # seconds per animation frame
FRAMES_PER_BRIDGE = 5


def animate_walk(example, analysis, graph_slot, status_slot, delay):
    """
    Plays the walk as an animation inside the two placeholders:
      * graph with a gold dot sliding across each bridge, which then turns coloured + numbered
      * possible graph   -> ends with a green "all bridges used" message
      * impossible graph -> shows the BEST attempt; ends with the stuck vertex ringed in red
                            and every bridge that can never be crossed drawn in red
    """
    total = len(example.edges)
    if analysis.kind != "none":
        tv, te = analysis.trail_vertices, analysis.trail_edges
        moves = [(te[i], tv[i], tv[i + 1]) for i in range(len(te))]
    else:
        status_slot.info("🔍 Searching for the longest walk that is possible ...")
        moves = longest_trail(example)
    if not moves:
        return

    order = {}
    start = moves[0][1]
    graph_slot.pyplot(draw_graph(example, order=order, current=start))
    status_slot.info(f"🚶 Start at **{start}**.")
    time.sleep(delay * 8)

    for k, (eid, frm, to) in enumerate(moves, 1):
        order[eid] = k
        status_slot.info(f"🚶 Step {k} of {total}: cross bridge #{eid + 1}  ({frm} → {to})")
        for f in range(1, FRAMES_PER_BRIDGE + 1):
            arrived = f == FRAMES_PER_BRIDGE
            graph_slot.pyplot(draw_graph(
                example, order=order,
                current=to if arrived else None,
                walker=None if arrived else point_on_edge(example, eid, frm, f / FRAMES_PER_BRIDGE)))
            time.sleep(delay)

    end = moves[-1][2]
    if analysis.kind != "none":
        kind = "circuit - back where it started" if end == start else "path"
        status_slot.success(f"✅ Success! All {total} bridges were crossed exactly once "
                            f"({start} → {end}): an Eulerian {kind}.")
    else:
        left_over = total - len(moves)
        graph_slot.pyplot(draw_graph(example, order=order, stuck=end))
        if not analysis.connected:
            why = "The remaining bridges are in a separate piece the walk can never reach."
        else:
            why = (f"{len(analysis.odd_vertices)} vertices have odd degree, so every walk "
                   "eventually runs out of unused bridges.")
        status_slot.error(f"❌ Stuck at **{end}** after {len(moves)} of {total} bridges - "
                          f"{left_over} bridge(s) (red) can never be crossed. {why}")


# ------------------------------------------------------------------ analysis
with tab_analysis:
    st.subheader(example.title)
    st.write(example.description)
    left, right = st.columns([3, 2])

    with left:
        trail = analysis.trail_edges
        b_play, b_speed = st.columns([1, 2])
        play = b_play.button("▶ Animate", key=f"anim_{example.key}", type="primary", width="stretch")
        speed = b_speed.radio("Speed", list(SPEEDS), index=1, horizontal=True,
                              key="anim_speed", label_visibility="collapsed")
        st.caption("▶ Animate shows the walk bridge by bridge - or, when it is impossible, "
                   "the best attempt getting stuck (red).")
        step = None
        if trail:
            st.markdown("**Walk through the solution** - press ▶ Animate, or drag the slider to step through it yourself.")
            step = st.slider("Bridges crossed so far", 0, len(trail), len(trail), key=f"step_{example.key}")
        status_slot = st.empty()
        graph_slot = st.empty()
        if trail:
            order = {eid: i + 1 for i, eid in enumerate(trail[:step])}
            graph_slot.pyplot(draw_graph(example, order=order, current=analysis.trail_vertices[step]))
            st.markdown("**Route:** " + " → ".join(analysis.trail_vertices[: step + 1]))
        else:
            graph_slot.pyplot(draw_graph(example))
            st.caption("Numbers on the edges are bridge numbers.")

    with right:
        verdict_banner()
        st.markdown("#### Vertex degrees")
        rows = []
        for n, d in analysis.degrees.items():
            row = {"Vertex": n, "Degree": d, "Parity": "odd" if d % 2 else "even"}
            if example.landmarks:
                row["Land mass"] = example.landmarks[n]
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        c1, c2, c3 = st.columns(3)
        c1.metric("Vertices", len(example.nodes))
        c2.metric("Edges", len(example.edges))
        c3.metric("Odd vertices", len(analysis.odd_vertices))
        degs = " + ".join(str(d) for d in analysis.degrees.values())
        st.caption(f"Handshake check: {degs} = {analysis.total_degree} = 2 × {len(example.edges)} edges")
        st.markdown("#### Why?")
        st.write(analysis.reason)

    if example.key == "original":
        st.markdown("---")
        st.markdown("### Formal proof for the original problem")
        st.markdown(
            "- Degrees: **A = 5, B = 3, C = 3, D = 3** (sum = 14 = 2 × 7 bridges ✔).\n"
            "- All **four** vertices have odd degree.\n"
            "- In an Eulerian path, every vertex *in the middle* of the walk is entered and left "
            "equally often, so it uses its edges in pairs → even degree.\n"
            "- Only the **first** and **last** vertex can have odd degree, so at most **2** odd "
            "vertices are allowed.\n"
            "- 4 > 2, therefore **no Eulerian path exists** - the walk across all seven bridges "
            "is impossible. ∎")

    with st.expander("Summary table of ALL examples"):
        summary = []
        for e in EXAMPLES:
            a = analyze(e.nodes, e.edges)
            summary.append({"Graph": e.title, "V": len(e.nodes), "E": len(e.edges),
                            "Odd vertices": len(a.odd_vertices),
                            "Connected": "yes" if a.connected else "no",
                            "Result": {"circuit": "Eulerian circuit", "path": "Eulerian path",
                                       "none": "None"}[a.kind]})
        st.dataframe(pd.DataFrame(summary), hide_index=True, width="stretch")

# ------------------------------------------------------------------ play
with tab_play:
    st.subheader(f"Try it yourself: {example.title}")
    st.write("Pick a starting vertex, then cross edges one at a time. "
             "Use every edge exactly once to win.")
    skey = f"play_{example.key}"
    if skey not in st.session_state:
        st.session_state[skey] = {"current": None, "used": [], "path": []}
    S = st.session_state[skey]

    def start(node):
        st.session_state[skey] = {"current": node, "used": [], "path": [node]}

    def cross(eid, nxt):
        S["used"].append(eid)
        S["path"].append(nxt)
        S["current"] = nxt

    def undo():
        if S["used"]:
            S["used"].pop()
            S["path"].pop()
            S["current"] = S["path"][-1]

    def reset():
        st.session_state[skey] = {"current": None, "used": [], "path": []}

    if S["current"] is None:
        st.info("Step 1 - choose where to start:")
        cols = st.columns(len(example.nodes))
        for col, n in zip(cols, example.nodes):
            col.button(n, key=f"{skey}_start_{n}", on_click=start, args=(n,), width="stretch")
        st.pyplot(draw_graph(example))
    else:
        order = {eid: i + 1 for i, eid in enumerate(S["used"])}
        gl, gr = st.columns([3, 2])
        with gl:
            st.pyplot(draw_graph(example, order=order, current=S["current"]))
        with gr:
            st.markdown(f"**Standing at:** {S['current']}")
            st.markdown("**Route so far:** " + " → ".join(S["path"]))
            st.progress(len(S["used"]) / len(example.edges),
                        text=f"{len(S['used'])} of {len(example.edges)} edges used")
            moves = []
            for eid, (u, v) in enumerate(example.edges):
                if eid not in S["used"] and S["current"] in (u, v):
                    moves.append((eid, v if u == S["current"] else u))
            if len(S["used"]) == len(example.edges):
                st.balloons()
                st.success("🎉 You used every edge exactly once - you found an Eulerian "
                           + ("circuit!" if S["path"][0] == S["path"][-1] else "path!"))
            elif not moves:
                st.error("💥 Dead end - no unused edge leaves this vertex. Undo or reset and try again.")
            else:
                st.markdown("**Next move:**")
                for eid, nxt in moves:
                    st.button(f"Cross edge #{eid + 1} → {nxt}", key=f"{skey}_cross_{eid}",
                              on_click=cross, args=(eid, nxt), width="stretch")
            b1, b2 = st.columns(2)
            b1.button("↩ Undo", on_click=undo, key=f"{skey}_undo", width="stretch")
            b2.button("🔄 Reset", on_click=reset, key=f"{skey}_reset", width="stretch")
            with st.expander("Hint"):
                if analysis.kind == "path":
                    st.write(f"A solution exists. Start at {analysis.odd_vertices[0]} or {analysis.odd_vertices[1]}.")
                elif analysis.kind == "circuit":
                    st.write("A solution exists. You can start anywhere - you will end where you began.")
                else:
                    st.write("No solution exists for this graph. Try anyway and see where you get stuck!")

# ------------------------------------------------------------------ theory
with tab_theory:
    st.markdown("""
### Euler's theorem (1736)
For a connected multigraph:
* **0 odd vertices** → an Eulerian **circuit** exists (start anywhere, finish where you began).
* **exactly 2 odd vertices** → an Eulerian **path** exists; it must start at one odd vertex and end at the other.
* **more than 2 odd vertices** → **no** Eulerian path exists.

(The number of odd vertices is always even - see the handshake lemma below - so "1 odd vertex" and "3 odd vertices" never occur.)

### Why it works
1. **Handshake lemma:** the sum of all degrees = 2 × (number of edges), because each edge has two ends. Hence the count of odd-degree vertices is even.
2. **Necessity:** whenever the walk passes *through* a vertex it uses one edge to arrive and one to leave - a pair. So every vertex that is neither the start nor the end has even degree.
3. **Sufficiency (constructive):** Hierholzer's algorithm builds the walk by following unused edges until stuck, then splicing in sub-tours at vertices that still have unused edges. It runs in O(E) time.

### How this project models the problem
* Each land mass is a **vertex**; each bridge is an **edge**.
* Two bridges between the same land masses are **parallel edges** → a *multigraph*.
* `euler.py` computes degrees, checks connectivity, classifies the graph and constructs the trail.
* `drawing.py` draws parallel edges as curves; `app.py` is the interactive interface.
""")

# ------------------------------------------------------------------ run the animation LAST
# (so the rest of the page - banner, tables, other tabs - is already on screen while it plays)
if play:
    animate_walk(example, analysis, graph_slot, status_slot, SPEEDS[speed])