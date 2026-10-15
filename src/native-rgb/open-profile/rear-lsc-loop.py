#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Closed-loop rear lens-shading calibration against a flat field (lab, camera boot).

The rear output tone curve need not be known: each iteration programs the
current 13x17 mesh (and start white balance), captures the diffuser-covered
flat field, and updates every node so the output becomes flat and neutral:
  g_c(node) *= (O_c(centre) / O_c(node)) ** K
O is the smoothed output channel value. The output rises with gain with an
unknown monotonic slope (steep near black: the path subtracts a pedestal), so a
gentle exponent K is used; only the fixed point (flat output) matters. The
centre node is held at 1.0; white balance is fixed (set neutral beforehand).
Requires the lab camss build that admits any rear input (no digest pin).
Usage: rear-lsc-loop.py source.json state-dir iterations
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

W, H, NX, NY = 3840, 2160, 17, 13
K = 0.5  # update exponent; converges for local output-vs-gain slopes 0..4
S = 255 / 256
M = np.array([[0.299, 0.587, 0.114], [-0.168736 * S, -0.331264 * S, 0.5 * S], [0.5 * S, -0.418688 * S, -0.081312 * S]])
Mi = np.linalg.inv(M)
FW = "/var/lib/sp11-camera-daily2/firmware/qcom/sp11/ov13858-rear-open-v1.bin"
HERE = Path(__file__).resolve().parent


def write_lsc(path, g):
    q = lambda a: np.clip(np.round(a * 1024), 1, 8191).astype(int)
    lines = ["# loop state"]
    for name, a in zip(("red", "green", "blue"), g):
        lines.append(name + ":")
        lines += [" ".join(str(v) for v in row) for row in q(a)]
    Path(path).write_text("\n".join(lines) + "\n")


def design(x, y, deg=6):
    xn = x / (W - 1) * 2 - 1; yn = y / (H - 1) * 2 - 1
    return np.stack([xn ** p * yn ** q for p in range(deg + 1) for q in range(deg + 1 - p)], -1)


def measure(frames):
    ys, us, vs = [], [], []
    for p in frames:
        d = np.fromfile(p, np.uint8)
        ys.append(d[:W * H].reshape(H, W).astype(np.float32))
        uv = d[W * H:].reshape(H // 2, W // 2, 2).astype(np.float32)
        us.append(uv[..., 0]); vs.append(uv[..., 1])
    Y = np.mean(ys, 0); U = np.mean(us, 0); V = np.mean(vs, 0)
    by = bx = 60
    ny, nx = H // by, W // bx
    blk = lambda a, b: a[:ny * b, :nx * b].reshape(ny, b, nx, b).mean((1, 3))
    yuv = np.stack([blk(Y, by), blk(U, 30) - 128, blk(V, 30) - 128])
    rgb = np.einsum("ij,jyx->iyx", Mi, yuv)
    cx = (np.arange(nx) + 0.5) * bx; cy = (np.arange(ny) + 0.5) * by
    gx, gy = np.meshgrid(cx, cy)
    A = design(gx.ravel(), gy.ravel())
    mx, my = np.meshgrid(np.arange(NX) / (NX - 1) * (W - 1), np.arange(NY) / (NY - 1) * (H - 1))
    An = design(mx.ravel(), my.ravel())
    out = []
    for c in range(3):
        coef, *_ = np.linalg.lstsq(A, np.clip(rgb[c].ravel(), 1, 254), rcond=None)
        out.append((An @ coef).reshape(NY, NX))
    return np.array(out), float(Y.max())


def main():
    src = json.load(open(sys.argv[1]))
    st = Path(sys.argv[2]); st.mkdir(parents=True, exist_ok=True)
    n = int(sys.argv[3])
    sf = st / "state.json"
    if sf.exists():
        s = json.load(open(sf)); g = np.array(s["g"]); wb = s["wb"]
    else:
        g = np.ones((3, NY, NX)); wb = [src["start_3a"]["wb_r_q10"], src["start_3a"]["wb_b_q10"]]
    for it in range(n):
        src["start_3a"]["wb_r_q10"], src["start_3a"]["wb_b_q10"] = int(wb[0]), int(wb[1])
        json.dump(src, open(st / "src.json", "w"))
        write_lsc(st / "lsc.txt", g)
        subprocess.run(["python3", str(HERE / "gen-rear-open-input.py"), str(st / "src.json"), str(st / "lsc.txt"), FW],
                       check=True, stdout=subprocess.DEVNULL)
        cap = st / ("cap%d" % it)
        subprocess.run(["sh", str(HERE / "capture-rear-frames.sh"), str(cap), "60"], check=True, stdout=subprocess.DEVNULL)
        frames = sorted(cap.glob("*.bin"))[-4:]
        O, ymax = measure(frames)
        for p in cap.glob("*.bin"):
            p.unlink()
        c = (NY // 2, NX // 2)
        ref = O[1][c]
        dev = [round(float(np.max(np.abs(O[k] / ref - 1))), 3) for k in range(3)]
        centre = [round(float(O[k][c]), 1) for k in range(3)]
        print(json.dumps({"iter": it, "centre_rgb_gamma": centre, "max_dev_vs_centre_G": dev, "wb": wb, "ymax": ymax}), flush=True)
        for k in range(3):
            g[k] *= (O[k][c] / np.clip(O[k], 1, None)) ** K  # flatten each channel to its centre
        for k in range(3):
            g[k] /= g[k][c]
        g = np.clip(g, 0.25, 7.9)
        json.dump({"g": g.tolist(), "wb": wb}, open(sf, "w"))


if __name__ == "__main__":
    main()
