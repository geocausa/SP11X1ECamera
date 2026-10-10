#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Refit front tone curves and colour matrix on automatic-vs-automatic data.

The Linux run used a known prior LUT/CST (prior fit JSON) with pipeline AE;
each Linux patch is first linearised through that prior (inverse CST matrix,
inverse per-channel LUT), then the same alternating curve/matrix fit as
fit-front-tone-ccm.py maps those linear values to the Windows automatic output.
The AE target is unchanged; the curves absorb the Windows/Linux exposure-level
difference. Usage: refit-front-auto.py prior.json linux.json windows.json lp wp
"""
import json, runpy, sys
from pathlib import Path
import numpy as np

F = runpy.run_path(str(Path(__file__).with_name("fit-front-tone-ccm.py")))
M, Mi, X, curve, to_yuv8 = F["M"], F["Mi"], F["X"], F["curve"], F["to_yuv8"]
GREYS, COLOURS = F["GREYS"], F["COLOURS"]


def main():
    prior = json.load(open(sys.argv[1]))
    L = json.load(open(sys.argv[2])); W = json.load(open(sys.argv[3]))
    lp, wp = int(sys.argv[4]), int(sys.argv[5])
    lin = L["phases"][lp]["patterns"]; win = W["phases"][wp]["patterns"]
    C0 = np.array(prior["ccm_gamma_domain_RGB"]); C0i = np.linalg.inv(C0)
    g0 = [np.array(prior[k], float) for k in ("gamma_r", "gamma_g", "gamma_b")]
    names = [n for n in GREYS + COLOURS if n in lin and n in win]

    def linearise(p):
        out10 = C0i @ (Mi @ np.array([p["Y"], p["U"] - 128, p["V"] - 128]) * 1023 / 255)
        return np.array([np.interp(out10[c], g0[c], X) for c in range(3)])
    xl = {n: linearise(lin[n]) for n in names}
    tw = {n: Mi @ np.array([win[n]["Y"], win[n]["U"] - 128, win[n]["V"] - 128]) * 1023 / 255 for n in names}
    C = np.eye(3)
    for _ in range(8):
        Ci = np.linalg.inv(C)
        curves, xm = [], []
        for c in range(3):
            g, m = curve([xl[n][c] for n in GREYS if n in names], [(Ci @ tw[n])[c] for n in GREYS if n in names])
            curves.append(g); xm.append(m)
        Fn = lambda v: np.array([np.interp(np.clip(v[c], 0, 1023), X, curves[c]) for c in range(3)])
        A = np.array([Fn(xl[n]) for n in names]); B = np.array([tw[n] for n in names])
        s = np.sqrt(np.array([4.0 if n in GREYS else 1.0 for n in names]))[:, None]
        C = np.linalg.lstsq(A * s, B * s, rcond=None)[0].T
    cst = M @ C
    q10 = [[int(round(cst[r][c] * 1024)) for c in (1, 2, 0)] for r in range(3)]
    res = []
    for n in names:
        p = to_yuv8(C @ Fn(xl[n])); w = np.array([win[n][k] for k in "YUV"])
        res.append(dict(pattern=n, windows=np.round(w, 1).tolist(), predicted=np.round(p, 1).tolist(),
                        dY=round(float(p[0] - w[0]), 1), dC=round(float(np.hypot(p[1] - w[1], p[2] - w[2])), 1)))
    col = [r for r in res if r["pattern"] in COLOURS]; gr = [r for r in res if r["pattern"] in GREYS]
    out = dict(gamma_r=[int(v) for v in curves[0]], gamma_g=[int(v) for v in curves[1]], gamma_b=[int(v) for v in curves[2]],
               data_x_max=[round(x, 1) for x in xm], ccm_gamma_domain_RGB=np.round(C, 4).tolist(), cst_q10_GBR=q10,
               grey_mean_abs_dY=round(float(np.mean([abs(r["dY"]) for r in gr])), 2),
               grey_mean_dC=round(float(np.mean([r["dC"] for r in gr])), 2),
               colour_mean_abs_dY=round(float(np.mean([abs(r["dY"]) for r in col])), 2),
               colour_mean_dC=round(float(np.mean([r["dC"] for r in col])), 2), residuals=res)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
