"""RAShR explainer -- layman-first Manim scenes (one class per narration scene).
Render: python build_video.py render [--quality low]   Pacing is driven by narration audio (see common.SyncScene)."""
from common import *
PI = np.pi

# ------------------------------------------------------------------ shared helpers
def toy(seed=5, nb=10, nr=6):
    """small crowd for chord pictures: nb honest dots on a rising trend + nr dots in a tight clump far right"""
    r = np.random.default_rng(seed)
    xb = np.linspace(0.6, 6.2, nb) + r.normal(0, .15, nb); yb = 0.6 + 0.9 * xb + r.normal(0, .3, nb)
    xr = 9.0 + r.normal(0, .18, nr); yr = 0.8 + r.normal(0, .18, nr)
    return np.r_[xb, xr], np.r_[yb, yr], np.r_[np.zeros(nb, bool), np.ones(nr, bool)]

def small_axes(w=7.4, h=4.8, xr=(0, 10, 2), yr=(-1, 9, 2), shift=LEFT * 2.2 + DOWN * 0.3):
    return Axes(x_range=list(xr), y_range=list(yr), x_length=w, y_length=h, tips=False,
                axis_config=dict(color=MUTED, stroke_width=2, font_size=16)).shift(shift)

def pdots(ax, x, y, bad=None, r=0.07):
    return VGroup(*[Dot(ax.c2p(a, b), radius=r, color=(RED if bad is not None and bad[i] else BLUE)) for i, (a, b) in enumerate(zip(x, y))])

def chord_ang(x0, y0, x1, y1):
    return np.arctan2(y1 - y0, x1 - x0) % PI

def circ_dist(a, b):
    d = abs(a - b) % PI; return min(d, PI - d)

def shorth_window(angles, h):
    """returns (start, width) of shortest circular window of h angles (radians, in [0,pi))"""
    a = np.sort(np.asarray(angles) % PI); m = len(a); e = np.r_[a, a + PI]
    best = (1e9, 0)
    for i in range(m):
        w = e[i + h - 1] - e[i]
        if w < best[0] - 1e-12: best = (w, i)
    return e[best[1]], best[0]

def arc_win(center, start_deg, width_deg, radius, color=TEAL, sw=9):
    """arc on projective circle: directions start..start+width (deg) are drawn at doubled angle"""
    return Arc(radius=radius, start_angle=2 * np.radians(start_deg), angle=2 * np.radians(max(width_deg, 0.4)), arc_center=center, color=color, stroke_width=sw)

def bullet_panel(lines, color=INK, size=24, buff=0.25):
    return VGroup(*[T(s, size, color) for s in lines]).arrange(DOWN, aligned_edge=LEFT, buff=buff)

def full_ax():
    return axes_xy().shift(DOWN * 0.35 + LEFT * 1.2)

