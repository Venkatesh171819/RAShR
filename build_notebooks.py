import nbformat as nbf
def nb(cells):
    n = nbf.v4.new_notebook(); n.cells = [nbf.v4.new_markdown_cell(c[1]) if c[0]=="m" else nbf.v4.new_code_cell(c[1]) for c in cells]
    n.metadata["kernelspec"] = {"display_name":"Python 3","language":"python","name":"python3"}; return n

SETUP = '''# --- setup (run once) -------------------------------------------------------
# %pip install numpy scipy matplotlib pandas   # uncomment if needed
import sys, os
sys.path.insert(0, os.path.abspath(".."))      # so that rashr_core.py (project root) is importable
import numpy as np, matplotlib.pyplot as plt
np.set_printoptions(precision=4, suppress=True)
SEED = 3                                         # deterministic everywhere'''

N1 = [
("m","""# RAShR from geometry to code
*Repeated Angular Shorth Regression* — Dharavath & Srivastava.  
This notebook builds the estimator **one geometric object at a time**:

`points → chords → directions → projective angles → angular shorth → local directions → repeated shorth → slope → intercept`

Every cell is paired with the paper equation it implements."""),
("c",SETUP),
("m","""## 0. The data: a compact high-leverage cluster (paper Fig. 1 setting)
62 points follow $y=1+2x+e$, 38 sit in a compact cluster centred at $(15,-10)$ (spread 0.3)."""),
("c","""from rashr_core import simulate
rng = np.random.default_rng(SEED)
x, y, bad = simulate(100, 0.38, "compact", rng)
plt.scatter(x[~bad], y[~bad], s=14, label="majority"); plt.scatter(x[bad], y[bad], marker="x", c="C3", s=20, label="cluster")
plt.xlabel("x"); plt.ylabel("y"); plt.legend(); plt.title("Data"); plt.show()"""),
("m","""## 1. Robust standardization — Eq. (2)
Angles depend on units, so both axes are centred at the median and scaled by $s=1.4826\\,\\mathrm{MAD}$ (standard deviation if MAD = 0)."""),
("c","""def robust_scale(z):
    s = 1.4826 * np.median(np.abs(z - np.median(z)))
    return s if s > 0 else np.std(z)

mx, my, sx, sy = np.median(x), np.median(y), robust_scale(x), robust_scale(y)
u, v = (x - mx) / sx, (y - my) / sy
print(f"s_x = {sx:.3f}, s_y = {sy:.3f}")"""),
("m","""## 2. Chord directions — Eq. (3)
For two points the chord direction is $\\phi_{ij}=\\operatorname{atan2}(v_j-v_i,\\,u_j-u_i)\\bmod\\pi$.  
`atan2` works with the *vector*, so a nearly vertical chord (tiny $u_j-u_i$) is harmless, unlike the ratio $\\Delta v/\\Delta u$."""),
("c","""def chord_angle(du, dv):
    return np.mod(np.arctan2(dv, du), np.pi)

i, j = 0, 1
print("direction of chord (0,1):", np.degrees(chord_angle(u[j]-u[i], v[j]-v[i])), "deg")
# all chords at once (n x n), then remove the diagonal -> Phi_i has n-1 entries
n = len(u)
phi = chord_angle(u[None, :] - u[:, None], v[None, :] - v[:, None])
Phi = phi[~np.eye(n, dtype=bool)].reshape(n, n - 1)
print(Phi.shape)"""),
("m","""## 3. The projective circle — Eq. (4)
A line has no orientation: $20^\\circ$ and $200^\\circ$ are the *same* line. So directions live on $[0,\\pi)$ with 0 and $\\pi$ glued, and the distance is
$d_\\pi(a,b)=\\min(|a-b|,\\pi-|a-b|)$."""),
("c","""def d_pi(a, b):
    d = np.abs(a - b); return np.minimum(d, np.pi - d)
print(np.degrees(chord_angle(np.cos(np.radians(20)), np.sin(np.radians(20)))),
      np.degrees(chord_angle(np.cos(np.radians(200)), np.sin(np.radians(200)))))   # both 20
print("d_pi(5°,175°) =", np.degrees(d_pi(np.radians(5), np.radians(175))), "deg  (not 170!)")"""),
("m","""## 4. The angular shorth — Eq. (5)
Classical shorth: *shortest interval containing half the data*. Circular version: sort the angles, append a copy shifted by $\\pi$ (so arcs crossing the seam become ordinary intervals), slide a window of $h$ consecutive angles, keep the narrowest (ties → smallest left endpoint), and return its midpoint mod $\\pi$."""),
("c","""def angular_shorth(A, h=None):
    a = np.sort(np.mod(A, np.pi)); m = len(a)
    h = int(np.ceil(m / 2)) if h is None else h
    ext = np.concatenate([a, a + np.pi])
    widths = ext[h-1 : h-1+m] - ext[:m]          # one window per left endpoint
    r = int(np.argmin(widths))                    # argmin returns the FIRST minimum -> deterministic tie rule
    return (0.5 * (ext[r] + ext[r+h-1])) % np.pi, widths[r]

demo = np.radians([2, 5, 9, 14, 20, 88, 100, 150, 165, 171, 174, 178])
mid, w = angular_shorth(demo)
print(f"ASh = {np.degrees(mid):.1f}°, width = {np.degrees(w):.0f}°  (window crosses the 0°/180° seam)")
print("naive median angle =", np.degrees(np.median(demo)), "° -- not where the data concentrate")"""),
("m","""## 5. Local directions — Eqs. (6)–(7)
Each observation is an *anchor*. $\\Phi_i=\\{\\phi_{ij}\\}_{j\\ne i}$, $\\theta_i=\\mathrm{ASh}(\\Phi_i)$ is the dominant direction anchor $i$ sees; $w_i$ is the width of that shortest half-window (small = strong agreement)."""),
("c","""hL = int(np.ceil((n - 1) / 2)); hO = int(np.ceil(n / 2))
theta = np.empty(n); wloc = np.empty(n)
for k in range(n):
    theta[k], wloc[k] = angular_shorth(Phi[k], h=hL)

theta_star = np.arctan(2 * sx / sy)               # the true direction in standardized space
sd = lambda t: np.degrees((t - theta_star + np.pi/2) % np.pi - np.pi/2)
plt.scatter(sd(theta)[~bad], np.degrees(wloc)[~bad], label="majority anchors")
plt.scatter(sd(theta)[bad], np.degrees(wloc)[bad], marker="x", c="C3", label="cluster anchors")
plt.xlabel(r"$\\theta_i-\\theta^*$ (deg)"); plt.ylabel(r"$w_i$ (deg)"); plt.legend(); plt.show()"""),
("m","""## 6. Repeated aggregation — Eq. (8)
Apply the *same* operation to $\\theta_1,\\dots,\\theta_n$ (with $h=\\lceil n/2\\rceil$). Local aggregation happens inside each anchor; outer aggregation happens across anchors — hence *repeated* angular shorth."""),
("c","""theta_hat, w_out = angular_shorth(theta, h=hO)
print("theta_hat =", np.degrees(theta_hat), "deg, outer width =", np.degrees(w_out), "deg")"""),
("m","""## 7. Back to the original scale — Eqs. (9)–(10)
$\\hat\\beta=\\frac{s_y}{s_x}\\tan\\hat\\theta$ (with $\\hat\\theta$ represented in $(-\\pi/2,\\pi/2]$), and $\\hat\\alpha=\\operatorname{med}_i(y_i-\\hat\\beta x_i)$."""),
("c","""th = theta_hat if theta_hat <= np.pi/2 else theta_hat - np.pi
beta = sy / sx * np.tan(th); alpha = np.median(y - beta * x)
print(f"RAShR: alpha = {alpha:.3f}, beta = {beta:.3f}   (true: 1, 2)")"""),
("m","""## 8. Validation
The inline implementation must agree with the project module, satisfy the exact-fit property (Prop. 1) and positive-scale equivariance (Prop. 2)."""),
("c","""from rashr_core import rashr, ols, lms, mm
a2, b2 = rashr(x, y)
assert np.isclose(b2, beta) and np.isclose(a2, alpha), "inline vs module mismatch"
print("module agrees:", round(b2, 4))

# Prop. 1: exact fit, even under contamination smaller than ceil((n-1)/2)  (Corollary 1)
r = np.random.default_rng(0); xe = r.uniform(-5, 5, 60); ye = 3 + 1.7 * xe
xe[:20], ye[:20] = r.normal(15, .3, 20), r.normal(-10, .3, 20)
ye[20:] = 3 + 1.7 * xe[20:]
print("exact fit with 20/60 contaminated:", rashr(xe, ye))

# Prop. 2: x' = 3+2x, y' = -1+5y  =>  beta' = (5/2) beta
a3, b3 = rashr(3 + 2 * x, -1 + 5 * y)
print("equivariance:", b3, 2.5 * b2)

print({"OLS": ols(x, y)[1], "LMS": lms(x, y)[1], "MM": mm(x, y)[1], "RAShR": b2})"""),
("m","""## 9. Where the formulas break (limitations stated in the paper)
* **Not fully affine equivariant**: $y\\to y+\\gamma x$ changes $s_y$, so it is not a rotation of the standardized data.
* **'All chords near θ*' is too strong** (Remark 1): pairs with almost equal $x$ give almost arbitrary chord directions; RAShR needs only a *concentrated half-sample*."""),
("c","""r = np.random.default_rng(5); xg = r.uniform(-5, 5, 100); yg = 1 + 2 * xg + r.normal(0, 1, 100)
ug, vg = (xg - np.median(xg)) / robust_scale(xg), (yg - np.median(yg)) / robust_scale(yg)
ii, jj = np.triu_indices(100, 1)
ph = chord_angle(ug[jj] - ug[ii], vg[jj] - vg[ii]); ts = np.arctan(2 * robust_scale(xg) / robust_scale(yg))
print("share of majority chords within 22.5° of θ*:", np.mean(np.degrees(d_pi(ph, ts)) < 22.5).round(2))
print("RAShR slope on this noisy sample:", round(rashr(xg, yg)[1], 3))"""),
]

