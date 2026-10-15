# 🌉 Seven Bridges of Königsberg - Eulerian Path Explorer

**Course:** Mathematics of Computing · **Foundation:** Graph Theory · **Project P014**

An animated, clickable demo: *a multigraph has an Eulerian path iff at most two vertices have odd degree.*
Click vertices to walk across the bridges - the app numbers every bridge you cross, tags each vertex with its
visit order, and tells you instantly whether the walk is possible.

## Run (Windows / Mac / Linux)
Needs only **Python 3.10+** with tkinter (included in the normal python.org installer). **No pip install.**
```
python main.py
```
Tests (optional): `pip install pytest` then `python -m pytest -q`

## How to use
| Action | What happens |
|---|---|
| Pick a graph in the sidebar | Result banner (path / circuit / impossible) appears automatically |
| Click a vertex | First click = start. Then click a glowing vertex to cross a bridge (animated) |
| Click a bridge | Choose which of two parallel bridges to cross |
| ▶ Auto-solve (Space) | Animates the Euler path/circuit; on impossible graphs it shows the best attempt getting stuck |
| ❓ Why? | Degree sum + parity argument in four lines |
| ↩ Undo (Ctrl+Z) / ⟲ Reset (R) | Step back / start over |

## Graphs included (15)
* **Original:** Seven Bridges (4 odd vertices → no path, degrees A=5, B=3, C=3, D=3)
* **0 odd → circuit:** K5, pentagon, bowtie, Königsberg + 2 bridges, *(trap)* two disconnected triangles
* **2 odd → path:** Königsberg + 1 bridge, the house, the envelope, path P5
* **4 odd → none:** K4, star, island chain
* **Bonus:** K3,3 (6 odd), cube (8 odd)

## Files
```
main.py        animated tkinter interface
game.py        walking-game rules (moves, undo, dead end, visit order, best-attempt search)
euler.py       degrees, connectivity, Euler's theorem, Hierholzer's algorithm
graph_data.py  the 15 example multigraphs
tests/         unit tests
```
Author: Aishwarya
