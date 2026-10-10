#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fit the front tone curves and linear CCM from the whole scene plus patches.

Model (global): linear camera RGB x -> K (rows sum to 1) -> per-channel LUT f_c
-> BT.601 full range. Samples:
  * scene: mean 16x9 grid cells of a linear Linux AE phase vs the Windows AE
    phase, excluding the display region and clipped cells;
  * patches: display patches (Linux linear vs Windows consensus). The Windows
    pipeline renders the display brighter than a global curve would (local
    tone mapping), so patch inputs get one fitted gain s.
For each candidate (K, s) the curves are refitted per channel (isotonic) from
all samples; K and s minimise the YUV error. Output: curves, K, Q7 (G,B,R).
Usage: fit-front-scene.py <linux run> <lphase> <linux analysis.json> <windows records.csv> <wphase> <windows patches.json>
"""
import json, runpy, sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

H = Path(__file__).resolve().parent
T = runpy.run_path(str(H / "fit-front-tone-ccm.py"))
S = runpy.run_path(str(H / "scene-check.py"))
M, Mi, X, curve, to_yuv8 = T["M"], T["Mi"], T["X"], T["curve"], T["to_yuv8"]
GREYS, COLOURS = T["GREYS"], T["COLOURS"]
GX = 16


def rgb10(y, u, v):
    return Mi @ np.array([y, u - 128, v - 128]) * 1023 / 255


def main():
    run, lp, la, wrec, wp, wpat = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], int(sys.argv[5]), sys.argv[6]
    Lg = S["linux_grid"](run, lp)
    Wg = S["windows_grid"](wrec, wp).reshape(3, -1).T
    A = json.load(open(la))
    rows, cols = set(A["roi_rows"]), set(A["roi_cols"])
    excl = {r * GX + c for r in range(min(rows) - 1, max(rows) + 2) for c in range(min(cols) - 1, max(cols) + 2)}
    cells = [i for i in range(len(Lg)) if i not in excl and Lg[i][0] < 235 and Wg[i][0] < 245]
    xs = [rgb10(*Lg[i]) for i in cells]; ts = [Wg[i] for i in cells]
    lin = A["phases"][lp]["patterns"]; win = json.load(open(wpat))["phases"][0]["patterns"]
    names = [n for n in GREYS + COLOURS if n in lin and n in win]
    xp = [rgb10(lin[n]["Y"], lin[n]["U"], lin[n]["V"]) for n in names]
    tp = [np.array([win[n][q] for q in "YUV"]) for n in names]
    wts = np.array([1.0] * len(cells) + [3.0 if n in GREYS else 2.0 for n in names])

    def unpack(v):
        k = np.zeros((3, 3))
        for r in range(3):
            off = [c for c in range(3) if c != r]
            k[r, off[0]], k[r, off[1]] = v[2 * r], v[2 * r + 1]
            k[r, r] = 1.0 - v[2 * r] - v[2 * r + 1]
        return k, float(np.exp(v[6]))

    def model(v):
        k, s = unpack(v)
        ins = [k @ x for x in xs] + [k @ (s * x) for x in xp]
        tg = [rgb10(*t) for t in ts + tp]
        cv = [curve([i[c] for i in ins], [t[c] for t in tg])[0] for c in range(3)]
        return k, s, ins, cv

    def predict(cv, i):
        return to_yuv8(np.array([np.interp(np.clip(i[c], 0, 1023), X, cv[c]) for c in range(3)]))

    def resid(v):
        k, s, ins, cv = model(v)
        e = [(predict(cv, i) - t) * w for i, t, w in zip(ins, ts + tp, wts)]
        return np.concatenate(e)

    sol = least_squares(resid, np.array([-0.4, -0.1, -0.4, -0.1, -0.4, -0.1, np.log(2.0)]),
                        diff_step=1e-3, max_nfev=300)
    k, s, ins, cv = model(sol.x)
    pr = [predict(cv, i) for i in ins]
    sc = np.array(pr[:len(cells)]) - np.array(ts); pa = np.array(pr[len(cells):]) - np.array(tp)
    res = [dict(pattern=n, windows=np.round(t, 1).tolist(), predicted=np.round(p, 1).tolist(),
                dY=round(float(p[0] - t[0]), 1), dC=round(float(np.hypot(p[1] - t[1], p[2] - t[2])), 1))
           for n, p, t in zip(names, pr[len(cells):], tp)]
    gi = [j for j, n in enumerate(names) if n in GREYS]; ci = [j for j, n in enumerate(names) if n in COLOURS]
    order = (1, 2, 0)
    out = dict(scene_cells=len(cells), patch_gain=round(s, 3),
               gamma_r=[int(v) for v in cv[0]], gamma_g=[int(v) for v in cv[1]], gamma_b=[int(v) for v in cv[2]],
               ccm_linear_RGB=np.round(k, 4).tolist(), ccm_q7_GBR=[[int(round(k[r][c] * 128)) for c in order] for r in order],
               scene_mean_abs_dY=round(float(np.abs(sc[:, 0]).mean()), 2),
               scene_mean_dC=round(float(np.hypot(sc[:, 1], sc[:, 2]).mean()), 2),
               grey_mean_abs_dY=round(float(np.abs(pa[gi, 0]).mean()), 2),
               grey_mean_dC=round(float(np.hypot(pa[gi, 1], pa[gi, 2]).mean()), 2),
               colour_mean_abs_dY=round(float(np.abs(pa[ci, 0]).mean()), 2),
               colour_mean_dC=round(float(np.hypot(pa[ci, 1], pa[ci, 2]).mean()), 2), residuals=res)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
