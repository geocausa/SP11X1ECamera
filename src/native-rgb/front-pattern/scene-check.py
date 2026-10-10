#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Whole-scene check of a fitted front tone/colour model.

Applies a fit (ccm_linear_RGB + gamma curves) to the mean 16x9 grid of a
linear Linux capture phase and compares every cell with the mean grid of a
Windows capture phase (same camera position). Optionally compares a direct
Linux capture phase instead (no model). Output: scalar error summary and the
per-row mean Y of both, no images.
Usage: scene-check.py <linux run dir> <lphase> <windows records.csv> <wphase> [fit.json|-]
"""
import csv, json, struct, sys
from pathlib import Path
import numpy as np

GX, GY = 16, 9
N = GX * GY
REC = struct.Struct("<IIQQ" + "f" * (3 * N))
M = np.array([[0.299, 0.587, 0.114], [-0.168736, -0.331264, 0.5], [0.5, -0.418688, -0.081312]])
Mi = np.linalg.inv(M)
X = np.linspace(0, 1023, 257)


def linux_grid(run, phase):
    d = (Path(run) / "private-pattern/records.bin").read_bytes()
    acc = []
    for i in range(len(d) // REC.size):
        v = REC.unpack_from(d, i * REC.size)
        if v[1] == phase:
            acc.append(v[4:])
    a = np.array(acc[30:], float)
    return a.mean(0).reshape(3, N).T  # cells x (Y,U,V)


def windows_grid(path, phase):
    acc = []
    with open(path, newline="") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if row and int(row[0]) == phase:
                acc.append([float(x) for x in row[6:6 + 3 * N]])
    a = np.array(acc[30:], float)
    # Windows grid layout: per cell? detect by comparing with expectation below
    return a.mean(0)


def main():
    L = linux_grid(sys.argv[1], int(sys.argv[2]))
    Wraw = windows_grid(sys.argv[3], int(sys.argv[4]))
    W = Wraw.reshape(3, N).T
    fit = sys.argv[5] if len(sys.argv) > 5 else "-"
    if fit != "-":
        F = json.load(open(fit))
        K = np.array(F["ccm_linear_RGB"]); cv = [np.array(F[k], float) for k in ("gamma_r", "gamma_g", "gamma_b")]
        P = []
        for y, u, v in L:
            rgb = K @ (Mi @ np.array([y, u - 128, v - 128]) * 1023 / 255)
            g = np.array([np.interp(np.clip(rgb[c], 0, 1023), X, cv[c]) for c in range(3)])
            P.append(M @ (g * 255 / 1023) + [0, 128, 128])
        P = np.array(P)
    else:
        P = L
    dY = P[:, 0] - W[:, 0]; dC = np.hypot(P[:, 1] - W[:, 1], P[:, 2] - W[:, 2])
    print(json.dumps(dict(mean_Y_pred=round(float(P[:, 0].mean()), 1), mean_Y_win=round(float(W[:, 0].mean()), 1),
                          mean_abs_dY=round(float(np.abs(dY).mean()), 1), median_dY=round(float(np.median(dY)), 1),
                          mean_dC=round(float(dC.mean()), 1),
                          rows_pred=[round(float(P[r * GX:(r + 1) * GX, 0].mean())) for r in range(GY)],
                          rows_win=[round(float(W[r * GX:(r + 1) * GX, 0].mean())) for r in range(GY)],
                          row0_pred=[round(float(x)) for x in P[:GX, 0]], row0_win=[round(float(x)) for x in W[:GX, 0]],
                          row0_predUV=[[round(float(a)), round(float(b))] for a, b in P[:GX:3, 1:]],
                          row0_winUV=[[round(float(a)), round(float(b))] for a, b in W[:GX:3, 1:]])))


if __name__ == "__main__":
    main()
