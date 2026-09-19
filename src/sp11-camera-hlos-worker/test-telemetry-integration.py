#!/usr/bin/env python3
"""E004gd: archived non-optical pattern -> bridge -> parity worker -> aggregate telemetry.

Offline only. No camera, PMIC, IR emitter, enrollment, face-matching or login I/O.
No image is saved outside subprocess memory. All executables are temporary.
"""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from collections import Counter
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HLOS = ROOT / "src/sp11-camera-hlos-worker"
CORE = ROOT / "src/sp11-camera-protected-worker"
ARCHIVE = ROOT / "experiments/E004-front-ir-vd55g0/e004fe-native-ir-frame-params/runtime/frames.bin"
ARCHIVE_SHA = "33dce2a2a6edacd608c998734e2635d7a9230c39d0f0fa27767dfa8b514918c3"
RGB_FRAME_SHA = "baf8aef482c894c21c0c3f6dd818bce6181b9cb1dff78ff4a497ccf5cfd99b28"
NV12_PROCESSED_SHA = "ea414ce89d3fdcf25f834baa3f8d13a1d04b25289ff34dba844a57986db655df"
W, H, COUNT, STRIDE = 644, 604, 16, 1936
YLEN = W * H
NVLEN = YLEN + YLEN // 2
RGBLEN = STRIDE * H

def need(ok, message):
    if not ok:
        raise AssertionError("E004GD_FAIL_CLOSED " + message)

def call(args, payload, success=True):
    r = subprocess.run([str(x) for x in args], input=payload,
                       capture_output=True, check=False, timeout=100)
    need((r.returncode == 0) == success,
         f"unexpected exit={r.returncode} for {args[0]}: {r.stderr[-500:]!r}")
    if not success:
        need(r.stdout == b"", "malformed last frame emitted partial output")
    return r.stdout

def compile_c(out, files, sanitize=False):
    flags = ["-std=c11", "-O1" if sanitize else "-O2",
             "-Wall", "-Wextra", "-Werror"]
    if sanitize:
        flags += ["-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
    r = subprocess.run(["clang", *flags, *map(str, files), "-o", str(out)],
                       capture_output=True, timeout=60)
    need(r.returncode == 0, "compiler failed: " + r.stderr[-600:].decode(errors="replace"))

def expected_metrics(frame):
    y = frame[:YLEN]
    hist = Counter(y)
    need(frame[YLEN:] == bytes([128]) * (YLEN // 2), "processed UV unexpectedly non-neutral")
    def pct(rank):
        n = 0
        for v in range(256):
            n += hist[v]
            if n >= rank:
                return v
        raise AssertionError("empty image")
    diffs = 0
    for row in range(H):
        s = row * W
        for x in range(W):
            if x:
                diffs += abs(y[s+x] - y[s+x-1])
            if row:
                diffs += abs(y[s+x] - y[s+x-W])
    edges = H * (W - 1) + (H - 1) * W
    return {
        "mean_milli": (sum(y) * 1000 + YLEN // 2) // YLEN,
        "p10": pct((YLEN + 9) // 10),
        "p90": pct((9 * YLEN + 9) // 10),
        "dark_0_15_permille": (sum(hist[v] for v in range(16)) * 1000 + YLEN//2)//YLEN,
        "bright_240_255_permille": (sum(hist[v] for v in range(240,256)) * 1000 + YLEN//2)//YLEN,
        "neighbor_abs_diff_milli": (diffs * 1000 + edges//2)//edges,
    }

def main():
    raw = ARCHIVE.read_bytes()
    need(sha256(raw).hexdigest() == ARCHIVE_SHA and
         len(raw) == COUNT * RGBLEN, "immutable E004fe raw pattern archive altered")
    need({sha256(raw[i:i+RGBLEN]).hexdigest()
          for i in range(0, len(raw), RGBLEN)} == {RGB_FRAME_SHA},
         "archived frame differs from established E004fe pattern")
    with TemporaryDirectory(prefix="sp11-e004gd-offline-") as temp:
        tmp = Path(temp)
        bridge, worker, metrics = (tmp / n for n in ("bridge", "worker", "metrics"))
        sanitize = os.getenv("HLOS_SANITIZE") == "1"
        compile_c(bridge, [HLOS / "sp11-ir-rgb888-to-nv12.c"], sanitize)
        compile_c(worker, [HLOS / "sp11-hlos-ir.c", *(
            CORE / n for n in (
                "sp11-parity-worker.c", "sp11-swabf-reference.c",
                "sp11-swasf-reference.c", "sp11-swasf-windows-tuning.c",
                "sp11-swasf-helpers.c", "sp11-swasf-c230.c",
                "sp11-swasf-c3e8.c", "sp11-swasf-cd90.c",
            ))], sanitize)
        compile_c(metrics, [HLOS / "sp11-ir-signal-metrics.c"], sanitize)
        converted = call([bridge, "--frames", str(COUNT)], raw)
        need(len(converted) == COUNT * NVLEN, "wrong RGB888 to NV12 conversion length")
        processed = call([worker, "--frames", str(COUNT)], converted)
        need(len(processed) == COUNT * NVLEN and
             sha256(processed).hexdigest() == NV12_PROCESSED_SHA,
             "existing Windows-oracle-backed pixel pipeline changed")
        reported = json.loads(call([metrics, "--frames", str(COUNT)], processed))
        need(reported["kind"] == "unprotected-offline-signal-telemetry" and
             reported["face_authentication_proven"] is False,
             "telemetry is being misrepresented as face authentication")
        entries = reported["frames"]
        need(len(entries) == COUNT, "not all processed frames measured")
        for i, entry in enumerate(entries):
            need(entry == {"frame": i + 1, **expected_metrics(processed[i*NVLEN:(i+1)*NVLEN])},
                 f"independent aggregate metric mismatch frame={i+1}")
        need(all(row == {**entries[0], "frame": i+1} for i, row in enumerate(entries)),
             "nominal repeated pattern yields inconsistent frame telemetry")
        # Both the bridge and telemetry reject corruption only in the last
        # frame; no bytes may leak from earlier validated frames.
        bad_rgb = bytearray(raw)
        bad_rgb[-RGBLEN + 1] ^= 1
        call([bridge, "--frames", str(COUNT)], bad_rgb, False)
        bad_uv = bytearray(processed)
        bad_uv[-1] ^= 1
        call([metrics, "--frames", str(COUNT)], bad_uv, False)
        call([metrics, "--frames", str(COUNT)], processed[:-1], False)
        call([metrics, "--frames", str(COUNT)], processed+b"\\x00", False)
        call([metrics, "--frames", "15"], processed, False)
        print("E004GD_ARCHIVED_GENERATED_PATTERN=PASS FRAMES=16 PIXEL_SHA256="+sha256(processed).hexdigest())
        print("E004GD_FULL_CHAIN_METRICS=PASS INDEPENDENT_PYTHON_REFERENCE=PASS")
        print("E004GD_LAST_FRAME_CORRUPTION_NO_PARTIAL_OUTPUT=PASS")
        print("E004GD_PATTERN_METRICS="+json.dumps(entries[0],sort_keys=True))
        print("E004GD_CAMERA=NO EMITTER=OFF REAL_FACE_IMAGES=NO FACE_UNLOCK=NOT_PROVEN")

if __name__ == "__main__":
    main()
