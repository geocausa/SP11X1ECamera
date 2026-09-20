#!/usr/bin/env python3
"""Export a bounded ordinary-memory offline NV12 batch through the HLOS worker to Y4M.

No camera device, protected buffer, illumination, face model or login access.
Playback cadence is supplied by the caller; it is not measured sensor timing.
"""
import argparse
import importlib.util
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
WIDTH, HEIGHT = 644, 604
YLEN = WIDTH * HEIGHT
FRAME_LEN = YLEN * 3 // 2
MAX_FRAMES = 16

def load_transaction():
    spec = importlib.util.spec_from_file_location("preview_transaction", HERE / "sp11-offline-transaction.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def export_preview(source, output, worker, fps):
    if type(fps) is not int or not 1 <= fps <= 120:
        raise ValueError("playback fps must be 1..120")
    # O_NONBLOCK prevents FIFO opens from hanging; regular files only.
    fd = os.open(source, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or not FRAME_LEN <= info.st_size <= FRAME_LEN * MAX_FRAMES:
            raise ValueError("expected a regular offline file containing 1..16 frames")
        data = stream.read(FRAME_LEN * MAX_FRAMES + 1)
    if len(data) != info.st_size or len(data) % FRAME_LEN:
        raise ValueError("offline frame extent changed or incomplete")
    frames = tuple(data[i:i+FRAME_LEN] for i in range(0, len(data), FRAME_LEN))
    processed, receipt = load_transaction().process_offline_frames(worker, frames, max_seconds=120)
    # Neutral UV is identical in interleaved NV12 and planar 4:2:0.
    if any(len(frame) != FRAME_LEN or frame[YLEN:] != bytes([128]) * (YLEN // 2) for frame in processed):
        raise ValueError("processed frame shape/chroma rejected")
    header = f"YUV4MPEG2 W{WIDTH} H{HEIGHT} F{fps}:1 Ip A1:1 C420jpeg XCOLORRANGE=FULL\n".encode("ascii")
    payload = header + b"".join(b"FRAME\n" + frame for frame in processed)
    # Create only after successful native transaction; never overwrite a file.
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
    except BaseException:
        Path(output).unlink(missing_ok=True)
        raise
    return len(processed)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path, help="ordinary offline neutral NV12, 644x604, 1..16 frames")
    ap.add_argument("--output", required=True, type=Path, help="new private .y4m file; existing files refused")
    ap.add_argument("--worker", required=True, type=Path, help="existing native offline stream executable in user-owned /tmp")
    ap.add_argument("--playback-fps", type=int, default=30, help="playback cadence only, default 30")
    a = ap.parse_args()
    try:
        count = export_preview(a.input, a.output, a.worker, a.playback_fps)
    except Exception:
        print("Offline preview failed; no successful export. Check input, worker and output path.", file=sys.stderr)
        return 1
    print(f"OFFLINE_PREVIEW=PASS FRAMES={count} CAMERA_RUNTIME=NO AUTHENTICATION=NO")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
