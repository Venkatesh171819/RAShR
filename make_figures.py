"""Create all static figures (PNG + PDF) shared by the PPTX, Beamer and notebooks."""
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Rectangle, FancyArrowPatch
from rashr_core import *
from paper_values import PAPER

# ---- shared visual identity -------------------------------------------------
C = dict(ink="#10213A", maj="#3E7CE0", bad="#D1495B", true="#111111", grid="#E3E8F0",
         RAShR="#1F6FEB", LMS="#E4572E", LTS="#17A398", MM="#F2A541", RANSAC="#7B4FB5",
         OLS="#8A94A6", accent="#0FA3B1", soft="#F4F7FB")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": C["ink"],
    "axes.labelcolor": C["ink"], "xtick.color": C["ink"], "ytick.color": C["ink"],
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": C["grid"], "grid.linewidth": 0.8, "figure.dpi": 110,
    "axes.titleweight": "bold", "axes.titlesize": 12, "legend.frameon": False})
OUT = "figures/"
def save(fig, name):
    fig.savefig(OUT + name + ".png", dpi=200, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT + name + ".pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)

x, y, bad = simulate(100, 0.38, "compact", np.random.default_rng(3))   # Figure-1 style data
D = rashr(x, y, return_details=True)
u, v, sx, sy = D["u"], D["v"], D["sx"], D["sy"]
theta_star = np.arctan(2 * sx / sy)           # true direction in standardized space
deg = np.degrees

def scatter(ax, x, y, bad, s=16):
    ax.scatter(x[~bad], y[~bad], s=s, c=C["maj"], alpha=.8, label="majority (62%)", zorder=3)
    ax.scatter(x[bad], y[bad], s=s+4, c=C["bad"], marker="x", label="leverage cluster (38%)", zorder=3)

# 1 -- Figure 1 -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.8)); scatter(ax, x, y, bad)
xs = np.array([-6, 17])
for m, st in [("OLS", ":"), ("LMS", "--"), ("MM", "-."), ("RAShR", "-")]:
    a, b = {"OLS": ols, "LMS": lms, "MM": mm, "RAShR": rashr}[m](x, y)
    ax.plot(xs, a + b * xs, st, c=C[m], lw=2.6 if m == "RAShR" else 1.8, label=f"{m} (slope {b:+.2f})")
ax.plot(xs, 1 + 2 * xs, c=C["true"], lw=1, label="true line (slope +2.00)")
ax.set_ylim(-16, 16); ax.set_xlabel("x"); ax.set_ylabel("y"); ax.legend(fontsize=8.5, loc="upper right")
ax.set_title("A compact high-leverage cluster (38%) misleads residual-based fits")
save(fig, "fig1_motivation")

# 2 -- chords from one anchor ------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(11, 4.6))
ia = int(np.argmin(np.abs(x - 0) + np.abs(y - 1)) if not bad[np.argmin(np.abs(x))] else 0)
ax = axs[0]; scatter(ax, x, y, bad, s=12)
for j in range(100):
    if j != ia: ax.plot([x[ia], x[j]], [y[ia], y[j]], c=C["bad"] if bad[j] else C["maj"], alpha=.22, lw=.8)
ax.scatter(x[ia], y[ia], s=90, c="gold", edgecolor=C["ink"], zorder=5, label="anchor i")
ax.set_title("Chords from one anchor"); ax.set_xlabel("x"); ax.set_ylabel("y"); ax.legend(fontsize=8)
ax = axs[1]
ph = D["Phi"][ia]; others = np.delete(np.arange(100), ia)
ax.hist(deg(ph[~bad[others]]), bins=np.arange(0, 181, 3), color=C["maj"], alpha=.85, label="to majority points")
ax.hist(deg(ph[bad[others]]), bins=np.arange(0, 181, 3), color=C["bad"], alpha=.85, label="to cluster points")
ax.axvline(deg(D["theta_i"][ia]), c=C["ink"], lw=2, ls="--", label=f"θᵢ = ASh(Φᵢ) = {deg(D['theta_i'][ia]):.1f}°")
ax.set_xlabel("chord direction φᵢⱼ (degrees, standardized coordinates, mod 180°)"); ax.set_ylabel("count"); ax.legend(fontsize=8)
ax.set_title("Directions seen from the anchor")
save(fig, "fig2_chords_anchor")

# 3 -- projective circle -------------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(11, 4.8))
ax = axs[0]; ax.set_aspect("equal"); ax.axis("off")
t = np.linspace(0, 2 * np.pi, 400); ax.plot(np.cos(t), np.sin(t), c=C["ink"], lw=1.5)
for d_ in range(0, 180, 15):                 # position on circle = 2*phi
    a = np.radians(2 * d_); ax.plot([np.cos(a)], [np.sin(a)], "o", c=C["ink"], ms=3)
    ax.text(1.16 * np.cos(a), 1.16 * np.sin(a), f"{d_}°", ha="center", va="center", fontsize=8)
for ang, col in [(20, C["maj"]), (200, C["bad"])]:
    p = np.radians(2 * (ang % 180)); ax.plot(np.cos(p), np.sin(p), "o", c=col, ms=11, zorder=5, mfc="none" if ang == 200 else col, mew=2.5)
ax.text(0, 0.1, "projective circle\nposition = 2φ", ha="center", fontsize=10, color=C["ink"])
ax.text(0, -0.3, "20° and 200°\nare ONE point", ha="center", fontsize=10, color=C["bad"], weight="bold")
ax.set_title("Unoriented directions live on [0, π)", pad=18)
ax = axs[1]; ax.set_ylim(-1, 1.7); ax.set_xlim(-10, 190); ax.axis("off")
ax.annotate("", (180, 0), (0, 0), arrowprops=dict(arrowstyle="-", lw=2, color=C["ink"]))
for d_ in range(0, 181, 30): ax.text(d_, -.25, f"{d_}°", ha="center"); ax.plot([d_, d_], [-.06, .06], c=C["ink"])
a_, b_ = 8, 172
ax.plot([a_, b_], [0, 0], "o", c=C["maj"], ms=10)
ax.annotate("", (b_, .5), (a_, .5), arrowprops=dict(arrowstyle="<->", color=C["bad"], lw=2))
ax.text(90, .62, f"|a−b| = {b_-a_}°  (looks far apart)", ha="center", color=C["bad"])
ax.plot([b_, 180], [.22, .22], c=C["accent"], lw=5, solid_capstyle="butt"); ax.plot([0, a_], [.22, .22], c=C["accent"], lw=5, solid_capstyle="butt")
ax.text(90, .9, "short way round: through the seam", ha="center", color=C["accent"], fontsize=9)
ax.text(90, 1.35, f"d_π(a,b) = min(|a−b|, 180°−|a−b|) = {180-(b_-a_)}°  → actually adjacent!", ha="center", color=C["accent"], weight="bold")
ax.text(90, -.75, "0° and 180° are glued: the interval wraps around", ha="center", color=C["ink"])
ax.set_title("Wrap-around: a plain interval is not enough", pad=18)
save(fig, "fig3_projective_circle")

# 4 -- angular shorth windows ----------------------------------------------------
def draw_window(ax, det, mid, ttl):
    ext, r, h = det["extended"], det["r"], det["h"]
    lo, hi = deg(ext[r]), deg(ext[r + h - 1])
    ax.eventplot(deg(det["sorted"]), colors=C["maj"], lineoffsets=0, linelengths=.6, linewidths=2.5)
    ax.set_xlim(-5, 185); ax.set_ylim(-1, 1.2); ax.set_yticks([])
    for a_, b_ in ([(lo, hi)] if hi <= 180 else [(lo, 180), (0, hi - 180)]):
        ax.add_patch(Rectangle((a_, -.45), b_ - a_, .9, fc=C["accent"], alpha=.25))
    ax.axvline(deg(mid), c=C["accent"], lw=2.5)
    ax.text(min(max(deg(mid), 22), 160), 1.02, f"ASh = {deg(mid):.0f}°", color=C["accent"], ha="center", weight="bold")
    ax.set_title(ttl, fontsize=11); ax.set_xlabel("angle (deg)")
fig, axs = plt.subplots(1, 3, figsize=(14, 4.2))
demo = np.radians([10, 30, 60, 66, 70, 75, 80, 84, 120, 135, 150, 165])
mid, w, det = angular_shorth(demo, h=6, return_details=True)
draw_window(axs[0], det, mid, "12 angles, h = 6: shortest window")
axs[0].axvline(deg(np.median(demo)), c=C["LMS"], lw=2, ls="--"); axs[0].text(deg(np.median(demo)), -.85, "median angle", color=C["LMS"], ha="center")
ax = axs[1]
ax.bar(range(len(det["widths"])), deg(det["widths"]), color=[C["accent"] if i == det["r"] else "#BFD0EA" for i in range(len(det["widths"]))])
ax.set_xlabel("window start r (sorted, with +180° copy)"); ax.set_ylabel("window width (deg)"); ax.set_title("Width of every h-window", fontsize=11)
w2 = np.radians([2, 5, 9, 14, 20, 88, 100, 150, 165, 171, 174, 178])
mid2, ww2, det2 = angular_shorth(w2, h=6, return_details=True)
draw_window(axs[2], det2, mid2, f"Wrap-around: window crosses the 0°/180° seam (width {deg(ww2):.0f}°)")
save(fig, "fig4_angular_shorth")

# 5 -- local directions & widths (Figure 3a) -------------------------------------
fig, ax = plt.subplots(figsize=(6.4, 4.6))
def signed(d): return deg((d - theta_star + PI / 2) % PI - PI / 2)
ax.scatter(signed(D["theta_i"])[~bad], deg(D["w_i"])[~bad], c=C["maj"], s=22, label="majority anchors")
ax.scatter(signed(D["theta_i"])[bad], deg(D["w_i"])[bad], c=C["bad"], marker="x", s=30, label="cluster anchors")
ax.set_xlabel("local direction θᵢ − θ* (deg)"); ax.set_ylabel("local width wᵢ (deg)"); ax.legend()
ax.set_title("Majority anchors form the larger, tighter group")
save(fig, "fig5_local_directions")

# 6 -- standardization --------------------------------------------------------------
fig, axs = plt.subplots(1, 3, figsize=(14, 4.2))
rng = np.random.default_rng(7); xr = rng.uniform(-5, 5, 60); yr = 1 + 2 * xr + rng.normal(0, 1, 60)
for ax, (xx, yy, ttl) in zip(axs[:2], [(xr, yr, "original (metres)"), (xr * 100, yr, "x in centimetres")]):
    ax.scatter(xx, yy, s=14, c=C["maj"]); b = np.polyfit(xx, yy, 1)[0]
    ax.set_title(f"{ttl}\nslope {b:.3g}, angle {deg(np.arctan(b)):.1f}°", fontsize=10); ax.set_xlabel("x"); ax.set_ylabel("y")
uu, vv, *_ = standardize(xr * 100, yr); ax = axs[2]; ax.set_aspect("equal")
ax.scatter(uu, vv, s=14, c=C["accent"]); b = np.polyfit(uu, vv, 1)[0]
ax.set_title(f"standardized (u, v)\nangle {deg(np.arctan(b)):.1f}° in both units", fontsize=10); ax.set_xlabel("u"); ax.set_ylabel("v")
save(fig, "fig6_standardization")

# 7 -- outer stage -------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.2))
order = np.argsort(D["theta_i"])
ax.scatter(np.arange(100), deg(D["theta_i"])[order], c=[C["bad"] if bad[o] else C["maj"] for o in order], s=18)
ax.axhline(deg(D["theta_hat"]), c=C["RAShR"], lw=2.5, label=f"θ̂ = ASh(θ₁..θₙ) = {deg(D['theta_hat']):.1f}°")
ax.axhspan(deg(D["theta_hat"]) - deg(D["w_out"]) / 2, deg(D["theta_hat"]) + deg(D["w_out"]) / 2, color=C["accent"], alpha=.2, label="outer shortest-half window")
ax.set_xlabel("local directions, sorted"); ax.set_ylabel("θᵢ (deg)"); ax.legend(fontsize=9)
ax.set_title("Outer aggregation: second angular shorth")
save(fig, "fig7_outer_stage")

# 8 -- simulation curves ----------------------------------------------------------------
R = json.load(open("results/simulation_results.json"))
fracs = [float(f) for f in R["fracs"]]
fig, axs = plt.subplots(1, 3, figsize=(15, 4.3), sharey=True)
for ax, (k, ttl) in zip(axs, [("compact", "(a) compact leverage cluster"), ("line", "(b) competing line"), ("funnel", "(c) funnel majority + line")]):
    for m in ["LMS", "LTS", "MM", "RANSAC", "RAShR"]:
        ax.plot(fracs, [R[k][f"{f:.2f}"][m]["fail"] for f in fracs], "-o", ms=4, c=C[m], lw=2.8 if m == "RAShR" else 1.6, label=m, zorder=5 if m == "RAShR" else 3)
    for f, d in PAPER[k].items():
        for m, val in d.items():
            if val is not None: ax.plot(f, val, "D", mfc="none", mec=C[m], ms=8, mew=1.4, zorder=6)
    ax.set_title(ttl); ax.set_xlabel("contamination fraction")
axs[0].set_ylabel("failure rate Pr(|β̂−2|>0.5)"); axs[0].legend(fontsize=9)
axs[2].plot([], [], "D", mfc="none", mec="k", label="◇ value reported in paper"); axs[2].legend(fontsize=9, loc="upper left")
fig.suptitle("Failure rate vs coherent-contamination fraction (lines: this re-implementation, 60 reps; ◇: paper)", y=1.02, fontsize=11)
save(fig, "fig8_failure_curves")

# 9 -- cluster movement ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.3))
for m in ["RANSAC", "LTS", "MM", "LMS", "RAShR"]:
    ax.plot(R["move"]["cx"], R["move"][m], "-", c=C[m], lw=3 if m == "RAShR" else 1.6, label=m)
ax.axhline(2, c=C["true"], lw=.8, ls=":"); ax.set_xlabel("cluster position cₓ"); ax.set_ylabel("estimated slope")
ax.legend(fontsize=9, ncol=3); ax.set_title("Slope while a fixed 36-point cluster moves horizontally")
save(fig, "fig9_cluster_move")

# 10 -- LMS attraction ----------------------------------------------------------------------
def W(a, b): return np.sort(np.abs(y - a - b * x))[49]
fig, ax = plt.subplots(figsize=(8, 4.6)); scatter(ax, x, y, bad)
xs = np.array([-6, 17]); wt = W(1, 2)
cx_, cy_ = x[bad].mean(), y[bad].mean(); bc = (cy_ - np.median(y[~bad] - 2 * x[~bad])) / 1  # placeholder
aL, bL = lms(x, y); wl = W(aL, bL)
ax.fill_between(xs, 1 + 2 * xs - wt, 1 + 2 * xs + wt, color=C["maj"], alpha=.15, label=f"strip around true line: W = {wt:.2f}")
ax.fill_between(xs, aL + bL * xs - wl, aL + bL * xs + wl, color=C["LMS"], alpha=.25, label=f"strip around line through cluster: W = {wl:.2f}")
ax.plot(xs, 1 + 2 * xs, c=C["maj"], lw=2); ax.plot(xs, aL + bL * xs, c=C["LMS"], lw=2)
ax.set_ylim(-16, 16); ax.legend(fontsize=8.5, loc="upper left"); ax.set_xlabel("x"); ax.set_ylabel("y")
ax.set_title("LMS criterion: narrowest strip holding half the data")
save(fig, "fig10_lms_attraction")

# 11 -- near-vertical chords / 'all chords' remark ----------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
rng = np.random.default_rng(5); xg = rng.uniform(-5, 5, 100); yg = 1 + 2 * xg + rng.normal(0, 1, 100)
ug, vg, *_ = standardize(xg, yg); i_, j_ = np.triu_indices(100, 1)
ph = np.mod(np.arctan2(vg[j_] - vg[i_], ug[j_] - ug[i_]), PI); ts = np.arctan(2 * robust_scale(xg) / robust_scale(yg))
ax = axs[0]; k = np.argsort(np.abs(xg[j_] - xg[i_]))[:8]
ax.scatter(xg, yg, s=10, c=C["maj"])
for kk in k: ax.plot([xg[i_[kk]], xg[j_[kk]]], [yg[i_[kk]], yg[j_[kk]]], c=C["bad"], lw=1.6)
ax.set_title("Nearly equal x → near-vertical chords", fontsize=10.5); ax.set_xlabel("x"); ax.set_ylabel("y")
ax = axs[1]; ax.hist(deg(ph), bins=np.arange(0, 181, 3), color=C["maj"])
ax.axvline(deg(ts), c=C["ink"], ls="--", lw=2, label="true direction θ*"); dd = deg(d_pi(ph, ts)); frac = np.mean(dd < 22.5)
ax.set_title(f"{frac:.0%} of chords within 22.5° of θ*, not all", fontsize=10.5); ax.set_xlabel("chord direction (deg)"); ax.legend()
save(fig, "fig11_all_chords_remark")

# 12 -- repeated median bridge -----------------------------------------------------------------
fig, axs = plt.subplots(1, 3, figsize=(14, 4.2))
xm, ym = x, y; ia2 = ia
ax = axs[0]; scatter(ax, xm, ym, bad, s=10)
for j in range(100):
    if j != ia2: ax.plot([xm[ia2], xm[j]], [ym[ia2], ym[j]], c="#999", alpha=.2, lw=.7)
ax.scatter(xm[ia2], ym[ia2], s=90, c="gold", edgecolor=C["ink"], zorder=5); ax.set_title("1. anchor + chords to all others")
sl = lambda i: np.array([(y[j] - y[i]) / (x[j] - x[i]) for j in range(100) if j != i])
ax = axs[1]; s_ = sl(ia2); ax.hist(np.clip(s_, -5, 8), bins=40, color="#9FB7DE"); ax.axvline(np.median(s_), c=C["MM"], lw=2.5, label=f"median = {np.median(s_):.2f}")
ax.legend(); ax.set_title("2. slopes → local median"); ax.set_xlabel("pairwise slope (clipped)")
ax = axs[2]; loc = np.array([np.median(sl(i)) for i in range(100)])
ax.hist(loc, bins=30, color="#9FB7DE"); ax.axvline(np.median(loc), c=C["MM"], lw=2.5, label=f"median of medians = {np.median(loc):.2f}")
ax.legend(); ax.set_title("3. repeat for all anchors → median"); ax.set_xlabel("local median slope")
save(fig, "fig12_repeated_median")

# 13 -- exact fit & corollary ---------------------------------------------------------------------
rng = np.random.default_rng(2); xe = rng.uniform(-5, 5, 60); ye = 3 + 1.7 * xe
xe2, ye2 = xe.copy(), ye.copy(); xe2[:20] = rng.normal(15, .3, 20); ye2[:20] = rng.normal(-10, .3, 20)
Dx = rashr(xe2, ye2, return_details=True)
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2)); ax = axs[0]
ax.scatter(xe2[20:], ye2[20:], c=C["maj"], s=14); ax.scatter(xe2[:20], ye2[:20], c=C["bad"], marker="x", s=24)
xs = np.array([-6, 17]); ax.plot(xs, Dx["alpha"] + Dx["beta"] * xs, c=C["RAShR"], lw=2)
ax.set_title(f"Exact fit under contamination: β̂ = {Dx['beta']:.4f}, α̂ = {Dx['alpha']:.4f}")
ax = axs[1]; ax.scatter(deg(Dx["theta_i"][20:]), deg(Dx["w_i"][20:]), c=C["maj"], label="majority anchors (w = 0)")
ax.scatter(deg(Dx["theta_i"][:20]), deg(Dx["w_i"][:20]), c=C["bad"], marker="x", label="cluster anchors")
ax.set_xlabel("θᵢ (deg)"); ax.set_ylabel("wᵢ (deg)"); ax.legend(); ax.set_title("Zero-width majority directions")
save(fig, "fig13_exact_fit")