N2 = [
("m","""# RAShR simulation study (paper Section 5)
Base model: $n=100$, $x\\sim U[-5,5]$, $y=1+2x+e$, $e\\sim N(0,1)$. A fraction $f$ is replaced by (a) a compact leverage cluster at $(15,-10)$ with spread 0.3, (b) a competing line $y=5-1.25x+e_c$, $e_c\\sim N(0,0.5^2)$, (c) a funnel majority (sd $0.2+0.6|x|$) plus a competing line (sd 0.3).  
Failure: $|\\hat\\beta-2|>0.5$.

> **Reproducibility note.** The numbers produced here come from *our re-implementation*; the paper's own values are in `paper_values.py`. The paper does not fully specify some tuning constants (e.g. RANSAC's residual threshold, LTS coverage), so small-to-moderate differences are expected. The qualitative picture is what we compare."""),
("c",SETUP + "\nfrom rashr_core import METHODS, simulate\nfrom paper_values import PAPER\nimport pandas as pd"),
("c","""REPS = 30            # paper: 60. Increase for smoother curves (run_simulations.py does 60)
FRACS = [0.20, 0.30, 0.36, 0.40, 0.44, 0.46]
def failure_curve(kind, reps=REPS):
    out = {m: [] for m in METHODS}
    for f in FRACS:
        errs = {m: [] for m in METHODS}
        for r in range(reps):
            rng = np.random.default_rng(1000*r + int(f*100))
            x, y, _ = simulate(100, f, kind, rng)
            for m, fn in METHODS.items(): errs[m].append(abs(fn(x, y, seed=r)[1] - 2))
        for m in METHODS: out[m].append(np.mean(np.array(errs[m]) > 0.5))
    return pd.DataFrame(out, index=FRACS)
curves = {k: failure_curve(k) for k in ["compact", "line", "funnel"]}
curves["compact"]"""),
("c","""fig, axs = plt.subplots(1, 3, figsize=(14, 3.8), sharey=True)
for ax, (k, df) in zip(axs, curves.items()):
    for m in df: ax.plot(df.index, df[m], "-o", lw=3 if m == "RAShR" else 1.4, label=m)
    ax.set_title(k); ax.set_xlabel("contamination fraction")
axs[0].set_ylabel("failure rate"); axs[0].legend(); plt.show()"""),
("m","""## Limitations: RAShR is *not* universally better
Median absolute slope error on clean / mildly contaminated data."""),
("c","""def med_err(kind, f, reps=60):
    e = {m: [] for m in METHODS}
    for r in range(reps):
        x, y, _ = simulate(100, f, kind, np.random.default_rng(77 + r))
        for m, fn in METHODS.items(): e[m].append(abs(fn(x, y, seed=r)[1] - 2))
    return {m: round(float(np.median(v)), 3) for m, v in e.items()}
tbl = pd.DataFrame({"clean": med_err("clean", 0), "20% vertical": med_err("vertical", .2), "10% bad leverage": med_err("leverage_pts", .1)}).T
display(tbl)
print("Paper reports: clean RAShR .033 / MM .024 / RANSAC .022;  20% vertical .040/.027/.037;  10% leverage .041/.020/.021")
print("-> MM (and RANSAC) are the more efficient choice in standard settings; this is reproduced.")"""),
("m","""## When does the advantage disappear?
(1) cluster on the *extension* of the majority line (≈30° and −150° ≡ 30° on the projective circle) and (2) a diffuse cluster."""),
("c","""import json
R = json.load(open("../results/simulation_results.json"))
pd.DataFrame({k: v for k, v in R["directions"].items() if k.startswith("30_")}).T.round(2)"""),
("c","""pd.DataFrame({k: {m: v[m]["fail"] for m in v} for k, v in R["spread"].items()}).T.rename_axis("spread")"""),
]
nbf.write(nb(N1), "notebooks/01_rashr_geometry_to_code.ipynb")
nbf.write(nb(N2), "notebooks/02_simulation_study.ipynb")
