"""Write the small CSV / TeX data files that the Beamer deck plots natively with TikZ/pgfplots."""
import json, numpy as np, csv, os
import rashr_core as rc
OUT = "beamer/data/"; os.makedirs(OUT, exist_ok=True)
R = json.load(open("results/simulation_results.json")); M = ["RAShR", "LMS", "LTS", "MM", "RANSAC"]
def wr(name, header, rows):
    with open(OUT + name, "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

x, y, bad = rc.fig1_example(3); d = rc.rashr(x, y, return_details=True)
wr("fig1_majority.csv", ["x", "y"], [(round(a, 3), round(b, 3)) for a, b, g in zip(x, y, bad) if not g])
wr("fig1_cluster.csv", ["x", "y"], [(round(a, 3), round(b, 3)) for a, b, g in zip(x, y, bad) if g])
wr("fig1_slopes.csv", ["method", "alpha", "beta"], [(m, *[round(v, 3) for v in f(x, y)]) for m, f in [("OLS", rc.ols), ("LMS", rc.lms), ("MM", rc.mm), ("RAShR", rc.rashr)]])
# standardized data + chords from one majority anchor
u, v = d["u"], d["v"]; i0 = int(np.argmin(np.abs(u - np.median(u[~bad])) + np.abs(v - np.median(v[~bad])) + 99 * bad))
wr("std_majority.csv", ["u", "v"], [(round(a, 4), round(b, 4)) for a, b, g in zip(u, v, bad) if not g])
wr("std_cluster.csv", ["u", "v"], [(round(a, 4), round(b, 4)) for a, b, g in zip(u, v, bad) if g])
phi = np.degrees(np.mod(np.arctan2(v - v[i0], u - u[i0]), np.pi)); mask = np.arange(len(u)) != i0
wr("anchor_chords.csv", ["phi", "bad"], [(round(p, 2), int(g)) for p, g in zip(phi[mask], bad[mask])])
mid, w, det = rc.angular_shorth(np.radians(phi[mask]), return_details=True)
ext = np.degrees(det["extended"]); r, h = det["r"], det["h"]
with open(OUT + "anchor_info.tex", "w") as f:
    f.write(f"\\def\\anchoru{{{u[i0]:.4f}}}\\def\\anchorv{{{v[i0]:.4f}}}\\def\\anchortheta{{{np.degrees(mid):.1f}}}\\def\\anchorw{{{np.degrees(w):.1f}}}\\def\\anchorlo{{{ext[r]:.2f}}}\\def\\anchorhi{{{ext[r+h-1]:.2f}}}\n")
    f.write(f"\\def\\sxval{{{d['sx']:.3f}}}\\def\\syval{{{d['sy']:.3f}}}\\def\\thetahat{{{np.degrees(d['theta_hat']):.1f}}}\\def\\betahat{{{d['beta']:.3f}}}\\def\\alphahat{{{d['alpha']:.3f}}}\n")
wr("local_dirs.csv", ["i", "theta", "w", "bad"], [(i, round(np.degrees(t), 2), round(np.degrees(ww), 2), int(g)) for i, (t, ww, g) in enumerate(zip(d["theta_i"], d["w_i"], bad))])
# a 12-angle shorth example (deterministic)
rng = np.random.default_rng(5); ang = np.sort(np.concatenate([rng.normal(72, 6, 7), rng.uniform(0, 180, 5)]) % 180)
mid, w, det = rc.angular_shorth(np.radians(ang), return_details=True)
wr("shorth_angles.csv", ["a"], [(round(a, 1),) for a in np.degrees(det["sorted"])])
wr("shorth_widths.csv", ["r", "other", "best"], [(k + 1, "nan" if k == det["r"] else round(np.degrees(wd), 1), round(np.degrees(wd), 1) if k == det["r"] else "nan") for k, wd in enumerate(det["widths"])])
ex = np.degrees(det["extended"])
with open(OUT + "shorth_info.tex", "w") as f:
    f.write(f"\\def\\shm{{{len(ang)}}}\\def\\shh{{{det['h']}}}\\def\\shr{{{det['r']+1}}}\\def\\shmid{{{np.degrees(mid):.1f}}}\\def\\shw{{{np.degrees(w):.1f}}}\\def\\shlo{{{ex[det['r']]:.2f}}}\\def\\shhi{{{ex[det['r']+det['h']-1]:.2f}}}\n")
# failure curves (our re-implementation) and the paper's reported points
for k in ("compact", "line", "funnel"):
    wr(f"fail_{k}.csv", ["f"] + M, [(float(fr), *[R[k][fr][mm]["fail"] * 100 for mm in M]) for fr in sorted(R[k], key=float)])
wr("move.csv", ["cx"] + M, list(zip(*[R["move"][c] for c in ["cx"] + M])))
wr("spread.csv", ["spread"] + M, [(s, *[R["spread"][s][mm]["fail"] * 100 for mm in M]) for s in R["spread"]])
dirs = sorted({int(k.split("_")[1]) for k in R["directions"]})
for dist in (15, 30):
    wr(f"dir_{dist}.csv", ["dir"] + M, [(dd, *[R["directions"][f"{dist}_{dd}"][mm] * 100 for mm in M]) for dd in dirs])
wr("standard.csv", ["setting"] + M, [(s, *[round(R["standard"][s][mm]["med_abs_err"], 3) for mm in M]) for s in R["standard"]])
print("ok", sorted(os.listdir(OUT)))

# ---------------- TikZ snippets (macros \pdot{deg}{colour} and friends are defined in the deck) -------------
sl = {m: f(x, y) for m, f in [("OLS", rc.ols), ("LMS", rc.lms), ("MM", rc.mm), ("RAShR", rc.rashr)]}
with open(OUT + "fig1_info.tex", "w") as f:
    for m, (a, b) in sl.items(): f.write(f"\\def\\a{m}{{{a:.4f}}}\\def\\b{m}{{{b:.4f}}}\n")
# segments from the anchor to every other point (nan rows break the polyline for pgfplots)
with open(OUT + "anchor_segments_maj.csv", "w") as f, open(OUT + "anchor_segments_bad.csv", "w") as g:
    f.write("u,v\n"); g.write("u,v\n")
    for j in range(len(u)):
        if j == i0: continue
        h_ = g if bad[j] else f
        h_.write(f"{u[i0]:.4f},{v[i0]:.4f}\n{u[j]:.4f},{v[j]:.4f}\nnan,nan\n")
# anchor circle
phi_all = phi[mask]; badm = bad[mask]
with open(OUT + "tikz_anchor_circle.tex", "w") as f:
    for p, g_ in zip(phi_all, badm): f.write(f"\\pdot{{{p:.2f}}}{{{'cbad' if g_ else 'cmaj'}}}\n")
with open(OUT + "tikz_local_circle.tex", "w") as f:
    for t_, g_ in zip(np.degrees(d["theta_i"]), bad): f.write(f"\\pdot{{{t_:.2f}}}{{{'cbad' if g_ else 'cmaj'}}}\n")
mid2, w2, det2 = rc.angular_shorth(d["theta_i"], return_details=True); e2 = np.degrees(det2["extended"])
with open(OUT + "outer_info.tex", "w") as f:
    f.write(f"\\def\\outerlo{{{e2[det2['r']]:.2f}}}\\def\\outerhi{{{e2[det2['r']+det2['h']-1]:.2f}}}\\def\\outertheta{{{np.degrees(mid2):.1f}}}\\def\\outerw{{{np.degrees(w2):.1f}}}\n")
# shorth number-line (0..360 with copies)
with open(OUT + "tikz_shorth_line.tex", "w") as f:
    for a_ in np.degrees(det["sorted"]):
        f.write(f"\\fill[cmaj] ({a_/30:.4f},0) circle (2.2pt);\n\\fill[cext] ({(a_+180)/30:.4f},0) circle (2.2pt);\n")
print("snippets ok")

# ---------------- table rows for the deck ----------------
names = {"clean": "clean", "vertical20": "20\\% vertical", "leverage10": "10\\% bad leverage", "line20": "20\\% competing line"}
with open(OUT + "standard_rows.tex", "w") as f:
    for s_, nm_ in names.items():
        vals = [R["standard"][s_][mm]["med_abs_err"] for mm in M]; best = min(vals)
        f.write(nm_ + " & " + " & ".join((f"\\textbf{{{v:.3f}}}" if v == best else f"{v:.3f}") for v in vals) + " \\\\\n")
with open(OUT + "spread_rows.tex", "w") as f:
    for s_ in R["spread"]:
        f.write(f"{s_} & " + " & ".join(f"{R['spread'][s_][mm]['fail']*100:.0f}" for mm in M) + " \\\\\n")
for fn in ("standard_rows.tex", "spread_rows.tex", "ransac_rows.tex"):
    pass
print("tables ok")

S_ = json.load(open("results/ransac_sensitivity.json"))
with open(OUT + "ransac_rows.tex", "w") as f:
    for name, row in S_["rows"].items():
        nm = name.replace("%", "\\%")
        f.write((f"\\midrule\n" if name.startswith("RAShR") else "") + f"{nm} & " + " & ".join(f"{v:.0f}" for v in row) + " \\\\\n")
print("ransac rows ok")

for fn in ("standard_rows.tex", "spread_rows.tex", "ransac_rows.tex"):
    s = open(OUT + fn).read().rstrip("\n"); open(OUT + fn, "w").write(s)

def wrap(fn, spec, head, rowsfile):
    body = open(OUT + rowsfile).read()
    open(OUT + fn, "w").write("\\begin{tabular}{" + spec + "}\n\\toprule\n" + head + "\\midrule\n" + body + "\n\\bottomrule\n\\end{tabular}\n")
wrap("standard_table.tex", "@{}lccccc@{}", "setting & RAShR & LMS & LTS & MM & RANSAC \\\\\n", "standard_rows.tex")
wrap("spread_table.tex", "@{}lccccc@{}", "spread & RAShR & LMS & LTS & MM & RANSAC \\\\\n", "spread_rows.tex")
hd = "& \\multicolumn{5}{c}{compact cluster, $f=$} & line & \\multicolumn{2}{c}{funnel}\\\\\n\\cmidrule(lr){2-6}\\cmidrule(lr){7-7}\\cmidrule(lr){8-9}\nresidual threshold & 30\\% & 36\\% & 40\\% & 44\\% & 46\\% & 46\\% & 40\\% & 44\\%\\\\\n"
wrap("ransac_table.tex", "@{}l ccccc c cc@{}", hd, "ransac_rows.tex")
