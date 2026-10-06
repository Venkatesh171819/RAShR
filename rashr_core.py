"""
rashr_core.py -- Repeated Angular Shorth Regression (RAShR) and competitors.

Reference: Dharavath & Srivastava, "Robust Linear Regression via the Repeated
Angular Shorth" (NIT Warangal).  Equation numbers below refer to that paper.

Conventions used everywhere in this project
-------------------------------------------
* Directions of unoriented lines live on the projective circle  [0, pi).
* d_pi(a, b) = min(|a-b|, pi-|a-b|)                                   (Eq. 4)
* ASh(A) = midpoint of the shortest arc holding >= h = ceil(m/2) angles (Eq. 5)
* ties -> window with the smallest left endpoint (deterministic)
"""
from __future__ import annotations

import numpy as np

PI = np.pi
MAD_CONST = 1.4826


# --------------------------------------------------------------------------
# 1. Robust standardization (Eq. 2)
# --------------------------------------------------------------------------
def robust_scale(z: np.ndarray) -> float:
    """1.4826 * MAD, falling back to the standard deviation if MAD == 0."""
    z = np.asarray(z, float)
    s = MAD_CONST * np.median(np.abs(z - np.median(z)))
    if s == 0:
        s = float(np.std(z))
    return float(s)


def standardize(x, y):
    """Return (u, v, med_x, med_y, s_x, s_y)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    mx, my = np.median(x), np.median(y)
    sx, sy = robust_scale(x), robust_scale(y)
    return (x - mx) / sx, (y - my) / sy, mx, my, sx, sy


# --------------------------------------------------------------------------
# 2. Projective geometry (Eqs. 3-4)
# --------------------------------------------------------------------------
def chord_angle(du, dv):
    """phi = atan2(dv, du) mod pi   -> value in [0, pi)."""
    return np.mod(np.arctan2(dv, du), PI)


def d_pi(a, b):
    """Angular distance on the projective circle."""
    d = np.abs(np.asarray(a) - np.asarray(b))
    return np.minimum(d, PI - d)


# --------------------------------------------------------------------------
# 3. The angular shorth operator (Eq. 5)
# --------------------------------------------------------------------------
def angular_shorth(angles, h=None, return_details=False):
    """
    ASh_h(A): midpoint of the shortest arc of the projective circle that
    contains at least h of the angles.

    Algorithm (as in the paper): sort, append a copy shifted by pi, slide a
    window of h consecutive sorted values, take the narrowest.  Ties are
    broken in favour of the window with the smallest left endpoint.

    Returns (midpoint, width).  With return_details=True also returns the
    sorted/extended array, all window widths and the winning index.
    """
    a = np.sort(np.mod(np.asarray(angles, float), PI))
    m = a.size
    if h is None:
        h = int(np.ceil(m / 2))
    h = max(1, min(h, m))
    ext = np.concatenate([a, a + PI])
    widths = ext[h - 1: h - 1 + m] - ext[:m]          # one window per left end
    r = int(np.argmin(widths))                         # argmin = first minimum
    mid = (0.5 * (ext[r] + ext[r + h - 1])) % PI
    w = float(widths[r])
    if return_details:
        return mid, w, dict(sorted=a, extended=ext, widths=widths, r=r, h=h)
    return mid, w


def _ash_rows(angle_matrix, h):
    """Vectorised ASh applied to every row of a matrix (rows already sorted
    internally here).  Returns (midpoints, widths)."""
    a = np.sort(np.mod(angle_matrix, PI), axis=1)
    m = a.shape[1]
    ext = np.concatenate([a, a + PI], axis=1)
    widths = ext[:, h - 1: h - 1 + m] - ext[:, :m]
    r = np.argmin(widths, axis=1)                      # first minimum per row
    idx = np.arange(a.shape[0])
    left = ext[idx, r]
    right = ext[idx, r + h - 1]
    return (0.5 * (left + right)) % PI, widths[idx, r]


# --------------------------------------------------------------------------
# 4. RAShR (Algorithm 1)
# --------------------------------------------------------------------------
def rashr(x, y, q=0.5, return_details=False):
    """
    Repeated Angular Shorth Regression.

    Returns (alpha, beta) or, with return_details=True, a dict containing all
    intermediate objects (standardized data, local directions theta_i, local
    widths w_i, outer direction theta_hat, outer width, scales).
    """
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = x.size
    u, v, mx, my, sx, sy = standardize(x, y)

    # all pairwise chord directions (n x n), diagonal removed -> n x (n-1)
    du = u[None, :] - u[:, None]
    dv = v[None, :] - v[:, None]
    phi = chord_angle(du, dv)                          # Eq. 3
    mask = ~np.eye(n, dtype=bool)
    Phi = phi[mask].reshape(n, n - 1)

    hL = int(np.ceil(q * (n - 1)))
    hO = int(np.ceil(q * n))

    theta_i, w_i = _ash_rows(Phi, hL)                  # local stage  (Eqs. 6-7)
    theta_hat, w_out = angular_shorth(theta_i, h=hO)   # outer stage  (Eq. 8)

    # back to (-pi/2, pi/2]  and original scale  (Eq. 9)
    th = theta_hat if theta_hat <= PI / 2 else theta_hat - PI
    beta = (sy / sx) * np.tan(th)
    alpha = float(np.median(y - beta * x))             # Eq. 10

    if not return_details:
        return alpha, float(beta)
    return dict(alpha=alpha, beta=float(beta), u=u, v=v, mx=mx, my=my, sx=sx,
                sy=sy, Phi=Phi, theta_i=theta_i, w_i=w_i,
                theta_hat=float(theta_hat), w_out=float(w_out), hL=hL, hO=hO)


# --------------------------------------------------------------------------
# 5. Competing estimators (kept simple and fixed across scenarios; see README
#    for the places where the paper leaves details unspecified)
# --------------------------------------------------------------------------
def _all_pairs(n):
    i, j = np.triu_indices(n, 1)
    return i, j


def _elemental_lines(x, y):
    """All lines through pairs of points with distinct x."""
    i, j = _all_pairs(x.size)
    dx = x[j] - x[i]
    ok = np.abs(dx) > 1e-12
    i, j, dx = i[ok], j[ok], dx[ok]
    b = (y[j] - y[i]) / dx
    a = y[i] - b * x[i]
    return a, b


def ols(x, y):
    X = np.column_stack([np.ones_like(x), x])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(coef[0]), float(coef[1])


def lms(x, y):
    """Least Median of Squares via exhaustive elemental search (O(n^3))."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    n = x.size
    a, b = _elemental_lines(x, y)
    h = n // 2 + 1                                     # median order statistic
    best, best_val = (0.0, 0.0), np.inf
    chunk = 2000
    for s in range(0, a.size, chunk):
        r2 = (y[None, :] - a[s:s+chunk, None] - b[s:s+chunk, None] * x[None, :]) ** 2
        crit = np.partition(r2, h - 1, axis=1)[:, h - 1]
        k = int(np.argmin(crit))
        if crit[k] < best_val:
            best_val, best = crit[k], (a[s + k], b[s + k])
    return float(best[0]), float(best[1])


