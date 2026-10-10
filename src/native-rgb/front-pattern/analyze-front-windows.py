#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Analyse the Windows front reference (records.csv) against the SP7 log.

Same ROI selection, alignment and per-pattern statistics as the Linux front
analysis so both tables are directly comparable. Scalars only on stdout.
"""
import json, os, runpy, sys
from pathlib import Path

A = runpy.run_path(str(Path(__file__).with_name("analyze-front-pattern.py")))
mean, corr, displayed, luminance, load_play, align = (A[k] for k in
    ("mean", "corr", "displayed", "luminance", "load_play", "align"))
N = 144


def load_csv(path):
    recs = []
    with open(path, encoding="utf-8-sig") as f:
        next(f)
        for line in f:
            p = line.rstrip("\r\n").split(",")
            if len(p) < 6 + 3 * N:
                continue
            g = [float(x) for x in p[6:6 + 3 * N]]
            recs.append(dict(phase=int(p[0]), rt=float(p[1]), ticks=int(p[2]), exp=p[3], auto=p[4],
                             y=g[:N], u=g[N:2 * N], v=g[2 * N:]))
    # Rebuild wall time from the monotonic SystemRelativeTime (100 ns ticks)
    # with the final frames' offset, removing any clock step during the run.
    good = [r for r in recs if r["ticks"] > 0]
    if len(good) == len(recs) and recs:
        tail = sorted(r["rt"] - r["ticks"] / 1e7 for r in recs[-100:])
        delta = tail[len(tail) // 2]
        for r in recs:
            r["rt"] = r["ticks"] / 1e7 + delta
    return recs


def main():
    recs = load_csv(sys.argv[1])
    play = load_play(sys.argv[2])
    roi_phase = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    ref = [r for r in recs if r["phase"] == roi_phase] or recs
    var = [sum((r["y"][c] - mean(q["y"][c] for q in ref[::10])) ** 2 for r in ref[::10]) for c in range(N)]
    key_cell = max(range(N), key=lambda c: var[c])
    c0, offset = align(ref, play, lambda r: r["y"][key_cell])
    cell = []
    for c in range(N):
        xs, ys = [], []
        for r in ref:
            s = displayed(play, r["rt"] + offset)
            if s:
                xs.append(luminance(s)); ys.append(r["y"][c])
        cell.append(corr(xs, ys) if xs else 0.0)
    roi = [c for c in range(N) if cell[c] >= 0.97] or sorted(range(N), key=lambda c: -cell[c])[:12]
    if os.environ.get("FRONT_ROI"):  # "rows:cols" override, see analyze-front-pattern.py
        rr, cc = os.environ["FRONT_ROI"].split(":")
        roi = [int(r) * 16 + int(c) for r in rr.split(",") for c in cc.split(",")]
    phases = []
    for ph in sorted({r["phase"] for r in recs}):
        rows = [r for r in recs if r["phase"] == ph]
        acc = {}
        for i, r in enumerate(rows):
            if i < 15:
                continue
            t = r["rt"] + offset
            s = displayed(play, t)
            if not s or t - s["start"] < 0.35 or s["start"] + s["hold"] - t < 0.35:
                continue
            a = acc.setdefault(s["id"], dict(y=[], u=[], v=[], e=[], rgb=(s["r"], s["g"], s["b"])))
            a["y"].append(mean(r["y"][c] for c in roi))
            a["u"].append(mean(r["u"][c] for c in roi))
            a["v"].append(mean(r["v"][c] for c in roi))
            a["e"].append(r["exp"])
        phases.append(dict(phase=ph, frames=len(rows),
                           exposure_ticks=sorted({r["exp"] for r in rows})[:4],
                           patterns={k: dict(rgb=v["rgb"], frames=len(v["y"]), Y=round(mean(v["y"]), 2),
                                             U=round(mean(v["u"]), 2), V=round(mean(v["v"]), 2),
                                             exposure_ticks=sorted(set(v["e"]))[:3])
                                     for k, v in sorted(acc.items())}))
    span = recs[-1]["rt"] - recs[0]["rt"] if len(recs) > 1 else 0
    print(json.dumps(dict(frames=len(recs), fps=round((len(recs) - 1) / span, 2) if span else 0,
                          clock_offset_s=round(offset, 3), alignment_correlation=round(c0, 4),
                          roi_cells=len(roi), roi_rows=sorted({c // 16 for c in roi}),
                          roi_cols=sorted({c % 16 for c in roi}), phases=phases), indent=1))


if __name__ == "__main__":
    main()
