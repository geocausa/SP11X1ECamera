#!/usr/bin/env python3
"""E004gc: no-camera, no-image-file, fail-closed NV12 telemetry regression."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import subprocess

HERE = Path(__file__).resolve().parent
W, H = 644, 604
Y = W * H
UV = bytes([128]) * (Y // 2)
SRC = HERE / "sp11-ir-signal-metrics.c"


def need(condition, msg):
    if not condition:
        raise AssertionError(msg)


def invoke(exe, image, frames=None, ok=True):
    args = [str(exe)]
    if frames is not None:
        args += ["--frames", str(frames)]
    r = subprocess.run(args, input=image, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=35, check=False)
    need((r.returncode == 0) == ok, f"unexpected rc {r.returncode}: {r.stderr[:150]!r}")
    if ok:
        answer = json.loads(r.stdout)
        need(answer["face_authentication_proven"] is False, "identity proof falsely claimed")
        need(answer["kind"] == "unprotected-offline-signal-telemetry", "changed output contract")
        return answer["frames"]
    need(r.stdout == b"", "invalid batch leaked partial telemetry")
    return None


def test(exe):
    dark = bytes(Y) + UV
    flat = bytes([40]) * Y + UV
    gradient = bytes([x % 256 for x in range(W)]) * H + UV
    alternating = bytes([0, 255]) * (Y // 2) + UV
    d = invoke(exe, dark)[0]
    need(d == {"frame": 1, "mean_milli": 0, "p10": 0, "p90": 0,
               "dark_0_15_permille": 1000, "bright_240_255_permille": 0,
               "neighbor_abs_diff_milli": 0}, "black image metrics mismatch")
    f = invoke(exe, flat)[0]
    need(f["mean_milli"] == 40000 and f["p10"] == f["p90"] == 40 and
         f["neighbor_abs_diff_milli"] == 0, "flat low-light scene mischaracterized")
    a = invoke(exe, alternating)[0]
    need(a["p10"] == 0 and a["p90"] == 255 and
         a["dark_0_15_permille"] == 500 and
         a["bright_240_255_permille"] == 500 and
         a["neighbor_abs_diff_milli"] > 0,
         "clipping and texture metrics mismatch")
    g = invoke(exe, gradient)[0]
    need(g["p90"] > g["p10"] and g["neighbor_abs_diff_milli"] > 0,
         "spatial variation not observed")
    mixed = invoke(exe, dark + flat + gradient, 3)
    need([f["frame"] for f in mixed] == [1, 2, 3] and
         mixed[1]["mean_milli"] == 40000, "frame isolation/order incorrect")
    sixteen = invoke(exe, flat * 16, 16)
    need(len(sixteen) == 16 and sixteen[-1]["frame"] == 16,
         "maximal batch not handled")
    invoke(exe, dark[:-1], ok=False)
    invoke(exe, dark + bytes([0]), ok=False)
    invoke(exe, b"", ok=False)
    invoke(exe, dark * 2, frames=2, ok=True)
    invoke(exe, dark, frames=2, ok=False)
    invoke(exe, dark, frames=16, ok=False)
    invoke(exe, dark * 2, frames=1, ok=False)
    invoke(exe, dark[:-1] + bytes([127]), ok=False)
    invoke(exe, dark + flat[:-1] + bytes([127]), frames=2, ok=False)
    invoke(exe, dark * 15 + dark[:-1] + bytes([127]), frames=16, ok=False)
    for bad in ("0", "17", "-1", "garbage", "1x"):
        r = subprocess.run([str(exe), "--frames", bad], input=dark,
                           capture_output=True, timeout=5, check=False)
        need(r.returncode != 0 and r.stdout == b"", "invalid frame count allowed: " + bad)
    print("E004GC_SYNTHETIC_NV12_METRICS=PASS 1_TO_16_FRAMES=PASS")
    print("E004GC_INVALID_LENGTH_CHROMA_COUNT_NO_PARTIAL_OUTPUT=PASS")
    print("E004GC_FACE_AUTH=NOT_TESTED EMITTER=OFF GOLDEN=UNTOUCHED")


def main():
    with TemporaryDirectory(prefix="sp11-e004gc-offline-") as folder:
        exe = Path(folder) / "sp11-ir-signal-metrics"
        flags = ["-std=c11", "-O1", "-g", "-Wall", "-Wextra", "-Werror"]
        if os.getenv("HLOS_SANITIZE") == "1":
            flags += ["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
        cmd = ["clang", *flags, str(SRC), "-o", str(exe)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        need(r.returncode == 0, "build failed: " + r.stderr[-1500:])
        test(exe)


if __name__ == "__main__":
    main()
