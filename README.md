# **🌉 Seven Bridges of Königsberg - Eulerian Path Explorer**

**Course:** Mathematics of Computing · **Foundation:** Graph Theory · **Project P014**

An animated, clickable demo: *a multigraph has an Eulerian path iff at most two vertices have odd degree.*
Click vertices to walk across the bridges - the app numbers every bridge you cross, tags each vertex with its
visit order, and tells you instantly whether the walk is possible.

## **🎥 Project Video**

https://github.com/user-attachments/assets/aebce559-0498-4f37-bc39-fbfbcbe5f77c

## **📜 The Problem**

The city of Königsberg (today's Kaliningrad) had four areas of land joined by seven bridges. The question: can you take a walk that crosses every bridge **exactly once**? In 1736 Leonhard Euler proved it is impossible, and in doing so he started graph theory.

## **💡 The Idea**

Each area of land is a **vertex** and each bridge is an **edge**. Two bridges between the same areas make it a *multigraph*.

- The **degree** of a vertex is the number of bridges touching it. In Königsberg: A = 5, B = 3, C = 3, D = 3.
- **Euler's theorem:** a connected multigraph has an Eulerian path if and only if it has **0 or 2** odd-degree vertices (0 gives a circuit, 2 gives a path that starts and ends at the odd vertices).
- Königsberg has **4** odd vertices, so the walk is impossible.
- Why: a vertex in the middle of a walk is entered and left equally often, so its bridges are used in pairs. Only the start and end of a walk can be odd.
- The graph must also be **connected**. The "two disconnected triangles" example has all-even degrees but still no walk.

## **✨ Features**

- Instant verdict (circuit / path / impossible) with degrees and a plain-English reason
- Animated walks, with a new random route each time; on impossible graphs a best attempt that gets stuck
- A playable game with undo, reset and hints
- 15 example graphs, a summary table and a proof for the original problem
- Two interfaces sharing the same math code: a **web app** (Streamlit) and a **desktop app** (Tkinter)

## **Run (Windows / Mac / Linux)**

**Desktop app** - needs only **Python 3.10+** with tkinter (included in the normal python.org installer). No pip install.
```
python main.py
```

**Web app** - install the requirements first.
```
pip install -r requirements.txt
streamlit run app.py
```
Tests (optional): `pip install pytest` then `python -m pytest -q`

## **How to use**
| Action | What happens |
|---|---|
| Pick a graph in the sidebar | Result banner (path / circuit / impossible) appears automatically |
| Click a vertex | First click = start. Then click a glowing vertex to cross a bridge (animated) |
| Click a bridge | Choose which of two parallel bridges to cross |
| ▶ Auto-solve (Space) | Animates the Euler path/circuit; on impossible graphs it shows the best attempt getting stuck |
| ❓ Why? | Degree sum + parity argument in four lines |
| ↩ Undo (Ctrl+Z) / ⟲ Reset (R) | Step back / start over |

(The web app has the same ideas in three tabs: Analysis, Play the game, and Theory & proof.)

## **Graphs included (15)**
* **Original:** Seven Bridges (4 odd vertices → no path, degrees A=5, B=3, C=3, D=3)
* **0 odd → circuit:** K5, pentagon, bowtie, Königsberg + 2 bridges, *(trap)* two disconnected triangles
* **2 odd → path:** Königsberg + 1 bridge, the house, the envelope, path P5
* **4 odd → none:** K4, star, island chain
* **Bonus:** K3,3 (6 odd), cube (8 odd)

## **Files**
```
main.py           animated tkinter interface (desktop)
app.py            Streamlit interface (web)
drawing.py        draws the graphs for the web app
game.py           walking-game rules (moves, undo, dead end, visit order, best-attempt search)
euler.py          degrees, connectivity, Euler's theorem, Hierholzer's algorithm
graph_data.py     the 15 example multigraphs
requirements.txt  packages for the web app
tests/            unit tests
```

## **Credits**
Euler (1736) for the problem and the odd-degree condition; Hierholzer (1873) for the algorithm that builds the walk.

Author: Aishwarya J S
