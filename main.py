"""
Seven Bridges of Königsberg - interactive Eulerian-path explorer.

Run:   python main.py          (needs only Python + tkinter, no pip install)

Click a vertex to start, then click glowing vertices (or a bridge itself) to
walk across the bridges.  Cross every bridge exactly once to win.
"""
import math
import random
import tkinter as tk
from collections import defaultdict

from euler import analyze
from game import Game, longest_trail
from graph_data import BY_KEY, CATEGORIES, EXAMPLES

# ------------------------------------------------------------------ look & feel
BG, PANEL, PANEL2 = "#0b1220", "#111a2e", "#1b2742"
TEXT, MUTED = "#e2e8f0", "#7b8aa5"
ODD, EVEN = "#f97316", "#14b8a6"
GOLD, GOOD, BAD = "#fbbf24", "#22c55e", "#ef4444"
EDGE_IDLE = "#3b4a66"
FONT = "Segoe UI"
R = 27                      # vertex radius in pixels
TOP_H, BOTTOM_H = 110, 118  # heads-up-display heights

SHORT = {
    "original": "Seven Bridges (original)",
    "circuit_k5": "Complete graph K5", "circuit_c5": "Pentagon cycle C5",
    "circuit_bowtie": "Bowtie", "circuit_kb_fixed": "Königsberg + 2 bridges",
    "trap_disconnected": "Two triangles (trap!)",
    "path_kb_plus1": "Königsberg + 1 bridge", "path_house": "The house",
    "path_envelope": "The envelope", "path_p5": "Path graph P5",
    "none_k4": "Complete graph K4", "none_star": "Star graph",
    "none_chain": "Island chain",
    "bonus_k33": "Utility graph K3,3", "bonus_cube": "Cube graph",
}
HEADERS = {
    CATEGORIES[0]: ("ORIGINAL PROBLEM", GOLD),
    CATEGORIES[1]: ("0 ODD VERTICES  ·  circuit", GOOD),
    CATEGORIES[2]: ("2 ODD VERTICES  ·  path", "#38bdf8"),
    CATEGORIES[3]: ("4 ODD VERTICES  ·  no path", BAD),
    CATEGORIES[4]: ("BONUS  ·  6+ odd vertices", MUTED),
}


