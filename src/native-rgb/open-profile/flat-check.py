#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Flat-field setup check: per displayed pattern, the 16x9 grid uniformity.

The camera sits against a diffuser on the SP7 screen, so every cell should see
the same light. For each pattern (aligned with the SP7 player log) prints the
mean Y, the cell range relative to the centre, the radial falloff (corner/centre),
the residual after a smooth quadratic fit (blotches from the diffuser), chroma
spread, and the clipped fraction. Scalars only.
Usage: flat-check.py <run dir> <play-log.csv.gz> <phase>
"""
import json, runpy, sys
from pathlib import Path
import numpy as np

A = runpy.run_path(str(Path(__file__).resolve().parents[1] / "front-pattern/analyze-front-pattern.py"))
GX, GY = 16, 9


def main():
    run, play, ph = Path(sys.argv[1]), A["load_play"](sys.argv[2]), int(sys.argv[3])
    recs = [r for r in A["load_records"](run / "private-pattern/records.bin") if r["phase"] == ph]
    best, off = A["align"](recs, play, lambda r: float(np.mean(r["y"])))
    acc = {}
    for r in recs[8:]:
        t = r["rt"] + off
        s = A["displayed"](play, t)
        if not s or t - s["start"] < 0.35 or s["start"] + s["hold"] - t < 0.35:
            continue
        acc.setdefault(s["id"], []).append((np.array(r["y"]), np.array(r["u"]), np.array(r["v"])))
    yy, xx = np.mgrid[0:GY, 0:GX]
    xn = (xx - (GX - 1) / 2) / ((GX - 1) / 2); yn = (yy - (GY - 1) / 2) / ((GY - 1) / 2)
    X = np.stack([np.ones(GX * GY), xn.ravel(), yn.ravel(), xn.ravel() ** 2, yn.ravel() ** 2, (xn * yn).ravel()], 1)
    out = {}
    for k, v in sorted(acc.items()):
        Y = np.mean([a[0] for a in v], 0); U = np.mean([a[1] for a in v], 0); V = np.mean([a[2] for a in v], 0)
        Yg = Y.reshape(GY, GX)
        c = Yg[3:6, 6:10].mean()
        coef, *_ = np.linalg.lstsq(X, Y, rcond=None)
        res = Y - X @ coef
        out[k] = dict(frames=len(v), meanY=round(float(Y.mean()), 1), centreY=round(float(c), 1),
                      min_rel=round(float(Y.min() / max(c, 1e-6)), 3), max_rel=round(float(Y.max() / max(c, 1e-6)), 3),
                      corners_rel=round(float(np.mean([Yg[0, 0], Yg[0, -1], Yg[-1, 0], Yg[-1, -1]]) / max(c, 1e-6)), 3),
                      edges_lr_rel=[round(float(Yg[:, 0].mean() / c), 3), round(float(Yg[:, -1].mean() / c), 3)],
                      edges_tb_rel=[round(float(Yg[0].mean() / c), 3), round(float(Yg[-1].mean() / c), 3)],
                      blotch_rms_pct=round(float(100 * res.std() / max(Y.mean(), 1e-6)), 2),
                      chroma_spread=round(float(np.hypot(U - U.mean(), V - V.mean()).max()), 1),
                      UV=[round(float(U.mean()), 1), round(float(V.mean()), 1)],
                      clipped_cells=int((Y > 250).sum()))
    print(json.dumps(dict(alignment=round(best, 3), offset_s=round(off, 2), patterns=out), indent=1))


if __name__ == "__main__":
    main()