# 14 -- equivariance & its limit ----------------------------------------------------------------------
fig, axs = plt.subplots(1, 3, figsize=(14, 4.2)); rng = np.random.default_rng(4)
xq = rng.uniform(-5, 5, 80); yq = 1 + 2 * xq + rng.normal(0, 1, 80); a0, b0 = rashr(xq, yq)
x2, y2 = 3 + 2 * xq, -1 + 5 * yq; a1, b1 = rashr(x2, y2)
for ax, (xx, yy, bb, aa, t) in zip(axs[:2], [(xq, yq, b0, a0, f"original  β̂={b0:.3f}"), (x2, y2, b1, a1, f"x'=3+2x, y'=−1+5y  β̂'={b1:.3f} = (5/2)β̂")]):
    ax.scatter(xx, yy, s=12, c=C["maj"]); xs = np.array([xx.min(), xx.max()]); ax.plot(xs, aa + bb * xs, c=C["RAShR"], lw=2); ax.set_title(t, fontsize=10)
ax = axs[2]; g_ = 3.0; yg2 = yq + g_ * xq
ua, va, *_ = standardize(xq, yq); ub, vb, *_ = standardize(xq, yg2)
ax.scatter(ua, va, s=10, c=C["maj"], label="(u,v)"); ax.scatter(ub, vb, s=10, c=C["bad"], label="(u,v) after y→y+γx", alpha=.6)
ax.set_aspect("equal"); ax.legend(fontsize=8); ax.set_title("y→y+γx is NOT a rotation: scale s_y changes", fontsize=10)
save(fig, "fig14_equivariance")

