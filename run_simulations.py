"""Reproduce the paper's Section 5 experiments. Writes results/*.json.
Usage: python run_simulations.py [reps]   (paper: 60 replications per point)"""
import json, sys, time, numpy as np
from concurrent.futures import ProcessPoolExecutor
from rashr_core import METHODS, simulate, rashr

REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 60
FRACS = [0.20, 0.25, 0.30, 0.35, 0.36, 0.38, 0.40, 0.42, 0.44, 0.46]
NAMES = list(METHODS)

def one(args):
    kind, frac, rep, kw = args
    rng = np.random.default_rng(hash((kind, round(frac*1000), rep)) % (2**32) if False else
                                (abs(rep) * 1_000_003 + int(frac*1000) * 101 + {"compact":1,"line":2,"funnel":3,"clean":4,"vertical":5,"leverage_pts":6}[kind]))
    x, y, _ = simulate(100, frac, kind, rng, **kw)
    return {m: METHODS[m](x, y, seed=rep)[1] for m in NAMES}

def sweep(kind, fracs, reps, kw=None, pool=None):
    kw = kw or {}
    out = {}
    for f in fracs:
        res = list(pool.map(one, [(kind, f, r, kw) for r in range(reps)]))
        b = {m: np.array([r[m] for r in res]) for m in NAMES}
        out[f"{f:.2f}"] = {m: dict(fail=float(np.mean(np.abs(b[m]-2) > 0.5)),
                                   med_abs_err=float(np.median(np.abs(b[m]-2))),
                                   slopes=[round(float(s), 4) for s in b[m]]) for m in NAMES}
    return out

if __name__ == "__main__":
    t0 = time.time()
    R = {"reps": REPS, "fracs": FRACS}
    with ProcessPoolExecutor() as pool:
        for kind in ["compact", "line", "funnel"]:
            R[kind] = sweep(kind, FRACS, REPS, pool=pool)
            print(kind, "done", round(time.time()-t0), "s", flush=True)
        # standard settings (median |beta-2|); more reps for stable medians
        std = {}
        for name, kind, f in [("clean","clean",0.0),("vertical20","vertical",0.20),("leverage10","leverage_pts",0.10),("line20","line",0.20)]:
            std[name] = sweep(kind, [f], max(REPS, 100), pool=pool)[f"{f:.2f}"]
        R["standard"] = std
        # compactness at 40%/38% cluster
        comp = {}
        for sp in [0.05, 0.3, 1.0, 3.0]:
            comp[str(sp)] = sweep("compact", [0.38], REPS, kw=dict(spread=sp), pool=pool)["0.38"]
        R["spread"] = comp
    # horizontal cluster-move experiment (Fig 3b): majority fixed, 36 pts moved
    rng = np.random.default_rng(3)
    xm = rng.uniform(-5, 5, 64); ym = 1 + 2*xm + rng.normal(0, 1, 64)
    cl_x = rng.normal(0, 0.3, 36); cl_y = rng.normal(0, 0.3, 36)
    move = {m: [] for m in NAMES}; cxs = list(np.arange(8, 40.5, 0.5))
    for cx in cxs:
        x = np.concatenate([xm, cl_x + cx]); y = np.concatenate([ym, cl_y - 10])
        for m in NAMES: move[m].append(float(METHODS[m](x, y, seed=0)[1]))
    R["move"] = dict(cx=[float(c) for c in cxs], **move)
    # direction experiment (cluster placed at angle ang, distance d from majority centre)
    dirs = {}
    for d in [15, 30]:
        for ang in range(0, 360, 30):
            fails = []
            for r in range(30):
                rng = np.random.default_rng(10_000 + r)
                x, y, bad = simulate(100, 0.38, "clean", rng)
                k = 38; idx = rng.choice(100, k, replace=False)
                cx0, cy0 = np.median(x), np.median(y)
                # direction measured in the (x, y) plane of the true line: 30 deg ~ along y=2x? use raw angle
                x[idx] = rng.normal(cx0 + d*np.cos(np.radians(ang)), 0.3, k)
                y[idx] = rng.normal(cy0 + d*np.sin(np.radians(ang)), 0.3, k)
                fails.append({m: abs(METHODS[m](x, y, seed=r)[1]-2) > 0.5 for m in NAMES})
            dirs[f"{d}_{ang}"] = {m: float(np.mean([f[m] for f in fails])) for m in NAMES}
    R["directions"] = dirs
    json.dump(R, open("results/simulation_results.json", "w"))
    print("total", round(time.time()-t0), "s")
