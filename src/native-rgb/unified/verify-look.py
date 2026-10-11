#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compare what applications receive from a webcam bridge (YUYV 1920x1080 frames,
one raw file) with a same-scene Windows capture scaled to 1920x1080 the same way.
Usage: verify-look.py <frames.yuyv> <W> <H> "<windows glob>"   Prints scalar JSON.
"""
import json, runpy, sys
from pathlib import Path
import numpy as np

F = runpy.run_path(str(Path(__file__).with_name("fit-look.py")))
OW, OH = 1920, 1080


def metrics(y, u, v):
    m = y.mean(0)
    c = np.hypot(u.mean(0) - 128, v.mean(0) - 128)
    return {"y_q": [round(float(x), 1) for x in np.percentile(m, [1, 10, 50, 90, 99])],
            "chroma_p95": round(float(np.percentile(c, 95)), 2),
            "noise_mid": round(F["noise_mid"](y, m), 2), "edge_p99": round(F["grad_p99"](m), 2)}


def main():
    a = np.fromfile(sys.argv[1], np.uint8)
    n = a.size // (OW * OH * 2)
    fr = a[: n * OW * OH * 2].reshape(n, OH, OW * 2)[-6:].astype(np.float32)
    ly, lu, lv = fr[:, :, 0::2], fr[:, :, 1::4], fr[:, :, 3::4]
    wy, wu, wv = F["load"](sys.argv[4], int(sys.argv[2]), int(sys.argv[3]))
    print(json.dumps({"bridge": metrics(ly, lu, lv), "windows": metrics(wy, wu, wv), "frames": int(n)}))


if __name__ == "__main__":
    main()