def lts(x, y, n_starts=10, n_csteps=20, return_resid_scale=False):
    """Least Trimmed Squares: ten best elemental fits + 20 concentration steps."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    n = x.size
    h = (n + 3) // 2
    a, b = _elemental_lines(x, y)
    # trimmed objective of each elemental fit
    crit = np.empty(a.size)
    chunk = 2000
    for s in range(0, a.size, chunk):
        r2 = (y[None, :] - a[s:s+chunk, None] - b[s:s+chunk, None] * x[None, :]) ** 2
        crit[s:s+chunk] = np.sort(r2, axis=1)[:, :h].sum(axis=1)
    starts = np.argsort(crit)[:n_starts]
    best, best_val = None, np.inf
    for k in starts:
        aa, bb = a[k], b[k]
        for _ in range(n_csteps):
            r2 = (y - aa - bb * x) ** 2
            idx = np.argsort(r2)[:h]
            aa, bb = ols(x[idx], y[idx])
        val = np.sort((y - aa - bb * x) ** 2)[:h].sum()
        if val < best_val:
            best_val, best = val, (aa, bb)
    return float(best[0]), float(best[1])


def mm(x, y, c=4.685, max_iter=100, tol=1e-10):
    """MM-regression: LTS start, MAD scale of its residuals, Tukey bisquare IRLS."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    a, b = lts(x, y)
    r = y - a - b * x
    s = MAD_CONST * np.median(np.abs(r - np.median(r)))
    s = max(s, 1e-8)
    X = np.column_stack([np.ones_like(x), x])
    coef = np.array([a, b])
    for _ in range(max_iter):
        u = (y - X @ coef) / s
        w = np.where(np.abs(u) < c, (1 - (u / c) ** 2) ** 2, 0.0)
        if w.sum() < 2:
            break
        W = X * w[:, None]
        new = np.linalg.solve(X.T @ W, W.T @ y)
        if np.max(np.abs(new - coef)) < tol:
            coef = new
            break
        coef = new
    return float(coef[0]), float(coef[1])


