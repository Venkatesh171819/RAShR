"""RAShR Lab -- interactive Streamlit companion to the paper
"Robust Linear Regression via the Repeated Angular Shorth".
Run from the project root:   streamlit run app/app.py
"""
import os, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import numpy as np, pandas as pd, streamlit as st
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rashr_core import METHODS, simulate, rashr, ols, PI, d_pi, angular_shorth
from paper_values import PAPER

st.set_page_config(page_title="RAShR Lab", page_icon="📐", layout="wide")
st.markdown(f"<style>{(pathlib.Path(__file__).parent / 'styles.css').read_text()}</style>", unsafe_allow_html=True)

COL = dict(RAShR="#1F6FEB", LMS="#E4572E", LTS="#17A398", MM="#F2A541", RANSAC="#7B4FB5", OLS="#8A94A6",
           maj="#3E7CE0", bad="#D1495B", ink="#10213A", teal="#0FA3B1")
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#E3E8F0", "axes.edgecolor": COL["ink"], "font.size": 10, "legend.frameon": False})
deg = np.degrees

st.markdown("""<div class="hero"><h1>RAShR Lab</h1>
<p>Fit a line by asking <i>which direction do pairwise chords agree on?</i> — not <i>which line has small residuals?</i></p>
<span class="tag">Repeated Angular Shorth Regression</span><span class="tag">Dharavath &amp; Srivastava</span><span class="tag">deterministic · O(n² log n)</span></div>""", unsafe_allow_html=True)

# ---------------------------------------------------------------- sidebar
sb = st.sidebar
sb.header("Data generator")
n = sb.slider("Sample size n", 40, 400, 100, 20)
kind_label = sb.selectbox("Contamination type", ["Compact high-leverage cluster", "Competing line", "Funnel majority + competing line", "Vertical outliers", "Clean (none)"])
kind = {"Compact high-leverage cluster": "compact", "Competing line": "line", "Funnel majority + competing line": "funnel",
        "Vertical outliers": "vertical", "Clean (none)": "clean"}[kind_label]
frac = sb.slider("Contamination fraction", 0.0, 0.49, 0.38, 0.01)
noise = sb.slider("Majority noise sd", 0.1, 3.0, 1.0, 0.1)
hetero = sb.checkbox("Heteroscedastic majority (sd 0.2+0.6|x|)", value=(kind == "funnel"))
cx = cy = spread = a_c = b_c = sd_c = None
if kind == "compact":
    sb.subheader("Cluster")
    cx = sb.slider("centre x", -10.0, 40.0, 15.0, 0.5); cy = sb.slider("centre y", -40.0, 40.0, -10.0, 0.5)
    spread = sb.select_slider("spread", options=[0.05, 0.1, 0.3, 0.5, 1.0, 2.0, 3.0], value=0.3)
if kind == "line":
    sb.subheader("Competing line  y = a + b·x + N(0, sd²)")
    a_c = sb.slider("a", -10.0, 10.0, 5.0, 0.25); b_c = sb.slider("b", -4.0, 4.0, -1.25, 0.05); sd_c = sb.slider("sd", 0.1, 2.0, 0.5, 0.1)
seed = sb.number_input("Random seed", 0, 10_000, 3)
reps = sb.slider("Simulation repetitions", 10, 200, 30, 10)
sb.caption("True model: y = 1 + 2x + e.  Failure ⇔ |β̂ − 2| > 0.5 (paper's criterion).")

kw = dict(noise_sd=noise, hetero=hetero)
if kind == "compact": kw.update(center=(cx, cy), spread=spread)
if kind == "line": kw.update(comp_line=(a_c, b_c), comp_sd=sd_c)

def gen(seed_):
    return simulate(n, frac, kind, np.random.default_rng(int(seed_)), **kw)

