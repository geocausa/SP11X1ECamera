#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fit the webcam bridge "look" of one camera against a same-scene Windows reference.

Both captures are scaled to the bridge output (1920x1080) with the bridge's own
bilinear resampler, then:
  tone     Y lookup table by quantile matching (Linux -> Windows), monotone, smoothed
  colour   chroma gain (p95 chroma magnitude ratio) and neutral U/V offset
  detail   unsharp-mask amount matching the Windows edge-gradient p99
  noise    temporal filter strength matching the Windows temporal noise (mid levels)
Usage: fit-look.py <W> <H> "<linux glob>" "<windows glob>" <out.look>
Writes a small text file the bridge reads (key value...). Prints scalar JSON.
"""
import glob, json, sys
import numpy as np

OW, OH = 1920, 1080


def axis(src, dst):
    s = (np.arange(dst) + 0.5) * src / dst - 0.5
    s = np.clip(s, 0, src - 1)
    i0 = np.minimum(s.astype(int), src - 2)
    w1 = np.round((s - i0) * 256).astype(np.int64)
    return i0, w1


def resample(p, oh, ow):
    """Bridge-identical bilinear (8-bit weights, rounding)."""
    h, w = p.shape
    yi, yw = axis(h, oh)
    xi, xw = axis(w, ow)
    p = p.astype(np.int64)
    a, b = p[yi][:, xi], p[yi][:, xi + 1]
    c, d = p[yi + 1][:, xi], p[yi + 1][:, xi + 1]
    t = a * (256 - xw) + b * xw
    u = c * (256 - xw) + d * xw
    return ((t * (256 - yw[:, None]) + u * yw[:, None] + 32768) >> 16).astype(np.float32)


def load(pattern, W, H):
    ys, us, vs = [], [], []
    for f in sorted(glob.glob(pattern)):
        b = np.fromfile(f, np.uint8)[: W * H * 3 // 2]
        y = b[: W * H].reshape(H, W)
        uv = b[W * H:].reshape(H // 2, W // 2, 2)
        ys.append(resample(y, OH, OW))
        us.append(resample(uv[..., 0], OH, OW // 2))
        vs.append(resample(uv[..., 1], OH, OW // 2))
    return np.stack(ys), np.stack(us), np.stack(vs)


def box3(a):
    p = np.pad(a, 1, mode="edge")
    return sum(p[i:i + a.shape[0], j:j + a.shape[1]] for i in range(3) for j in range(3)) / 9


def grad_p99(m):
    gx = np.abs(m[:, 2:] - m[:, :-2]) / 2
    gy = np.abs(m[2:] - m[:-2]) / 2
    return float(np.percentile(np.hypot(gx[1:-1], gy[:, 1:-1]), 99))


def sharpen(y, amount, core=2.0):
    d = y - box3(y)
    d = np.sign(d) * np.maximum(np.abs(d) - core, 0)
    return np.clip(y + amount * d, 0, 255)


def tnr(frames, k, thr):
    out, prev = [], None
    for f in frames:
        if prev is None:
            cur = f
        else:
            d = np.abs(f - prev)
            w = k * np.clip(1 - d / thr, 0, 1)
            cur = f + w * (prev - f)
        out.append(cur)
        prev = cur
    return np.stack(out)


def noise_mid(frames, ref_mean):
    s = frames.std(0, ddof=1)
    flat = box3(np.abs(ref_mean - box3(ref_mean))) < 1.5
    sel = flat & (ref_mean > 40) & (ref_mean < 200)
    return float(s[sel].mean())


def main():
    W, H = int(sys.argv[1]), int(sys.argv[2])
    ly, lu, lv = load(sys.argv[3], W, H)
    wy, wu, wv = load(sys.argv[4], W, H)
    lm, wm = ly.mean(0), wy.mean(0)
    # tone: quantile matching on the mean frames
    q = np.linspace(0, 100, 201)
    lq, wq = np.percentile(lm, q), np.percentile(wm, q)
    x = np.arange(256, dtype=np.float64)
    lut = np.interp(x, lq, wq)
    # outside the observed range: straight lines to (0, 0) and (255, 255)
    lo, hi = x < lq[0], x > lq[-1]
    lut[lo] = x[lo] * wq[0] / max(lq[0], 1e-3)
    lut[hi] = wq[-1] + (x[hi] - lq[-1]) * (255 - wq[-1]) / max(255 - lq[-1], 1e-3)
    lut = np.convolve(np.pad(lut, 4, mode="edge"), np.ones(9) / 9, mode="valid")
    lut = np.maximum.accumulate(np.clip(lut, 0, 255))
    toned = np.interp(lm, np.arange(256), lut)
    # colour
    lc = np.hypot(lu.mean(0) - 128, lv.mean(0) - 128)
    wc = np.hypot(wu.mean(0) - 128, wv.mean(0) - 128)
    cgain = float(np.clip(np.percentile(wc, 95) / max(np.percentile(lc, 95), 1e-3), 0.5, 2.5))
    lus, lvs = (lu.mean(0) - 128) * cgain, (lv.mean(0) - 128) * cgain
    wus, wvs = wu.mean(0) - 128, wv.mean(0) - 128

    def neutral(u, v, y):
        c = np.hypot(u, v)
        yy = y[:, ::2][:, : u.shape[1]]
        sel = (c <= np.percentile(c, 20)) & (yy > 40) & (yy < 230)
        return float(u[sel].mean()), float(v[sel].mean())

    ln, wn = neutral(lus, lvs, toned), neutral(wus, wvs, wm)
    uoff, voff = float(np.clip(wn[0] - ln[0], -12, 12)), float(np.clip(wn[1] - ln[1], -12, 12))
    # noise: temporal filter on the toned sequence
    tseq = np.interp(ly, np.arange(256), lut)
    target = noise_mid(wy, wm)
    best = (1e9, 0.0)
    for k in np.arange(0.0, 0.71, 0.05):  # stronger smoothing ghosts on motion
        n = noise_mid(tnr(tseq, k, 12.0)[2:], toned)
        best = min(best, (abs(n - target), float(k)))
    k = best[1]
    filt = tnr(tseq, k, 12.0)[-1]
    # detail
    wg = grad_p99(wm)
    best = (1e9, 0.0)
    for a in np.arange(0.0, 1.51, 0.1):  # stronger sharpening amplifies noise and halos
        best = min(best, (abs(grad_p99(sharpen(filt, a)) - wg), float(a)))
    amount = best[1]
    with open(sys.argv[5], "w") as f:
        f.write("# sp11-webcam look v1 (fit-look.py)\n")
        f.write("lut " + " ".join(str(int(round(x))) for x in lut) + "\n")
        f.write(f"chroma_gain {cgain:.3f}\nu_offset {uoff:.2f}\nv_offset {voff:.2f}\n")
        f.write(f"sharpen {amount:.2f}\nsharpen_core 2.0\ntnr_strength {k:.2f}\ntnr_threshold 12\n")
    print(json.dumps({"lut_at": {str(i): int(round(lut[i])) for i in (0, 16, 32, 64, 96, 128, 160, 192, 224, 255)},
                      "chroma_gain": round(cgain, 3), "u_offset": round(uoff, 2), "v_offset": round(voff, 2),
                      "tnr_strength": k, "noise_target": round(target, 2),
                      "noise_linux_toned": round(noise_mid(tseq[2:], toned), 2),
                      "noise_after": round(noise_mid(tnr(tseq, k, 12.0)[2:], toned), 2),
                      "sharpen": amount, "edge_windows": round(wg, 2), "edge_linux_toned": round(grad_p99(toned), 2),
                      "edge_after": round(grad_p99(sharpen(filt, amount)), 2)}))


if __name__ == "__main__":
    main()
