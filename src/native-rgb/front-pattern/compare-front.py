#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compare one Linux front phase with one Windows phase, pattern by pattern.
Usage: compare-front.py linux.json windows.json linux_phase windows_phase
Scalar ROI means only."""
import json, math, sys

GREYS = ["grey_0", "grey_8", "grey_16", "grey_32", "grey_48", "grey_64", "grey_96",
         "grey_128", "grey_160", "grey_192", "grey_224", "grey_255"]
COLOURS = ["red", "green", "blue", "cyan", "magenta", "yellow", "red50", "green50", "blue50"]


def main():
    L = json.load(open(sys.argv[1])); W = json.load(open(sys.argv[2]))
    lp, wp = int(sys.argv[3]), int(sys.argv[4])
    lin = L["phases"][lp]["patterns"]; win = W["phases"][wp]["patterns"]
    rows = []
    for n in GREYS + COLOURS:
        if n not in lin or n not in win:
            continue
        l = [lin[n][k] for k in "YUV"]; w = [win[n][k] for k in "YUV"]
        cw = math.hypot(w[1] - 128, w[2] - 128); cl = math.hypot(l[1] - 128, l[2] - 128)
        rows.append(dict(pattern=n, linux=l, windows=w, dY=round(l[0] - w[0], 1),
                         dC=round(math.hypot(l[1] - w[1], l[2] - w[2]), 1),
                         sat=round(cl / cw, 3) if cw > 3 else None))

    def avg(sel, key):
        v = [abs(r[key]) for r in rows if r["pattern"] in sel and r[key] is not None]
        return round(sum(v) / len(v), 2) if v else None
    sats = [r["sat"] for r in rows if r["pattern"] in COLOURS and r["sat"]]
    out = dict(linux_phase=lp, windows_phase=wp,
               grey_mean_abs_dY=avg(GREYS, "dY"), grey_mean_dC=avg(GREYS, "dC"),
               colour_mean_abs_dY=avg(COLOURS, "dY"), colour_mean_dC=avg(COLOURS, "dC"),
               colour_mean_sat=round(sum(sats) / len(sats), 3) if sats else None,
               all_mean_abs_dY=avg(GREYS + COLOURS, "dY"), all_mean_dC=avg(GREYS + COLOURS, "dC"),
               patterns=rows)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
