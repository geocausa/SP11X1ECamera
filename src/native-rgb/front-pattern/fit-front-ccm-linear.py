#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fit a linear-domain colour matrix (IFE colour-correction module, before the
gamma LUT) plus per-channel tone curves, keeping the stock BT.601 CST.

Model:  x (linear camera RGB, after the profile WB) -> CCM (rows sum to 1, so
neutrals are preserved) -> per-channel LUT -> BT.601 full-range CST.
Linux patches come from an automatic-exposure run made with a known prior
(LUT0 + gamma-domain matrix C0 in the CST); they are linearised through that
prior and scaled by the planned AE-target ratio. Targets are the Windows
automatic-exposure patches. Alternating fit: curves from greys, then the CCM
by constrained least squares in the linear domain (targets pulled back through
the current inverse curves).
Usage: fit-front-ccm-linear.py prior.json linux.json windows.json lp wp ae_scale
"""
import json, runpy, sys
from pathlib import Path
import numpy as np

F = runpy.run_path(str(Path(__file__).with_name("fit-front-tone-ccm.py")))
M, Mi, X, curve, to_yuv8 = F["M"], F["Mi"], F["X"], F["curve"], F["to_yuv8"]
GREYS, COLOURS = F["GREYS"], F["COLOURS"]


def constrained_rows(A, B, w):
    """Solve min ||diag(w)(A c - b_r)|| per row with sum(c) = 1."""
    Aw = A * w[:, None]
    C = np.zeros((3, 3))
    for r in range(3):
        K = np.zeros((4, 4)); K[:3, :3] = 2 * Aw.T @ Aw; K[:3, 3] = 1; K[3, :3] = 1
        rhs = np.concatenate([2 * Aw.T @ (B[:, r] * w), [1.0]])
        C[r] = np.linalg.solve(K, rhs)[:3]
    return C


def main():
    prior = json.load(open(sys.argv[1]))
    L = json.load(open(sys.argv[2])); W = json.load(open(sys.argv[3]))
    lp, wp, scale = int(sys.argv[4]), int(sys.argv[5]), float(sys.argv[6])
    lin = L["phases"][lp]["patterns"]; win = W["phases"][wp]["patterns"]
    # Prior pipeline: either a gamma-domain matrix folded into the CST
    # (ccm_gamma_domain_RGB) or a linear colour-correction matrix before the LUT
    # (ccm_linear_RGB) with the stock CST.
    C0i = np.linalg.inv(np.array(prior.get("ccm_gamma_domain_RGB", np.eye(3).tolist())))
    K0i = np.linalg.inv(np.array(prior["ccm_linear_RGB"])) if "ccm_linear_RGB" in prior else np.eye(3)
    g0 = [np.array(prior[k], float) for k in ("gamma_r", "gamma_g", "gamma_b")]
    names = [n for n in GREYS + COLOURS if n in lin and n in win]

    def linearise(p):
        out10 = C0i @ (Mi @ np.array([p["Y"], p["U"] - 128, p["V"] - 128]) * 1023 / 255)
        return scale * (K0i @ np.array([np.interp(out10[c], g0[c], X) for c in range(3)]))
    xl = {n: linearise(lin[n]) for n in names}
    tw = {n: Mi @ np.array([win[n]["Y"], win[n]["U"] - 128, win[n]["V"] - 128]) * 1023 / 255 for n in names}
    K = np.eye(3)
    for _ in range(12):
        curves, xm = [], []
        for c in range(3):
            g, m = curve([(K @ xl[n])[c] for n in GREYS if n in names], [tw[n][c] for n in GREYS if n in names])
            curves.append(g); xm.append(m)
        inv = lambda v: np.array([np.interp(np.clip(v[c], 0, 1023), curves[c], X) for c in range(3)])
        A = np.array([xl[n] for n in names])
        B = np.array([inv(tw[n]) for n in names])
        w = np.array([2.0 if n in GREYS else 1.0 for n in names])
        K = constrained_rows(A, B, w)
    # Refine the CCM against the output-domain (YUV) error; curves are refitted
    # from the greys for every candidate so neutrals stay exact.
    from scipy.optimize import least_squares

    def unpack(v):
        k = np.zeros((3, 3))
        for r in range(3):
            off = [c for c in range(3) if c != r]
            k[r, off[0]], k[r, off[1]] = v[2 * r], v[2 * r + 1]
            k[r, r] = 1.0 - v[2 * r] - v[2 * r + 1]
        return k

    def model(v):
        k = unpack(v)
        cv = [curve([(k @ xl[n])[c] for n in GREYS if n in names], [tw[n][c] for n in GREYS if n in names])[0]
              for c in range(3)]
        return k, cv

    def resid(v):
        k, cv = model(v)
        e = []
        for n in names:
            g = np.array([np.interp(np.clip((k @ xl[n])[c], 0, 1023), X, cv[c]) for c in range(3)])
            p = to_yuv8(g); t = np.array([win[n][q] for q in "YUV"])
            e.extend(((p - t) * (2.0 if n in GREYS else 1.0)).tolist())
        return np.array(e)
    v0 = np.array([K[r, c] for r in range(3) for c in range(3) if c != r])
    sol = least_squares(resid, v0, diff_step=1e-3, max_nfev=400)
    K, curves = model(sol.x)
    Fn = lambda v: np.array([np.interp(np.clip(v[c], 0, 1023), X, curves[c]) for c in range(3)])
    res = []
    for n in names:
        p = to_yuv8(Fn(K @ xl[n])); t = np.array([win[n][k] for k in "YUV"])
        res.append(dict(pattern=n, windows=np.round(t, 1).tolist(), predicted=np.round(p, 1).tolist(),
                        dY=round(float(p[0] - t[0]), 1), dC=round(float(np.hypot(p[1] - t[1], p[2] - t[2])), 1)))
    col = [r for r in res if r["pattern"] in COLOURS]; gr = [r for r in res if r["pattern"] in GREYS]
    # Register order of the colour-correction module: rows/cols G,B,R, Q7.
    order = (1, 2, 0)
    q7 = [[int(round(K[r][c] * 128)) for c in order] for r in order]
    out = dict(ae_scale=scale, gamma_r=[int(v) for v in curves[0]], gamma_g=[int(v) for v in curves[1]],
               gamma_b=[int(v) for v in curves[2]], data_x_max=[round(x, 1) for x in xm],
               ccm_linear_RGB=np.round(K, 4).tolist(), ccm_q7_GBR=q7,
               grey_mean_abs_dY=round(float(np.mean([abs(r["dY"]) for r in gr])), 2),
               grey_mean_dC=round(float(np.mean([r["dC"] for r in gr])), 2),
               colour_mean_abs_dY=round(float(np.mean([abs(r["dY"]) for r in col])), 2),
               colour_mean_dC=round(float(np.mean([r["dC"] for r in col])), 2), residuals=res)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
