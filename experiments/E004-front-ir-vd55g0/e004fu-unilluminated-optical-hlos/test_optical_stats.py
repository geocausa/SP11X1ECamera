#!/usr/bin/env python3
"""Offline safety tests for privacy-minimized camera-frame statistics."""
from hashlib import sha256
from pathlib import Path
from optical_stats import FRAME_BYTES, summarize

BASE = Path(__file__).resolve().parent
ARCHIVE = BASE.parent / "e004fe-native-ir-frame-params/runtime/frames.bin"
raw = ARCHIVE.read_bytes()
assert sha256(raw).hexdigest() == (
    "33dce2a2a6edacd608c998734e2635d7a9230c39d0f0fa27767dfa8b514918c3"
)
stats = summarize(raw)
assert len(stats) == 16
assert all(x["min"] == 15 and x["max"] == 212 and
           x["nonuniform"] and x["frame"] == i for i, x in enumerate(stats))
assert all("pixels" not in x and "sha256" not in x for x in stats)

def reject(payload, kind):
    try:
        summarize(payload)
    except ValueError:
        return
    raise AssertionError("accepted invalid " + kind)

reject(raw[:-1], "short batch")
reject(raw + b"\x00", "long batch")
wrong_color = bytearray(raw)
wrong_color[-FRAME_BYTES+1] ^= 1
reject(wrong_color, "non-neutral last frame")
del wrong_color
bad_padding = bytearray(raw)
bad_padding[-FRAME_BYTES+644*3] ^= 1
reject(bad_padding, "padding corrupt last frame")
print("E004FU_OPTICAL_STATS_OFFLINE=PASS FRAMES=16 REJECTIONS=4 RAW_IMAGE_RETAINED=NO")
