#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Carry a bridge look over to a changed ISP path (same scene, same camera pose).

Given native NV12 captures of one static scene from the reference ISP path
(whose look is already fitted) and from the new ISP path, fit the native
correction new -> reference and fold it into the look:
  tone    Y lookup table from pixel-paired medians (isotonic, monotone), composed with the old lut
  chroma  per-axis linear fit (U_ref-128) = a (U_new-128) + b over chromatic pixels;
          u_gain *= a, u_offset += chroma_gain * u_gain * b (same for v)
Usage: match-look.py W H "<ref glob>" "<new glob>" old.look new.look
"""
import glob, json, sys
import numpy as np


def load(pattern, W, H):
    ys, us, vs = [], [], []
    for f in sorted(glob.glob(pattern)):
        b = np.fromfile(f, np.uint8)[: W * H * 3 // 2]
        ys.append(b[: W * H].reshape(H, W)[::2, ::2].astype(np.float32))
        uv = b[W * H:].reshape(H // 2, W // 2, 2).astype(np.float32)
        us.append(uv[..., 0]); vs.append(uv[..., 1])
    return np.mean(ys, 0), np.mean(us, 0), np.mean(vs, 0)


def read_look(path):
    keys, order = {}, []
    for ln in open(path):
        s = ln.strip()
        if not s or s.startswith("#"):
            order.append(("#", ln.rstrip("\n")))
            continue
        k, v = s.split(None, 1)
        keys[k] = v
        order.append((k, None))
    return keys, order


def main():
    W, H = int(sys.argv[1]), int(sys.argv[2])
    yr, ur, vr = load(sys.argv[3], W, H)
    yn, un, vn = load(sys.argv[4], W, H)
    keys, order = read_look(sys.argv[5])
    # tone: quantile matching new -> ref on the whole frame
    # same pose: pixel-paired medians per 4-code bin, then weighted isotonic fit
    xs, ms, ws = [0.0], [0.0], [1e6]
    for lo in range(0, 256, 4):
        sel = (yn >= lo) & (yn < lo + 4)
        if sel.sum() > 2000:
            xs.append(float(yn[sel].mean())); ms.append(float(np.median(yr[sel]))); ws.append(float(sel.sum()))
    xs.append(255.0); ms.append(255.0); ws.append(1e6)
    blocks = []  # pool adjacent violators
    for x, m, w in zip(xs, ms, ws):
        blocks.append([m * w, w, [x]])
        while len(blocks) > 1 and blocks[-2][0] / blocks[-2][1] > blocks[-1][0] / blocks[-1][1]:
            a = blocks.pop(); blocks[-1][0] += a[0]; blocks[-1][1] += a[1]; blocks[-1][2] += a[2]
    px = [np.mean(b[2]) for b in blocks]; py = [b[0] / b[1] for b in blocks]
    t = np.clip(np.interp(np.arange(256), px, py), 0, 255)
    t = np.maximum.accumulate(np.convolve(np.pad(t, 4, mode="edge"), np.ones(9) / 9, "valid"))
    lut = np.array([int(x) for x in keys["lut"].split()], float)
    new_lut = np.clip(np.round(np.interp(t, np.arange(256), lut)), 0, 255).astype(int)
    # chroma per axis over chromatic, unclipped pixels
    cg = float(keys.get("chroma_gain", "1"))
    res = {}
    for ax, (cr, cn) in (("u", (ur, un)), ("v", (vr, vn))):
        m = (np.abs(cn - 128) > 6) & (yr[: cn.shape[0], : cn.shape[1]] > 20) & (yr[: cn.shape[0], : cn.shape[1]] < 235)
        a, b = np.polyfit(cn[m] - 128, cr[m] - 128, 1)
        g = float(keys.get(ax + "_gain", "1"))
        off = float(keys.get(ax + "_offset", "0"))
        keys[ax + "_gain"] = "%.3f" % float(np.clip(g * a, 0.5, 2.0))
        keys[ax + "_offset"] = "%.2f" % (off + cg * g * b)
        res[ax] = {"slope": round(float(a), 3), "intercept": round(float(b), 2), "pixels": int(m.sum())}
    keys["lut"] = " ".join(str(v) for v in new_lut)
    out, done = [], set()
    for k, line in order:
        if k == "#":
            out.append(line)
        else:
            out.append("%s %s" % (k, keys[k])); done.add(k)
    out[0:0] = ["# carried over from %s by match-look.py (open rear ISP path, camss 50)" % sys.argv[5].split("/")[-1]]
    out += ["%s %s" % (k, keys[k]) for k in keys if k not in done]
    open(sys.argv[6], "w").write("\n".join(out) + "\n")
    res["tone_new_to_ref_at"] = {str(x): round(float(t[x]), 1) for x in (16, 32, 64, 96, 128, 160, 192, 224)}
    print(json.dumps(res))


if __name__ == "__main__":
    main()
