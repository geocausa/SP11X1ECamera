#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""How much of a new Windows scene is explained by exposure + white balance alone.

Linearises a tuned Linux capture through its known model (fit JSON: K + LUTs),
then fits the Windows capture of the same session with the reference model's
tone curve T and K fixed and only exposure k, WB gains (R,B) and the display
gain s free (model A), versus a full refit (model B, fit-front-param style).
Usage: fit-front-adapt.py <linux run> <lphase> <linux analysis> <windows records> <wphase> <windows analysis> <wpatphase> <model fit.json>
"""
import json, runpy, sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

H = Path(__file__).resolve().parent
P = runpy.run_path(str(H / "fit-front-param.py"))
S = runpy.run_path(str(H / "scene-check.py"))
rgb10, yuv8, unpack, KNOTS, X = P["rgb10"], P["yuv8"], P["unpack"], P["KNOTS"], P["X"]
GREYS, COLOURS = P["GREYS"], P["COLOURS"]
GX = 16


def main():
    run, lp, la, wrec, wp, wa, wpp, fit = sys.argv[1:9]
    lp, wp, wpp = int(lp), int(wp), int(wpp)
    F = json.load(open(fit))
    K = np.array(F["ccm_linear_RGB"]); Ki = np.linalg.inv(K)
    luts = [np.array(F[k], float) for k in ("gamma_r", "gamma_g", "gamma_b")]
    wref = np.array(F["wb_gains_RGB"])
    from scipy.interpolate import PchipInterpolator
    T = PchipInterpolator(np.array(F["tone_knots_x"]), np.array(F["tone_knots_y"]))

    def linearise(yuv):
        g = rgb10(yuv)
        lin = np.array([[np.interp(v[c], luts[c], X) for c in range(3)] for v in g])
        return lin @ Ki.T  # undo K (LUT input = K x)

    Lg = S["linux_grid"](run, lp); Wg = S["windows_grid"](wrec, wp).reshape(3, -1).T
    A = json.load(open(la))
    rows, cols = A["roi_rows"], A["roi_cols"]
    excl = {r * GX + c for r in range(min(rows) - 1, max(rows) + 2) for c in range(min(cols) - 1, max(cols) + 2)}
    cells = [i for i in range(len(Lg)) if i not in excl and Lg[i][0] < 235 and Wg[i][0] < 245]
    lin = A["phases"][lp]["patterns"]; win = json.load(open(wa))["phases"][wpp]["patterns"]
    names = [n for n in GREYS + COLOURS if n in lin and n in win]
    x = np.vstack([linearise(Lg[cells]), linearise(np.array([[lin[n][q] for q in "YUV"] for n in names]))])
    t = np.vstack([Wg[cells], np.array([[win[n][q] for q in "YUV"] for n in names])])
    patch = np.array([False] * len(cells) + [True] * len(names))
    wts = np.concatenate([np.ones(len(cells)), [3.0 if n in GREYS else 2.0 for n in names]])
    n0 = len(cells)

    def modelA(v):
        k, wr, wb, s = np.exp(v)
        w = wref * [wr, 1, wb]
        l = (x * np.where(patch, s, 1.0)[:, None] * k) @ K.T * w
        return yuv8(T(np.clip(l, 0, 1023)))

    ra = least_squares(lambda v: ((modelA(v) - t) * wts[:, None]).ravel(), np.zeros(4) + [0, 0, 0, np.log(2)])
    pa = modelA(ra.x); da = pa - t

    def modelB(v):
        return P["apply"](v, x, patch)

    v0 = np.concatenate([[-0.3, -0.1, -0.3, -0.1, -0.3, -0.1, 0.0, 0.0, np.log(2.0)], np.zeros(len(KNOTS) - 1)])
    rb = least_squares(lambda v: np.concatenate([((modelB(v) - t) * wts[:, None]).ravel(), 10 * np.diff(v[9:], 2)]), v0, max_nfev=4000)
    pb = modelB(rb.x); db = pb - t
    kb, wbB, sb, tb = unpack(rb.x)

    def summ(d):
        gi = [n0 + j for j, n in enumerate(names) if n in GREYS]; ci = [n0 + j for j, n in enumerate(names) if n in COLOURS]
        return dict(scene_abs_dY=round(float(np.abs(d[:n0, 0]).mean()), 2), scene_dC=round(float(np.hypot(d[:n0, 1], d[:n0, 2]).mean()), 2),
                    grey_abs_dY=round(float(np.abs(d[gi, 0]).mean()), 2), grey_dC=round(float(np.hypot(d[gi, 1], d[gi, 2]).mean()), 2),
                    colour_abs_dY=round(float(np.abs(d[ci, 0]).mean()), 2), colour_dC=round(float(np.hypot(d[ci, 1], d[ci, 2]).mean()), 2))
    print(json.dumps(dict(cells=n0, A=dict(exposure=round(float(np.exp(ra.x[0])), 3), wb_rel_R=round(float(np.exp(ra.x[1])), 3),
                                          wb_rel_B=round(float(np.exp(ra.x[2])), 3), patch_gain=round(float(np.exp(ra.x[3])), 3), **summ(da)),
                          B=dict(patch_gain=round(sb, 3), wb=np.round(wbB, 3).tolist(), K=np.round(kb, 3).tolist(),
                                 tone_y=np.round(tb(KNOTS), 1).tolist(), **summ(db)),
                          ref_tone_y=np.round(T(KNOTS), 1).tolist()), indent=1))


if __name__ == "__main__":
    main()