def ransac(x, y, n_trials=1000, seed=0, threshold=None):
    """RANSAC: 2-point samples, MAD-based threshold, 1000 trials, final LS refit
    on the consensus set.  threshold defaults to 1.4826 * MAD(residuals of OLS...)
    -- here simply MAD(y) as in the common default, see README."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    n = x.size
    if threshold is None:
        threshold = np.median(np.abs(y - np.median(y)))
    rng = np.random.default_rng(seed)
    i = rng.integers(0, n, n_trials)
    j = rng.integers(0, n, n_trials)
    ok = np.abs(x[i] - x[j]) > 1e-12
    i, j = i[ok], j[ok]
    b = (y[j] - y[i]) / (x[j] - x[i])
    a = y[i] - b * x[i]
    res = np.abs(y[None, :] - a[:, None] - b[:, None] * x[None, :])
    inl = res <= threshold
    cnt = inl.sum(axis=1)
    best = int(np.argmax(cnt))
    mask = inl[best]
    if mask.sum() >= 2 and np.ptp(x[mask]) > 0:
        return ols(x[mask], y[mask])
    return float(a[best]), float(b[best])


METHODS = {
    "RAShR": lambda x, y, seed=0: rashr(x, y),
    "LMS": lambda x, y, seed=0: lms(x, y),
    "LTS": lambda x, y, seed=0: lts(x, y),
    "MM": lambda x, y, seed=0: mm(x, y),
    "RANSAC": lambda x, y, seed=0: ransac(x, y, seed=seed),
}


# --------------------------------------------------------------------------
# 6. Data generation (Section 5 of the paper)
# --------------------------------------------------------------------------
def simulate(n=100, frac=0.0, kind="clean", rng=None, center=(15.0, -10.0),
             spread=0.3, comp_line=(5.0, -1.25), comp_sd=0.5, noise_sd=1.0,
             hetero=False):
    """
    Generate one data set.  Majority: x~U[-5,5], y = 1 + 2x + e.
    kind in {'clean','compact','line','funnel','vertical','leverage_pts'}
      compact : cluster at `center`, Gaussian spread `spread`
      line    : competing line y = a + b x + N(0, comp_sd^2) over same x-range
      funnel  : heteroscedastic majority (sd 0.2+0.6|x|) + competing line (sd 0.3)
      vertical: replaced points get large vertical errors
    Returns x, y, is_contaminated (bool mask).
    """
    rng = np.random.default_rng() if rng is None else rng
    x = rng.uniform(-5, 5, n)
    if kind == "funnel" or hetero:
        e = rng.normal(0, 1, n) * (0.2 + 0.6 * np.abs(x))
    else:
        e = rng.normal(0, noise_sd, n)
    y = 1 + 2 * x + e
    k = int(round(frac * n))
    bad = np.zeros(n, bool)
    if k > 0 and kind != "clean":
        idx = rng.choice(n, k, replace=False)
        bad[idx] = True
        if kind == "compact":
            x[idx] = rng.normal(center[0], spread, k)
            y[idx] = rng.normal(center[1], spread, k)
        elif kind in ("line", "funnel"):
            sd = 0.3 if kind == "funnel" else comp_sd
            x[idx] = rng.uniform(-5, 5, k)
            y[idx] = comp_line[0] + comp_line[1] * x[idx] + rng.normal(0, sd, k)
        elif kind == "vertical":
            y[idx] = y[idx] + rng.normal(0, 10, k)
        elif kind == "leverage_pts":
            x[idx] = rng.normal(15, 0.5, k)
            y[idx] = rng.normal(-10, 2, k)
    return x, y, bad


def fig1_example(seed=1):
    """38 compact leverage points at (15,-10) + 62 majority points (paper Fig 1)."""
    rng = np.random.default_rng(seed)
    return simulate(100, 0.38, "compact", rng)