# ================================================================== PART A : the problem
class A00_title(SyncScene):
    sid = "A00_title"
    def construct(self):
        self.seg(0)
        cen = RIGHT * 4.1; R = 1.8; circ = unit_circle(R, cen)
        ttl = VGroup(T("RAShR", 34, TEAL, weight=BOLD), T("Finding the true line\nwhen the crowd misleads", 50, INK, weight=BOLD),
                     T("a picture-first explanation, no maths background needed", 24, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.4).to_edge(LEFT, buff=0.9)
        rng = np.random.default_rng(1)
        good = VGroup(*[Dot(on_circle(34 + rng.normal(0, 4), R, cen), radius=0.06, color=BLUE) for _ in range(26)])
        bad = VGroup(*[Dot(on_circle(rng.uniform(120, 170), R, cen), radius=0.06, color=RED) for _ in range(9)])
        self.play(FadeIn(ttl[0]), Write(ttl[1]), run_time=3.0)
        self.play(FadeIn(ttl[2]), FadeIn(circ), run_time=1.5)
        self.play(LaggedStart(*[FadeIn(d, scale=2) for d in [*good, *bad]], lag_ratio=0.05), run_time=3)
        arc = Arc(radius=R + 0.14, start_angle=2 * np.radians(28), angle=2 * np.radians(12), arc_center=cen, color=TEAL, stroke_width=8)
        words = T("Repeated   Angular   Shorth", 26, GOLD).next_to(circ, DOWN, buff=0.5)
        self.play(Create(arc)); self.play(Write(words)); self.end_seg()

class A01_hook(SyncScene):
    sid = "A01_hook"
    def construct(self):
        x, y, bad = fig1(); ax = full_ax(); self.add(ax)
        t = T("Which line is the right one?", 34, INK, weight=BOLD).to_corner(UL, buff=0.45); self.add(t)
        self.seg(0)
        maj = dots(ax, x[~bad], y[~bad]); clu = dots(ax, x[bad], y[bad], bad[bad])
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in maj], lag_ratio=0.01), run_time=2.0)
        self.play(FadeIn(clu, scale=1.4), run_time=1.0)
        lab = VGroup(T("62 dots: a rising trend", 22, BLUE), T("38 dots: a tight clump", 22, RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR, buff=0.5)
        self.play(FadeIn(lab)); self.end_seg()
        self.seg(1)
        a, b = rc.ols(x, y); ln = line_on(ax, a, b, GRAY_B, stroke_width=5)
        r1 = T(f"least squares: slope {b:+.2f}", 22, GRAY_B).next_to(lab, DOWN, aligned_edge=LEFT, buff=0.4)
        self.play(Create(ln), FadeIn(r1)); self.end_seg()
        self.seg(2)
        rows = VGroup(); anims = []
        for name, (a, b), col in [("LMS", rc.lms(x, y), ORANGE), ("MM", rc.mm(x, y), PURPLE)]:
            anims.append(Create(line_on(ax, a, b, col, stroke_width=4))); rows.add(T(f"{name}: slope {b:+.2f}", 22, col))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(r1, DOWN, aligned_edge=LEFT, buff=0.15)
        self.play(LaggedStart(*anims, lag_ratio=0.6), FadeIn(rows), run_time=3); self.end_seg()
        self.seg(3)
        a, b = rc.rashr(x, y)
        ln = line_on(ax, a, b, GOLD, stroke_width=7); r = T(f"RAShR: slope {b:+.2f}", 26, GOLD, weight=BOLD).next_to(rows, DOWN, aligned_edge=LEFT, buff=0.3)
        self.play(Create(ln), FadeIn(r), run_time=1.8)
        c = T("true slope = 2", 22, TEAL).next_to(r, DOWN, aligned_edge=LEFT, buff=0.2); self.play(FadeIn(c)); self.end_seg()
        self.seg(4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        steps = VGroup(*[T(s, 30, INK) for s in ["1   What is a line, and how do bad dots break it?", "2   The new idea: directions between pairs of dots",
                 "3   Why it works", "4   Honest tests, including where it fails"]]).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        for s in steps: self.play(FadeIn(s, shift=RIGHT * 0.3), run_time=0.8)
        self.end_seg()

class A02_line_basics(SyncScene):
    sid = "A02_line_basics"
    def construct(self):
        ax = Axes(x_range=[0, 8, 1], y_range=[0, 10, 2], x_length=7.4, y_length=4.8, tips=False, axis_config=dict(color=MUTED, stroke_width=2, font_size=16)).shift(LEFT * 2.2 + DOWN * 0.3)
        xl = T("hours studied", 20, MUTED).next_to(ax, DOWN, buff=0.15); yl = T("exam score", 20, MUTED).rotate(PI / 2).next_to(ax, LEFT, buff=0.15)
        self.add(ax, xl, yl)
        r = np.random.default_rng(2); xs = np.linspace(0.5, 7.5, 14); ys = 1.5 + 1.0 * xs + r.normal(0, .55, 14)
        self.seg(0)
        d = pdots(ax, xs, ys); self.play(LaggedStart(*[FadeIn(p, scale=0.4) for p in d], lag_ratio=0.1), run_time=2.5)
        ln = Line(ax.c2p(0, 1.5), ax.c2p(8, 9.5), color=GOLD, stroke_width=5); self.play(Create(ln), run_time=1.5)
        self.play(FadeIn(T("more hours  →  higher score", 24, GOLD).to_corner(UR, buff=0.5)), run_time=1); self.end_seg()
        self.seg(1)
        p0 = ax.c2p(3, 4.5); p1 = ax.c2p(4, 4.5); p2 = ax.c2p(4, 5.5)
        run = Line(p0, p1, color=TEAL, stroke_width=6); rise = Line(p1, p2, color=ORANGE, stroke_width=6)
        self.play(Create(run)); self.play(Create(rise))
        lr = T("1 step right", 20, TEAL).next_to(run, DOWN, buff=0.1); lu = T("slope = steps up", 20, ORANGE).next_to(rise, RIGHT, buff=0.1)
        self.play(FadeIn(lr), FadeIn(lu))
        panel = bullet_panel(["climbs 2  →  slope 2", "falls 1  →  slope −1", "flat  →  slope 0"], INK, 24).to_corner(UR, buff=0.5).shift(DOWN * 0.9)
        self.play(FadeIn(panel)); self.end_seg()
        self.seg(2)
        dd = Dot(ax.c2p(0, 1.5), radius=0.13, color=RED); circ = Circle(radius=0.3, color=RED).move_to(dd)
        lab = T("intercept: the height at zero", 22, RED).next_to(panel, DOWN, aligned_edge=LEFT, buff=0.5)
        self.play(FadeIn(dd, scale=2), Create(circ), FadeIn(lab)); self.end_seg()
        self.seg(3)
        eq = T("score = intercept + slope × hours", 30, GOLD, weight=BOLD).to_edge(DOWN, buff=0.12)
        self.play(Write(eq))
        t2 = T("the whole video: find these two numbers\nwhen some of the dots lie", 22, MUTED).to_corner(UR, buff=0.5).shift(DOWN * 3.3); self.play(FadeIn(t2)); self.end_seg()

class A03_best_line(SyncScene):
    sid = "A03_best_line"
    def construct(self):
        ax = Axes(x_range=[0, 8, 1], y_range=[0, 10, 2], x_length=7.4, y_length=4.8, tips=False, axis_config=dict(color=MUTED, stroke_width=2, font_size=16)).shift(LEFT * 2.2 + DOWN * 0.3)
        self.add(ax)
        r = np.random.default_rng(2); xs = np.linspace(0.5, 7.5, 14); ys = 1.5 + 1.0 * xs + r.normal(0, .55, 14)
        d = pdots(ax, xs, ys); self.add(d)
        sl = ValueTracker(1.0); ic = ValueTracker(1.5)
        line = always_redraw(lambda: Line(ax.c2p(0, ic.get_value()), ax.c2p(8, ic.get_value() + 8 * sl.get_value()), color=GOLD, stroke_width=5))
        def gaps():
            g = VGroup()
            for a, b in zip(xs, ys):
                yl = ic.get_value() + sl.get_value() * a
                g.add(Line(ax.c2p(a, b), ax.c2p(a, yl), color=ORANGE, stroke_width=3))
            return g
        def squares():
            g = VGroup()
            for a, b in zip(xs, ys):
                yl = ic.get_value() + sl.get_value() * a; side = abs(ax.c2p(0, b)[1] - ax.c2p(0, yl)[1])
                if side < 0.01: continue
                s = Square(side, color=RED, stroke_width=1, fill_color=RED, fill_opacity=0.18)
                s.move_to(ax.c2p(a, (b + yl) / 2) + RIGHT * side / 2); g.add(s)
            return g
        self.seg(0)
        self.play(Create(line)); self.play(sl.animate.set_value(0.5), run_time=1.0)
        gp = always_redraw(gaps); self.add(gp)
        self.play(FadeIn(T("each vertical gap = a miss (residual)", 22, ORANGE).to_corner(UR, buff=0.5)))
        self.play(sl.animate.set_value(1.0), run_time=1.0); self.end_seg()
        self.seg(1)
        sq = always_redraw(squares); self.add(sq)
        tot = always_redraw(lambda: T(f"total area of squares: {sum(s.width**2 for s in squares())/ (ax.c2p(1,0)[0]-ax.c2p(0,0)[0])**2:.1f}", 24, RED).to_corner(UR, buff=0.5).shift(DOWN * 0.8))
        self.add(tot); self.end_seg()
        self.seg(2)
        self.play(sl.animate.set_value(0.2), ic.animate.set_value(3), run_time=1.5)
        self.play(sl.animate.set_value(1.6), ic.animate.set_value(0), run_time=1.5)
        self.play(sl.animate.set_value(1.0), ic.animate.set_value(1.5), run_time=1.5)
        self.end_seg()
        self.seg(3)
        far = Dot(ax.c2p(7.5, 1.2), radius=0.12, color=RED); self.play(FadeIn(far, scale=2))
        # one-dot pull: new best line (OLS incl. far dot)
        X = np.r_[xs, 7.5]; Y = np.r_[ys, 1.2]; b, a = np.polyfit(X, Y, 1)
        self.play(sl.animate.set_value(b), ic.animate.set_value(a), run_time=3)
        self.play(FadeIn(T("one far dot, one huge square: the line swings", 24, RED).to_edge(DOWN, buff=0.4))); self.end_seg()

class A04_crowds(SyncScene):
    sid = "A04_crowds"
    def panel(self, title, x0, kind):
        ax = Axes(x_range=[0, 10, 5], y_range=[0, 10, 5], x_length=3.4, y_length=2.6, tips=False, axis_config=dict(color=MUTED, stroke_width=1.5, include_ticks=False)).move_to([x0, 0.3, 0])
        rng = np.random.default_rng(3); xs = rng.uniform(0.5, 9.5, 30); ys = 0.8 * xs + 1 + rng.normal(0, .4, 30)
        g = VGroup(*[Dot(ax.c2p(a, b), radius=0.04, color=BLUE) for a, b in zip(xs, ys)]); extra = VGroup()
        if kind == "outlier": extra.add(Dot(ax.c2p(2, 9), radius=0.09, color=RED))
        if kind == "coherent": extra.add(*[Dot(ax.c2p(8.5 + rng.normal(0, .15), 1 + rng.normal(0, .15)), radius=0.05, color=RED) for _ in range(12)])
        if kind == "leverage": extra.add(Dot(ax.c2p(10, 1), radius=0.1, color=ORANGE))
        return VGroup(ax, g, extra, T(title, 22, INK).next_to(ax, UP, buff=0.25))
    def construct(self):
        t = self.title("Kinds of bad dots")
        self.seg(0)
        p1 = self.panel("one outlier", -4.4, "outlier"); self.play(FadeIn(p1))
        self.play(FadeIn(T("a lone oddball: easy to handle", 20, MUTED).next_to(p1, DOWN, buff=0.3)))
        p2 = self.panel("a whole group", 0, "coherent"); self.play(FadeIn(p2)); self.end_seg()
        self.seg(1)
        n2 = T("coherent contamination", 24, RED, weight=BOLD).next_to(p2, DOWN, buff=0.3); self.play(FadeIn(n2))
        vote = bullet_panel(["1 voter differs: no change", "a group agrees with itself:", "a rival opinion"], INK, 22).to_corner(DL, buff=0.5)
        self.play(FadeIn(vote)); self.end_seg()
        self.seg(2)
        p3 = self.panel("far to the right", 4.4, "leverage"); self.play(FadeIn(p3))
        lev = Line(LEFT * 1.2, RIGHT * 1.2, color=ORANGE, stroke_width=8).shift(RIGHT * 4.4 + DOWN * 2.1); fulc = Triangle(color=MUTED, fill_opacity=1, fill_color=MUTED).scale(0.18).move_to(lev.get_center() + DOWN * 0.2)
        self.play(Create(lev), FadeIn(fulc)); self.play(FadeIn(T("far = long handle = strong pull (leverage)", 20, ORANGE).next_to(lev, DOWN, buff=0.5)))
        self.end_seg()

class A05_breakdown(SyncScene):
    sid = "A05_breakdown"
    def construct(self):
        t = self.title("How many bad dots can a method survive?")
        self.seg(0)
        N = 20; row = VGroup(*[Dot(radius=0.14, color=BLUE) for _ in range(N)]).arrange(RIGHT, buff=0.3).shift(UP * 0.5)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in row], lag_ratio=0.05), run_time=1.5)
        bar = Rectangle(width=9, height=0.4, color=MUTED, stroke_width=2).shift(DOWN * 1.5)
        lbl = T("fraction replaced by bad dots", 20, INK).next_to(bar, UP, buff=0.2); self.play(FadeIn(bar), FadeIn(lbl))
        fill = Rectangle(width=0.01, height=0.4, color=RED, fill_opacity=0.8, stroke_width=0).align_to(bar, LEFT).align_to(bar, DOWN)
        self.add(fill)
        for k in range(0, 11):
            self.play(row[N - 1 - k].animate.set_color(RED), fill.animate.stretch_to_fit_width(9 * (k + 1) / N, about_edge=LEFT), run_time=0.45)
        self.end_seg()
        self.seg(1)
        a = T("ordinary average: breaks with ONE bad dot", 24, RED).to_edge(DOWN, buff=1.4)
        b = T("strong robust methods: survive almost half", 24, TEAL).next_to(a, DOWN, buff=0.2)
        self.play(FadeIn(a)); self.play(FadeIn(b))
        mark = DashedLine(bar.get_top() + UP * 0.1, bar.get_bottom() + DOWN * 0.1, color=TEAL).move_to(bar.get_center()); self.play(Create(mark)); self.end_seg()
        self.seg(2)
        q = VGroup(T("a promise:  \"the line stays somewhere reasonable\"", 26, TEAL), T("NOT a promise:  \"the line follows the honest crowd\"", 26, ORANGE)).arrange(DOWN, buff=0.4, aligned_edge=LEFT).to_edge(UP, buff=1.7)
        self.play(FadeIn(q[0])); self.play(FadeIn(q[1])); self.end_seg()

