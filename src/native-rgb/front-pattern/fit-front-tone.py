#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fit independent front tone curves (and report the colour gap) from the
Linux linear-gamma pattern run and the Windows reference run.

Both NV12 streams are interpreted with the same BT.601 full-range matrix, so
the fitted per-channel curves reproduce the Windows YUV values through the
Linux CST regardless of the Windows range convention. Scalars only.
Usage: fit-front-tone.py linux.json windows.json [linux_phase] [windows_phase]
"""
import json, sys

GREYS = ["grey_0", "grey_8", "grey_16", "grey_32", "grey_48", "grey_64", "grey_96",
         "grey_128", "grey_160", "grey_192", "grey_224", "grey_255"]
COLOURS = ["red", "green", "blue", "cyan", "magenta", "yellow", "red50", "green50", "blue50"]


def rgb(p):
    y, u, v = p["Y"], p["U"] - 128, p["V"] - 128
    return [y + 1.402 * v, y - 0.344136 * u - 0.714136 * v, y + 1.772 * u]


def yuv(c):
    r, g, b = c
    y = 0.299 * r + 0.587 * g + 0.114 * b
    return [y, 128 + 0.564 * (b - y), 128 + 0.713 * (r - y)]


def interp(xs, ys, x):
    if x <= xs[0]:
        return ys[0] + (x - xs[0]) * (ys[1] - ys[0]) / (xs[1] - xs[0])
    for i in range(1, len(xs)):
        if x <= xs[i]:
            t = (x - xs[i - 1]) / (xs[i] - xs[i - 1])
            return ys[i - 1] + t * (ys[i] - ys[i - 1])
    return ys[-1] + (x - xs[-1]) * (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])


def monotone(points):
    pts = sorted(points)
    xs, ys = [], []
    for x, y in pts:
        if xs and x <= xs[-1] + 1e-6:
            continue
        y = max(y, ys[-1] + 1e-3) if ys else y
        xs.append(x); ys.append(y)
    return xs, ys


def main():
    L = json.load(open(sys.argv[1]))
    W = json.load(open(sys.argv[2]))
    lp = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    wp = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    lin = L["phases"][lp]["patterns"]
    win = W["phases"][wp]["patterns"]
    curves = []
    for ch in range(3):
        curves.append(monotone([(rgb(lin[g])[ch], rgb(win[g])[ch]) for g in GREYS if g in lin and g in win]))
    out = {"linux_phase": L["phases"][lp].get("again"), "linux_dgain": L["phases"][lp].get("dgain"),
           "windows_phase": wp, "curve_points": [[[round(a, 2), round(b, 2)] for a, b in zip(*c)] for c in curves]}
    res = []
    for name in GREYS + COLOURS:
        if name not in lin or name not in win:
            continue
        pred = yuv([interp(*curves[ch], rgb(lin[name])[ch]) for ch in range(3)])
        w = [win[name][k] for k in "YUV"]
        res.append({"pattern": name, "windows": [round(x, 1) for x in w],
                    "linux_linear": [lin[name][k] for k in "YUV"],
                    "predicted": [round(x, 1) for x in pred],
                    "dY": round(pred[0] - w[0], 1),
                    "dC": round(((pred[1] - w[1]) ** 2 + (pred[2] - w[2]) ** 2) ** 0.5, 1),
                    "sat_ratio": round(((pred[1] - 128) ** 2 + (pred[2] - 128) ** 2) ** 0.5 /
                                       max(1e-6, ((w[1] - 128) ** 2 + (w[2] - 128) ** 2) ** 0.5), 3)})
    out["residuals"] = res
    col = [r for r in res if r["pattern"] in COLOURS]
    out["colour_mean_abs_dY"] = round(sum(abs(r["dY"]) for r in col) / len(col), 2)
    out["colour_mean_dC"] = round(sum(r["dC"] for r in col) / len(col), 2)
    out["colour_mean_sat_ratio"] = round(sum(r["sat_ratio"] for r in col) / len(col), 3)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