def lerp_color(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class App:
    def __init__(self, root):
        self.root = root
        root.title("Seven Bridges of Königsberg - Eulerian Path Explorer")
        root.geometry("1220x780")
        root.minsize(980, 640)
        root.configure(bg=BG)

        self.gen = 0               # bumps whenever we must cancel pending animations
        self.t = 0                 # global tick counter (drives pulsing)
        self.anim = None           # the walker's current bridge crossing
        self.auto_queue = []
        self.auto_running = False
        self.confetti = []
        self.show_why = False
        self.status, self.status_color = "", MUTED
        self.flash = {}            # vertex -> frames of red flash left
        self.speed = tk.IntVar(value=2)
        self.btns = {}

        self.build_sidebar()
        self.build_main()
        self.select("original")
        self.tick()

    # ================================================================== layout
    def build_sidebar(self):
        side = tk.Frame(self.root, bg=PANEL, width=250)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="🌉  Königsberg", bg=PANEL, fg=TEXT,
                 font=(FONT, 16, "bold")).pack(anchor="w", padx=16, pady=(16, 0))
        tk.Label(side, text="Pick a graph and walk it", bg=PANEL, fg=MUTED,
                 font=(FONT, 9)).pack(anchor="w", padx=16, pady=(0, 6))
        for cat in CATEGORIES:
            head, col = HEADERS[cat]
            tk.Label(side, text=head, bg=PANEL, fg=col, font=(FONT, 8, "bold")
                     ).pack(anchor="w", padx=16, pady=(9, 2))
            for ex in [e for e in EXAMPLES if e.category == cat]:
                b = tk.Button(side, text="   " + SHORT[ex.key], anchor="w", relief="flat",
                              bg=PANEL, fg=TEXT, activebackground=PANEL2, activeforeground=TEXT,
                              bd=0, font=(FONT, 10), cursor="hand2", pady=3,
                              command=lambda k=ex.key: self.select(k))
                b.pack(fill="x", padx=8)
                self.btns[ex.key] = b

    def build_main(self):
        main = tk.Frame(self.root, bg=BG)
        main.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(main, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        bar = tk.Frame(main, bg=PANEL, height=56)
        bar.pack(fill="x")

        def mk(text, cmd, bg=PANEL2):
            b = tk.Button(bar, text=text, command=cmd, bg=bg, fg=TEXT, relief="flat", bd=0,
                          activebackground="#2b3b61", activeforeground=TEXT,
                          font=(FONT, 11, "bold"), cursor="hand2", padx=16, pady=7)
            b.pack(side="left", padx=(12, 0), pady=10)
            return b

        mk("↩  Undo", self.undo)
        mk("⟲  Reset", self.reset)
        mk("▶  Auto-solve", self.auto_solve, bg="#1d4ed8")
        mk("❓  Why?", self.toggle_why)
        tk.Label(bar, text="Speed", bg=PANEL, fg=MUTED, font=(FONT, 9)).pack(side="right", padx=(0, 16))
        tk.Scale(bar, from_=1, to=3, orient="horizontal", variable=self.speed, showvalue=False,
                 length=110, bg=PANEL, fg=TEXT, troughcolor=PANEL2, highlightthickness=0,
                 bd=0).pack(side="right", padx=(0, 6))

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("r", lambda e: self.reset())
        self.root.bind("<space>", lambda e: self.auto_solve())

    # ================================================================== state
    def select(self, key):
        self.cancel()
        self.ex = BY_KEY[key]
        self.analysis = analyze(self.ex.nodes, self.ex.edges)
        self.game = Game(self.ex)
        self.show_why = False
        for k, b in self.btns.items():
            b.configure(bg=PANEL2 if k == key else PANEL,
                        fg=GOLD if k == key else TEXT)
        self.set_status("Click any vertex to start your walk.", MUTED)
        self.redraw()

    def cancel(self):
        """Stop every running animation / auto-solve."""
        self.gen += 1
        self.anim = None
        self.auto_queue = []
        self.auto_running = False
        self.confetti = []

    def reset(self):
        self.cancel()
        self.game.reset()
        self.set_status("Click any vertex to start your walk.", MUTED)
        self.redraw()

    def undo(self):
        if self.anim or self.auto_running:
            self.cancel()
        self.confetti = []
        self.game.undo()
        if self.game.started:
            self.set_status(f"Back at {self.game.current}. Choose another bridge.", MUTED)
        else:
            self.set_status("Click any vertex to start your walk.", MUTED)
        self.redraw()

    def toggle_why(self):
        self.show_why = not self.show_why
        self.redraw()

    def set_status(self, text, color=MUTED):
        self.status, self.status_color = text, color

    # ================================================================== geometry
    def layout(self):
        W, H = self.canvas.winfo_width(), self.canvas.winfo_height()
        W, H = max(W, 400), max(H, 400)
        pos = self.ex.positions
        xs = [p[0] for p in pos.values()]
        ys = [p[1] for p in pos.values()]
        bw, bh = max(max(xs) - min(xs), 1e-6), max(max(ys) - min(ys), 1e-6)
        aw, ah = W - 2 * 90, H - TOP_H - BOTTOM_H - 112   # room for tags & labels
        s = min(aw / bw, ah / bh, 175)
        cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
        oy = TOP_H + 64 + ah / 2
        self.W, self.H = W, H
        self.px = {v: (W / 2 + (x - cx) * s, oy - (y - cy) * s) for v, (x, y) in pos.items()}

        # curved geometry for every edge; parallel bridges bend in opposite directions
        index = {n: i for i, n in enumerate(pos)}
        groups = defaultdict(list)
        for eid, (u, v) in enumerate(self.ex.edges):
            groups[tuple(sorted((u, v), key=index.get))].append(eid)
        self.geo, self.ends = {}, {}
        for (a, b), ids in groups.items():
            (x1, y1), (x2, y2) = self.px[a], self.px[b]
            for j, eid in enumerate(ids):
                rad = (j - (len(ids) - 1) / 2) * 0.45
                cx_, cy_ = (x1 + x2) / 2 + rad * (y2 - y1), (y1 + y2) / 2 - rad * (x2 - x1)
                pts = []
                for i in range(41):
                    t = i / 40
                    pts.append(((1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx_ + t ** 2 * x2,
                                (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy_ + t ** 2 * y2))
                self.geo[eid], self.ends[eid] = pts, (a, b)

    def pts_from(self, eid, frm):
        pts = self.geo[eid]
        return pts if self.ends[eid][0] == frm else pts[::-1]

    # ================================================================== input
    def on_click(self, ev):
        if self.show_why:
            self.show_why = False
            self.redraw()
            return
        if self.anim or self.auto_running:
            return
        for v, (x, y) in self.px.items():
            if math.hypot(ev.x - x, ev.y - y) <= R + 8:
                return self.click_vertex(v)
        best, best_d = None, 11
        for eid, pts in self.geo.items():
            d = min(math.hypot(ev.x - x, ev.y - y) for x, y in pts[4:-4])
            if d < best_d:
                best, best_d = eid, d
        if best is not None:
            self.click_edge(best)

    def click_vertex(self, v):
        g = self.game
        if not g.started:
            g.start(v)
            self.set_status(f"Started at {v}. Click a glowing vertex to cross a bridge.", GOLD)
            return self.redraw()
        if g.won or g.dead_end:
            return
        ids = g.free_edges(to=v)
        if ids:
            self.begin_move(ids[0])
        elif v == g.current:
            self.set_status(f"You are already at {v}.", MUTED)
            self.redraw()
        else:
            self.reject(v, f"No free bridge from {g.current} to {v}.")

    def click_edge(self, eid):
        g = self.game
        if not g.started or g.won or g.dead_end:
            return
        if eid in g.used:
            self.set_status("You already crossed that bridge.", BAD)
        elif eid in g.free_edges():
            return self.begin_move(eid)
        else:
            self.set_status(f"That bridge doesn't touch {g.current}.", BAD)
        self.redraw()

    def reject(self, v, msg):
        self.set_status(msg, BAD)
        self.flash[v] = 14
        self.redraw()

    # ================================================================== moving
    def begin_move(self, eid):
        g = self.game
        frm, to = g.current, g.other_end(eid, g.current)
        self.anim = dict(eid=eid, frm=frm, to=to, pts=self.pts_from(eid, frm), i=0,
                         n=len(g.moves) + 1)
        self.step_anim(self.gen)

    def step_anim(self, gen):
        if gen != self.gen or not self.anim:
            return
        a = self.anim
        a["i"] = min(a["i"] + {1: 1, 2: 2, 3: 4}[self.speed.get()], len(a["pts"]) - 1)
        self.redraw()
        if a["i"] >= len(a["pts"]) - 1:
            self.finish_move(gen)
        else:
            self.root.after(16, lambda: self.step_anim(gen))

    def finish_move(self, gen):
        a, g = self.anim, self.game
        g.move(a["eid"])
        self.anim = None
        left = g.remaining
        if g.won:
            kind = "circuit" if g.is_circuit else "path"
            self.set_status(f"🎉  Every bridge crossed exactly once - Eulerian {kind}!", GOOD)
            self.start_confetti()
        elif g.dead_end:
            self.set_status(f"💥  Dead end at {g.current}: {left} bridge{'s' if left != 1 else ''} "
                            f"left but none touch {g.current}. Undo or Reset.", BAD)
        else:
            self.set_status(f"Crossed bridge #{len(g.moves)} to {g.current}.   "
                            f"{left} to go.", MUTED)
        self.redraw()
        if self.auto_running:
            self.root.after(260, lambda: self.auto_step(gen))

    # ================================================================== auto-solve
    def auto_solve(self):
        if self.anim:
            return
        self.cancel()
        self.game.reset()
        a = self.analysis
        if a.kind == "none":
            trail = longest_trail(self.ex)
            start, eids = trail[0][1], [m[0] for m in trail]
            self.set_status("Watch: no matter how it tries, a bridge is always left over...", BAD)
        else:
            start, eids = a.trail_vertices[0], list(a.trail_edges)
            self.set_status(f"Auto-solving from {start}...", GOLD)
        self.game.start(start)
        self.auto_queue, self.auto_running = eids, True
        self.redraw()
        gen = self.gen
        self.root.after(550, lambda: self.auto_step(gen))

    def auto_step(self, gen):
        if gen != self.gen:
            return
        if self.auto_queue:
            self.begin_move(self.auto_queue.pop(0))
        else:
            self.auto_running = False
            g = self.game
            if self.analysis.kind == "none":
                self.set_status(f"💥  Stuck! Best walk crosses {len(g.moves)} of {len(self.ex.edges)}"
                                f" bridges - an Eulerian path is impossible.", BAD)
            self.redraw()

    # ================================================================== animation tick
    def start_confetti(self):
        cols = [GOLD, GOOD, "#38bdf8", "#e879f9", ODD]
        self.confetti = [[random.uniform(0, self.W), random.uniform(-80, 0), random.uniform(-1.5, 1.5),
                          random.uniform(2, 6), random.choice(cols), random.uniform(4, 9)]
                         for _ in range(110)]

    def tick(self):
        self.t += 1
        moved = False
        for p in self.confetti:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += 0.08
        before = len(self.confetti)
        self.confetti = [p for p in self.confetti if p[1] < self.H + 20]
        moved = bool(before)
        for v in list(self.flash):
            self.flash[v] -= 1
            moved = True
            if self.flash[v] <= 0:
                del self.flash[v]
        pulsing = self.game.started and not self.game.won and not self.game.dead_end
        if not self.anim and (pulsing or moved):
            self.redraw()
        self.root.after(40, self.tick)

    # ================================================================== drawing
    def rrect(self, x1, y1, x2, y2, r, **kw):
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2,
               x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.canvas.create_polygon(pts, smooth=True, **kw)

    def edge_color(self, n):
        return lerp_color("#38bdf8", "#e879f9", (n - 1) / max(len(self.ex.edges) - 1, 1))

    def redraw(self):
        if not hasattr(self, "game"):
            return
        c, g = self.canvas, self.game
        c.delete("all")
        self.layout()
        pulse = (math.sin(self.t * 0.22) + 1) / 2
        deg = self.analysis.degrees
        free = g.free_edges() if (g.started and not g.won and not self.anim) else []
        avail = {g.other_end(e, g.current) for e in free}
        move_no = {m[0]: i + 1 for i, m in enumerate(g.moves)}
        move_dir = {m[0]: m[1] for m in g.moves}

        # ---- edges
        for eid, pts in self.geo.items():
            flat = [coord for p in pts for coord in p]
            if eid in move_no:
                col = self.edge_color(move_no[eid])
                c.create_line(*flat, fill=col, width=6, capstyle="round", joinstyle="round")
                oriented = self.pts_from(eid, move_dir[eid])
                (x1, y1), (x2, y2) = oriented[24], oriented[27]
                ang = math.atan2(y2 - y1, x2 - x1)
                tri = [(x2, y2)] + [(x2 - 13 * math.cos(ang + s), y2 - 13 * math.sin(ang + s))
                                    for s in (0.5, -0.5)]
                c.create_polygon(*[v for p in tri for v in p], fill=col, outline=BG)
                lx, ly = pts[14]
                c.create_oval(lx - 13, ly - 13, lx + 13, ly + 13, fill=BG, outline=col, width=2)
                c.create_text(lx, ly, text=str(move_no[eid]), fill=col, font=(FONT, 11, "bold"))
            elif eid in free:
                col = lerp_color("#8a6a1f", GOLD, pulse)
                c.create_line(*flat, fill=col, width=5, capstyle="round", joinstyle="round")
            else:
                c.create_line(*flat, fill=EDGE_IDLE, width=4, capstyle="round", joinstyle="round")

        # ---- the bridge being crossed right now
        if self.anim:
            a = self.anim
            part = [coord for p in a["pts"][: a["i"] + 1] for coord in p]
            col = self.edge_color(a["n"])
            if len(part) >= 4:
                c.create_line(*part, fill=col, width=6, capstyle="round", joinstyle="round")
            wx, wy = a["pts"][a["i"]]
            c.create_oval(wx - 14, wy - 14, wx + 14, wy + 14, fill="", outline=GOLD, width=2)
            c.create_oval(wx - 9, wy - 9, wx + 9, wy + 9, fill=GOLD, outline=BG, width=2)

        # ---- vertices
        order = g.visit_order()
        for v, (x, y) in self.px.items():
            if v in avail:
                r = R + 8 + 3 * pulse
                c.create_oval(x - r, y - r, x + r, y + r, outline=GOLD, width=3)
            if v == g.current and not self.anim:
                r = R + 8
                c.create_oval(x - r, y - r, x + r, y + r, outline=GOLD, width=4)
                c.create_oval(x - R - 15 - 2 * pulse, y - R - 15 - 2 * pulse, x + R + 15 + 2 * pulse,
                              y + R + 15 + 2 * pulse, outline=lerp_color(BG, GOLD, 0.35), width=2)
            if v in self.flash:
                r = R + 8 + (14 - self.flash[v]) * 0.6
                c.create_oval(x - r, y - r, x + r, y + r, outline=BAD, width=4)
            c.create_oval(x - R, y - R, x + R, y + R, fill=ODD if deg[v] % 2 else EVEN,
                          outline="#0b1220", width=3)
            c.create_text(x, y - 5, text=v, fill="white", font=(FONT, 15, "bold"))
            c.create_text(x, y + 13, text=f"deg {deg[v]}", fill="#0b1220", font=(FONT, 8, "bold"))
            if self.ex.landmarks:
                c.create_text(x, y + R + 14, text=self.ex.landmarks[v], fill=MUTED, font=(FONT, 9))
            if v in order:
                label = " · ".join(map(str, order[v]))
                w = 12 + 8 * len(label)
                self.rrect(x - w / 2, y - R - 30, x + w / 2, y - R - 10, 8, fill=GOLD, outline="")
                c.create_text(x, y - R - 20, text=label, fill="#0b1220", font=(FONT, 10, "bold"))

        self.draw_hud()
        if self.show_why:
            self.draw_why()
        for x, y, _, _, col, s in self.confetti:
            c.create_rectangle(x, y, x + s, y + s * 0.6, fill=col, outline="")

    # ------------------------------------------------------------------ HUD
    def verdict(self):
        a = self.analysis
        odd = ", ".join(a.odd_vertices)
        if not a.connected:
            return ("✗  No Eulerian path", "The graph is split into separate pieces", BAD)
        if a.kind == "circuit":
            return ("✓  Eulerian circuit exists", "0 odd vertices - start anywhere, end where you began", GOOD)
        if a.kind == "path":
            return ("✓  Eulerian path exists", f"2 odd vertices ({odd}) - start at one, finish at the other", GOOD)
        return ("✗  No Eulerian path", f"{len(a.odd_vertices)} odd vertices ({odd}) - at most 2 allowed", BAD)

    def draw_hud(self):
        c, g, W, H = self.canvas, self.game, self.W, self.H
        c.create_text(24, 16, text=self.ex.title, anchor="nw", fill=TEXT,
                      font=(FONT, 16, "bold"), width=W - 470)
        c.create_text(24, 62, text=self.ex.description, anchor="nw", fill=MUTED,
                      font=(FONT, 10), width=W - 470)
        title, sub, col = self.verdict()
        self.rrect(W - 424, 14, W - 20, 92, 14, fill=PANEL, outline=col, width=2)
        c.create_text(W - 408, 32, text=title, anchor="w", fill=col, font=(FONT, 15, "bold"))
        c.create_text(W - 408, 66, text=sub, anchor="w", fill=TEXT, font=(FONT, 9), width=370)
        c.create_line(0, TOP_H, W, TOP_H, fill=PANEL2)

        y0 = H - BOTTOM_H
        c.create_line(0, y0, W, y0, fill=PANEL2)
        c.create_text(24, y0 + 22, text=self.status, anchor="w", fill=self.status_color,
                      font=(FONT, 12, "bold"), width=W - 48)
        total, used = len(self.ex.edges), len(g.moves)
        c.create_text(24, y0 + 56, text="Bridges", anchor="w", fill=MUTED, font=(FONT, 9))
        self.rrect(90, y0 + 50, W - 90, y0 + 62, 6, fill=PANEL2, outline="")
        if used:
            self.rrect(90, y0 + 50, 90 + (W - 180) * used / total, y0 + 62, 6,
                       fill=GOOD if g.won else "#38bdf8", outline="")
        c.create_text(W - 24, y0 + 56, text=f"{used} / {total}", anchor="e", fill=TEXT,
                      font=(FONT, 10, "bold"))
        route = [g.moves[0][1]] + [m[2] for m in g.moves] if g.moves else ([g.current] if g.started else [])
        txt = " → ".join(route if len(route) <= 16 else ["…"] + route[-15:])
        c.create_text(24, y0 + 90, text="Route:  " + (txt or "-"), anchor="w", fill=TEXT,
                      font=("Consolas", 15, "bold"), width=W - 48)

    def draw_why(self):
        c, a, W, H = self.canvas, self.analysis, self.W, self.H
        deg = a.degrees
        sums = "  ".join(f"{v}={d}" for v, d in deg.items())
        lines = [f"Degrees:  {sums}   (sum {a.total_degree} = 2 × {len(self.ex.edges)} bridges)",
                 "A walk enters and leaves every middle vertex in pairs → it must have EVEN degree.",
                 "Only the start and the end may be odd → at most 2 odd vertices."]
        if not a.connected:
            lines.append("But the graph is disconnected, so one walk can't reach every bridge  ✗")
            col = BAD
        elif a.kind == "none":
            lines.append(f"Here {len(a.odd_vertices)} vertices are odd ({', '.join(a.odd_vertices)})  →  impossible  ✗")
            col = BAD
        elif a.kind == "path":
            lines.append(f"Here exactly 2 are odd ({', '.join(a.odd_vertices)})  →  path from one to the other  ✓")
            col = GOOD
        else:
            lines.append("Here all vertices are even and connected  →  closed circuit possible  ✓")
            col = GOOD
        w, h = 720, 210
        x1, y1 = (W - w) / 2, (H - h) / 2 - 10
        self.rrect(x1, y1, x1 + w, y1 + h, 16, fill=PANEL, outline=col, width=3)
        c.create_text(W / 2, y1 + 28, text="Why?", fill=col, font=(FONT, 15, "bold"))
        for i, ln in enumerate(lines):
            c.create_text(x1 + 28, y1 + 66 + i * 34, text=ln, anchor="w", fill=TEXT, font=(FONT, 11),
                          width=w - 56)
        c.create_text(W / 2, y1 + h - 14, text="click anywhere to close", fill=MUTED, font=(FONT, 8))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