class A06_median_mad(SyncScene):
    sid = "A06_median_mad"
    def construct(self):
        t = self.title("Two small tools: median and typical spread")
        vals = [3, 4, 5, 6, 8, 9, 10]
        def row(vs, y, cols=None):
            g = VGroup(*[VGroup(Square(0.8, color=MUTED, stroke_width=2), T(str(v), 26, INK)).arrange(ORIGIN) for v in vs]); 
            for m in g: m[1].move_to(m[0])
            g.arrange(RIGHT, buff=0.1).move_to([0, y, 0]); return g
        self.seg(0)
        r1 = row(vals, 1.0); self.play(LaggedStart(*[FadeIn(b) for b in r1], lag_ratio=0.1))
        ar = Arrow(DOWN * 0.7 + RIGHT * 0, UP * 0.55, color=GOLD, buff=0).move_to(r1[3].get_bottom() + DOWN * 0.5); self.play(GrowArrow(ar))
        medl = T("median = the middle one", 24, GOLD).next_to(ar, DOWN, buff=0.1)
        self.play(r1[3][0].animate.set_fill(GOLD, 0.4), FadeIn(medl)); self.end_seg()
        self.seg(1)
        r2 = row([3, 4, 5, 6, 8, 9, 1000000], -1.8); r2[6][1].scale(0.5); self.play(FadeOut(ar), FadeOut(medl))
        self.play(FadeIn(r2), FadeIn(T("push the last number to a million:", 22, RED).next_to(r2, UP, buff=0.2)))
        self.play(FadeIn(T("average explodes (≈ 142 860)     median still 6", 24, INK).next_to(r2, DOWN, buff=0.4))); self.end_seg()
        self.seg(2)
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not t])), run_time=0.5)
        line = NumberLine(x_range=[0, 12, 1], length=10, include_numbers=True, font_size=22, color=MUTED).shift(DOWN * 0.3)
        pts = [3, 4, 5, 6, 8, 9, 10]; dts = VGroup(*[Dot(line.n2p(v), radius=0.1, color=BLUE) for v in pts]); med = Dot(line.n2p(6), radius=0.14, color=GOLD)
        self.play(Create(line), FadeIn(dts), FadeIn(med))
        arrs = VGroup(*[Arrow(line.n2p(6), line.n2p(v), color=ORANGE, buff=0.15, stroke_width=3, max_tip_length_to_length_ratio=0.2).shift(UP * (0.5 + 0.12 * i)) for i, v in enumerate(pts) if v != 6])
        self.play(LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=0.2), run_time=2)
        self.play(FadeIn(T("distance of each number from the median →  take the median of those distances", 22, ORANGE).to_edge(UP, buff=1.5)))
        self.end_seg()
        self.seg(3)
        f = VGroup(T("robust scale  =  1.4826  ×  (typical distance from the median)", 26, GOLD, weight=BOLD), T("median → where the centre is        robust scale → how big the spread is", 22, INK)).arrange(DOWN, buff=0.3).to_edge(DOWN, buff=0.7)
        self.play(FadeIn(f[0])); self.play(FadeIn(f[1])); self.end_seg()

class A07_residual_methods(SyncScene):
    sid = "A07_residual_methods"
    def construct(self):
        x, y, bad = fig1(); ax = full_ax(); self.add(ax); self.add(dots(ax, x, y, bad))
        t = self.title("The ribbon idea (least median of squares)")
        def strip(a, b, w, col):
            xs = np.linspace(-6, 18, 2); pts = [ax.c2p(u, a + b * u + w) for u in xs] + [ax.c2p(u, a + b * u - w) for u in xs[::-1]]
            return Polygon(*pts, color=col, fill_color=col, fill_opacity=0.25, stroke_width=1)
        self.seg(0)
        s1 = strip(1, 2, 1.4, TEAL); l1 = line_on(ax, 1, 2, TEAL, stroke_width=3)
        self.play(Create(l1), FadeIn(s1)); self.play(FadeIn(T("thinnest ribbon that covers half the dots", 22, TEAL).to_corner(UR, buff=0.5).shift(DOWN * 0.5))); self.end_seg()
        self.seg(1)
        w1 = T("honest line: noisy dots → fairly wide ribbon", 22, TEAL).to_corner(UR, buff=0.5).shift(DOWN * 1.0); self.play(FadeIn(w1))
        a, b = rc.lms(x, y); s2 = strip(a, b, 0.9, ORANGE); l2 = line_on(ax, a, b, ORANGE, stroke_width=3)
        self.play(FadeOut(s1), FadeOut(l1), Create(l2), FadeIn(s2)); self.end_seg()
        self.seg(2)
        circ = Circle(radius=0.65, color=RED).move_to(dots(ax, [15], [-10]))
        self.play(Create(circ)); w2 = T("38 dots almost in one spot:\nonly 12 more needed", 22, ORANGE).next_to(w1, DOWN, aligned_edge=LEFT, buff=0.4); self.play(FadeIn(w2)); self.end_seg()
        self.seg(3)
        eps = ValueTracker(0.30)
        txt = always_redraw(lambda: T(f"bad share = {eps.get_value():.0%}", 26, INK).next_to(w2, DOWN, aligned_edge=LEFT, buff=0.5))
        need = always_redraw(lambda: T(f"honest dots still needed: {int(round((0.5 - eps.get_value()) * 100))}", 24, RED).next_to(txt, DOWN, aligned_edge=LEFT, buff=0.2))
        self.add(txt, need); self.play(eps.animate.set_value(0.49), run_time=5, rate_func=linear)
        msg = T("ribbon through the clump → thinner and thinner → wins", 22, ORANGE).to_edge(DOWN, buff=0.3); self.play(FadeIn(msg)); self.end_seg()
        self.seg(4)
        n = VGroup(T("proved: least median of squares", 22, TEAL), T("seen in experiments only: trimmed squares, MM", 22, MUTED)).arrange(DOWN, aligned_edge=LEFT).to_edge(DOWN, buff=0.3)
        self.play(FadeOut(msg), FadeIn(n)); self.end_seg()

