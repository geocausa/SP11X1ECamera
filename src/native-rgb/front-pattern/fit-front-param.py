#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Parametric front tone/colour fit: smooth shared tone curve, white-balance
gains and a linear CCM, from the whole scene plus display patches.

Model: x (linear camera RGB, 10-bit) -> K (rows sum to 1) -> WB gains (G = 1)
-> shared monotone tone curve T (PCHIP through log-spaced knots, T(0)=0,
T(1023)=1023) -> BT.601 full range. Programmed as per-channel 257-point LUTs
gamma_c[i] = T(w_c * X[i]) plus the CCM in the colour-correction module.
Samples as in fit-front-scene.py (scene cells outside the display, display
patches with one gain s for the Windows local tone mapping of the display).
Usage: fit-front-param.py <linux run> <lphase> <linux analysis.json> <windows records.csv> <wphase> <windows patches.json> [patch_weight]
"""
import json, os, runpy, sys
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import least_squares

H = Path(__file__).resolve().parent
T0 = runpy.run_path(str(H / "fit-front-tone-ccm.py"))
S = runpy.run_path(str(H / "scene-check.py"))
M, Mi, X = T0["M"], T0["Mi"], T0["X"]
GREYS, COLOURS = T0["GREYS"], T0["COLOURS"]
GX = 16
KNOTS = np.array([0, 6, 12, 24, 48, 96, 192, 384, 700, 1023], float)


def rgb10(p):
    p = np.atleast_2d(p)
    return (Mi @ (p - [0, 128, 128]).T).T * 1023 / 255


def yuv8(g):
    return (M @ (np.asarray(g) * 255 / 1023).T).T + [0, 128, 128]


def tone(p):
    inc = np.log1p(np.exp(p))
    y = np.concatenate([[0.0], np.cumsum(inc)])
    return PchipInterpolator(KNOTS, 1023 * y / y[-1])


def unpack(v):
    k = np.zeros((3, 3))
    for r in range(3):
        off = [c for c in range(3) if c != r]
        k[r, off[0]], k[r, off[1]] = v[2 * r], v[2 * r + 1]
        k[r, r] = 1.0 - v[2 * r] - v[2 * r + 1]
    w = np.array([np.exp(v[6]), 1.0, np.exp(v[7])])
    return k, w, float(np.exp(v[8])), tone(v[9:])


def apply(v, x, patch):
    k, w, s, t = unpack(v)
    lin = (x * np.where(patch, s, 1.0)[:, None]) @ k.T * w
    return yuv8(t(np.clip(lin, 0, 1023)))


def main():
    run, lp, la, wrec, wp, wpat = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], int(sys.argv[5]), sys.argv[6]
    pw = float(sys.argv[7]) if len(sys.argv) > 7 else 2.0
    Lg = S["linux_grid"](run, lp)
    Wg = S["windows_grid"](wrec, wp).reshape(3, -1).T
    A = json.load(open(la))
    rows, cols = A["roi_rows"], A["roi_cols"]
    excl = {r * GX + c for r in range(min(rows) - 1, max(rows) + 2) for c in range(min(cols) - 1, max(cols) + 2)}
    cells = [i for i in range(len(Lg)) if i not in excl and Lg[i][0] < 235 and Wg[i][0] < 245]
    lin = A["phases"][lp]["patterns"]; win = json.load(open(wpat))["phases"][0]["patterns"]
    names = [n for n in GREYS + COLOURS if n in lin and n in win]
    x = np.vstack([rgb10(Lg[cells]), rgb10(np.array([[lin[n][q] for q in "YUV"] for n in names]))])
    t = np.vstack([Wg[cells], np.array([[win[n][q] for q in "YUV"] for n in names])])
    patch = np.array([False] * len(cells) + [True] * len(names))
    wts = np.concatenate([np.ones(len(cells)), [1.5 * pw if n in GREYS else pw for n in names]])

    def resid(v):
        e = (apply(v, x, patch) - t) * wts[:, None]
        smooth = float(os.environ.get("FIT_SMOOTH", "0.5")) * np.diff(v[9:], 2)  # gentle curvature regulariser on knot increments
        return np.concatenate([e.ravel(), smooth])

    v0 = np.concatenate([[-0.3, -0.1, -0.3, -0.1, -0.3, -0.1, 0.0, 0.0, np.log(2.0)], np.zeros(len(KNOTS) - 1)])
    sol = least_squares(resid, v0, max_nfev=4000)
    v = sol.x
    k, w, s, tc = unpack(v)
    pr = apply(v, x, patch); d = pr - t
    n0 = len(cells)
    gi = [n0 + j for j, n in enumerate(names) if n in GREYS]; ci = [n0 + j for j, n in enumerate(names) if n in COLOURS]
    # Channels whose WB gain is below 1 would never reach full scale; ramp their
    # top quarter to 1023 so clipped highlights stay neutral.
    top = np.clip((X - 768) / 255, 0, 1) ** 2
    luts = []
    for c in range(3):
        g = tc(np.clip(w[c] * X, 0, 1023))
        g = g + (1023 - tc(min(w[c] * 1023, 1023))) * top
        luts.append(np.maximum.accumulate(np.clip(np.round(g), 0, 1023)).astype(int))
    order = (1, 2, 0)
    res = [dict(pattern=n, windows=np.round(t[n0 + j], 1).tolist(), predicted=np.round(pr[n0 + j], 1).tolist(),
                dY=round(float(d[n0 + j, 0]), 1), dC=round(float(np.hypot(*d[n0 + j, 1:])), 1)) for j, n in enumerate(names)]
    out = dict(scene_cells=n0, patch_gain=round(s, 3), wb_gains_RGB=np.round(w, 4).tolist(),
               tone_knots_x=KNOTS.tolist(), tone_knots_y=np.round(tc(KNOTS), 1).tolist(),
               gamma_r=luts[0].tolist(), gamma_g=luts[1].tolist(), gamma_b=luts[2].tolist(),
               ccm_linear_RGB=np.round(k, 4).tolist(), ccm_q7_GBR=[[int(round(k[r][c] * 128)) for c in order] for r in order],
               scene_mean_abs_dY=round(float(np.abs(d[:n0, 0]).mean()), 2), scene_median_dY=round(float(np.median(d[:n0, 0])), 2),
               scene_mean_dC=round(float(np.hypot(d[:n0, 1], d[:n0, 2]).mean()), 2),
               grey_mean_abs_dY=round(float(np.abs(d[gi, 0]).mean()), 2), grey_mean_dC=round(float(np.hypot(d[gi, 1], d[gi, 2]).mean()), 2),
               colour_mean_abs_dY=round(float(np.abs(d[ci, 0]).mean()), 2), colour_mean_dC=round(float(np.hypot(d[ci, 1], d[ci, 2]).mean()), 2),
               cost=round(float(sol.cost), 1), residuals=res)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
