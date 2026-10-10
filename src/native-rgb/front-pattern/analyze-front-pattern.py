#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Analyse a front pattern calibration run (same-SP11, private inputs).

Inputs: <run dir> (private-pattern/records.bin, PRIVATE-CAPTURE-STDERR.txt,
RESULT.json) and the SP7 player log (csv or csv.gz). Output: scalar JSON per
exposure phase and displayed pattern (ROI means only, no spatial arrays).
"""
import csv, gzip, io, json, math, os, re, struct, sys
from datetime import datetime
from pathlib import Path

GX, GY = 16, 9
N = GX * GY
SEARCH = 12  # seconds; lab clocks are NTP-synchronised (fresh boots may drift), a loop alias is ~51 s
REC = struct.Struct("<IIQQ" + "f" * (3 * N))


def load_records(path):
    data = Path(path).read_bytes()
    assert len(data) % REC.size == 0, "record size"
    out = []
    for i in range(len(data) // REC.size):
        v = REC.unpack_from(data, i * REC.size)
        out.append(dict(seq=v[0], phase=v[1], comp=v[2], rt=v[3] / 1e9,
                        y=v[4:4 + N], u=v[4 + N:4 + 2 * N], v=v[4 + 2 * N:4 + 3 * N]))
    # The capture starts seconds after boot, often before the NTP step, so
    # CLOCK_REALTIME can jump mid-run. Rebuild wall time from the monotonic
    # completion timestamp using the (post-sync) offset of the final frames.
    if out:
        tail = sorted(r["rt"] - r["comp"] / 1e9 for r in out[-100:])
        delta = tail[len(tail) // 2]
        for r in out:
            r["rt"] = r["comp"] / 1e9 + delta
    return out


def load_meter(path):
    m = {}
    for f, l in re.findall(r"CAMSS_X1E_IPA_METER frame=(\d+) stream=\d+ timestamp=\d+ luma=([-+0-9.eE]+)",
                           Path(path).read_text(errors="replace")):
        m[int(f)] = float(l)
    return m


def load_play(path):
    raw = Path(path).read_bytes()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    steps = []
    for row in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        if row["loop"] == "done" or not row.get("start_utc"):
            continue
        s = row["start_utc"].replace("Z", "+00:00")
        s = re.sub(r"\.(\d{6})\d+", r".\1", s)
        t = datetime.fromisoformat(s)
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
    if not steps or t < steps[0]["start"]:
        return None
    lo, hi = 0, len(steps) - 1
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


def align(rows, play, key):
    best = (-2, 0.0)
    for coarse in range(-SEARCH, SEARCH + 1):
        off = float(coarse)
        xs, ys = [], []
        for r in rows[::3]:
            s = displayed(play, r["rt"] + off)
            if s:
                xs.append(luminance(s)); ys.append(key(r))
        if len(xs) > 100:
            c = corr(xs, ys)
            if c > best[0]:
                best = (c, off)
    c0, base = best
    for k in range(-100, 101):
        off = base + k * 0.01
        xs, ys = [], []
        for r in rows:
            s = displayed(play, r["rt"] + off)
            if s:
                xs.append(luminance(s)); ys.append(key(r))
        if len(xs) > 100:
            c = corr(xs, ys)
            if c > best[0]:
                best = (c, off)
    return best


def main():
    run = Path(sys.argv[1])
    play = load_play(sys.argv[2])
    roi_phase = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    recs = [r for r in load_records(run / "private-pattern/records.bin") if r["phase"] != 0xffffffff]
    meter = load_meter(run / "PRIVATE-CAPTURE-STDERR.txt")
    info = json.loads((run / "RESULT.json").read_text())["capture"]
    phases = info["phases"]
    ref = [r for r in recs if r["phase"] == roi_phase]
    # Align on the most variable cell (the displayed screen), not the whole frame.
    var = [sum((r["y"][c] - mean(q["y"][c] for q in ref[::10])) ** 2 for r in ref[::10]) for c in range(N)]
    key_cell = max(range(N), key=lambda c: var[c])
    corr_best, offset = align(ref, play, lambda r: r["y"][key_cell])
    cell = []
    for c in range(N):
        xs, ys = [], []
        for r in ref:
            s = displayed(play, r["rt"] + offset)
            if s:
                xs.append(luminance(s)); ys.append(r["y"][c])
        cell.append(corr(xs, ys) if xs else 0.0)
    roi = [c for c in range(N) if cell[c] >= 0.97]
    if len(roi) < 4:
        roi = sorted(range(N), key=lambda c: -cell[c])[:12]
    if os.environ.get("FRONT_ROI"):  # "rows:cols", e.g. 7,8:5,6,7 (a clipped display defeats correlation)
        rr, cc = os.environ["FRONT_ROI"].split(":")
        roi = [int(r) * GX + int(c) for r in rr.split(",") for c in cc.split(",")]
    out_phases = []
    for ph in range(len(phases)):
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
        out_phases.append(dict(phases[ph], patterns={k: dict(rgb=v["rgb"], frames=len(v["y"]),
            Y=round(mean(v["y"]), 2), U=round(mean(v["u"]), 2), V=round(mean(v["v"]), 2),
            Ymax=round(max(v["y"]), 2) if v["y"] else None,
            meter=round(mean(v["m"]), 1) if v["m"] else None) for k, v in sorted(acc.items())}))
    print(json.dumps(dict(frames=len(recs), fps=info.get("fps"), meter_samples=len(meter),
                          clock_offset_s=round(offset, 3), alignment_correlation=round(corr_best, 4),
                          roi_cells=len(roi), roi_rows=sorted({c // GX for c in roi}),
                          roi_cols=sorted({c % GX for c in roi}), phases=out_phases), indent=1))


if __name__ == "__main__":
    main()
