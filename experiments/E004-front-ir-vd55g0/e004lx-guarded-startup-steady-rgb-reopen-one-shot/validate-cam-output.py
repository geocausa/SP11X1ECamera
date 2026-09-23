#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Accept 900 consecutive processed XRGB8888 frame metadata records, never pixel files."""
import re
import sys
from pathlib import Path

def main() -> int:
    if len(sys.argv) != 4 or sys.argv[2] not in ("front", "rear") or sys.argv[3] not in ("1", "2"):
        return 2
    text = Path(sys.argv[1]).read_text()
    if "cam0: Capture 900 frames" not in text:
        return 3
    sample = re.compile(
        r"^(?P<seconds>[0-9]+)\.(?P<micro>[0-9]{6}) "
        r"\([0-9]+(?:\.[0-9]+)? fps\) "
        r"cam0-stream0 seq:\s*(?P<seq>[0-9]+) bytesused:\s*(?P<bytes>[0-9]+)"
        r"(?:/[0-9]+)*$", re.M
    )
    matches = list(sample.finditer(text))
    if len(matches) != 900:
        return 4
    seq = [int(m.group("seq")) for m in matches]
    ts = [int(m.group("seconds")) * 1000000 +
          int(m.group("micro")) for m in matches]
    used = [int(m.group("bytes")) for m in matches]
    if (seq != list(range(900)) or
        any(b != 1228800 for b in used) or
        any(b <= a for a, b in zip(seq, seq[1:])) or
        any(b <= a for a, b in zip(ts, ts[1:]))):
        return 5
    gaps = [b - a for a, b in zip(ts, ts[1:])]
    span = ts[-1] - ts[0]
    # Keep a strict steady-state contract while separately reporting
    # any first-ten-frame startup interruptions rather than hiding them.
    early = [g for g in gaps[:10] if g > 250_000]
    steady = gaps[10:]
    if (not 26_000_000 <= span <= 40_000_000 or
        len(early) > 1 or any(g > 2_000_000 for g in early) or
        any(g < 10_000 for g in gaps) or
        any(g > 250_000 for g in steady)):
        return 6
    print(f"E004LX_XRGB8888_METADATA=PASS CAMERA={sys.argv[2]} "
          f"REOPEN={sys.argv[3]} FRAMES=900 SEQUENCES_CONTIGUOUS=YES BYTES_1228800=YES "
          f"TIMESTAMP_SPAN_US={span} STARTUP_GAP_COUNT={len(early)} "
          f"STARTUP_GAP_MAX_US={max(early, default=0)} "
          f"STEADY_MAX_GAP_US={max(steady, default=0)} "
          f"STEADY_INTERVALS={len(steady)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
