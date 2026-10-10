#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fit a global tone lift that makes the pipeline with the vendor tone mapper disabled
match the pipeline with it enabled, and fold it into our gamma LUTs.

Inputs are two still-capture runs of the same static chart at identical exposure
(same camera position): <on-dir> (tone mapper enabled) and <off-dir> (disabled).
For every 8-bit output level of the 'off' run the median 'on' level is taken
(both phases pooled, each phase weighted equally), smoothed and made monotone.
The lift F is applied to each gamma LUT entry in the output domain:
  gamma'[i] = 4 * F(gamma[i] / 4).
Usage: fit-tone-lift.py <frames-per-phase> <on-dir> <off-dir> <tuning-in.yaml> <tuning-out.yaml>
Prints scalars only.
"""
import json, sys
from pathlib import Path
import numpy as np
import yaml

W, H = 2560, 1440


def means(d, per):
    ph = {}
    for p in sorted(Path(d).glob("frame-*.nv12")):
        n = int(p.stem.split("-")[1])
        ph.setdefault(n // per, []).append(np.fromfile(p, np.uint8)[:W * H].reshape(H, W).astype(np.float32))
    return {k: np.mean(v, 0) for k, v in ph.items()}


def main():
    per = int(sys.argv[1])
    on, off = means(sys.argv[2], per), means(sys.argv[3], per)
    acc_w = np.zeros(256); curve = np.zeros(256)
    for k in sorted(set(on) & set(off)):
        a = off[k].ravel(); b = on[k].ravel()
        keep = (b < 250) & (a < 250)
        a, b = a[keep], b[keep]
        idx = np.clip(np.rint(a).astype(int), 0, 255)
        for v in range(256):
            sel = idx == v
            n = int(sel.sum())
            if n >= 200:
                curve[v] += np.median(b[sel]); acc_w[v] += 1
    ok = acc_w > 0
    lv = np.arange(256)
    f = np.where(ok, curve / np.maximum(acc_w, 1), np.nan)
    good = ~np.isnan(f)
    # lift = f - identity; interpolate gaps, fade to zero above the measured range and at 0
    lift = np.interp(lv, lv[good], (f - lv)[good])
    top = lv[good].max()
    lift[lv > top] *= np.clip((255 - lv[lv > top]) / max(255 - top, 1), 0, 1)
    lift[0] = 0
    k = np.ones(9) / 9
    lift = np.convolve(np.pad(lift, 4, mode="edge"), k, mode="valid")
    F = np.maximum.accumulate(np.clip(lv + lift, 0, 255))
    t = yaml.safe_load(Path(sys.argv[4]).read_text())
    for c in ("gamma_r", "gamma_g", "gamma_b"):
        g = np.array(t[c], float)
        t[c] = [int(round(min(1023, 4 * np.interp(v / 4, lv, F)))) for v in g]
    out = Path(sys.argv[5])
    lines = [l for l in Path(sys.argv[4]).read_text().splitlines()]
    res = []
    for l in lines:
        key = l.split(":")[0]
        res.append(f"{key}: [{', '.join(str(v) for v in t[key])}]" if key in ("gamma_r", "gamma_g", "gamma_b") else l)
    out.write_text("\n".join(res) + "\n")
    print(json.dumps({"measured_levels": int(good.sum()), "top_level": int(top),
                      "lift_at": {str(v): round(float(F[v] - v), 2) for v in (8, 16, 32, 48, 64, 96, 128, 160, 192, 224)},
                      "out": str(out)}))


if __name__ == "__main__":
    main()
