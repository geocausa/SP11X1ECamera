#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fit the temporal noise model var = a*m + b of a linear still capture (identity gamma,
denoise and tone mapping off) of the static chart, per capture phase.
m and var are in 8-bit output units of the linear pipeline (proportional to raw).
Usage: fit-noise-model.py <frames-per-phase> <dir>
"""
import json, sys
from pathlib import Path
import numpy as np

W, H = 2560, 1440


def box(a, r):
    c = np.cumsum(np.cumsum(np.pad(a, ((r + 1, r), (r + 1, r)), mode="edge"), 0), 1)
    k = 2 * r + 1
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def main():
    per = int(sys.argv[1]); ph = {}
    for p in sorted(Path(sys.argv[2]).glob("frame-*.nv12")):
        n = int(p.stem.split("-")[1])
        ph.setdefault(n // per, []).append(np.fromfile(p, np.uint8)[:W * H].reshape(H, W).astype(np.float32))
    out = {}
    for k, fr in sorted(ph.items()):
        y = np.stack(fr); m = y.mean(0); v = y.var(0, ddof=1)
        gx = np.abs(np.diff(box(m, 1), axis=1, prepend=0)); gy = np.abs(np.diff(box(m, 1), axis=0, prepend=0))
        flat = (box(gx + gy, 4) < 0.8) & (m > 1) & (m < 240)
        mm, vv = m[flat], v[flat]
        edges = np.geomspace(1, 240, 31)
        xs, ys, ns = [], [], []
        for lo, hi in zip(edges[:-1], edges[1:]):
            s = (mm >= lo) & (mm < hi)
            if s.sum() > 300:
                xs.append(float(mm[s].mean())); ys.append(float(np.median(vv[s]) / 0.9549)); ns.append(int(s.sum()))
        xs, ys = np.array(xs), np.array(ys)
        A = np.vstack([xs, np.ones_like(xs)]).T
        (a, b), *_ = np.linalg.lstsq(A, ys, rcond=None)
        out[f"phase{k}"] = dict(frames=len(fr), a=round(float(a), 4), b=round(float(b), 4),
                                levels=[round(x, 1) for x in xs], var=[round(x, 3) for x in ys],
                                max_level=round(float(np.percentile(m, 99.9)), 1))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
