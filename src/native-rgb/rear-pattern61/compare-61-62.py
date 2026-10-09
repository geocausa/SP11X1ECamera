#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Side-by-side Linux run 61 vs Windows run 62 on one shared grid ROI.

args: linux_run_dir play61.csv win_records.csv play62.csv win_analysis.json
ROI = Windows cells with luminance correlation >= 0.97 (central screen).
Phases compared: 33.25 ms with Linux gain 1/2/4/8x vs Windows ISO 100/200/400/800.
"""
import json, runpy, sys
from pathlib import Path
H = Path(__file__).parent
A = runpy.run_path(str(H / "analyze-pattern61.py"))
B = runpy.run_path(str(H / "analyze-pattern62.py"))
mean, displayed = A["mean"], A["displayed"]


def table(recs, play, offset, roi, phase, skip):
    rows = [r for r in recs if r["phase"] == phase]
    acc = {}
    for i, r in enumerate(rows):
        if i < skip:
            continue
        t = r["rt"] + offset
        s = displayed(play, t)
        if not s or t - s["start"] < 0.35 or s["start"] + s["hold"] - t < 0.35:
            continue
        a = acc.setdefault(s["id"], [[], [], []])
        a[0].append(mean(r["y"][c] for c in roi)); a[1].append(mean(r["u"][c] for c in roi)); a[2].append(mean(r["v"][c] for c in roi))
    return {k: [round(mean(x), 2) for x in v] for k, v in acc.items()}


def main():
    lrun, p61, wrec, p62, wan = sys.argv[1:6]
    wa = json.loads(Path(wan).read_text())
    grid = wa["cell_corr_grid"]
    roi = [y * 16 + x for y in range(9) for x in range(16) if grid[y][x] >= 0.97]
    lin = A["load_records"](Path(lrun) / "private-pattern/records.bin")
    win = B["load_csv"](wrec)
    l61 = json.loads((Path(lrun).parent.parent / "home/geoca/Documents/SP11-PROJECT/06-camera/private/pattern61-analysis.json").read_text()) if False else None
    loff = float(sys.argv[6]); woff = wa["clock_offset_s"]
    play61 = A["load_play"](p61); play62 = A["load_play"](p62)
    ids = ["grey_0", "grey_16", "grey_32", "grey_64", "grey_96", "grey_128", "grey_160", "grey_192", "grey_224", "grey_255",
           "red", "green", "blue", "cyan", "magenta", "yellow"]
    out = dict(roi_cells=len(roi), roi_rows=sorted({c // 16 for c in roi}), roi_cols=sorted({c % 16 for c in roi}), auto={}, ladder=[])
    wauto = table(win, play62, woff, roi, 0, 30)
    out["auto"] = {k: wauto.get(k) for k in ids}
    for i, (g, iso) in enumerate([(1, 100), (2, 200), (4, 400), (8, 800)]):
        lt = table(lin, play61, loff, roi, i + 1, 8)
        wt = table(win, play62, woff, roi, i + 1, 30)
        out["ladder"].append(dict(linux_gain=g, windows_iso=iso, patterns={k: dict(linux=lt.get(k), windows=wt.get(k)) for k in ids}))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