def half_width(x, y, a, b):                       # LMS criterion W(l): smallest half-width strip holding half the data
    return float(np.sort(np.abs(y - a - b * x))[len(x) // 2])

@st.cache_data(show_spinner=False)
def fit_all(x, y, seed_):
    return {m: fn(x, y, seed=int(seed_)) for m, fn in METHODS.items()} | {"OLS": ols(x, y)}

x, y, bad = gen(seed)
fits = fit_all(x, y, seed)
D = rashr(x, y, return_details=True)

tab1, tab2, tab3, tab4 = st.tabs(["① One data set", "② Geometry mode", "③ Simulation lab", "④ Reading guide"])

# ---------------------------------------------------------------- tab 1
with tab1:
    c1, c2 = st.columns([3, 2])
    with c1:
        fig, ax = plt.subplots(figsize=(7.4, 4.6))
        ax.scatter(x[~bad], y[~bad], s=14, c=COL["maj"], alpha=.8, label="majority")
        if bad.any(): ax.scatter(x[bad], y[bad], s=20, c=COL["bad"], marker="x", label="contamination")
        xs = np.array([x.min() - 1, x.max() + 1]); ax.plot(xs, 1 + 2 * xs, "k", lw=1, label="true line")
        for m, st_ in [("OLS", ":"), ("LMS", "--"), ("LTS", "--"), ("MM", "-."), ("RANSAC", "--"), ("RAShR", "-")]:
            a, b = fits[m]; ax.plot(xs, a + b * xs, st_, c=COL[m], lw=2.8 if m == "RAShR" else 1.4, label=f"{m} ({b:+.2f})")
        yl = np.percentile(y, [0, 100]); pad = .15 * np.ptp(yl); ax.set_ylim(yl[0] - pad, yl[1] + pad)
        ax.set_xlabel("x"); ax.set_ylabel("y"); ax.legend(fontsize=8, ncol=2); st.pyplot(fig, width="stretch")
    with c2:
        rows = []
        for m in ["RAShR", "LMS", "LTS", "MM", "RANSAC", "OLS"]:
            b = fits[m][1]; rows.append({"method": m, "slope β̂": round(b, 3), "|β̂−2|": round(abs(b - 2), 3), "status": "✅ ok" if abs(b - 2) <= .5 else "❌ failure"})
        st.dataframe(pd.DataFrame(rows).set_index("method"), width="stretch")
        fails = [r["method"] for r in rows if r["status"].startswith("❌") and r["method"] != "OLS"]
        st.markdown(f"<div class='small'>RAShR local half-sample size h<sub>L</sub>={D['hL']}, outer h<sub>O</sub>={D['hO']}; outer width w = {deg(D['w_out']):.1f}°.</div>", unsafe_allow_html=True)
    # --- explanation
    n_bad = int(bad.sum())
    msg = []
    if kind in ("compact", "line", "funnel") and n_bad > 0:
        wt = half_width(x, y, 1, 2)
        lines = {m: half_width(x, y, *fits[m]) for m in ["LMS", "RAShR"]}
        msg.append(f"<b>Residual view.</b> A strip around the <i>true</i> line needs half-width {wt:.2f} to capture half the data; the line LMS returned needs {lines['LMS']:.2f}. "
                   + ("LMS prefers the line that is narrower — even if it follows the contamination." if lines["LMS"] < wt - 1e-9 else "Here the true line is competitive, so LMS is not misled."))
        inw = d_pi(D["theta_i"], D["theta_hat"]) <= D["w_out"] / 2 + 1e-9
        msg.append(f"<b>Chord view.</b> {inw[~bad].mean():.0%} of majority anchors but {inw[bad].mean():.0%} of contaminated anchors have a local direction inside RAShR's outer window — "
                   "the majority agrees on one direction, the contamination does not agree with it.")
    if fails: msg.append("<b>Followed the contamination:</b> " + ", ".join(fails) + ".")
    elif n_bad: msg.append("<b>No method failed</b> in this particular draw — try a larger fraction (≈0.40–0.44) or use ③ to see failure *rates*.")
    st.markdown("<div class='why'>" + "<br>".join(msg) + "</div>", unsafe_allow_html=True)
    if frac < .3 or kind in ("clean", "vertical"):
        st.markdown("<div class='warn'><b>Honest note.</b> At low contamination or for ordinary outliers, MM-regression/RANSAC are typically <i>more accurate</i> than RAShR (paper: clean median error 0.033 vs 0.024/0.022). RAShR's advantage is specific to large, <i>coherent</i> contamination.</div>", unsafe_allow_html=True)
    if kind == "compact" and cx is not None and abs(np.degrees(np.arctan2(cy - np.median(y), cx - np.median(x))) % 180 - 30) < 12:
        st.markdown("<div class='warn'>The cluster lies close to the <b>≈30° / −150°</b> direction from the majority centre — i.e. near the extension of the majority line. Chords to the cluster then point almost the same way as majority chords and the angular separation is lost (paper, 'When does the advantage disappear?').</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------- tab 2
with tab2:
    st.markdown("**Walk through the algorithm on the current data set.** Standardize → chords from an anchor → local shorth → outer shorth → slope.")
    ia = st.slider("Anchor i", 0, n - 1, int(np.argmin(np.abs(x - np.median(x)))))
    others = np.delete(np.arange(n), ia)
    ph = D["Phi"][ia]; mid, w, det = angular_shorth(ph, h=D["hL"], return_details=True)
    g1, g2 = st.columns(2)
    with g1:
        fig, ax = plt.subplots(figsize=(6, 4.2))
        for j in others: ax.plot([x[ia], x[j]], [y[ia], y[j]], c=COL["bad"] if bad[j] else COL["maj"], alpha=.22, lw=.8)
        ax.scatter(x[~bad], y[~bad], s=10, c=COL["maj"]); ax.scatter(x[bad], y[bad], s=14, c=COL["bad"], marker="x")
        ax.scatter(x[ia], y[ia], s=110, c="gold", edgecolor=COL["ink"], zorder=5)
        ax.set_title(f"Chords from anchor {ia}"); ax.set_xlabel("x"); ax.set_ylabel("y"); st.pyplot(fig, width="stretch")
    with g2:
        fig, ax = plt.subplots(figsize=(6, 4.2))
        bins = np.arange(0, 181, 3)
        ax.hist(deg(ph[~bad[others]]), bins=bins, color=COL["maj"], alpha=.85, label="chords to majority")
        ax.hist(deg(ph[bad[others]]), bins=bins, color=COL["bad"], alpha=.85, label="chords to contamination")
        lo, hi = det["extended"][det["r"]], det["extended"][det["r"] + det["h"] - 1]
        for a_, b_ in ([(lo, hi)] if hi <= PI else [(lo, PI), (0, hi - PI)]): ax.axvspan(deg(a_), deg(b_), color=COL["teal"], alpha=.18)
        ax.axvline(deg(mid), c=COL["ink"], lw=2, ls="--", label=f"θᵢ = {deg(mid):.1f}°  (wᵢ = {deg(w):.1f}°)")
        ax.set_title("Directions Φᵢ and the shortest half-window"); ax.set_xlabel("chord direction (deg, mod 180°)"); ax.legend(fontsize=8); st.pyplot(fig, width="stretch")
    g3, g4 = st.columns(2)
    theta_star = np.arctan(2 * D["sx"] / D["sy"])
    with g3:
        fig, ax = plt.subplots(figsize=(6, 4.2))
        sd_ = lambda t: deg((t - theta_star + PI / 2) % PI - PI / 2)
        ax.scatter(sd_(D["theta_i"])[~bad], deg(D["w_i"])[~bad], c=COL["maj"], s=18, label="majority anchors")
        if bad.any(): ax.scatter(sd_(D["theta_i"])[bad], deg(D["w_i"])[bad], c=COL["bad"], marker="x", s=26, label="contaminated anchors")
        ax.set_xlabel("θᵢ − θ* (deg)"); ax.set_ylabel("local width wᵢ (deg)"); ax.set_title("All local directions and widths"); ax.legend(fontsize=8); st.pyplot(fig, width="stretch")
    with g4:
        fig, ax = plt.subplots(figsize=(6, 4.2)); order = np.argsort(D["theta_i"])
        ax.scatter(range(n), deg(D["theta_i"])[order], c=[COL["bad"] if bad[o] else COL["maj"] for o in order], s=14)
        ax.axhline(deg(D["theta_hat"]), c=COL["RAShR"], lw=2.4, label=f"θ̂ = {deg(D['theta_hat']):.1f}°")
        ax.axhspan(deg(D["theta_hat"]) - deg(D["w_out"]) / 2, deg(D["theta_hat"]) + deg(D["w_out"]) / 2, color=COL["teal"], alpha=.2, label="outer shortest-half window")
        ax.set_title("Outer (repeated) angular shorth"); ax.set_xlabel("anchors sorted by θᵢ"); ax.set_ylabel("θᵢ (deg)"); ax.legend(fontsize=8); st.pyplot(fig, width="stretch")
    st.markdown(f"""<div class='card eq'>θ̂ = {deg(D['theta_hat']):.2f}° &nbsp;→&nbsp; tan θ̂ = {np.tan(D['theta_hat'] if D['theta_hat']<=PI/2 else D['theta_hat']-PI):.3f}
&nbsp;→&nbsp; β̂ = (s<sub>y</sub>/s<sub>x</sub>)·tan θ̂ = ({D['sy']:.3f}/{D['sx']:.3f})·tan θ̂ = <b>{D['beta']:.3f}</b> &nbsp;→&nbsp; α̂ = med(yᵢ − β̂xᵢ) = <b>{D['alpha']:.3f}</b></div>""", unsafe_allow_html=True)
    st.caption("Under the paper's separation conditions (L) and (O) moving the contaminated points does not change θ̂ (Theorem 1). Try dragging the cluster centre x in the sidebar: β̂ stays fixed once the cluster is well separated. The intercept (a median over all points) can still shift.")

# ---------------------------------------------------------------- tab 3
with tab3:
    st.markdown(f"Repeat the experiment **{reps}×** with the sidebar settings (seed {int(seed)} + replicate index). Failure ⇔ |β̂−2|>0.5.")
    run = st.button("▶ Run simulation", type="primary")
    @st.cache_data(show_spinner=False)
    def run_sim(params, reps_):
        out = {m: [] for m in METHODS}
        for r in range(reps_):
            xx, yy, _ = simulate(params["n"], params["frac"], params["kind"], np.random.default_rng(params["seed"] + r), **params["kw"])
            for m, fn in METHODS.items(): out[m].append(fn(xx, yy, seed=r)[1])
        return {m: np.array(v) for m, v in out.items()}
    if run:
        params = dict(n=n, frac=frac, kind=kind, seed=int(seed), kw=kw)
        bar = st.progress(0, text="simulating…")
        res = run_sim(params, reps); bar.empty()
        rate = {m: float(np.mean(np.abs(v - 2) > .5)) for m, v in res.items()}
        cols = st.columns(5)
        for c, m in zip(cols, METHODS): c.metric(f"{m} failure rate", f"{rate[m]:.0%}", f"median |err| {np.median(np.abs(res[m]-2)):.3f}", delta_color="off")
        fig, axs = plt.subplots(1, 2, figsize=(12, 4))
        axs[0].bar(list(rate), list(rate.values()), color=[COL[m] for m in rate]); axs[0].set_ylim(0, 1.05); axs[0].set_title("Failure rate")
        bp = axs[1].boxplot([np.clip(res[m], -4, 6) for m in METHODS], patch_artist=True, showfliers=True)
        axs[1].set_xticklabels(list(METHODS))
        for p, m in zip(bp["boxes"], METHODS): p.set_facecolor(COL[m]); p.set_alpha(.7)
        axs[1].axhline(2, c="k", lw=1); axs[1].axhspan(1.5, 2.5, color="#0FA3B1", alpha=.1); axs[1].set_title("Distribution of slope estimates (clipped to [-4, 6]); band = success region")
        st.pyplot(fig, width="stretch")
        best = min(rate, key=rate.get)
        txt = f"Lowest failure rate here: <b>{best}</b> ({rate[best]:.0%}). "
        if rate["RAShR"] <= min(rate.values()) + 1e-9 and frac >= .35 and kind in ("compact", "line", "funnel"):
            txt += "This is the regime (~35–46% coherent contamination) the paper identifies as RAShR's sweet spot."
        elif frac < .3 or kind in ("clean", "vertical"):
            txt += "At low contamination the methods are all fine; MM/RANSAC are usually more <i>efficient</i> (smaller error), which the median errors above show."
        else:
            txt += "Check the geometry: is the cluster near the line's extension (≈30°) or diffuse? Then RAShR loses its edge (see ④)."
        st.markdown(f"<div class='why'>{txt}</div>", unsafe_allow_html=True)
        st.download_button("Download slopes (CSV)", pd.DataFrame(res).to_csv(index=False), "rashr_simulation_slopes.csv")
    else:
        st.info("Set the generator in the sidebar and press **Run simulation**. Defaults reproduce the paper's compact-cluster scenario at 38%.")
    with st.expander("Paper's reported failure rates (for comparison)"):
        rows = []
        for sc in ["compact", "line", "funnel"]:
            for f, d in PAPER[sc].items():
                rows.append({"scenario": sc, "fraction": f, **{k: (f"{v:.0%}" if v is not None else "—") for k, v in d.items()}})
        st.dataframe(pd.DataFrame(rows).fillna("—"), width="stretch", hide_index=True)
        st.caption("Compact cluster @44%: RAShR succeeds in 40% of samples, every competitor fails in ≥97%; @46% all methods fail. Our re-implementation matches the pattern, not every digit (tuning constants such as the RANSAC threshold are not fully specified).")

# ---------------------------------------------------------------- tab 4
with tab4:
    st.markdown("""
<div class="card"><h4>The idea in one line</h4>Instead of asking <i>which line gives small residuals?</i>, RAShR asks <i>which direction receives the strongest agreement from pairwise chords?</i></div>
<div class="card"><h4>Why LMS/LTS/MM can be pulled to a cluster</h4>A compact cluster holding fraction ε of the data lets a line through it capture a lot of mass in a very narrow strip. As ε→½ the strip needed to hold half the mass shrinks to zero (paper, Proposition 3 — proven for population LMS only; for LTS/MM this app and the paper only show it empirically).</div>
<div class="card"><h4>Why RAShR resists</h4>Chords from majority anchors to majority points concentrate near one direction. Chords to the cluster are seen from many different places, so their directions spread out. The local shorth picks the concentrated half, the outer shorth repeats this across anchors. When the two groups are angularly separated, the contaminated points do not influence θ̂ at all (Theorem 1).</div>
<div class="card"><h4>Where it does <u>not</u> help</h4>• Clean or lightly contaminated data: MM/RANSAC are more efficient.<br>• Cluster near the majority line's extension (≈30°, −150° ≡ 30° on the projective circle): angular separation is lost.<br>• Diffuse clusters (spread 1–3) or arbitrary outliers: the advantage disappears.<br>• Compact cluster at ≈46%: all methods fail.<br>• Not fully affine equivariant (only translation and positive scaling).</div>
""", unsafe_allow_html=True)
