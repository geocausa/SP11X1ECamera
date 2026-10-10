#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fit independent front tone curves and colour matrix from matched captures.

Model of the front IFE output path with the param-queue gamma:
  linear RGB (10-bit) -> per-channel gamma LUT (257 points, 10-bit) -> CST.
The Linux run used an identity LUT and the stock BT.601 full-range CST, so
linear RGB per patch = BT.601^-1(Linux YUV). Targets are BT.601^-1(Windows YUV).
We alternate:
  * per-channel monotone curves f_c from grey patches (targets C^-1 W);
  * a 3x3 gamma-domain matrix C (weighted least squares, greys weighted to
    stay on their Windows values) from all patches.
The CST to program is BT.601 x C (Q10, kernel column order G,B,R).
Usage: fit-front-tone-ccm.py linux.json windows.json linux_phase windows_phase
Output: JSON (curves, matrix, residuals). Scalars and curves only.
"""
import json, sys
import numpy as np

GREYS = ["grey_0", "grey_8", "grey_16", "grey_32", "grey_48", "grey_64", "grey_96",
         "grey_128", "grey_160", "grey_192", "grey_224", "grey_255"]
COLOURS = ["red", "green", "blue", "cyan", "magenta", "yellow", "red50", "green50", "blue50"]
# BT.601 full range, rows Y,U,V, columns R,G,B.
M = np.array([[0.299, 0.587, 0.114], [-0.168736, -0.331264, 0.5], [0.5, -0.418688, -0.081312]])
Mi = np.linalg.inv(M)
X = np.linspace(0, 1023, 257)


def to_rgb10(p):
    return Mi @ (np.array([p["Y"], p["U"] - 128, p["V"] - 128])) * 1023 / 255


def to_yuv8(rgb10):
    v = M @ (np.asarray(rgb10) * 255 / 1023)
    return v + np.array([0, 128, 128])


def isotonic(x, y):
    o = np.argsort(x); x = np.asarray(x, float)[o]; y = np.asarray(y, float)[o]
    b = [[yy, 1.0, xx] for xx, yy in zip(x, y)]
    i = 0
    while i < len(b) - 1:
        if b[i][0] > b[i + 1][0]:
            w = b[i][1] + b[i + 1][1]
            b[i] = [(b[i][0] * b[i][1] + b[i + 1][0] * b[i + 1][1]) / w, w,
                    (b[i][2] * b[i][1] + b[i + 1][2] * b[i + 1][1]) / w]
            del b[i + 1]; i = max(i - 1, 0)
        else:
            i += 1
    return np.array([q[2] for q in b]), np.array([q[0] for q in b])


def curve(x, y):
    bx, by = isotonic(x, y)
    bx = np.concatenate([[0.0], bx]); by = np.concatenate([[0.0], np.maximum(by, 0)])
    xmax, ymax = bx[-1], min(by[-1], 1000.0)
    slope = max((by[-1] - by[-3]) / max(bx[-1] - bx[-3], 1e-6), 0.05)
    g = np.interp(X, bx, by)
    hi = X > xmax
    tau = (1023.0 - ymax) / slope
    g[hi] = ymax + (1023.0 - ymax) * (1 - np.exp(-(X[hi] - xmax) / tau))
    g[-1] = 1023.0
    g = np.maximum.accumulate(np.clip(np.round(g), 0, 1023))
    for i in range(1, len(g)):  # encoder limit: per-step delta <= 511
        g[i] = min(g[i], g[i - 1] + 500)
    return g, float(xmax)


def main():
    L = json.load(open(sys.argv[1])); W = json.load(open(sys.argv[2]))
    lp, wp = int(sys.argv[3]), int(sys.argv[4])
    lin = L["phases"][lp]["patterns"]; win = W["phases"][wp]["patterns"]
    names = [n for n in GREYS + COLOURS if n in lin and n in win]
    xl = {n: to_rgb10(lin[n]) for n in names}
    tw = {n: to_rgb10(win[n]) for n in names}
    C = np.eye(3)
    for _ in range(6):
        Ci = np.linalg.inv(C)
        curves, xmaxes = [], []
        for c in range(3):
            g, xm = curve([xl[n][c] for n in GREYS if n in names], [(Ci @ tw[n])[c] for n in GREYS if n in names])
            curves.append(g); xmaxes.append(xm)
        F = lambda v: np.array([np.interp(np.clip(v[c], 0, 1023), X, curves[c]) for c in range(3)])
        A, B, Wt = [], [], []
        for n in names:
            A.append(F(xl[n])); B.append(tw[n]); Wt.append(4.0 if n in GREYS else 1.0)
        A = np.array(A); B = np.array(B); s = np.sqrt(np.array(Wt))[:, None]
        C = np.linalg.lstsq(A * s, B * s, rcond=None)[0].T
    cst = M @ C  # rows Y,U,V ; cols R,G,B
    q10_gbr = [[int(round(cst[r][c] * 1024)) for c in (1, 2, 0)] for r in range(3)]
    res = []
    for n in names:
        p = to_yuv8(C @ F(xl[n])); w = np.array([win[n][k] for k in "YUV"])
        b = np.array([lin[n][k] for k in "YUV"])
        res.append(dict(pattern=n, windows=np.round(w, 1).tolist(), predicted=np.round(p, 1).tolist(),
                        dY=round(float(p[0] - w[0]), 1), dC=round(float(np.hypot(p[1] - w[1], p[2] - w[2])), 1),
                        sat=round(float(np.hypot(p[1] - 128, p[2] - 128) / max(np.hypot(w[1] - 128, w[2] - 128), 1e-6)), 3)))
    col = [r for r in res if r["pattern"] in COLOURS]
    out = dict(linux_phase=L["phases"][lp].get("again"), linux_dgain=L["phases"][lp].get("dgain"), windows_phase=wp,
               gamma_r=[int(v) for v in curves[0]], gamma_g=[int(v) for v in curves[1]], gamma_b=[int(v) for v in curves[2]],
               data_x_max=[round(x, 1) for x in xmaxes], ccm_gamma_domain_RGB=np.round(C, 4).tolist(),
               cst_q10_GBR=q10_gbr, colour_mean_abs_dY=round(float(np.mean([abs(r["dY"]) for r in col])), 2),
               colour_mean_dC=round(float(np.mean([r["dC"] for r in col])), 2),
               colour_mean_sat=round(float(np.mean([r["sat"] for r in col])), 3),
               grey_mean_abs_dY=round(float(np.mean([abs(r["dY"]) for r in res if r["pattern"] in GREYS])), 2),
               grey_mean_dC=round(float(np.mean([r["dC"] for r in res if r["pattern"] in GREYS])), 2),
               residuals=res)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
