#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compare Linux captures with a Windows reference of the same scene (same camera pose).
Usage: compare-windows.py <W> <H> <name>=<glob> [<name>=<glob> ...]
The first set is the reference. Each glob selects NV12 frames of one set (one exposure state).
Prints scalar JSON only: luma quantiles, clipping, temporal noise by level, neutral colour cast,
chroma, sharpness, alignment to the reference and the luma transfer curve against it.
"""
import glob, json, sys
import numpy as np


def load(pattern, W, H):
    files = sorted(glob.glob(pattern))
    ys, uvs = [], []
    for f in files:
        b = np.fromfile(f, np.uint8)
        assert b.size == W * H * 3 // 2, f
        ys.append(b[:W * H].reshape(H, W).astype(np.float32))
        uvs.append(b[W * H:].reshape(H // 2, W // 2, 2).astype(np.float32))
    y = np.stack(ys); uv = np.stack(uvs)
    return dict(n=len(files), m=y.mean(0), s=y.std(0, ddof=1) if len(files) > 1 else None, uv=uv.mean(0))


def box(a, r):
    c = np.cumsum(np.cumsum(np.pad(a, ((r + 1, r), (r + 1, r)), mode="edge"), 0), 1)
    k = 2 * r + 1
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def grad(m):
    gx = np.zeros_like(m); gy = np.zeros_like(m)
    gx[:, 1:-1] = (m[:, 2:] - m[:, :-2]) / 2; gy[1:-1] = (m[2:] - m[:-2]) / 2
    return np.hypot(gx, gy)


def small(m, f):
    H, W = m.shape
    return m[:H // f * f, :W // f * f].reshape(H // f, f, W // f, f).mean((1, 3))


def align(ref, m, f=8):
    a = small(ref, f); b = small(m, f)
    a = a - a.mean(); b = b - b.mean()
    X = np.fft.fft2(a) * np.conj(np.fft.fft2(b))
    c = np.fft.ifft2(X / np.maximum(np.abs(X), 1e-9)).real
    dy, dx = np.unravel_index(np.argmax(c), c.shape)
    if dy > c.shape[0] // 2: dy -= c.shape[0]
    if dx > c.shape[1] // 2: dx -= c.shape[1]
    bs = np.roll(b, (dy, dx), (0, 1))
    ncc = float((a * bs).sum() / np.sqrt((a * a).sum() * (bs * bs).sum()))
    return int(dy * f), int(dx * f), round(ncc, 4)


def stats(s, W, H):
    m = s["m"]; uv = s["uv"]
    r = {"frames": s["n"]}
    q = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    r["y_quantiles"] = dict(zip(map(str, q), [round(float(v), 1) for v in np.percentile(m, q)]))
    r["clip_hi"] = round(float((m >= 250).mean()), 4)
    r["clip_lo"] = round(float((m <= 17).mean()), 4)
    g = grad(box(m, 1))
    flat = (box(g, 4) < 1.5)
    lv = np.clip((m // 32).astype(int), 0, 7)
    if s["s"] is not None:
        r["noise_by_level"] = [round(float(s["s"][flat & (lv == i)].mean()), 2) if (flat & (lv == i)).sum() > 2000 else None
                               for i in range(8)]
    m2 = m[::2, ::2][:uv.shape[0], :uv.shape[1]]
    du = uv[..., 0] - 128; dv = uv[..., 1] - 128
    chroma = np.hypot(du, dv)
    r["chroma_mean"] = round(float(chroma.mean()), 2)
    r["chroma_p95"] = round(float(np.percentile(chroma, 95)), 2)
    neutral = (chroma <= np.percentile(chroma, 20)) & (m2 > 40) & (m2 < 230)
    r["neutral_u"] = round(float(du[neutral].mean()), 2)
    r["neutral_v"] = round(float(dv[neutral].mean()), 2)
    r["global_u"] = round(float(du.mean()), 2)
    r["global_v"] = round(float(dv.mean()), 2)
    r["edge_grad_p99"] = round(float(np.percentile(grad(m), 99)), 2)
    lap = 4 * m[1:-1, 1:-1] - m[:-2, 1:-1] - m[2:, 1:-1] - m[1:-1, :-2] - m[1:-1, 2:]
    r["laplace_rms"] = round(float(np.sqrt((lap ** 2).mean())), 2)
    return r


def main():
    W, H = int(sys.argv[1]), int(sys.argv[2])
    sets = [a.split("=", 1) for a in sys.argv[3:]]
    ref = None; out = {}
    for name, pat in sets:
        s = load(pat, W, H)
        r = stats(s, W, H)
        if ref is None:
            ref = s
        else:
            dy, dx, ncc = align(ref["m"], s["m"])
            r["align_dy_dx_ncc"] = [dy, dx, ncc]
            a = ref["m"]; b = np.roll(s["m"], (dy, dx), (0, 1))
            pad = max(abs(dy), abs(dx)) + 8
            a = a[pad:-pad, pad:-pad]; b = b[pad:-pad, pad:-pad]
            edges = np.arange(0, 257, 16)
            idx = np.clip(np.digitize(a, edges) - 1, 0, 15)
            r["transfer_vs_ref"] = [round(float(np.median(b[idx == i])), 1) if (idx == i).sum() > 5000 else None
                                    for i in range(16)]
        out[name] = r
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