# 15 -- directions at distance 30 -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.2)); angs = list(range(0, 360, 30)); wdt = .16
for k_, m in enumerate(["RAShR", "LMS", "LTS", "MM", "RANSAC"]):
    ax.bar(np.arange(12) + (k_ - 2) * wdt, [R["directions"][f"30_{a}"][m] for a in angs], wdt, color=C[m], label=m)
ax.set_xticks(range(12)); ax.set_xticklabels([f"{a}°" for a in angs]); ax.set_xlabel("direction of the 38% cluster from the majority centre (distance 30)")
ax.set_ylabel("failure rate"); ax.legend(ncol=5, fontsize=8); ax.set_title("Cluster on the line's extension (30°, 210°≡−150°): edge lost", fontsize=11)
save(fig, "fig15_directions")

# 16 -- spread experiment ---------------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4)); sp = ["0.05", "0.3", "1.0", "3.0"]
for k_, m in enumerate(["RAShR", "LMS", "LTS", "MM"]):
    ax.bar(np.arange(4) + (k_ - 1.5) * .2, [R["spread"][s][m]["fail"] for s in sp], .2, color=C[m], label=m)
ax.set_xticks(range(4)); ax.set_xticklabels(sp); ax.set_xlabel("cluster spread"); ax.set_ylabel("failure rate"); ax.legend(ncol=4, fontsize=9)
ax.set_title("Compactness matters (38% cluster)")
save(fig, "fig16_spread")
print("figures ok")
