#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Daily boot check: read each SP11 webcam loopback device like an application
and report frame rate and basic picture statistics (scalars only).
Usage: test-webcams.py [frames] [out-dir] [order e.g. rear,front,rear]   (frames are kept in out-dir, private)
"""
import json, re, subprocess, sys, time
from pathlib import Path
import numpy as np

W, H = 1920, 1080
N = int(sys.argv[1]) if len(sys.argv) > 1 else 150
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/var/lib/sp11-camera-daily2-test")


def grab(dev, name):
    OUT.mkdir(mode=0o700, exist_ok=True)
    f = OUT / f"{name}.yuyv"
    t0 = time.time()
    p = subprocess.run(["v4l2-ctl", "-d", dev, "--set-fmt-video=width=1920,height=1080,pixelformat=YUYV",
                        "--stream-mmap=4", f"--stream-count={N}", f"--stream-to={f}"],
                       capture_output=True, text=True, timeout=90)
    dt = time.time() - t0
    fps = [float(x) for x in re.findall(r"([0-9.]+) fps", p.stderr + p.stdout)]
    r = {"rc": p.returncode, "seconds": round(dt, 2), "v4l2ctl_fps_last": fps[-1] if fps else None}
    if f.exists() and f.stat().st_size >= W * H * 2:
        a = np.fromfile(f, np.uint8)
        n = a.size // (W * H * 2)
        fr = a[: n * W * H * 2].reshape(n, H, W * 2)
        y = fr[:, :, 0::2].astype(np.float32)
        u = fr[:, :, 1::4].astype(np.float32)
        v = fr[:, :, 3::4].astype(np.float32)
        means = y.mean((1, 2))
        r.update(frames=int(n), y_mean_first=round(float(means[0]), 1), y_mean_last=round(float(means[-1]), 1),
                 y_p1_p50_p99_last=[round(float(q), 1) for q in np.percentile(y[-1], [1, 50, 99])],
                 u_mean_last=round(float(u[-1].mean()) - 128, 2), v_mean_last=round(float(v[-1].mean()) - 128, 2),
                 identical_consecutive=int((np.abs(np.diff(means)) == 0).sum()),
                 black_frames=int((means < 2).sum()))
        np.save(OUT / f"{name}-last.npy", fr[-1])
        f.unlink()
    else:
        r["stderr"] = p.stderr[-400:]
    return r


def main():
    res = {"services": {s: subprocess.run(["systemctl", "is-active", s], capture_output=True, text=True).stdout.strip()
                        for s in ("sp11-camera-daily2", "sp11-webcam-front", "sp11-webcam-rear")}}
    order = sys.argv[3].split(",") if len(sys.argv) > 3 else ["front", "rear", "front"]
    for i, cam in enumerate(order):
        if i:
            time.sleep(6)
        res[f"{i}-{cam}"] = grab("/dev/video50" if cam == "front" else "/dev/video51", f"{cam}{i}")
    log = subprocess.run(["journalctl", "-b", "-u", "sp11-webcam-front", "-u", "sp11-webcam-rear", "-u",
                          "sp11-camera-daily2", "--no-pager", "-o", "cat"], capture_output=True, text=True).stdout
    res["log_tail"] = log.splitlines()[-25:]
    dm = subprocess.run(["dmesg"], capture_output=True, text=True).stdout
    res["kernel_oops"] = len(re.findall(r"(Oops|BUG:|Call trace|WARNING: CPU)", dm))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
