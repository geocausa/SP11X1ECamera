#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fit an independent rear tone curve and colour matrix from matched captures.

Input: compare-61-62.json (Linux run 61 vs Windows run 62, same exposure,
same displayed patches, same ROI) plus the current Linux gamma curve.
Model of the Linux IFE output path: rgb_lin -> gamma(12b) -> CST(BT.601).
We invert the current path to recover linear camera RGB per patch, then fit:
  * g1: one monotone tone curve (257 x 12-bit samples) from grey patches;
  * C : 3x3 gamma-domain colour matrix, rows summing to 1 (greys stay neutral),
        least squares against Windows output for the colour patches.
The CST matrix to program is BT.601 x C. Output: JSON with the new curve,
matrix (Q10, CST column order G,B,R) and residuals before/after.
"""
import json, re, sys
from pathlib import Path
import numpy as np

M601 = np.array([[0.5869140028953552, 0.11425799876451492, 0.29882800579071045],
                 [-0.33007800579071045, 0.49804699420928955, -0.1679690033197403],
                 [-0.4169920086860657, -0.08105500042438507, 0.49804699420928955]])  # cols G,B,R
OFF = np.array([0.0, 2048.0, 2048.0])


def load_gamma(inc):
    t = Path(inc).read_text()
    body = t[t.index("e007t_gamma_curve[E007T_GAMMA_SAMPLES] = {"):]
    body = body[body.index("{") + 1:body.index("};")]
    g = np.array([int(x) for x in re.findall(r"\d+", body)], dtype=float)
    assert len(g) == 257
    return g


def yuv8_to_gbr12(yuv):
    v = np.array(yuv, dtype=float) * (4095.0 / 255.0)
    return np.linalg.solve(M601, v - OFF)


def gbr12_to_yuv8(gbr):
    return (M601 @ gbr + OFF) * (255.0 / 4095.0)


def main():
    cmp = json.loads(Path(sys.argv[1]).read_text())
    g0 = load_gamma(sys.argv[2])
    xs = np.linspace(0, 4095, 257)
    inv_g0 = lambda y: np.interp(np.clip(y, 0, 4095), g0, xs)
    greys = ["grey_0", "grey_16", "grey_32", "grey_64", "grey_96", "grey_128", "grey_160", "grey_192", "grey_224", "grey_255"]
    colours = ["red", "green", "blue", "cyan", "magenta", "yellow"]
    pts = []  # (linear gbr 12b, windows yuv8, linux yuv8, name, gain)
    for L in cmp["ladder"]:
        for k, v in L["patterns"].items():
            if not v["linux"] or not v["windows"]:
                continue
            lin = inv_g0(yuv8_to_gbr12(v["linux"]))
            pts.append((lin, np.array(v["windows"]), np.array(v["linux"]), k, L["linux_gain"]))
    # Tone curve from greys: x = mean linear channel, y = Windows Y (12-bit).
    gx, gy = [], []
    for lin, w, l, k, g in pts:
        if k in greys:
            gx.append(lin.mean()); gy.append(w[0] * 4095.0 / 255.0)
    order = np.argsort(gx); gx = np.array(gx)[order]; gy = np.array(gy)[order]
    # isotonic (pool adjacent violators)
    blocks = [[y, 1.0, x] for x, y in zip(gx, gy)]
    i = 0
    while i < len(blocks) - 1:
        if blocks[i][0] > blocks[i + 1][0]:
            a, b = blocks[i], blocks[i + 1]
            w = a[1] + b[1]
            blocks[i] = [(a[0] * a[1] + b[0] * b[1]) / w, w, (a[2] * a[1] + b[2] * b[1]) / w]
            del blocks[i + 1]
            i = max(i - 1, 0)
        else:
            i += 1
    bx = np.array([b[2] for b in blocks]); by = np.array([b[0] for b in blocks])
    x0 = max(bx[0], 1.0)
    bx = np.concatenate([[0.0], bx]); by = np.concatenate([[0.0], by])
    xmax, ymax = bx[-1], by[-1]
    slope = (by[-1] - by[-3]) / max(bx[-1] - bx[-3], 1e-6)
    g1 = np.interp(xs, bx, by)
    hi = xs > xmax
    # smooth shoulder to 4095 at full scale, slope-continuous at xmax
    tau = (4095.0 - ymax) / max(slope, 1e-6)
    g1[hi] = ymax + (4095.0 - ymax) * (1 - np.exp(-(xs[hi] - xmax) / tau))
    g1[-1] = 4095.0
    g1 = np.maximum.accumulate(np.clip(np.round(g1), 0, 4095))
    G1 = lambda x: np.interp(np.clip(x, 0, 4095), xs, g1)
    # Colour matrix in gamma domain, rows constrained to sum to 1.
    A, B = [], []
    for lin, w, l, k, g in pts:
        if k in colours or k in greys[3:]:
            A.append(G1(lin)); B.append(yuv8_to_gbr12(w))
    A = np.array(A); B = np.array(B)
    C = np.zeros((3, 3))
    for r in range(3):
        # minimise ||A c - B_r|| s.t. sum(c)=1 via KKT
        K = np.zeros((4, 4)); K[:3, :3] = 2 * A.T @ A; K[:3, 3] = 1; K[3, :3] = 1
        rhs = np.concatenate([2 * A.T @ B[:, r], [1.0]])
        C[r] = np.linalg.solve(K, rhs)[:3]
    Mnew = M601 @ C
    q10 = np.round(Mnew * 1024).astype(int)
    def err(pred_fn):
        e = []
        for lin, w, l, k, g in pts:
            p = pred_fn(lin, l)
            e.append(dict(name=k, gain=g, dY=round(float(p[0] - w[0]), 1), dUV=round(float(np.hypot(p[1] - w[1], p[2] - w[2])), 1)))
        return e
    before = err(lambda lin, l: l)
    after = err(lambda lin, l: gbr12_to_yuv8(C @ G1(lin)))
    summ = lambda e, key: round(float(np.mean([abs(x[key]) for x in e])), 2)
    out = dict(tone_curve_12bit=[int(v) for v in g1], tone_points=len(gx), data_x_max_fraction=round(xmax / 4095, 4),
               ccm_gamma_domain_GBR=np.round(C, 4).tolist(), cst_q10_GBR=q10.tolist(), cst_q10_in_range=bool(np.all(np.abs(q10) <= 4095)),
               mean_abs_dY_before=summ(before, "dY"), mean_abs_dY_after=summ(after, "dY"),
               mean_dUV_before=summ(before, "dUV"), mean_dUV_after=summ(after, "dUV"),
               per_patch_after=[x for x in after if x["gain"] in (1, 8)])
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
