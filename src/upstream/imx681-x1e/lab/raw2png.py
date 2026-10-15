#!/usr/bin/env python3
"""MIPI RAW10 packed (RGGB) frame -> quick-look PNG (2x2 binned demosaic, grey-world WB, sRGB gamma).
Usage: raw2png.py raw.bin W H bytesperline out.png [frame-index]"""
import sys, zlib, struct
import numpy as np
f, W, H, bpl, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
idx = int(sys.argv[6]) if len(sys.argv) > 6 else -1
d = np.fromfile(f, np.uint8)
n = len(d) // (bpl * H)
fr = d[(idx % n) * bpl * H:((idx % n) + 1) * bpl * H].reshape(H, bpl)[:, :W * 5 // 4].reshape(H, -1, 5).astype(np.uint16)
px = np.empty((H, fr.shape[1], 4), np.uint16)
for k in range(4):
    px[..., k] = (fr[..., k] << 2) | ((fr[..., 4] >> (2 * k)) & 3)
raw = px.reshape(H, -1)[:, :W].astype(np.float32)
print("frames", n, "raw min/mean/max", raw.min(), round(float(raw.mean()), 1), raw.max())
black = 64.0
r = raw[0::2, 0::2]; g = (raw[0::2, 1::2] + raw[1::2, 0::2]) / 2; b = raw[1::2, 1::2]
h2, w2 = min(r.shape[0], b.shape[0]), min(r.shape[1], b.shape[1])
rgb = np.stack([r[:h2, :w2], g[:h2, :w2], b[:h2, :w2]], -1) - black
rgb = np.clip(rgb, 0, None)
m = rgb.reshape(-1, 3).mean(0)
print("mean R G B (minus 64)", [round(float(x), 1) for x in m])
rgb *= (m[1] / np.maximum(m, 1e-3))
rgb /= max(np.percentile(rgb, 99.5), 1)
img = (np.clip(rgb, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)[::2, ::2]
h, w, _ = img.shape
rows = b"".join(b"\x00" + img[y].tobytes() for y in range(h))
chunk = lambda t, c: struct.pack(">I", len(c)) + t + c + struct.pack(">I", zlib.crc32(t + c) & 0xffffffff)
open(out, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows, 6)) + chunk(b"IEND", b""))
print("png", out, w, h)