# ================================================================== PART B : the idea
class B01_pairs(SyncScene):
    sid = "B01_pairs"
    def construct(self):
        x, y, bad = toy(); ax = small_axes(); self.add(ax); n = len(x)
        t = self.title("Look at pairs of dots")
        self.seg(0)
        d = pdots(ax, x, y, bad); self.play(LaggedStart(*[FadeIn(p, scale=0.4) for p in d], lag_ratio=0.05), run_time=1.5)
        i, j = 3, 6
        seg = Line(d[i].get_center(), d[j].get_center(), color=GOLD, stroke_width=5)
        self.play(Indicate(d[i]), Indicate(d[j])); self.play(Create(seg))
        self.play(FadeIn(T("a segment between two dots = a chord", 24, GOLD).to_corner(UR, buff=0.5)))
        self.play(FadeIn(T("it has a direction", 22, INK).to_corner(UR, buff=0.5).shift(DOWN * 0.6))); self.end_seg()
        self.seg(1)
        self.play(FadeOut(seg))
        allc = VGroup(); 
        for a in range(n):
            for b in range(a + 1, n):
                col = BLUE if (not bad[a] and not bad[b]) else (RED if (bad[a] and bad[b]) else PURPLE)
                allc.add(Line(d[a].get_center(), d[b].get_center(), color=col, stroke_width=1.3, stroke_opacity=0.55))
        self.play(LaggedStart(*[Create(c) for c in allc], lag_ratio=0.01), run_time=4)
        key = VGroup(T("blue dot – blue dot", 20, BLUE), T("blue dot – red dot", 20, PURPLE), T("red dot – red dot", 20, RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UR, buff=0.5).shift(DOWN * 1.4)
        self.play(FadeIn(key)); self.end_seg()
        self.seg(2)
        grp = {BLUE: [], PURPLE: [], RED: []}
        mapk = {}
        k = 0
        for a in range(n):
            for b in range(a + 1, n):
                mapk[k] = (a, b); k += 1
        def show(kind):
            return [allc[q] for q, (a, b) in mapk.items() if (kind == "bb" and not bad[a] and not bad[b]) or (kind == "br" and bad[a] != bad[b]) or (kind == "rr" and bad[a] and bad[b])]
        for kind, txt in [("bb", "lean upward: near the true trend"), ("br", "all lean the same way, downward"), ("rr", "tiny, pointing every which way")]:
            others = [c for c in allc if c not in show(kind)]
            self.play(*[c.animate.set_stroke(opacity=0.06) for c in others], *[c.animate.set_stroke(width=3, opacity=1) for c in show(kind)], run_time=0.8)
            m = T(txt, 22, INK).to_edge(DOWN, buff=0.4); self.play(FadeIn(m)); self.wait(1.8); self.play(FadeOut(m), *[c.animate.set_stroke(width=1.3, opacity=0.55) for c in allc], run_time=0.5)
        self.end_seg()
        self.seg(3)
        self.play(FadeIn(T("honest trend = the favourite direction among chords", 26, GOLD, weight=BOLD).to_edge(DOWN, buff=0.7)))
        self.end_seg()

class B02_units(SyncScene):
    sid = "B02_units"
    def construct(self):
        x, y, bad = toy(); ax = small_axes(); n = len(x)
        t = self.title("Directions depend on the units")
        self.seg(0)
        # stretch demo: redraw axes with different y_length
        sy = ValueTracker(1.0)
        g = always_redraw(lambda: VGroup(*[Dot([ax.c2p(a, 0)[0], ax.c2p(0, 4)[1] + (ax.c2p(0, b)[1] - ax.c2p(0, 4)[1]) * sy.get_value(), 0], radius=0.07, color=(RED if bad[k] else BLUE)) for k, (a, b) in enumerate(zip(x[:10], y[:10]))]))
        ln = always_redraw(lambda: Line([ax.c2p(0.5, 0)[0], ax.c2p(0, 4)[1] + (ax.c2p(0, 1.0)[1] - ax.c2p(0, 4)[1]) * sy.get_value(), 0], [ax.c2p(6.5, 0)[0], ax.c2p(0, 4)[1] + (ax.c2p(0, 6.5)[1] - ax.c2p(0, 4)[1]) * sy.get_value(), 0], color=GOLD, stroke_width=5))
        self.add(ax, g, ln)
        self.play(sy.animate.set_value(1.7), run_time=2); self.play(sy.animate.set_value(0.4), run_time=2.5); self.play(sy.animate.set_value(1.0), run_time=1.2)
        self.play(FadeIn(T("same dots, different angle, just by changing units", 22, GOLD).to_corner(UR, buff=0.4).shift(DOWN * 0.5)))
        self.end_seg()
        self.seg(1)
        ex = VGroup(T("height in metres  ×  weight in grams", 24, INK), T("switch to kilometres →  the angle changes", 24, ORANGE)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_corner(UR, buff=0.5).shift(DOWN * 1.6)
        self.play(FadeIn(ex[0])); self.play(FadeIn(ex[1])); self.end_seg()
        self.seg(2)
        self.remove(g, ln)
        self.play(FadeOut(ax), FadeOut(ex))
        xm, ym = np.median(x), np.median(y)
        def rs(v): m = np.median(v); return 1.4826 * np.median(np.abs(v - m))
        u = (x - xm) / rs(x); v = (y - ym) / rs(y)
        ax2 = Axes(x_range=[-3, 4, 1], y_range=[-3, 4, 1], x_length=6.2, y_length=6.2, tips=False, axis_config=dict(color=MUTED, stroke_width=2, font_size=16)).shift(LEFT * 2.2 + DOWN * 0.1)
        # show raw -> shifted -> scaled as three mini steps with dots morphing
        raw = pdots(ax, x, y, bad); self.play(FadeIn(ax), FadeIn(raw))
        c1 = T("① slide: median of each axis → 0", 24, TEAL).to_corner(UR, buff=0.5).shift(DOWN * 0.6); self.play(FadeIn(c1))
        mid_ax = Axes(x_range=[-6, 5, 2], y_range=[-5, 5, 2], x_length=7.4, y_length=4.8, tips=False, axis_config=dict(color=MUTED, stroke_width=2, font_size=16)).shift(LEFT * 2.2 + DOWN * 0.3)
        self.play(ReplacementTransform(ax, mid_ax), *[p.animate.move_to(mid_ax.c2p(x[k] - xm, y[k] - ym)) for k, p in enumerate(raw)], run_time=2)
        self.play(FadeIn(T("② divide each axis by its robust scale", 24, TEAL).next_to(c1, DOWN, aligned_edge=LEFT, buff=0.3))); self.wait(0.6)
        ax3 = ax2.copy(); self.play(ReplacementTransform(mid_ax, ax2), *[p.animate.move_to(ax2.c2p(u[k], v[k])) for k, p in enumerate(raw)], run_time=2.5)
        self.end_seg()
        self.seg(3)
        self.play(FadeIn(T("new coordinates  (u, v):  both axes now in units of 'typical spread'", 24, GOLD, weight=BOLD).to_edge(DOWN, buff=0.5))); self.end_seg()

class B03_angles(SyncScene):
    sid = "B03_angles"
    def construct(self):
        t = self.title("A direction is an angle")
        cen = LEFT * 3.3 + DOWN * 0.3
        self.seg(0)
        base = Line(cen, cen + RIGHT * 3.2, color=MUTED, stroke_width=3); p = cen + 3 * np.array([np.cos(0.8), np.sin(0.8), 0])
        seg = Line(cen, p, color=GOLD, stroke_width=6); ang = Angle(base, seg, radius=1.0, color=TEAL, stroke_width=5)
        d0 = Dot(cen, color=BLUE); d1 = Dot(p, color=BLUE)
        self.play(FadeIn(d0), FadeIn(d1), Create(base)); self.play(Create(seg), Create(ang))
        self.play(FadeIn(T("face right, turn up until you face the other dot", 22, TEAL).to_corner(UR, buff=0.5)))
        lab = T("angle = 46°", 24, TEAL).move_to(cen + RIGHT * 1.7 + UP * 0.3); self.play(FadeIn(lab)); self.end_seg()
        self.seg(1)
        ssl = VGroup(T("slope = rise ÷ run", 24, ORANGE), T("near-vertical:  run ≈ 0  → slope enormous", 22, RED), T("angle:  89° and 91° are neighbours", 22, TEAL)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_corner(UR, buff=0.5).shift(DOWN * 0.9)
        self.play(FadeIn(ssl[0]))
        tr = ValueTracker(0.8)
        sg = always_redraw(lambda: Line(cen, cen + 3 * np.array([np.cos(tr.get_value()), np.sin(tr.get_value()), 0]), color=GOLD, stroke_width=6))
        self.remove(seg); self.add(sg); self.play(FadeOut(ang), FadeOut(lab), tr.animate.set_value(PI / 2 - 0.02), run_time=3); self.play(FadeIn(ssl[1]))
        self.play(tr.animate.set_value(PI / 2 + 0.05), run_time=1.5); self.play(FadeIn(ssl[2])); self.end_seg()
        self.seg(2)
        self.play(FadeOut(ssl))
        f = VGroup(T("computers use atan2:", 24, INK), T("(how far up, how far right)  →  which way the arrow points", 22, GOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_corner(UR, buff=0.5).shift(DOWN * 0.7)
        self.play(FadeIn(f)); self.play(tr.animate.set_value(0.3), run_time=2); self.play(tr.animate.set_value(1.2), run_time=2)
        self.play(FadeIn(T("a direction is an arrow, and an arrow has an angle", 26, GOLD, weight=BOLD).to_edge(DOWN, buff=0.5))); self.end_seg()

class B04_half_turn(SyncScene):
    sid = "B04_half_turn"
    def construct(self):
        t = self.title("A line has no front or back")
        cen = LEFT * 3.5 + DOWN * 0.2
        self.seg(0)
        a1 = Arrow(cen, cen + 2.2 * np.array([np.cos(np.radians(20)), np.sin(np.radians(20)), 0]), color=GOLD, buff=0)
        a2 = Arrow(cen, cen - 2.2 * np.array([np.cos(np.radians(20)), np.sin(np.radians(20)), 0]), color=ORANGE, buff=0)
        full = Line(cen - 2.4 * np.array([np.cos(np.radians(20)), np.sin(np.radians(20)), 0]), cen + 2.4 * np.array([np.cos(np.radians(20)), np.sin(np.radians(20)), 0]), color=MUTED, stroke_width=2)
        self.play(Create(full)); self.play(GrowArrow(a1)); self.play(GrowArrow(a2))
        tA = T("20° and 200°: the same line", 24, GOLD).to_corner(UR, buff=0.5); tB = T("so we only need angles from 0° up to 180°", 22, INK).to_corner(UR, buff=0.5).shift(DOWN * 0.6)
        self.play(FadeIn(tA)); self.play(FadeIn(tB)); self.end_seg()
        self.seg(1)
        self.play(FadeOut(VGroup(a1, a2, full)), FadeOut(tA), FadeOut(tB))
        for deg, col in [(5, TEAL), (175, ORANGE)]:
            r = np.radians(deg); L = Line(cen - 2.4 * np.array([np.cos(r), np.sin(r), 0]), cen + 2.4 * np.array([np.cos(r), np.sin(r), 0]), color=col, stroke_width=5); self.play(Create(L), run_time=0.8)
        self.play(FadeIn(T("5° and 175°: nearly the same line!\nonly 10° apart", 24, ORANGE).to_corner(UR, buff=0.5)))
        self.end_seg()
        self.seg(2)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not t])
        strip = NumberLine(x_range=[0, 180, 30], length=8, include_numbers=True, font_size=20, color=MUTED).shift(UP * 1.2)
        self.play(Create(strip))
        d5 = Dot(strip.n2p(5), color=TEAL, radius=0.12); d175 = Dot(strip.n2p(175), color=ORANGE, radius=0.12); self.play(FadeIn(d5), FadeIn(d175))
        self.play(FadeIn(T("far apart on a strip…", 22, MUTED).next_to(strip, UP, buff=0.3)))
        cen2 = DOWN * 1.5; R = 1.5
        self.play(FadeIn(T("…but glue the two ends together:", 22, INK).move_to(UP * 0.1)))
        circ = unit_circle(R, cen2 + LEFT * 3.5)
        cc = Circle(radius=R, color=MUTED, stroke_width=3).move_to(cen2 + LEFT * 3.5)
        self.play(Create(cc), d5.animate.move_to(cen2 + LEFT * 3.5 + R * np.array([np.cos(2 * np.radians(5)), np.sin(2 * np.radians(5)), 0])), d175.animate.move_to(cen2 + LEFT * 3.5 + R * np.array([np.cos(2 * np.radians(175)), np.sin(2 * np.radians(175)), 0])), run_time=2)
        self.play(FadeIn(T("a circle: 5° and 175° are neighbours", 22, GOLD).next_to(cc, RIGHT, buff=0.6)))
        self.end_seg()
        self.seg(3)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not t])
        cen3 = LEFT * 3.0 + DOWN * 0.2; R = 2.0; circ = unit_circle(R, cen3); self.play(FadeIn(circ))
        pa = Dot(on_circle(40, R, cen3), color=BLUE, radius=0.12); pb = Dot(on_circle(150, R, cen3), color=RED, radius=0.12)
        self.play(FadeIn(pa), FadeIn(pb))
        # shorter way round: 40 -> 150 is 110 deg ; other way is 70
        sh = Arc(radius=R, start_angle=2 * np.radians(150), angle=2 * np.radians(70), arc_center=cen3, color=GOLD, stroke_width=8)
        self.play(Create(sh)); self.play(FadeIn(T("distance = the shorter way round (never over 90°)", 24, GOLD).to_corner(UR, buff=0.5)))
        self.play(FadeIn(T("one dot on this circle = one direction of a line", 24, INK).to_corner(UR, buff=0.5).shift(DOWN * 0.9)))
        self.play(FadeIn(T("(drawn at double angle so the half-turn fills a full circle)", 18, MUTED).to_edge(DOWN, buff=0.4)))
        self.end_seg()

class B05_shorth(SyncScene):
    sid = "B05_shorth"
    def construct(self):
        t = self.title("The shorth: the shortest stretch holding half")
        self.seg(0)
        cen = LEFT * 3.2 + DOWN * 0.2; R = 2.0; circ = unit_circle(R, cen)
        ang = np.array([20, 24, 27, 30, 33, 37, 41, 100, 135, 150, 165, 8])
        dts = VGroup(*[Dot(on_circle(a, R, cen), radius=0.09, color=BLUE) for a in ang])
        self.play(FadeIn(circ), LaggedStart(*[FadeIn(d, scale=2) for d in dts], lag_ratio=0.08), run_time=2.5)
        cq = T("a circle of directions; where do the dots pile up?", 24, INK).to_corner(UR, buff=0.5); self.play(FadeIn(cq)); self.end_seg()
        self.seg(1)
        self.play(FadeOut(circ), FadeOut(dts), FadeOut(cq))
        road = NumberLine(x_range=[0, 100, 10], length=10, color=MUTED, include_numbers=False).shift(DOWN * 0.3)
        hx = [8, 11, 14, 17, 19, 22, 24, 52, 70, 78, 90, 93]
        houses = VGroup(*[VGroup(Square(0.22, color=BLUE, fill_opacity=0.5, stroke_width=1.5), Triangle(color=RED, fill_opacity=0.5, stroke_width=1).scale(0.15).shift(UP * 0.18)).move_to(road.n2p(v) + UP * 0.2) for v in hx])
        self.play(Create(road), FadeIn(houses))
        hq = T("houses along a road: find the busiest neighbourhood", 24, INK).to_corner(UR, buff=0.5); self.play(FadeIn(hq))
        win = Rectangle(width=3.0, height=0.8, color=GOLD, stroke_width=4, fill_color=GOLD, fill_opacity=0.15).move_to(road.n2p(11) + UP * 0.25)
        self.play(Create(win)); hq2 = T("a stretch of road wide enough for half of the houses", 22, GOLD).to_corner(UR, buff=0.5).shift(DOWN * 0.7); self.play(FadeIn(hq2))
        self.end_seg()
        self.seg(2)
        self.play(FadeOut(win), FadeOut(hq), FadeOut(hq2)); road_s = np.array(hx); h = 6; best = None
        wins = []
        for i in range(len(hx) - h + 1):
            wd = hx[i + h - 1] - hx[i]; wins.append((i, wd))
        info = T("", 22)
        for i, wd in wins:
            w = Rectangle(width=(road.n2p(hx[i + h - 1])[0] - road.n2p(hx[i])[0]) + 0.3, height=0.8, color=ORANGE, stroke_width=3, fill_color=ORANGE, fill_opacity=0.12).move_to((road.n2p(hx[i]) + road.n2p(hx[i + h - 1])) / 2 + UP * 0.25)
            nt = T(f"6 houses:  width {wd}", 22, ORANGE).to_edge(DOWN, buff=0.6); self.play(FadeIn(w), FadeIn(nt), run_time=0.5); self.wait(0.8); self.play(FadeOut(w), FadeOut(nt), run_time=0.3)
        bi = min(wins, key=lambda q: q[1])[0]
        bw = Rectangle(width=(road.n2p(hx[bi + h - 1])[0] - road.n2p(hx[bi])[0]) + 0.3, height=0.8, color=GOLD, stroke_width=5, fill_color=GOLD, fill_opacity=0.2).move_to((road.n2p(hx[bi]) + road.n2p(hx[bi + h - 1])) / 2 + UP * 0.25)
        self.play(FadeIn(bw)); self.play(FadeIn(T("narrowest window wins; its midpoint = the shorth", 24, GOLD, weight=BOLD).to_edge(DOWN, buff=0.6)))
        self.end_seg()
        self.seg(3)
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not t])))
        cen = LEFT * 3.0 + DOWN * 0.2; R = 2.0; circ = unit_circle(R, cen)
        ang2 = [160, 165, 170, 175, 3, 8, 12, 80]; d2 = VGroup(*[Dot(on_circle(a, R, cen), radius=0.09, color=BLUE) for a in ang2])
        self.play(FadeIn(circ), FadeIn(d2))
        # window across the seam
        arc = arc_win(cen, 160, 25, R + 0.18, GOLD); self.play(Create(arc))
        self.play(FadeIn(T("the window may cross the seam at 180°/0°", 24, GOLD).to_corner(UR, buff=0.5)))
        self.play(FadeIn(T("trick: copy all angles one more lap, so no seam exists", 22, INK).to_corner(UR, buff=0.5).shift(DOWN * 0.7)))
        self.end_seg()
        self.seg(4)
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not t])))
        nl = NumberLine(x_range=[0, 100, 10], length=10, color=MUTED, include_numbers=False).shift(DOWN * 0.3)
        vals = [20, 22, 24, 26, 28, 30, 55, 60, 70, 80, 90, 95]
        dd = VGroup(*[Dot(nl.n2p(v), radius=0.1, color=BLUE) for v in vals])
        self.play(Create(nl), FadeIn(dd))
        med = np.median(vals); sh = 25
        mk = VGroup(Dot(nl.n2p(med), radius=0.16, color=ORANGE), T("median", 22, ORANGE).next_to(nl.n2p(med), UP, buff=0.4))
        sk = VGroup(Dot(nl.n2p(sh), radius=0.16, color=GOLD), T("shorth", 22, GOLD).next_to(nl.n2p(sh), DOWN, buff=0.4))
        self.play(FadeIn(mk)); self.play(FadeIn(sk))
        self.play(FadeIn(T("the median is tugged by stragglers; the shorth stays in the crowd", 24, INK).to_edge(DOWN, buff=0.6))); self.end_seg()

