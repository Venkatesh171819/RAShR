"""Shared helpers for the RAShR Manim scenes: palette, data, and narration-synchronised scene base class."""
import json, os, sys
import numpy as np
from manim import *

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ROOT))          # project root -> rashr_core
import rashr_core as rc
from narration import NARRATION

BG = "#0E1B2E"; INK = "#EAF1FB"; MUTED = "#8FA3BF"
BLUE = "#4C8DFF"; RED = "#FF5C6C"; TEAL = "#2CC6B8"; ORANGE = "#F5A04A"; PURPLE = "#A57BE0"; GOLD = "#F2D45C"
config.background_color = BG
TEXT_FONT = "Sans"

DUR_FILE = os.path.join(ROOT, "build", "durations.json")
TIMING_DIR = os.path.join(ROOT, "build", "timings")

def load_durations():
    if os.path.exists(DUR_FILE):
        return json.load(open(DUR_FILE))
    # fallback: estimate ~2.5 words/second + 0.6 s of air
    return {k: [len(t.split()) / 2.5 + 0.6 for t in v] for k, v in NARRATION.items()}
DURS = load_durations()

def T(s, size=28, color=INK, **kw):
    return Text(s, font=TEXT_FONT, font_size=size, color=color, **kw)

class SyncScene(Scene):
    """Segments of the narration are the clock.  `self.seg(k)` starts segment k; `self.end_seg()`
    waits until that segment's audio (plus a short breath) is over.  Actual start times are written
    to build/timings/<scene>.json, which the mux step uses to place the audio -- so even if an
    animation overruns, voice and picture stay aligned."""
    sid = None
    def setup(self):
        self._title_m, self._dy = None, 0.0
        self.starts, self._t0, self._k = [], 0.0, None
        self.durs = DURS[self.sid]
    def seg(self, k):
        self._k = k; self._t0 = self.renderer.time; self.starts.append(self._t0)
    def end_seg(self):
        remaining = self.durs[self._k] + 0.35 - (self.renderer.time - self._t0)
        if remaining > 0.02: self.wait(remaining)
        else: print(f"[sync] {self.sid} seg {self._k} overran by {-remaining:.2f}s")
    def caption(self, text, old=None):
        c = T(text, 22, MUTED).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(c, shift=UP*0.1), *( [FadeOut(old)] if old else [] ), run_time=0.4)
        return c
    def _textonly(self, m):
        if isinstance(m, Text): return True
        return isinstance(m, VGroup) and len(m.submobjects) > 0 and all(self._textonly(s) for s in m.submobjects)
    def _adjust(self, m):
        """keep text on screen and out of the title band (applied once per text object)"""
        if getattr(m, "_adj", False) or not self._textonly(m): return
        m._adj = True
        if m.get_right()[0] > 6.75: m.shift(LEFT * (m.get_right()[0] - 6.75))
        if m.get_left()[0] < -6.75: m.shift(RIGHT * (-6.75 - m.get_left()[0]))
        t = self._title_m
        if t is None or m is t or m.get_top()[1] < 2.2: return
        if self._dy: m.shift(DOWN * self._dy)
        hov = m.get_left()[0] < t.get_right()[0] + 0.1 and m.get_right()[0] > t.get_left()[0] - 0.1
        if hov and m.get_top()[1] > t.get_bottom()[1] - 0.05:
            need = m.get_top()[1] - t.get_bottom()[1] + 0.15; m.shift(DOWN * need); self._dy += need
    def play(self, *args, **kw):
        for a in args:
            m = getattr(a, "mobject", None)
            if m is not None: self._adjust(m)
        return super().play(*args, **kw)
    def title(self, s):
        t = T(s, 36, INK, weight=BOLD).to_corner(UL, buff=0.45); self._title_m = t; t._adj = True
        self.play(FadeIn(t, shift=DOWN*0.2), run_time=0.5); return t
    def tear_down(self):
        os.makedirs(TIMING_DIR, exist_ok=True)
        json.dump({"starts": self.starts, "total": self.renderer.time}, open(os.path.join(TIMING_DIR, self.sid + ".json"), "w"))
        super().tear_down()

# ---------------------------------------------------------------- data (paper's Fig.1 setting)
def fig1():
    x, y, bad = rc.fig1_example(seed=3)
    return np.asarray(x), np.asarray(y), np.asarray(bad)

def axes_xy(xr=(-6, 18, 4), yr=(-14, 16, 5), w=8.4, h=5.2):
    return Axes(x_range=list(xr), y_range=list(yr), x_length=w, y_length=h,
                axis_config=dict(color=MUTED, stroke_width=2, include_tip=False, font_size=18),
                tips=False).set_color(MUTED)

def dots(ax, x, y, bad=None, r=0.045):
    g = VGroup()
    for i in range(len(x)):
        c = RED if (bad is not None and bad[i]) else BLUE
        g.add(Dot(ax.c2p(x[i], y[i]), radius=r, color=c))
    return g

def line_on(ax, a, b, color, x0=-6, x1=18, **kw):
    """line y=a+b x drawn only inside the plotted axes box"""
    xr = ax.x_range; yr = ax.y_range
    x0 = max(x0, xr[0]); x1 = min(x1, xr[1])
    if abs(b) > 1e-9:
        xa, xb = sorted([(yr[0] - a) / b, (yr[1] - a) / b]); x0 = max(x0, xa); x1 = min(x1, xb)
    return Line(ax.c2p(x0, a + b * x0), ax.c2p(x1, a + b * x1), color=color, **kw)

def unit_circle(radius=2.3, center=ORIGIN):
    """Projective circle: direction phi in [0,pi) is drawn at angle 2*phi."""
    c = Circle(radius=radius, color=MUTED, stroke_width=3).move_to(center)
    ticks = VGroup(); labs = VGroup()
    for d in range(0, 180, 30):
        a = 2 * np.radians(d); p = center + radius * np.array([np.cos(a), np.sin(a), 0])
        ticks.add(Dot(p, radius=0.04, color=MUTED))
        labs.add(T(f"{d}°", 18, MUTED).move_to(center + (radius + 0.4) * np.array([np.cos(a), np.sin(a), 0])))
    return VGroup(c, ticks, labs)

def on_circle(deg, radius=2.3, center=ORIGIN):
    a = 2 * np.radians(deg % 180)
    return center + radius * np.array([np.cos(a), np.sin(a), 0])
