#!/usr/bin/env python3
"""Per-frame stats of RAW10 packed 644x604 (816 B/line) captures; optional PNG of the last frame (auto-stretched).
Usage: ir-stats.py file.raw [out.png]"""
import sys, zlib, struct
W, H, B = 644, 604, 816
d = open(sys.argv[1], 'rb').read()
fs = B * H
n = len(d) // fs
def frame(k):
    out = []
    base = k * fs
    for y in range(H):
        r = d[base + y * B: base + y * B + 805]
        row = []
        for i in range(0, 805, 5):
            l = r[i + 4]
            for j in range(4):
                row.append((r[i + j] << 2) | ((l >> (2 * j)) & 3))
        out.append(row)
    return out
for k in range(n):
    f = frame(k)
    vals = sorted(v for row in f[::8] for v in row[::8])
    m = sum(vals) / len(vals)
    print("frame %d mean %.1f p1 %d p50 %d p99 %d max %d" % (k, m, vals[len(vals)//100], vals[len(vals)//2], vals[len(vals)*99//100], vals[-1]))
if len(sys.argv) > 2:
    lo, hi = vals[len(vals)//200], vals[len(vals)*995//1000]
    hi = max(hi, lo + 1)
    raw = b''.join(b'\0' + bytes(min(255, max(0, (v - lo) * 255 // (hi - lo))) for v in row) for row in f)
    def ch(t, b): return struct.pack('>I', len(b)) + t + b + struct.pack('>I', zlib.crc32(t + b) & 0xffffffff)
    open(sys.argv[2], 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 0, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw, 6)) + ch(b'IEND', b''))
    print("png", sys.argv[2], "stretch", lo, hi)