class B06_local(SyncScene):
    sid = "B06_local"
    def construct(self):
        x, y, bad = toy(); ax = small_axes(); self.add(ax); n = len(x)
        t = self.title("Local opinion of one dot")
        d = pdots(ax, x, y, bad); self.add(d)
        cen = RIGHT * 3.6 + DOWN * 0.3; R = 1.7; circ = unit_circle(R, cen)
        phi = np.degrees(np.array([[chord_ang(x[i], y[i], x[j], y[j]) if j != i else np.nan for j in range(n)] for i in range(n)]))
        def anchor_scene(i, col, label):
            ch = VGroup(*[Line(d[i].get_center(), d[j].get_center(), color=col, stroke_width=1.6, stroke_opacity=0.8) for j in range(n) if j != i])
            cdots = VGroup(*[Dot(on_circle(phi[i, j], R, cen), radius=0.07, color=col) for j in range(n) if j != i])
            return ch, cdots
        self.seg(0)
        self.play(FadeIn(circ)); i = 4
        self.play(Indicate(d[i], scale_factor=2, color=GOLD))
        ch, cd = anchor_scene(i, GOLD, "")
        self.play(LaggedStart(*[Create(c) for c in ch], lag_ratio=0.08), LaggedStart(*[FadeIn(p, scale=2) for p in cd], lag_ratio=0.08), run_time=3)
        self.play(FadeIn(T("what this dot sees when it looks around", 22, INK).to_corner(UR, buff=0.4).shift(DOWN * 0.1))); self.end_seg()
        self.seg(1)
        angs = np.radians([phi[i, j] for j in range(n) if j != i]); h = int(np.ceil((n - 1) / 2)); s, w = shorth_window(angs, h)
        arc = arc_win(cen, np.degrees(s), np.degrees(w), R + 0.2, TEAL); self.play(Create(arc))
        msg = T("narrow pile → confident local direction", 22, TEAL).to_corner(UR, buff=0.4).shift(DOWN * 0.7); self.play(FadeIn(msg))
        mid = (s + w / 2) % PI
        loc = Line(d[i].get_center() - 2.2 * np.array([np.cos(mid), np.sin(mid), 0]), d[i].get_center() + 2.2 * np.array([np.cos(mid), np.sin(mid), 0]), color=TEAL, stroke_width=5)
        self.play(Create(loc)); self.end_seg()
        self.seg(2)
        self.play(FadeOut(ch), FadeOut(cd), FadeOut(arc), FadeOut(loc), FadeOut(msg))
        j = n - 2
        self.play(Indicate(d[j], scale_factor=2, color=GOLD))
        ch, cd = anchor_scene(j, ORANGE, "")
        self.play(LaggedStart(*[Create(c) for c in ch], lag_ratio=0.08), LaggedStart(*[FadeIn(p, scale=2) for p in cd], lag_ratio=0.08), run_time=3)
        angs = np.radians([phi[j, k] for k in range(n) if k != j]); s, w = shorth_window(angs, h)
        arc = arc_win(cen, np.degrees(s), np.degrees(w), R + 0.2, ORANGE); self.play(Create(arc))
        self.play(FadeIn(T(f"no tight pile: wide window ({np.degrees(w):.0f}° wide) → weak opinion", 22, ORANGE).to_corner(UR, buff=0.4).shift(DOWN * 0.7))); self.end_seg()
        self.seg(3)
        self.play(FadeOut(ch), FadeOut(cd), FadeOut(arc))
        self.play(FadeIn(T("every dot: one local direction + a width = how sure it is", 26, GOLD, weight=BOLD).to_edge(DOWN, buff=0.4))); self.end_seg()

