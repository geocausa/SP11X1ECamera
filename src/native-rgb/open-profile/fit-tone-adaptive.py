#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fit our scene-adaptive shadow lift (replacement for the vendor local tone mapper).

Inputs: two still-capture runs of the same static chart and camera position:
<ref-dir> (vendor tone mapper on) and <open-dir> (our open configuration with a
global tone curve). Phase 0 is the fixed-exposure scene (little shadow area),
phase 1 the auto-exposure scene (large lifted shadow area).

For the dark scene the extra lift per output level is the median reference level
minus the open level (smoothed, made monotone in the result). The scene weight is
the fraction of the 32x32 metering regions whose displayed level falls in the
shadow band; phase 0 sets weight 0, phase 1 weight 1. Writes tuning keys:
  tone_dark_lift   17 lifts (u10) at output levels 0, 64, ..., 1024
  tone_shadow_lo/hi  shadow band (u10 displayed level)
  tone_dark_low/high region fractions mapping to weight 0 and 1
  tone_speed         per-frame smoothing of the weight
Usage: fit-tone-adaptive.py <frames-per-phase> <ref-dir> <open-dir> <tuning-in> <tuning-out>
"""
import json, sys
from pathlib import Path
import numpy as np

W, H = 2560, 1440
SHADOW_LO, SHADOW_HI = 12.0, 110.0  # 8-bit displayed level


def means(d, per):
    ph = {}
    for p in sorted(Path(d).glob("frame-*.nv12")):
        n = int(p.stem.split("-")[1])
        ph.setdefault(n // per, []).append(np.fromfile(p, np.uint8)[:W * H].reshape(H, W).astype(np.float32))
    return {k: np.mean(v, 0) for k, v in ph.items()}


def shadow_fraction(y):
    r = y[:H // 32 * 32, :].reshape(32, H // 32, 32, W // 32).mean((1, 3))
    return float(((r >= SHADOW_LO) & (r <= SHADOW_HI)).mean())


def main():
    per = int(sys.argv[1])
    ref, opn = means(sys.argv[2], per), means(sys.argv[3], per)
    frac = {k: shadow_fraction(opn[k]) for k in sorted(opn)}
    # Quantile matching on smoothed flat areas: robust to noise and to the small
    # misregistration between boots, unlike per-pixel binning.
    def box(img, r):
        c = np.cumsum(np.cumsum(np.pad(img, ((r + 1, r), (r + 1, r)), mode="edge"), 0), 1)
        k = 2 * r + 1
        return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)
    sa, sb = box(opn[1], 4), box(ref[1], 4)
    g = np.abs(np.diff(sa, axis=1, prepend=sa[:, :1])) + np.abs(np.diff(sa, axis=0, prepend=sa[:1]))
    flat = (box(g, 4) < 1.0) & (sa < 245) & (sb < 245)
    q = np.linspace(0.5, 99.5, 199)
    qa, qb = np.percentile(sa[flat], q), np.percentile(sb[flat], q)
    qa, idx = np.unique(qa, return_index=True)
    qb = np.maximum.accumulate(qb[idx])
    lv = np.arange(256)
    lift = np.interp(lv, qa, qb - qa, left=0.0, right=0.0)
    good = (lv >= qa.min()) & (lv <= qa.max())
    top = int(qa.max())
    lift[lv > top] *= np.clip((255 - lv[lv > top]) / max(255 - top, 1), 0, 1)
    lift[:3] = 0
    lift = np.convolve(np.pad(lift, 8, mode="edge"), np.ones(17) / 17, mode="valid")
    pts = [int(round(4 * float(np.interp(o / 4, lv, lift)))) for o in range(0, 1025, 64)]
    pts[0] = 0
    pts[-1] = 0
    lines = Path(sys.argv[4]).read_text().rstrip("\n").splitlines()
    lines = [l for l in lines if not l.startswith("tone_")]
    lo, hi = frac[0], frac[1]
    lines += [f"tone_dark_lift: [{', '.join(str(p) for p in pts)}]",
              f"tone_shadow_lo: {4 * SHADOW_LO:.0f}", f"tone_shadow_hi: {4 * SHADOW_HI:.0f}",
              f"tone_dark_low: {lo:.3f}", f"tone_dark_high: {hi:.3f}", "tone_speed: 0.05"]
    Path(sys.argv[5]).write_text("\n".join(lines) + "\n")
    print(json.dumps({"shadow_fraction": frac, "measured_levels": int(good.sum()),
                      "lift_u10": pts, "out": sys.argv[5]}))


if __name__ == "__main__":
    main()
