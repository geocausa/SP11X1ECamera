#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fit our own lens-shading (LSC) table from a flat-field capture.

Input: a capture made with the IFE LSC module disabled and identity tone/CCM
(linear output), the camera pressed to a diffuser on a uniformly lit display.
The full NV12 frame (a known uniform grey) is block-averaged, converted to
linear RGB (BT.601 full range), and each channel is fitted with a smooth 2D
polynomial in log space, which is evaluated at the 17x13 LSC mesh nodes.
Gains: colour shading is equalised to green; the luma (green) correction is
applied with exponent `strength` (1.0 = flat; <1 leaves some vignetting to
limit corner noise). Centre gain is 1.0.

Mesh encoding (as programmed by the module, inferred from the register
format): 221 x u32 per DMI selector, row-major 13 rows x 17 columns;
bits 0-12 = channel gain, bits 14-26 = green gain, unsigned Q10.
Selector 1 = red/green, selector 2 = blue/green, selector 3 = zeros.
Usage: fit-lsc.py <frame.nv12> <out.bin> [strength] [--colour grid-ratios.json]
"""
import json, struct, sys
from pathlib import Path
import numpy as np

W, H = 2560, 1440
NX, NY = 17, 13
M = np.array([[0.299, 0.587, 0.114], [-0.168736, -0.331264, 0.5], [0.5, -0.418688, -0.081312]])
Mi = np.linalg.inv(M)


def frame_rgb_blocks(path, bx=40, by=40):
    d = np.frombuffer(Path(path).read_bytes(), np.uint8)
    Y = d[:W * H].reshape(H, W).astype(np.float64)
    UV = d[W * H:W * H * 3 // 2].reshape(H // 2, W // 2, 2).astype(np.float64)
    U = np.repeat(np.repeat(UV[..., 0], 2, 0), 2, 1); V = np.repeat(np.repeat(UV[..., 1], 2, 0), 2, 1)
    ny, nx = H // by, W // bx
    def blk(a):
        return a[:ny * by, :nx * bx].reshape(ny, by, nx, bx).mean((1, 3))
    yb, ub, vb = blk(Y), blk(U) - 128, blk(V) - 128
    rgb = np.einsum('ij,jyx->iyx', Mi, np.stack([yb, ub, vb]))
    cx = (np.arange(nx) + 0.5) * bx; cy = (np.arange(ny) + 0.5) * by
    return rgb, cx, cy


def design(x, y, deg=8):
    xn = x / (W - 1) * 2 - 1; yn = y / (H - 1) * 2 - 1
    cols = [xn ** p * yn ** q for p in range(deg + 1) for q in range(deg + 1 - p)]
    return np.stack(cols, -1)


def main():
    frame, out = sys.argv[1], sys.argv[2]
    strength = float(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else 0.82
    rgb, cx, cy = frame_rgb_blocks(frame)
    gx, gy = np.meshgrid(cx, cy)
    A = design(gx.ravel(), gy.ravel())
    nxg = np.arange(NX) / (NX - 1) * (W - 1); nyg = np.arange(NY) / (NY - 1) * (H - 1)
    mx, my = np.meshgrid(nxg, nyg)
    An = design(mx.ravel(), my.ravel())
    centre = design(np.array([(W - 1) / 2]), np.array([(H - 1) / 2]))
    falloff, rms = [], []
    for c in range(3):
        v = np.clip(rgb[c].ravel(), 1e-3, None)
        coef, *_ = np.linalg.lstsq(A, np.log(v), rcond=None)
        rms.append(float(np.std(np.log(v) - A @ coef)))
        f = np.exp(An @ coef - centre @ coef).reshape(NY, NX)  # relative to centre
        falloff.append(f)
    fr, fg, fb = falloff
    if '--colour' in sys.argv:
        # Colour shading from the 16x9 grid of many bright frames (better chroma SNR
        # than one dim full frame): smooth degree-4 fits of log(R/G), log(B/G).
        cg = json.load(open(sys.argv[sys.argv.index('--colour') + 1]))
        gx16, gy9 = np.meshgrid((np.arange(16) + 0.5) * W / 16, (np.arange(9) + 0.5) * H / 9)
        Ag = design(gx16.ravel(), gy9.ravel(), 4)
        An4 = design(mx.ravel(), my.ravel(), 4); c4 = design(np.array([(W - 1) / 2]), np.array([(H - 1) / 2]), 4)
        ratios = []
        for key in ('r_over_g', 'b_over_g'):
            v = np.log(np.clip(np.array(cg[key]), 1e-3, None))
            coef, *_ = np.linalg.lstsq(Ag, v, rcond=None)
            ratios.append(np.exp(An4 @ coef - c4 @ coef).reshape(NY, NX))
        fr, fb = fg * ratios[0], fg * ratios[1]
    gG = (1 / fg) ** strength
    gR = gG * fg / fr
    gB = gG * fg / fb
    q = lambda g: np.clip(np.round(g * 1024), 0, 8191).astype(np.uint32)
    sel1 = q(gR) | (q(gG) << 14)
    sel2 = q(gB) | (q(gG) << 14)
    sel3 = np.zeros_like(sel1)
    blob = sel1.astype('<u4').tobytes() + sel2.astype('<u4').tobytes() + sel3.astype('<u4').tobytes()
    Path(out).write_bytes(blob)
    summ = dict(strength=strength, fit_log_rms=[round(r, 4) for r in rms],
                falloff_corner=[round(float(np.mean([f[0, 0], f[0, -1], f[-1, 0], f[-1, -1]])), 3) for f in (fr, fg, fb)],
                falloff_edge_lr=[round(float((f[NY // 2, 0] + f[NY // 2, -1]) / 2), 3) for f in falloff],
                falloff_edge_tb=[round(float((f[0, NX // 2] + f[-1, NX // 2]) / 2), 3) for f in falloff],
                gain_corner_RGB=[round(float(np.mean([g[0, 0], g[0, -1], g[-1, 0], g[-1, -1]])), 2) for g in (gR, gG, gB)],
                gain_max=round(float(max(gR.max(), gG.max(), gB.max())), 2), bytes=len(blob))
    print(json.dumps(summ))


if __name__ == '__main__':
    main()
