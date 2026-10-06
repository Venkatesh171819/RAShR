"""How much does RANSAC's (unspecified) residual threshold matter?  Failure rate (%), 60 replications, deterministic seeds.
The paper only says 'MAD-based residual threshold'; we report the scikit-learn style default MAD(y) used in the main
simulations and four alternatives, one of which (2.5 = 2.5 x the true noise sd) uses oracle knowledge of the noise scale."""
import json, numpy as np, rashr_core as rc
def mad(y): return np.median(np.abs(y - np.median(y)))
T = {"MAD(y) [default]": mad, "0.5 MAD(y)": lambda y: 0.5 * mad(y), "2.0 (oracle)": lambda y: 2.0, "2.5 (oracle)": lambda y: 2.5, "4.0 (oracle)": lambda y: 4.0}
S = [("compact", 0.30), ("compact", 0.36), ("compact", 0.40), ("compact", 0.44), ("compact", 0.46), ("line", 0.46), ("funnel", 0.40), ("funnel", 0.44)]
out = {"scenarios": [f"{k}@{int(f*100)}" for k, f in S], "rows": {}}
for name, fn in T.items():
    row = []
    for k, f in S:
        fails = 0
        for s in range(60):
            x, y, _ = rc.simulate(100, f, k, np.random.default_rng(1000 * int(round(f * 100)) + s))
            fails += abs(rc.ransac(x, y, seed=s, threshold=float(fn(y)))[1] - 2) > 0.5
        row.append(round(fails / 60 * 100, 1))
    out["rows"][name] = row
rr = []
for k, f in S:
    fails = 0
    for s in range(60):
        x, y, _ = rc.simulate(100, f, k, np.random.default_rng(1000 * int(round(f * 100)) + s)); fails += abs(rc.rashr(x, y)[1] - 2) > 0.5
    rr.append(round(fails / 60 * 100, 1))
out["rows"]["RAShR (same samples)"] = rr
json.dump(out, open("results/ransac_sensitivity.json", "w"), indent=1)
for k, v in out["rows"].items(): print(f"{k:22s}", v)
