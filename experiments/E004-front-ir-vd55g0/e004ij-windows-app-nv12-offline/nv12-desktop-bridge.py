#!/usr/bin/env python3
"""E004ij: bounded offline 2560x1440 NV12 -> 1920x1080 NV12 desktop bridge.

Only generated/independently validated linear NV12; NEVER feed QC10C here.
No camera node, kernel driver, hardware access, IR or Windows operation.
"""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile

SRC_W, SRC_H = 2560, 1440
DST_W, DST_H = 1920, 1080
SRC_FRAME = SRC_W * SRC_H * 3 // 2
DST_FRAME = DST_W * DST_H * 3 // 2
WINDOWS_RECORD_PROVENANCE_SHA256 = "c3482698b31668771a8ad531455cd03b31e26793063415a9df0444cae8707d02"

def bridge(input_path: Path, output_path: Path, frames: int, *, runner=subprocess.run):
    if type(frames) is not int or not (1 <= frames <= 27):
        raise ValueError("only a positive bounded count of 1..27 frames is allowed")
    src = input_path.resolve(strict=True)
    target = output_path.resolve(strict=False)
    if input_path.is_symlink() or not src.is_file() or not src.is_relative_to(Path("/tmp")):
        raise ValueError("input must be a regular offline file under /tmp")
    if not target.is_relative_to(Path("/tmp")) or not target.parent.is_dir():
        raise ValueError("output must be in an existing directory under /tmp")
    parent = target.parent
    pstat = parent.stat()
    if pstat.st_uid != os.getuid() or not stat.S_ISDIR(pstat.st_mode) or pstat.st_mode & 0o022:
        raise ValueError("output directory must be private and owned by caller")
    if output_path.exists() or output_path.is_symlink() or src == target:
        raise ValueError("do not replace input, preexisting output or a symlink")
    if src.stat().st_size != SRC_FRAME * frames:
        raise ValueError("input length is not exactly the claimed count of linear NV12 frames")
    if shutil.which("gst-launch-1.0") is None:
        raise RuntimeError("system GStreamer binary unavailable")
    with src.open("rb") as inp:
        source_digest = hashlib.file_digest(inp, "sha256").hexdigest()
    fd, temporary = tempfile.mkstemp(prefix=".e004ij-", suffix=".nv12", dir=parent)
    os.close(fd)
    try:
        cmd = [
            "gst-launch-1.0", "-q",
            "filesrc", f"location={src}",
            "!", "rawvideoparse", "format=nv12", f"width={SRC_W}", f"height={SRC_H}",
            "framerate=30/1", "!", "videoscale",
            "!", f"video/x-raw,format=NV12,width={DST_W},height={DST_H},framerate=30/1",
            "!", "filesink", f"location={temporary}",
        ]
        completed = runner(cmd, check=True, capture_output=True, text=True, timeout=45)
        if Path(temporary).stat().st_size != DST_FRAME * frames:
            raise ValueError("GStreamer did not emit precisely the expected number of NV12 bytes")
        with src.open("rb") as inp:
            unchanged_digest = hashlib.file_digest(inp, "sha256").hexdigest()
        if unchanged_digest != source_digest:
            raise ValueError("input changed while offline scaling")
        if output_path.exists() or output_path.is_symlink():
            raise ValueError("output path became occupied")
        os.replace(temporary, target)
        with target.open("rb") as out:
            output_digest = hashlib.file_digest(out, "sha256").hexdigest()
        return {
            "input_sha256": source_digest,
            "output_sha256": output_digest,
            "input_frame_bytes": SRC_FRAME,
            "output_frame_bytes": DST_FRAME,
            "frames": frames,
            "output_width": DST_W,
            "output_height": DST_H,
            "output_format": "NV12",
            "source_is_validated_camera_capture": False,
            "colorimetry_optical_parity_proven": False,
            "camera_or_hardware_used": False,
        }
    finally:
        Path(temporary).unlink(missing_ok=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--frames", type=int, required=True)
    a = parser.parse_args()
    import json
    print(json.dumps(bridge(a.input, a.output, a.frames), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
