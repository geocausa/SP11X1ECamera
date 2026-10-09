#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Analyse a rear pattern calibration run.

Inputs (all private, SAME SP11):
  <run>/private-pattern/records.bin   per-frame 16x9 Y/U/V grid means
  <run>/PRIVATE-CAPTURE-STDERR.txt     NATIVE_REAR_METER raw meter per sequence
  <play-log.csv>                       SP7 player log (pattern id + UTC start)
Output: scalar JSON summary (no spatial arrays) on stdout.
"""
import csv, json, math, re, struct, sys
from datetime import datetime
from pathlib import Path

GX, GY = 16, 9
N = GX * GY
REC = struct.Struct("<IIQQ" + "f" * (3 * N))
PHASES = [(800, 1.0), (3206, 1.0), (3206, 2.0), (3206, 4.0), (3206, 8.0)]


def load_records(path):
    data = Path(path).read_bytes()
    assert len(data) % REC.size == 0, "record size"
    out = []
    for i in range(len(data) // REC.size):
        v = REC.unpack_from(data, i * REC.size)
        out.append(dict(seq=v[0], phase=v[1], comp=v[2], rt=v[3] / 1e9,
                        y=v[4:4 + N], u=v[4 + N:4 + 2 * N], v=v[4 + 2 * N:4 + 3 * N]))
    return out


def load_meter(path):
    m = {}
    for s, mv in re.findall(r"NATIVE_REAR_METER sequence=(\d+) timestamp=\d+ meter=([0-9.eE+-]+)",
                            Path(path).read_text(errors="replace")):
        m[int(s)] = float(mv)
    return m


def load_play(path):
    steps = []
    for row in csv.DictReader(open(path, encoding="utf-8-sig")):
        if row["loop"] == "done" or not row.get("start_utc"):
            continue
        t = datetime.fromisoformat(row["start_utc"].replace("Z", "+00:00"))
        steps.append(dict(id=row["id"], r=int(row["r"]), g=int(row["g"]), b=int(row["b"]),
                          start=t.timestamp(), hold=int(row["hold_ms"]) / 1000.0))
    return steps


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def corr(a, b):
    ma, mb = mean(a), mean(b)
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 0 or vb <= 0:
        return 0.0
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb)


def displayed(steps, t):
    lo, hi = 0, len(steps) - 1
    if t < steps[0]["start"]:
        return None
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if steps[mid]["start"] <= t:
            lo = mid
        else:
            hi = mid - 1
    s = steps[lo]
    return s if t < s["start"] + s["hold"] else None


def luminance(s):
    return 0.2126 * (s["r"] / 255) ** 2.2 + 0.7152 * (s["g"] / 255) ** 2.2 + 0.0722 * (s["b"] / 255) ** 2.2


def main():
    run = Path(sys.argv[1])
    play = load_play(sys.argv[2])
    recs = load_records(run / "private-pattern/records.bin")
    meter = load_meter(run / "PRIVATE-CAPTURE-STDERR.txt")
    p1 = [r for r in recs if r["phase"] == 1]
    yall = [mean(r["y"]) for r in p1]
    best = (-2, 0.0)
    for k in range(-400, 401):
        off = k * 0.01
        xs, ys = [], []
        for r, y in zip(p1, yall):
            s = displayed(play, r["rt"] + off)
            if s:
                xs.append(luminance(s)); ys.append(y)
        if len(xs) > 100:
            c = corr(xs, ys)
            if c > best[0]:
                best = (c, off)
    corr_best, offset = best
    cell_corr = []
    for c in range(N):
        xs, ys = [], []
        for r in p1:
            s = displayed(play, r["rt"] + offset)
            if s:
                xs.append(luminance(s)); ys.append(r["y"][c])
        cell_corr.append(corr(xs, ys) if xs else 0.0)
    roi = [c for c in range(N) if cell_corr[c] >= 0.97]
    if len(roi) < 4:
        roi = sorted(range(N), key=lambda c: -cell_corr[c])[:12]
    table = {}
    for ph in range(len(PHASES)):
        rows = [r for r in recs if r["phase"] == ph]
        first = rows[0]["seq"] if rows else 0
        acc = {}
        for r in rows:
            if r["seq"] - first < 8:
                continue
            t = r["rt"] + offset
            s = displayed(play, t)
            if not s or t - s["start"] < 0.35 or s["start"] + s["hold"] - t < 0.35:
                continue
            a = acc.setdefault(s["id"], dict(y=[], u=[], v=[], m=[], rgb=(s["r"], s["g"], s["b"])))
            a["y"].append(mean(r["y"][c] for c in roi))
            a["u"].append(mean(r["u"][c] for c in roi))
            a["v"].append(mean(r["v"][c] for c in roi))
            if r["seq"] in meter:
                a["m"].append(meter[r["seq"]])
        table[ph] = {k: dict(rgb=v["rgb"], frames=len(v["y"]), Y=round(mean(v["y"]), 2),
                             U=round(mean(v["u"]), 2), V=round(mean(v["v"]), 2),
                             Y_max_frame=round(max(v["y"]), 2) if v["y"] else None,
                             meter=round(mean(v["m"]), 1) if v["m"] else None)
                     for k, v in acc.items()}
    fps = (len(recs) - 1) / (recs[-1]["rt"] - recs[0]["rt"]) if len(recs) > 1 else 0
    out = dict(frames=len(recs), fps=round(fps, 3), meter_samples=len(meter),
               clock_offset_s=round(offset, 3), alignment_correlation=round(corr_best, 4),
               roi_cells=len(roi), roi_rows=sorted({c // GX for c in roi}), roi_cols=sorted({c % GX for c in roi}),
               cell_corr_grid=[[round(cell_corr[y * GX + x], 2) for x in range(GX)] for y in range(GY)],
               phases=[dict(lines=l, gain=g, patterns=table[i]) for i, (l, g) in enumerate(PHASES)])
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
