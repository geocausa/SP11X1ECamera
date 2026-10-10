#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Infer the Windows front AE metering weights and output-domain target.

A converged AE holds its metering statistic constant while the scene changes.
For the Windows automatic phase we evaluate centre-weighted Gaussian weight
maps on the 16x9 output-luma grid and pick the one whose weighted mean is the
most constant across the bright displayed fields (dark fields can saturate the
exposure range and are excluded). Output: centre, sigma, target (8-bit Y).
Usage: fit-windows-metering.py windows-records.csv play-log offset_s
"""
import json, math, runpy, sys
from pathlib import Path

H = Path(__file__).with_name
A = runpy.run_path(str(H("analyze-front-pattern.py")))
W = runpy.run_path(str(H("analyze-front-windows.py")))
BRIGHT = {"grey_96", "grey_128", "grey_160", "grey_192", "grey_224", "grey_255", "grey_128b",
          "red", "green", "blue", "cyan", "magenta", "yellow", "green50", "sync_w0", "sync_w1"}


def main():
    recs = [r for r in W["load_csv"](sys.argv[1]) if r["phase"] == 0]
    play = A["load_play"](sys.argv[2])
    off = float(sys.argv[3])
    rows = []
    for r in recs[60:]:
        t = r["rt"] + off
        s = A["displayed"](play, t)
        if s and s["id"] in BRIGHT and t - s["start"] > 1.2 and s["start"] + s["hold"] - t > 0.1:
            rows.append((s["id"], r["y"]))
    best = None
    for cy in [3.0, 4.0, 5.0, 6.0]:
        for cx in [6.5, 7.5, 8.5]:
            for sig in [1.5, 2.0, 3.0, 4.0, 6.0, 100.0]:
                w = [math.exp(-(((c % 16) - cx) ** 2 + ((c // 16) - cy) ** 2) / (2 * sig * sig)) for c in range(144)]
                sw = sum(w)
                per = {}
                for pid, y in rows:
                    per.setdefault(pid, []).append(sum(a * b for a, b in zip(w, y)) / sw)
                means = [sum(v) / len(v) for v in per.values()]
                m = sum(means) / len(means)
                cv = math.sqrt(sum((x - m) ** 2 for x in means) / len(means)) / m
                if not best or cv < best[0]:
                    best = (cv, cx, cy, sig, m, {k: round(sum(v) / len(v), 1) for k, v in per.items()})
    cv, cx, cy, sig, m, per = best
    print(json.dumps(dict(frames=len(rows), centre_col=cx, centre_row=cy, sigma_cells=sig,
                          target_y8=round(m, 1), cv=round(cv, 4), per_pattern=per), indent=1))


if __name__ == "__main__":
    main()