class B07_vote(SyncScene):
    sid = "B07_vote"
    def construct(self):
        x, y, bad = toy(seed=6, nb=40, nr=24); n = len(x)
        t = self.title("Repeat: the local opinions vote")
        phi = np.array([[chord_ang(x[i], y[i], x[j], y[j]) if j != i else np.nan for j in range(n)] for i in range(n)])
        h = int(np.ceil((n - 1) / 2)); loc = []; wid = []
        for i in range(n):
            a = np.delete(phi[i], i); s, w = shorth_window(a, h); loc.append((s + w / 2) % PI); wid.append(w)
        loc = np.array(loc); wid = np.array(wid)
        cen = LEFT * 3.2 + DOWN * 0.2; R = 2.2; circ = unit_circle(R, cen)
        self.seg(0)
        self.play(FadeIn(circ))
        dots_ = VGroup(*[Dot(on_circle(np.degrees(loc[i]), R, cen), radius=0.07, color=(RED if bad[i] else BLUE)) for i in range(n)])
        self.play(LaggedStart(*[FadeIn(p, scale=2) for p in dots_], lag_ratio=0.03), run_time=3)
        op = T("each dot's local opinion is now a point on the circle", 22, INK).to_corner(UR, buff=0.4).shift(DOWN * 0.1)
        self.play(FadeIn(op))
        self.end_seg()
        self.seg(1)
        cm = VGroup(T("① each member consults everybody → personal opinion", 22, INK), T("② the committee finds the opinion most members share", 22, INK)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_corner(UR, buff=0.4).shift(DOWN * 0.8)
        self.play(FadeOut(op)); self.play(FadeIn(cm, lag_ratio=0.6), run_time=2); self.end_seg()
        self.seg(2)
        ho = int(np.ceil(n / 2)); s, w = shorth_window(loc, ho); mid = (s + w / 2) % PI
        arc = arc_win(cen, np.degrees(s), np.degrees(w), R + 0.22, GOLD, 10); self.play(Create(arc))
        mk = Dot(on_circle(np.degrees(mid), R, cen), radius=0.17, color=GOLD); self.play(FadeIn(mk, scale=2))
        self.play(FadeOut(cm)); self.play(FadeIn(T("shortest half-window  →  final direction  θ̂", 24, GOLD, weight=BOLD).to_corner(UR, buff=0.4).shift(DOWN * 0.9))); self.end_seg()
        self.seg(3)
        self.play(FadeIn(T("never asked: which line fits best?  Only: where do directions agree?", 24, INK).to_edge(DOWN, buff=0.5))); self.end_seg()

class B08_back(SyncScene):
    sid = "B08_back"
    def construct(self):
        x, y, bad = fig1(); ax = full_ax(); t = self.title("From a direction back to a line")
        a, b = rc.rashr(x, y)
        self.seg(0)
        cen = RIGHT * 1.6 + DOWN * 0.8; base = Line(cen, cen + RIGHT * 2.4, color=MUTED); th = 0.75
        tip = cen + 2.4 * np.array([1, np.tan(th), 0]) / 1.0
        run = Line(cen, cen + RIGHT * 2.0, color=TEAL, stroke_width=5); rise = Line(cen + RIGHT * 2.0, cen + RIGHT * 2.0 + UP * 2.0 * np.tan(th), color=ORANGE, stroke_width=5)
        hyp = Line(cen, cen + RIGHT * 2.0 + UP * 2.0 * np.tan(th), color=GOLD, stroke_width=5)
        self.play(Create(run), Create(rise), Create(hyp))
        slab = T("slope = rise ÷ run = tan(angle)", 24, GOLD, weight=BOLD).next_to(run, DOWN, buff=0.5); self.play(FadeIn(slab)); self.end_seg()
        self.seg(1)
        st = VGroup(T("slope(original) = slope(squeezed) × vertical scale ÷ horizontal scale", 22, INK)).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(st)); self.end_seg()
        self.seg(2)
        self.play(FadeOut(VGroup(run, rise, hyp, st[0], slab)))
        self.add(ax); d = dots(ax, x, y, bad); self.play(FadeIn(ax), FadeIn(d))
        sl = line_on(ax, 0, b, GOLD, stroke_width=3)
        d0 = DashedLine(ax.c2p(-6, -6 * b), ax.c2p(18, 18 * b), color=MUTED)
        self.play(Create(d0)); self.play(FadeIn(T("each dot proposes where the line should cross the vertical axis", 22, INK).to_corner(UR, buff=0.4)))
        sg = VGroup(*[Dot(ax.c2p(0, y[k] - b * x[k]), radius=0.04, color=(RED if bad[k] else BLUE)) for k in range(len(x)) if abs(y[k] - b * x[k]) < 14])
        self.play(LaggedStart(*[FadeIn(p, scale=3) for p in sg], lag_ratio=0.02), run_time=2)
        self.play(FadeIn(T("take their median →  the intercept", 22, GOLD).to_corner(UR, buff=0.4).shift(DOWN * 0.6))); self.end_seg()
        self.seg(3)
        self.play(FadeOut(d0), FadeOut(sg))
        ln = line_on(ax, a, b, GOLD, stroke_width=7); self.play(Create(ln))
        self.play(FadeIn(T(f"slope {b:.2f}   (true slope 2)", 28, GOLD, weight=BOLD).to_edge(DOWN, buff=0.5))); self.end_seg()
        self.seg(4)
        self.play(FadeIn(T("the intercept leans on all dots, clump included, so it can sit a bit off", 22, ORANGE).to_corner(UR, buff=0.4).shift(DOWN * 1.2))); self.end_seg()

class B09_recap(SyncScene):
    sid = "B09_recap"
    def construct(self):
        t = self.title("The whole machine in one picture")
        steps = ["1  Put both axes in 'typical spread' units", "2  Draw the direction of every pair", "3  Fold directions onto the half-turn circle",
                 "4  For each dot: shortest half-window → local opinion", "5  Repeat: shortest half-window of the local opinions", "6  Direction → slope → undo units; median for height"]
        icons = []
        self.seg(0)
        col = VGroup(*[T(s, 25, INK) for s in steps]).arrange(DOWN, aligned_edge=LEFT, buff=0.38).to_edge(LEFT, buff=0.8).shift(DOWN * 0.3)
        for k in range(4): self.play(FadeIn(col[k], shift=RIGHT * 0.3), run_time=1.0)
        self.end_seg()
        self.seg(1)
        for k in range(4, 6): self.play(FadeIn(col[k], shift=RIGHT * 0.3), run_time=1.0)
        cen = RIGHT * 4.3; circ = unit_circle(1.7, cen); self.play(FadeIn(circ))
        rng = np.random.default_rng(1); self.play(LaggedStart(*[FadeIn(Dot(on_circle(34 + rng.normal(0, 4), 1.7, cen), radius=0.06, color=BLUE)) for _ in range(20)], lag_ratio=0.05)); self.end_seg()
        self.seg(2)
        self.play(FadeIn(T("time ∝ n² log n  ·  no random guessing  ·  same data → same line", 26, GOLD, weight=BOLD).to_edge(DOWN, buff=0.5))); self.end_seg()

# ================================================================== PART C : why it works
class C01_exact(SyncScene):
    sid = "C01_exact"
    def construct(self):
        t = self.title("Best case: dots exactly on a line")
        ax = small_axes(); self.add(ax)
        xs = np.linspace(0.5, 6.5, 9); ys = 1 + 0.8 * xs
        self.seg(0)
        d = pdots(ax, xs, ys); self.play(LaggedStart(*[FadeIn(p) for p in d], lag_ratio=0.1))
        ch = VGroup(*[Line(d[a].get_center(), d[b].get_center(), color=GOLD, stroke_width=1.5) for a in range(9) for b in range(a + 1, 9)])
        self.play(Create(ch), run_time=2)
        cen = RIGHT * 3.8 + DOWN * 0.3; circ = unit_circle(1.7, cen); self.play(FadeIn(circ))
        ph = np.degrees(np.arctan(0.8)); pile = Dot(on_circle(ph, 1.7, cen), radius=0.14, color=GOLD); self.play(FadeIn(pile, scale=3))
        self.play(FadeIn(T("every chord: the same direction → window of width 0", 22, GOLD).to_edge(DOWN, buff=0.5))); self.end_seg()
        self.seg(1)
        r = np.random.default_rng(4)
        bad = VGroup(*[Dot(ax.c2p(r.uniform(0.5, 9.5), r.uniform(-0.5, 8.5)), radius=0.07, color=RED) for _ in range(3)])
        self.play(FadeIn(bad, scale=2)); self.play(*[b.animate.shift(RIGHT * 0.5 * (k - 1)) for k, b in enumerate(bad)])
        self.play(FadeIn(T("fewer than half bad, none on the line: answer cannot change", 22, RED).next_to(circ, DOWN, buff=0.2)))
        self.end_seg()
        self.seg(2)
        self.play(FadeIn(T("a perfect pile beats any smaller scatter", 26, TEAL, weight=BOLD).to_edge(UP, buff=1.3))); self.end_seg()

