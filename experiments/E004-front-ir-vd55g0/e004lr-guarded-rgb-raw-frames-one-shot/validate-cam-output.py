#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Accept six distinct non-empty RAW frame metadata records, never pixel files."""
import re
import sys
from pathlib import Path

def main() -> int:
    if len(sys.argv) != 3 or sys.argv[2] not in ("front", "rear"):
        return 2
    text = Path(sys.argv[1]).read_text()
    if "cam0: Capture 6 frames" not in text:
        return 3
    sample = re.compile(
        r"^(?P<seconds>[0-9]+)\.(?P<micro>[0-9]{6}) "
        r"\([0-9]+(?:\.[0-9]+)? fps\) "
        r"cam0-stream0 seq:\s*(?P<seq>[0-9]+) bytesused:\s*(?P<bytes>[0-9]+)"
        r"(?:/[0-9]+)*$", re.M
    )
    matches = list(sample.finditer(text))
    if len(matches) != 6:
        return 4
    seq = [int(m.group("seq")) for m in matches]
    ts = [int(m.group("seconds")) * 1000000 +
          int(m.group("micro")) for m in matches]
    used = [int(m.group("bytes")) for m in matches]
    if (len(set(seq)) != 6 or
        any(b <= 0 for b in used) or
        any(b <= a for a, b in zip(seq, seq[1:])) or
        any(b <= a for a, b in zip(ts, ts[1:]))):
        return 5
    print(f"E004LR_RAW_METADATA=PASS CAMERA={sys.argv[2]} "
          f"FRAMES=6 DISTINCT_SEQUENCES=6 BYTES_NONZERO=YES "
          f"TIMESTAMP_SPAN_US={ts[-1]-ts[0]}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
