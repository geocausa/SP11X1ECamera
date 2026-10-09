#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Analyse the Windows rear reference run 62 (records.csv) against the SP7 log.

Same ROI selection, alignment and per-pattern statistics as run 61, so the
Windows and Linux tables are directly comparable. Scalars only on stdout.
"""
import csv, json, runpy, sys
from pathlib import Path

A = runpy.run_path(str(Path(__file__).with_name("analyze-pattern61.py")))
mean, corr, displayed, luminance, load_play = A["mean"], A["corr"], A["displayed"], A["luminance"], A["load_play"]
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
            recs.append(dict(phase=int(p[0]), rt=float(p[1]), exp=p[3], auto=p[4], iso=p[5],
                             y=g[:N], u=g[N:2 * N], v=g[2 * N:]))
    return recs


def main():
    recs = load_csv(sys.argv[1])
    play = load_play(sys.argv[2])
    names = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8-sig"))["phases"] if len(sys.argv) > 3 else None
    ref = [r for r in recs if r["phase"] == 1] or recs
    ref = ref[::3]
    best = (-2, 0.0)
    cands = [k * 0.1 for k in range(-900, 901)]
    def score(off):
        xs, ys = [], []
        for r in ref:
            s = displayed(play, r["rt"] + off)
            if s:
                xs.append(luminance(s)); ys.append(mean(r["y"]))
        return corr(xs, ys) if len(xs) > 100 else -2
    coarse = max(cands, key=score)
    for k in range(-20, 21):
        off = coarse + k * 0.01
        xs, ys = [], []
        for r in ref:
            s = displayed(play, r["rt"] + off)
            if s:
                xs.append(luminance(s)); ys.append(mean(r["y"]))
        if len(xs) > 100:
            c = corr(xs, ys)
            if c > best[0]:
                best = (c, off)
    c0, offset = best
    cell = []
    for c in range(N):
        xs, ys = [], []
        for r in ref:
            s = displayed(play, r["rt"] + offset)
            if s:
                xs.append(luminance(s)); ys.append(r["y"][c])
        cell.append(corr(xs, ys) if xs else 0.0)
    roi = [c for c in range(N) if cell[c] >= 0.97] or sorted(range(N), key=lambda c: -cell[c])[:12]
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
            a = acc.setdefault(s["id"], dict(y=[], u=[], v=[], e=[], i=[], rgb=(s["r"], s["g"], s["b"])))
            a["y"].append(mean(r["y"][c] for c in roi))
            a["u"].append(mean(r["u"][c] for c in roi))
            a["v"].append(mean(r["v"][c] for c in roi))
            a["e"].append(r["exp"]); a["i"].append(r["iso"])
        phases.append(dict(phase=ph, name=(names[ph]["name"] if names and ph < len(names) else None), frames=len(rows),
                           patterns={k: dict(rgb=v["rgb"], frames=len(v["y"]), Y=round(mean(v["y"]), 2),
                                             U=round(mean(v["u"]), 2), V=round(mean(v["v"]), 2),
                                             exposure_ticks=sorted(set(v["e"]))[:3], iso=sorted(set(v["i"]))[:3])
                                     for k, v in acc.items()}))
    span = recs[-1]["rt"] - recs[0]["rt"] if len(recs) > 1 else 0
    print(json.dumps(dict(frames=len(recs), fps=round((len(recs) - 1) / span, 2) if span else 0,
                          clock_offset_s=round(offset, 3), alignment_correlation=round(c0, 4),
                          roi_cells=len(roi), roi_cols=sorted({c % 16 for c in roi}),
                          cell_corr_grid=[[round(cell[y * 16 + x], 2) for x in range(16)] for y in range(9)],
                          phases=phases), indent=1))


if __name__ == "__main__":
    main()
