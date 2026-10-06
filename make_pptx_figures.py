"""Extra single-purpose, large-format geometry figures used by the PowerPoint deck."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Wedge
from rashr_core import *
exec(open("make_figures.py").read().split("# 1 -- Figure 1")[0])   # palette, style, helpers, data (x,y,bad,D,...)
OUT = "figures/"
ia = int(np.argmin(np.abs(x - np.median(x[~bad])) + 5 * bad))      # a central majority anchor
others = np.delete(np.arange(100), ia); ph = D["Phi"][ia]
mid, w, det = angular_shorth(ph, h=D["hL"], return_details=True)
tr = lambda d: np.tan(d)

# --- A. chord fan --------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5.4)); scatter(ax, x, y, bad, s=22)
for j in others: ax.plot([x[ia], x[j]], [y[ia], y[j]], c=C["bad"] if bad[j] else C["maj"], alpha=.25, lw=.9)
beta_i = D["sy"] / D["sx"] * np.tan(mid if mid <= PI / 2 else mid - PI)
xs = np.array([-6, 17]); ax.plot(xs, y[ia] + beta_i * (xs - x[ia]), c=C["ink"], lw=2.6, ls="--", label="dominant local direction θᵢ")
ax.scatter(x[ia], y[ia], s=170, c="gold", edgecolor=C["ink"], zorder=6, label="anchor i")
ax.set_ylim(-16, 16); ax.legend(loc="lower left", fontsize=10); ax.set_xlabel("x"); ax.set_ylabel("y"); ax.grid(alpha=.5)
fig.savefig(OUT + "p_chord_fan.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# --- B. filmstrip: one anchor, step by step --------------------------------------------
fig, axs = plt.subplots(1, 5, figsize=(21, 4.2))
ttl = ["① anchor i", "② chords to all others", "③ each chord → a direction φᵢⱼ", "④ shortest window with half of them", "⑤ its midpoint → θᵢ"]
for a_ in list(axs[:2]) + list(axs[4:]): scatter(a_, x, y, bad, s=10); a_.set_ylim(-16, 16); a_.set_xticks([]); a_.set_yticks([])
for a_ in list(axs[:2]) + list(axs[4:]): a_.scatter(x[ia], y[ia], s=120, c="gold", edgecolor=C["ink"], zorder=6)
for j in others: axs[1].plot([x[ia], x[j]], [y[ia], y[j]], c=C["bad"] if bad[j] else C["maj"], alpha=.25, lw=.8)
axs[4].plot(xs, y[ia] + beta_i * (xs - x[ia]), c=C["ink"], lw=3, ls="--")
rng = np.random.default_rng(1)
for a_ in axs[2:4]:
    a_.scatter(deg(ph[~bad[others]]), rng.uniform(.1, .9, (~bad[others]).sum()), s=14, c=C["maj"]); a_.scatter(deg(ph[bad[others]]), rng.uniform(.1, .9, bad[others].sum()), s=16, c=C["bad"], marker="x")
    a_.set_xlim(0, 180); a_.set_ylim(0, 1); a_.set_yticks([]); a_.set_xlabel("angle (deg), mod 180°")
lo, hi = det["extended"][det["r"]], det["extended"][det["r"] + det["h"] - 1]
for a_, b_ in ([(lo, hi)] if hi <= PI else [(lo, PI), (0, hi - PI)]): axs[3].axvspan(deg(a_), deg(b_), color=C["accent"], alpha=.3)
axs[3].axvline(deg(mid), c=C["accent"], lw=3)
for a_, t in zip(axs, ttl): a_.set_title(t, fontsize=13)
fig.tight_layout(); fig.savefig(OUT + "p_filmstrip_anchor.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# --- C. projective circle with the anchor's chord directions -----------------------------------
fig, ax = plt.subplots(figsize=(6.6, 6.6)); ax.set_aspect("equal"); ax.axis("off")
t = np.linspace(0, 2 * PI, 400); ax.plot(np.cos(t), np.sin(t), c=C["ink"], lw=2)
for d_ in range(0, 180, 15):
    a = np.radians(2 * d_); ax.plot(np.cos(a), np.sin(a), "o", c=C["ink"], ms=3); ax.text(1.12 * np.cos(a), 1.12 * np.sin(a), f"{d_}°", ha="center", va="center", fontsize=9)
rr = np.where(bad[others], .86, .93)
ax.scatter(rr * np.cos(2 * ph), rr * np.sin(2 * ph), s=26, c=[C["bad"] if b else C["maj"] for b in bad[others]], zorder=4)
ax.add_patch(Wedge((0, 0), 1.0, deg(2 * lo), deg(2 * hi), width=.22, color=C["accent"], alpha=.35))
ax.plot([0, 1.02 * np.cos(2 * mid)], [0, 1.02 * np.sin(2 * mid)], c=C["accent"], lw=3)
ax.text(0, 0, "position = 2φ\nteal = shortest\nhalf-arc", ha="center", va="center", fontsize=11, color=C["ink"])
fig.savefig(OUT + "p_circle_anchor.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# --- D. standardization filmstrip --------------------------------------------------------------------
fig, axs = plt.subplots(1, 4, figsize=(19, 4.3)); xm, ym = np.median(x), np.median(y)
panels = [(x, y, "raw data", "x", "y"), (x - xm, y - ym, "subtract medians", "x − med(x)", "y − med(y)"), ((x - xm) / D["sx"], (y - ym) / D["sy"], "divide by 1.4826·MAD", "u", "v")]
for a_, (xx, yy, t_, xl, yl) in zip(axs[:3], panels):
    scatter(a_, xx, yy, bad, s=10); a_.set_title(t_, fontsize=13); a_.set_xlabel(xl); a_.set_ylabel(yl)
    if t_ == "raw data": a_.set_aspect("auto")
    else: a_.axhline(0, c=C["ink"], lw=.8); a_.axvline(0, c=C["ink"], lw=.8)
ax = axs[3]; ax.set_title("angles now unit-free", fontsize=13)
for scale, col in [(1, C["maj"]), (100, C["bad"])]:
    ang = np.arctan(2 * scale) if False else None
ts = np.linspace(-1, 1, 2)
ax.plot(ts, np.tan(theta_star) * ts, c=C["RAShR"], lw=3); ax.set_aspect("equal"); ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5)
ax.text(0, -1.3, f"true direction θ* = {deg(theta_star):.1f}°\n(same whatever the units)", ha="center", fontsize=11)
fig.tight_layout(); fig.savefig(OUT + "p_filmstrip_scale.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# --- E. two-level picture ---------------------------------------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(15, 5.2), gridspec_kw=dict(width_ratios=[1.15, 1]))
ax = axs[0]; picks = [int(i) for i in np.where(~bad)[0][[3, 20, 40]]] + [int(i) for i in np.where(bad)[0][[2, 14, 30]]]
for row, i in enumerate(picks):
    o_ = np.delete(np.arange(100), i); p_ = D["Phi"][i]; m_, w_, d_ = angular_shorth(p_, h=D["hL"], return_details=True); yy = 5 - row
    ax.scatter(deg(p_[~bad[o_]]), yy + rng.uniform(-.25, .25, (~bad[o_]).sum()), s=9, c=C["maj"]); ax.scatter(deg(p_[bad[o_]]), yy + rng.uniform(-.25, .25, bad[o_].sum()), s=10, c=C["bad"], marker="x")
    l_, h_ = d_["extended"][d_["r"]], d_["extended"][d_["r"] + d_["h"] - 1]
    for a1, b1 in ([(l_, h_)] if h_ <= PI else [(l_, PI), (0, h_ - PI)]): ax.add_patch(Rectangle((deg(a1), yy - .4), deg(b1 - a1), .8, fc=C["accent"], alpha=.25))
    ax.plot([deg(m_)] * 2, [yy - .4, yy + .4], c=C["accent"], lw=3)
    ax.text(182, yy, f"θ={deg(m_):.0f}°\nw={deg(w_):.0f}°", va="center", fontsize=9, color=C["bad"] if bad[i] else C["maj"])
ax.set_yticks([5 - k for k in range(6)]); ax.set_yticklabels([("majority " if not bad[i] else "cluster ") + "anchor" for i in picks], fontsize=9); ax.set_xlim(0, 200); ax.set_xlabel("chord direction (deg)")
ax.set_title("Level 1 — local: each anchor finds its own half-concentration", fontsize=12); ax.grid(axis="y", alpha=0)
ax = axs[1]; order = np.argsort(D["theta_i"]); ax.scatter(deg(D["theta_i"])[order], range(100), c=[C["bad"] if bad[o] else C["maj"] for o in order], s=16)
ax.axvspan(deg(D["theta_hat"]) - deg(D["w_out"]) / 2, deg(D["theta_hat"]) + deg(D["w_out"]) / 2, color=C["accent"], alpha=.25); ax.axvline(deg(D["theta_hat"]), c=C["RAShR"], lw=3)
ax.set_xlabel("local directions θᵢ (deg)"); ax.set_yticks([]); ax.set_title("Level 2 — outer: the same shorth across all θᵢ", fontsize=12)
fig.tight_layout(); fig.savefig(OUT + "p_two_level.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# --- F. intercept sliding ---------------------------------------------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(14, 4.8)); ax = axs[0]; scatter(ax, x, y, bad, s=14)
b_ = D["beta"]; inter = y - b_ * x; xs = np.array([-6, 17])
for a0 in np.linspace(-8, 6, 8): ax.plot(xs, a0 + b_ * xs, c="#BBB", lw=1)
ax.plot(xs, D["alpha"] + b_ * xs, c=C["RAShR"], lw=3, label=f"α̂ = median intercept = {D['alpha']:.2f}"); ax.set_ylim(-16, 16); ax.legend(fontsize=10); ax.set_xlabel("x"); ax.set_ylabel("y")
ax.set_title("Same slope β̂, lines slide vertically", fontsize=12)
ax = axs[1]; ax.hist(inter[~bad], bins=30, color=C["maj"], alpha=.85, label="majority"); ax.hist(inter[bad], bins=30, color=C["bad"], alpha=.85, label="contamination")
ax.axvline(np.median(inter), c=C["RAShR"], lw=3, label="median"); ax.legend(); ax.set_xlabel("implied intercept yᵢ − β̂ xᵢ"); ax.set_title("Each point implies an intercept", fontsize=12)
fig.tight_layout(); fig.savefig(OUT + "p_intercept.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# --- G. moving cluster filmstrip -----------------------------------------------------------------------------------------
rng2 = np.random.default_rng(3); xm_ = rng2.uniform(-5, 5, 64); ym_ = 1 + 2 * xm_ + rng2.normal(0, 1, 64); cxz = rng2.normal(0, .3, 36); cyz = rng2.normal(0, .3, 36)
fig, axs = plt.subplots(1, 4, figsize=(20, 4.3), sharey=True)
for a_, cx_ in zip(axs, [10, 18, 26, 36]):
    X = np.concatenate([xm_, cxz + cx_]); Y = np.concatenate([ym_, cyz - 10]); bb = np.r_[np.zeros(64, bool), np.ones(36, bool)]
    a_.scatter(X[~bb], Y[~bb], s=10, c=C['maj']); a_.scatter(X[bb], Y[bb], s=12, c=C['bad'], marker='x'); xs_ = np.array([-6, 42])
    for m, st in [("LMS", "--"), ("MM", "-."), ("RAShR", "-")]:
        aa, b__ = METHODS[m](X, Y); a_.plot(xs_, aa + b__ * xs_, st, c=C[m], lw=3 if m == "RAShR" else 1.6, label=f"{m} {b__:+.2f}")
    a_.set_ylim(-18, 16); a_.set_xlim(-7, 42); a_.set_title(f"cluster at cₓ = {cx_}", fontsize=13); a_.legend(fontsize=9, loc="upper left")
fig.tight_layout(); fig.savefig(OUT + "p_filmstrip_move.png", dpi=170, bbox_inches="tight"); plt.close(fig)
print("pptx figures ok")
