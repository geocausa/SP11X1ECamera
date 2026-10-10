#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compare front still captures of the static chart: baseline run vs module-ablation runs.
Position independent: every metric is computed per pixel against the baseline frames.
Usage: ablate-compare.py <frames-per-phase> <baseline-dir> <variant-dir> [...]
Each dir holds frame-<n>.nv12 (2560x1440 NV12). Prints scalar JSON only.
"""
import json, sys
from pathlib import Path
import numpy as np

W, H = 2560, 1440


def load(d, per):
    ph = {}
    for p in sorted(Path(d).glob("frame-*.nv12")):
        n = int(p.stem.split("-")[1])
        b = np.fromfile(p, np.uint8)
        y = b[:W * H].reshape(H, W).astype(np.float32)
        uv = b[W * H:].reshape(H // 2, W // 2, 2).astype(np.float32)
        ph.setdefault(n // per, []).append((y, uv))
    out = {}
    for k, fr in ph.items():
        ys = np.stack([f[0] for f in fr]); uvs = np.stack([f[1] for f in fr])
        out[k] = dict(m=ys.mean(0), s=ys.std(0, ddof=1) if len(fr) > 1 else np.zeros((H, W), np.float32),
                      uv=uvs.mean(0), uvs=uvs.std(0, ddof=1) if len(fr) > 1 else np.zeros((H // 2, W // 2, 2), np.float32),
                      n=len(fr))
    return out


def box(a, r):
    c = np.cumsum(np.cumsum(np.pad(a, ((r + 1, r), (r + 1, r)), mode="edge"), 0), 1)
    k = 2 * r + 1
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def grad(m):
    gx = np.zeros_like(m); gy = np.zeros_like(m)
    gx[:, 1:-1] = (m[:, 2:] - m[:, :-2]) / 2; gy[1:-1] = (m[2:] - m[:-2]) / 2
    return np.hypot(gx, gy)


def med3(m):
    p = np.pad(m, 1, mode="edge")
    st = np.stack([p[i:i + H, j:j + W] for i in range(3) for j in range(3)])
    return np.median(st, 0)


def checker(m):
    c = np.zeros_like(m)
    c[:-1, :-1] = (m[:-1, :-1] - m[:-1, 1:] - m[1:, :-1] + m[1:, 1:]) / 4
    return np.abs(c)


def metrics(base, var):
    m0 = base["m"]; m = var["m"]
    g0 = grad(box(m0, 1))
    flat = (box(g0, 4) < 1.5) & (m0 > 8) & (m0 < 245)
    edges = g0 >= np.percentile(g0, 98)
    lv = np.clip((m0 // 32).astype(int), 0, 7)
    r = {}
    r["frames"] = var["n"]
    r["flat_fraction"] = round(float(flat.mean()), 4)
    r["clip_fraction"] = round(float((m >= 250).mean()), 5)
    r["mean_abs_diff"] = round(float(np.abs(m - m0).mean()), 3)
    r["p99_abs_diff"] = round(float(np.percentile(np.abs(m - m0), 99)), 2)
    r["tone_by_level"] = [round(float(np.median(m[(lv == i)] - m0[(lv == i)])), 2) if (lv == i).any() else None
                          for i in range(8)]
    r["noise_by_level"] = [round(float(var["s"][flat & (lv == i)].mean()), 3) if (flat & (lv == i)).sum() > 500 else None
                           for i in range(8)]
    r["edge_strength_ratio"] = round(float(grad(m)[edges].mean() / max(grad(m0)[edges].mean(), 1e-6)), 4)
    lap = lambda a: (4 * a[1:-1, 1:-1] - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:])
    e = edges[1:-1, 1:-1]
    r["hf_energy_ratio_edges"] = round(float((lap(m)[e] ** 2).mean() / max((lap(m0)[e] ** 2).mean(), 1e-6)), 4)
    d = np.abs(m - med3(m))
    r["defects_flat_gt12"] = int(((d > 12) & flat).sum())
    r["defects_flat_gt6"] = int(((d > 6) & flat).sum())
    r["checker_flat"] = round(float(checker(m)[flat].mean()), 4)
    fl2 = flat[::2, ::2]
    for i, c in enumerate("uv"):
        r[f"{c}_mean_flat_delta"] = round(float((var["uv"][..., i] - base["uv"][..., i])[fl2].mean()), 3)
        r[f"{c}_noise_flat"] = round(float(var["uvs"][..., i][fl2].mean()), 3)
    return r


def main():
    per = int(sys.argv[1]); base = load(sys.argv[2], per)
    res = {}
    for d in sys.argv[2:]:
        v = load(d, per)
        res[Path(d).parent.name] = {f"phase{k}": metrics(base[k], v[k]) for k in sorted(v) if k in base}
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