class C02_units(SyncScene):
    sid = "C02_units"
    def construct(self):
        t = self.title("Changing units does not change the answer")
        x, y, bad = toy(); n = len(x)
        self.seg(0)
        ax = small_axes(); d = pdots(ax, x, y, bad); self.add(ax, d)
        f = lambda a, c: 1.0 * a
        sl = (lambda xx, yy: np.polyfit(xx[~bad], yy[~bad], 1)[0])
        b = sl(x, y); L = Line(ax.c2p(0, np.polyfit(x[~bad], y[~bad], 1)[1]), ax.c2p(7, np.polyfit(x[~bad], y[~bad], 1)[1] + 7 * b), color=GOLD, stroke_width=5)
        self.play(Create(L))
        self.play(FadeIn(T("new units / shifted axes → same line, in new units", 24, GOLD).to_corner(UR, buff=0.4)))
        sh = ValueTracker(0)
        self.play(*[p.animate.shift(RIGHT * 0.8) for p in d], L.animate.shift(RIGHT * 0.8), run_time=1.5); self.end_seg()
        self.seg(1)
        self.play(FadeIn(T("shift + rescale are removed by step 1, so chords, circle and windows are identical", 22, INK).to_edge(DOWN, buff=0.5))); self.end_seg()
        self.seg(2)
        self.play(*[p.animate.shift(UP * 0.0) for p in d])
        # tilt demo
        ang = ValueTracker(0)
        self.play(*[p.animate.shift(UP * 0.12 * (ax.p2c(p.get_center())[0])) for p in d], L.animate.rotate(0.25, about_point=ax.c2p(0, 1)), run_time=2)
        self.play(FadeIn(T("a shear (tilt) can change the answer: not every distortion is covered", 22, ORANGE).to_corner(UR, buff=0.4).shift(DOWN * 0.8))); self.end_seg()

class C03_separation(SyncScene):
    sid = "C03_separation"
    def construct(self):
        t = self.title("Separation: why bad dots can have zero influence")
        cen = LEFT * 3.2 + DOWN * 0.2; R = 2.1; circ = unit_circle(R, cen)
        rng = np.random.default_rng(2)
        self.seg(0)
        self.play(FadeIn(circ))
        g = VGroup(*[Dot(on_circle(40 + rng.normal(0, 3), R, cen), radius=0.08, color=BLUE) for _ in range(25)]); b = VGroup(*[Dot(on_circle(rng.uniform(100, 160), R, cen), radius=0.08, color=RED) for _ in range(12)])
        self.play(FadeIn(g), FadeIn(b))
        self.play(FadeIn(T("honest directions: a tight pile\nbad directions: somewhere else", 22, INK).to_corner(UR, buff=0.4))); self.end_seg()
        self.seg(1)
        arc = arc_win(cen, 33, 15, R + 0.2, GOLD, 9); self.play(Create(arc))
        self.play(FadeIn(T("any window reaching a bad direction would be wider\n→ the shortest window never touches one", 22, GOLD).to_corner(UR, buff=0.4).shift(DOWN * 1.0)))
        self.play(*[p.animate.move_to(on_circle(rng.uniform(100, 170), R, cen)) for p in b], run_time=2); self.play(*[p.animate.move_to(on_circle(rng.uniform(100, 170), R, cen)) for p in b], run_time=2)
        self.end_seg()
        self.seg(2)
        self.play(FadeIn(T("needed twice: among each dot's chords, then among local opinions", 22, INK).to_edge(DOWN, buff=0.5))); self.end_seg()
        self.seg(3)
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not t])))
        ax = full_ax(); self.add(ax)
        x, y, bad = rc.fig1_example(seed=3); x = np.asarray(x); y = np.asarray(y); bad = np.asarray(bad)
        dist = ValueTracker(0)
        def cur():
            xx = x.copy(); yy = y.copy(); xx[bad] += dist.get_value() * 0.6; yy[bad] -= dist.get_value() * 0.0; return xx, yy
        dd = always_redraw(lambda: dots(ax, *cur(), bad))
        sl = {}
        def lines():
            xx, yy = cur(); a, bb = rc.rashr(xx, yy); a2, b2 = rc.lms(xx, yy)
            return VGroup(line_on(ax, a, bb, GOLD, stroke_width=6), line_on(ax, a2, b2, ORANGE, stroke_width=4))
        ls = always_redraw(lines)
        self.add(dd, ls)
        lab = always_redraw(lambda: T(f"cluster moved: {dist.get_value():.0f}      RAShR slope {rc.rashr(*cur())[1]:+.2f}      LMS slope {rc.lms(*cur())[1]:+.2f}", 22, INK).to_edge(DOWN, buff=0.35))
        self.add(lab)
        self.play(dist.animate.set_value(10), run_time=7, rate_func=linear); self.end_seg()
        self.seg(4)
        self.play(FadeIn(T("separated contamination has zero influence", 28, GOLD, weight=BOLD).to_corner(UR, buff=0.4))); self.end_seg()
        self.seg(5)
        cv = VGroup(T("• the median and scale of step 1 must not move", 22, ORANGE), T("• the theorem says IF separated; the tests ask WHEN", 22, ORANGE)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_corner(UR, buff=0.4).shift(DOWN * 0.8)
        self.play(FadeIn(cv)); self.end_seg()

class C04_attraction(SyncScene):
    sid = "C04_attraction"
    def construct(self):
        t = self.title("Why ribbon methods get attracted")
        ax = Axes(x_range=[0, 10, 2], y_range=[-2, 8, 2], x_length=7.4, y_length=4.6, tips=False, axis_config=dict(color=MUTED, stroke_width=2, font_size=16)).shift(LEFT * 2.2 + DOWN * 0.3)
        self.add(ax)
        r = np.random.default_rng(1); xs = r.uniform(0.3, 6.5, 40); ys = 1 + 0.8 * xs + r.normal(0, .7, 40)
        self.seg(0)
        d = pdots(ax, xs, ys); pt = Dot(ax.c2p(9, 0), radius=0.2, color=RED)
        self.play(FadeIn(d)); self.play(FadeIn(pt, scale=2))
        eps = ValueTracker(0.3)
        txt = always_redraw(lambda: T(f"ε = {eps.get_value():.0%} of all dots sit at that point", 22, RED).to_corner(UR, buff=0.4).shift(DOWN * 0.9))
        self.add(txt); self.end_seg()
        self.seg(1)
        def strip(a, b, w, col):
            xx = [0, 10]; pts = [ax.c2p(u, a + b * u + w) for u in xx] + [ax.c2p(u, a + b * u - w) for u in xx[::-1]]
            return Polygon(*pts, color=col, fill_color=col, fill_opacity=0.25, stroke_width=1)
        wid = always_redraw(lambda: strip(0.0, 0.0 + 0.0, 0.0, RED) if False else Polygon(ax.c2p(0, 0 + 0.1 + (0.5 - eps.get_value()) * 3), ax.c2p(10, 0.1 + (0.5 - eps.get_value()) * 3 - 0.0), ax.c2p(10, -0.1 - (0.5 - eps.get_value()) * 3), ax.c2p(0, -0.1 - (0.5 - eps.get_value()) * 3), color=RED, fill_color=RED, fill_opacity=0.25, stroke_width=1))
        self.add(wid); self.play(eps.animate.set_value(0.45), run_time=4)
        self.play(FadeIn(T("ribbon through the point: thinner as ε → 50%", 22, RED).to_edge(DOWN, buff=0.4))); self.end_seg()
        self.seg(2)
        tr = strip(1, 0.8, 1.3, TEAL); self.play(FadeIn(tr)); self.play(FadeIn(T("ribbon around the honest line: always as fat as the honest noise", 22, TEAL).to_edge(DOWN, buff=0.9)))
        self.end_seg()
        self.seg(3)
        n = VGroup(T("proved: least median of squares", 22, TEAL), T("only seen in experiments: LTS, MM", 22, MUTED)).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.4).shift(DOWN * 0.7)
        self.play(FadeIn(n)); self.end_seg()

class C05_remark(SyncScene):
    sid = "C05_remark"
    def construct(self):
        t = self.title("Not every honest chord must be right")
        ax = small_axes(); self.add(ax)
        r = np.random.default_rng(8); xs = np.linspace(0.5, 7, 20); ys = 1 + 0.8 * xs + r.normal(0, .35, 20)
        self.seg(0)
        d = pdots(ax, xs, ys); self.play(FadeIn(d))
        j = np.argsort(np.abs(xs - 3.0))[:2]
        p = ax.c2p(3.0, 4.0)
        d1 = Dot(ax.c2p(3.0, 3.6), radius=0.09, color=GOLD); d2 = Dot(ax.c2p(3.08, 4.5), radius=0.09, color=GOLD); self.play(FadeIn(d1), FadeIn(d2))
        self.play(Create(Line(d1.get_center(), d2.get_center(), color=GOLD, stroke_width=5)))
        cap = T("two neighbours with a little noise: the chord can point almost anywhere", 22, GOLD).to_edge(DOWN, buff=0.5); self.play(FadeIn(cap)); self.end_seg()
        self.seg(1)
        cen = RIGHT * 3.8 + DOWN * 0.3; circ = unit_circle(1.7, cen); self.play(FadeIn(circ))
        ph = []
        for a in range(20):
            for b in range(a + 1, 20): ph.append(np.degrees(chord_ang(xs[a], ys[a], xs[b], ys[b])))
        ps = VGroup(*[Dot(on_circle(v, 1.7, cen), radius=0.045, color=BLUE) for v in ph]); self.play(FadeIn(ps), run_time=2)
        self.end_seg()
        self.seg(2)
        s, w = shorth_window(np.radians(ph), int(np.ceil(len(ph) / 2))); arc = arc_win(cen, np.degrees(s), np.degrees(w), 1.9, GOLD, 9); self.play(Create(arc), FadeOut(cap))
        self.play(FadeIn(T("half of the chords agree: that is all the shorth needs", 24, GOLD, weight=BOLD).to_edge(DOWN, buff=0.5))); self.end_seg()

