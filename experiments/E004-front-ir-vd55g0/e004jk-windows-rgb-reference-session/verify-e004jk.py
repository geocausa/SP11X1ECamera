#!/usr/bin/env python3
"""Verify privacy-redacted, same-SP11 Windows RGB camera oracle evidence."""
import json
from pathlib import Path

p = Path(__file__).resolve().parent / "evidence" / "windows-rgb-observations.json"
d = json.loads(p.read_text())
assert d["session_date"] == "2026-09-20"
assert d["private_original_sha256"] == "3bcc114bdff518481021c6979dbaef75b63cb448929df5cbc81b2d50aceb1b50"
assert "machine" not in d
expected = {
    ("Surface Camera Rear", "VideoPreview"): (1920, 1080, 7),
    ("Surface Camera Rear", "VideoRecord"): (3840, 2160, 8),
    ("Surface Camera Front", "VideoRecord"): (1920, 1080, 7),
}
assert len(d["observations"]) == len(expected)
for o in d["observations"]:
    key = o["camera"], o["stream"]
    assert key in expected
    w, h, nformats = expected.pop(key)
    assert o["default_subtype"] == "NV12"
    assert o["delivered_dimensions"] == [w, h], key
    assert o["start_status"] == "Success"
    assert o["acquired_frame_handles"] == o["cpu_accessible_nv12_bitmaps"] == 45
    assert o["null_system_timestamps"] == 45
    fmts = o["advertised_formats"]
    assert len(fmts) == nformats
    assert all(f["subtype"] == "NV12" and f["fps_numerator"] == 30
               and f["fps_denominator"] == 1 for f in fmts)
    assert any((f["width"], f["height"]) == (w, h) for f in fmts)
    if o["camera"] == "Surface Camera Front":
        assert any((f["width"], f["height"]) == (2560, 1440) for f in fmts)
        assert o["delivered_dimensions"] == [1920, 1080]
    print("E004jk PASS:", o["camera"], o["stream"],
          "%dx%d" % (w, h), "CPU NV12 handles=45",
          "advertised formats=%d" % nformats)
assert not expected
assert any("not" in q.lower() and "sustained" in q.lower() for q in d["limitations"])
assert any("not" in q.lower() and "image-quality" in q.lower() for q in d["limitations"])
print("E004jk VERIFY: PASS (Windows RGB buffer baseline; advertised != delivered)")
