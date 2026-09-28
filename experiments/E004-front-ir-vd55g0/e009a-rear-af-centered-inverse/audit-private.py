#!/usr/bin/env python3
"""Private inverse source-shape audit. Output only aggregate counts/booleans."""
from __future__ import annotations
import importlib.util
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "e008u-rear-bf-roi-geometry-audit/audit-private.py"
spec = importlib.util.spec_from_file_location("e009a_private_source", SRC)
audit = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(audit)

def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]

def cell(size: int) -> int:
    return int(f32(float(size) * f32(1.0 / 5.0)))

def candidate_axes(rows: list[dict[str, int]], width: int, height: int):
    horizontal = set()
    for af_width in range(200, width + 1):
        x = ((width >> 1) - (af_width >> 1)) & ~1
        w = af_width & ~1
        x = max(x, 76)
        if x + w > width - 12:
            x = min(x, width - 18)
            w = min(w, width - x - 12)
        cw = cell(w)
        roi_w = cw - 1
        if roi_w > 0 and not roi_w & 1:
            roi_w -= 1
        if cw and all(rows[r * 5 + c]["left"] == x + c * cw and
                      rows[r * 5 + c]["width"] == roi_w
                      for r in range(5) for c in range(5)):
            horizontal.add(af_width)
    vertical = set()
    for af_height in range(200, height + 1):
        y = ((height >> 1) - (af_height >> 1)) & ~1
        h = (af_height & ~1) + 5 + 11
        y = max(y, 64)
        if y + h > height:
            y = min(y, height - 8)
            h = min(h, height - y)
        ch = cell(h)
        roi_h = ch - 1
        if roi_h > 0 and not roi_h & 1:
            roi_h -= 1
        if ch and all(rows[r * 5 + c]["top"] == ((y + r * ch) & ~1) and
                      rows[r * 5 + c]["height"] == roi_h
                      for r in range(5) for c in range(5)):
            vertical.add(af_height)
    return horizontal, vertical

rows = {name: audit.decode(payload) for name, payload in audit.observed().items()
        if name != "startup0"}
assert set(rows) == {"startup1", "startup2", "startup3", "steady_ac8"}
result = {"schema": "E009A-private-centered-inverse-v1", "classification":
          "CENTERED_DIRECT_PATH_COMPATIBLE_NOT_REQUEST_SOURCE_CLOSED",
          "samples": len(rows), "roi_records": len(rows) * 25,
          "tested_geometry": {}, "captured_coordinates_or_hashes_emitted": False,
          "native_rear_runtime_authorized": False}
for key, dims in {"active_crop": (4064, 2286), "raw_sensor": (4076, 2806),
                  "video_output": (3840, 2160)}.items():
    axes = {label: candidate_axes(rec, *dims) for label, rec in rows.items()}
    report = {label: {"horizontal_count": len(a), "vertical_count": len(b),
                      "full_geometry_candidate": bool(a and b)}
              for label, (a, b) in axes.items()}
    a1, b1 = axes["startup1"]
    a2, b2 = axes["startup2"]
    report["packet1_to_2_horizontal_shared_candidates"] = len(a1 & a2)
    report["packet1_to_2_vertical_shared_candidates"] = len(b1 & b2)
    if a1 and a2 and b1 and b2:
        report["packet1_to_2_possible_absolute_size_delta_range"] = {
            "horizontal": [min(abs(y - x) for x in a1 for y in a2),
                           max(abs(y - x) for x in a1 for y in a2)],
            "vertical": [min(abs(y - x) for x in b1 for y in b2),
                         max(abs(y - x) for x in b1 for y in b2)]}
    result["tested_geometry"][key] = report
active = result["tested_geometry"]["active_crop"]
assert all(active[label]["horizontal_count"] == 2 and
           active[label]["vertical_count"] == 2 for label in rows)
assert active["packet1_to_2_horizontal_shared_candidates"] == 0
assert active["packet1_to_2_vertical_shared_candidates"] == 0
for key in ("raw_sensor", "video_output"):
    assert all(not result["tested_geometry"][key][label]["full_geometry_candidate"]
               for label in rows)
(HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print("E009A_PRIVATE_INVERSE_PASS 4 samples, 100 records, active crop compatible")