# ================================================================== PART D : evidence
class D01_experiments(SyncScene):
    sid = "D01_experiments"
    def construct(self):
        t = self.title("The tests")
        self.seg(0)
        self.play(FadeIn(T("100 dots on a line with noise,\nthen replace a share by bad dots", 30, INK).shift(UP * 2)))
        self.end_seg()
        self.seg(1)
        self.clear()
        t = self.title("The tests")
        rng = np.random.default_rng(0)
        panels = VGroup()
        for k, (kind, name) in enumerate([("compact", "compact clump"), ("line", "competing line"), ("funnel", "funnel")]):
            x, y, bad = rc.simulate(n=100, frac=0.4, kind=kind, rng=rng)
            ax = Axes(x_range=[float(np.min(x)) - 1, float(np.max(x)) + 1], y_range=[float(np.min(y)) - 2, float(np.max(y)) + 2], x_length=3.6, y_length=2.8, tips=False, axis_config=dict(color=MUTED, stroke_width=1.5, include_ticks=False)).move_to([(k - 1) * 4.3, -0.4, 0])
            g = VGroup(*[Dot(ax.c2p(a, b), radius=0.035, color=(RED if bad[i] else BLUE)) for i, (a, b) in enumerate(zip(x, y))])
            panels.add(VGroup(ax, g, T(name, 22, INK).next_to(ax, UP, buff=0.2)))
        for p in panels: self.play(FadeIn(p), run_time=1.2)
        self.end_seg()
        self.seg(2)
        self.play(FadeIn(T("60 repetitions each · a fit FAILS if its slope is off by more than 0.5", 24, GOLD).to_edge(DOWN, buff=0.5))); self.end_seg()

class D02_ordinary(SyncScene):
    sid = "D02_ordinary"
    def construct(self):
        t = self.title("Everyday settings: the established methods win")
        self.seg(0)
        self.play(FadeIn(T("clean data · light contamination · a lone oddball", 28, INK).shift(UP * 2)))
        self.end_seg()
        self.seg(1)
        rows = [("setting", "RAShR", "MM", "RANSAC"), ("clean", "0.033", "0.024", "0.022"), ("20% vertical outliers", "0.040", "0.027", "0.037"), ("10% bad leverage", "0.041", "0.020", "0.021")]
        tb = VGroup()
        for i, r in enumerate(rows):
            tb.add(VGroup(*[T(c, 26, (GOLD if (i == 0 or j == 0) else [GOLD, TEAL, PURPLE][j - 1]) if i else MUTED, weight=BOLD if i == 0 else NORMAL) for j, c in enumerate(r)]))
        for i, r in enumerate(tb):
            for j, c in enumerate(r): c.move_to([-4 + [0, 3.8, 5.8, 7.8][j] - (0 if j else 0), 1.0 - i * 0.8, 0] if False else [[-4.2, 1.2, 3.4, 5.4][j], 0.8 - i * 0.8, 0])
        self.play(LaggedStart(*[FadeIn(r) for r in tb], lag_ratio=0.3), run_time=3)
        self.play(FadeIn(T("typical slope error (lower is better)", 22, MUTED).to_edge(DOWN, buff=1.2))); self.end_seg()
        self.seg(2)
        self.play(FadeIn(T("mostly honest data → use the established methods", 28, TEAL, weight=BOLD).to_edge(DOWN, buff=0.5))); self.end_seg()

class D03_near_half(SyncScene):
    sid = "D03_near_half"
    def construct(self):
        t = self.title("Near-half contamination: compact clump")
        ax = Axes(x_range=[34, 48, 2], y_range=[0, 100, 20], x_length=8.2, y_length=4.4, tips=False, axis_config=dict(color=MUTED, stroke_width=2, font_size=18)).shift(LEFT * 1.4 + UP * 0.35)
        ax.y_axis.add_numbers([0, 50, 100], font_size=18); ax.x_axis.add_numbers([36, 40, 44, 46], font_size=18)
        xl = T("share of bad dots (%)", 20, MUTED).next_to(ax, DOWN, buff=0.2); yl = T("fails (%)", 20, MUTED).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        lv = [36, 40, 44, 46]
        D = {"RAShR": ([0, 0, 60, 100], GOLD), "LMS": ([2, 58, 97, 100], ORANGE), "LTS / MM": ([23, 100, 100, 100], PURPLE), "RANSAC": ([50, 77, 99, 100], TEAL)}
        leg = VGroup(*[T(n, 20, D[n][1]) for n in D]).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UR, buff=0.4).shift(DOWN * 1.4)
        self.add(ax, xl, yl)
        self.seg(0)
        self.play(FadeIn(T("how often each method fails (lower is better)", 22, INK).to_corner(UR, buff=0.4)), FadeIn(leg)); self.end_seg()
        # RAShR value at 44% is shown as 60 (fails in 60% of runs = succeeds in 40%); competitor 44% values are >=97 (paper)
        notes = ["36%:  RAShR 0 · LMS 2 · LTS/MM 23 · RANSAC 50", "40%:  RAShR 0 · LMS 58 · LTS/MM 100 · RANSAC 77",
                 "44%:  RAShR succeeds in 40% of runs; rivals fail ≥ 97%", "46%:  everything fails"]
        prev = {n: None for n in D}; note = None
        for seg, idxs in [(1, [0]), (2, [1]), (3, [2, 3])]:
            self.seg(seg)
            for k in idxs:
                anims = []
                for n, (ys, col) in D.items():
                    p = ax.c2p(lv[k], ys[k]); dot = Dot(p, radius=0.1, color=col); anims.append(FadeIn(dot, scale=2))
                    if prev[n] is not None: anims.append(Create(Line(prev[n], p, color=col, stroke_width=5)))
                    prev[n] = p
                nn = T(notes[k], 22, INK).to_edge(DOWN, buff=0.4); anims.append(FadeIn(nn))
                if note is not None: anims.append(FadeOut(note))
                note = nn; self.play(*anims, run_time=1.0); self.wait(1.2 if len(idxs) > 1 else 0.2)
            self.end_seg()
        self.seg(4)
        self.play(FadeOut(note))
        rows = VGroup(T("competing line:  RAShR fails 0% all the way to 46%  (RANSAC 12%, LMS 60%, LTS/MM 93%)", 22, INK),
                      T("funnel:  RAShR fails 0% at 40%, 3% at 44%, 8% at 46%", 22, INK)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(rows)); self.end_seg()

class D04_limits(SyncScene):
    sid = "D04_limits"
    def construct(self):
        t = self.title("Where it fails")
        cen = LEFT * 3.0 + DOWN * 0.2; R = 2.1; circ = unit_circle(R, cen)
        self.seg(0)
        self.play(FadeIn(circ))
        good = VGroup(*[Dot(on_circle(30 + np.random.default_rng(i).normal(0, 3), R, cen), radius=0.07, color=BLUE) for i in range(25)])
        bad = VGroup(*[Dot(on_circle(30 + np.random.default_rng(100 + i).normal(0, 3), R, cen), radius=0.07, color=RED) for i in range(12)])
        self.play(FadeIn(good)); self.play(FadeIn(bad)); self.play(FadeIn(T("clump along the honest line (30° / −150°):\nthe two piles overlap, separation is lost", 22, ORANGE).to_corner(UR, buff=0.4))); self.end_seg()
        self.seg(1)
        self.play(FadeIn(T("RAShR fails 78% and 75% of runs there (distance 30);\nin 10 of 12 tested directions: no failures", 22, INK).to_corner(UR, buff=0.4).shift(DOWN * 1.3))); self.end_seg()
        self.seg(2)
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not t])))
        rows = [("spread of bad group", "RAShR", "LMS", "LTS/MM"), ("0.05  (very tight)", "0 %", "25 %", "≈ 98 %"), ("1 or 3  (loose)", "≤ 2 %", "≤ 2 %", "≤ 2 %")]
        tb = VGroup()
        for i, r in enumerate(rows):
            for j, c in enumerate(r):
                tb.add(T(c, 26, MUTED if i == 0 else [INK, GOLD, ORANGE, PURPLE][j]).move_to([[-3.8, 0.7, 2.6, 4.6][j], 1.0 - i * 0.9, 0]))
        self.play(FadeIn(tb), run_time=2); self.end_seg()
        self.seg(3)
        self.play(FadeIn(T("advantage: compact, coherent, separated bad groups.   Beyond ~46%: nothing works.", 24, GOLD, weight=BOLD).to_edge(DOWN, buff=0.5))); self.end_seg()

class D05_wrap(SyncScene):
    sid = "D05_wrap"
    def construct(self):
        t = self.title("The story in four lines")
        self.seg(0)
        q1 = T("✗  ordinary methods ask: which line has small misses?", 28, RED); q2 = T("✓  this method asks: which direction do pairs agree on?", 28, TEAL)
        VGroup(q1, q2).arrange(DOWN, aligned_edge=LEFT, buff=0.5).shift(UP * 1.2)
        self.play(FadeIn(q1)); self.play(FadeIn(q2)); self.end_seg()
        self.seg(1)
        g = VGroup(T("use it: a big, tight, coherent bad group (≈ ⅓ – ½ of the data)", 24, GOLD), T("prefer classic methods: clean or lightly contaminated data", 24, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).shift(DOWN * 0.7)
        self.play(FadeIn(g[0])); self.play(FadeIn(g[1])); self.end_seg()
        self.seg(2)
        self.play(FadeIn(T("robust ≠ safe.   It matters what a method rewards.", 30, INK, weight=BOLD).to_edge(DOWN, buff=1.0))); self.end_seg()
        self.seg(3)
        self.play(FadeOut(Group(*[m for m in self.mobjects])))
        self.play(FadeIn(T("Thank you for watching", 44, GOLD, weight=BOLD))); self.end_seg()
