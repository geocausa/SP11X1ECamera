#!/usr/bin/env python3
"""Compare clean E008t output with private same-SP11 DMI, emitting aggregates only."""
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
META = REPO / "experiments/E004-front-ir-vd55g0/e006b-windows-rear-dmi-source-payloads/PARTIAL-RESULT.json"
PRIVATE = REPO.parent / "private/e006b"
FILES = {
    "startup0": "E006B-START0-SOURCE.bin",
    "startup1": "E006B-START1-SOURCE.bin",
    "startup2": "E006B-START2-SOURCE.bin",
    "startup3": "E006B-START3-SOURCE.bin",
    "steady_ac8": "E006B-STEADY-AC8-SOURCE.bin",
}
FIELDS = ("left", "top", "width", "height", "rid", "oid", "merge", "eob", "type")


def decode(payload: bytes) -> list[dict[str, int]]:
    assert len(payload) == 300
    rows = []
    for i in range(25):
        a, b, c = struct.unpack_from("<III", payload, i * 12)
        rows.append({
            "height": a & 0x1fff,
            "width": (a >> 14) & 0x0fff,
            "top": ((a >> 27) & 31) | ((b & 0x1ff) << 5),
            "left": (b >> 9) & 0x1fff,
            "rid": (b >> 23) & 0xff,
            "oid": ((b >> 31) & 1) | ((c & 0x7f) << 1),
            "merge": (c >> 7) & 1,
            "eob": (c >> 8) & 1,
            "type": (c >> 9) & 1,
        })
    return rows


def observed() -> dict[str, bytes]:
    meta = json.loads(META.read_text())
    result = {}
    for cap in meta["captured"]["captures"]:
        label = cap["label"]
        if label not in FILES:
            continue
        candidates = [
            x for x in cap["payloads"]
            if x["dmi_register_offset"] == "0xbc08" and x["selector"] == 1
        ]
        assert len(candidates) == 1
        item = candidates[0]
        assert item["payload_bytes"] == 300
        blob = (PRIVATE / FILES[label]).read_bytes()
        assert hashlib.sha256(blob).hexdigest() == cap["private_source_file_sha256"]
        start = int(item["source_offset"], 16) - int(cap["captured_source_window_base"], 16)
        assert start >= 0 and start + 300 <= len(blob)
        result[label] = blob[start:start + 300]
    assert set(result) == set(FILES)
    return result


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="e008u-host-") as tmp:
        binary = str(Path(tmp) / "offline-roi")
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
             str(HERE / "offline-roi.c"), "-o", binary],
            cwd=HERE, check=True, capture_output=True,
        )
        generated = subprocess.check_output([binary], cwd=HERE)
    assert len(generated) == 4 * 300
    expected = {f"startup{i}": generated[i * 300:(i + 1) * 300] for i in range(4)}
    actual = observed()
    assert expected["startup0"] == actual["startup0"]
    assert all(expected[f"startup{i}"] != actual[f"startup{i}"] for i in (1, 2, 3))
    assert actual["startup2"] == actual["startup3"] == actual["steady_ac8"]

    mismatch = {}
    for label, clean in expected.items():
        a, b = decode(clean), decode(actual[label])
        mismatch[label] = {
            key: sum(x[key] != y[key] for x, y in zip(a, b))
            for key in FIELDS
        }
    assert all(mismatch["startup0"][key] == 0 for key in FIELDS)
    for i in (1, 2, 3):
        m = mismatch[f"startup{i}"]
        assert all(m[key] == 0 for key in ("rid", "oid", "merge", "eob", "type"))
        assert any(m[key] for key in ("left", "top", "width", "height"))

    b1, b2 = decode(actual["startup1"]), decode(actual["startup2"])
    assert len({y["left"] - x["left"] for x, y in zip(b1, b2)}) == 1
    assert len({y["top"] - x["top"] for x, y in zip(b1, b2)}) == 1

    safe = {
        "schema": "E008U-roi-geometry-audit-v1",
        "classification": "OFFLINE_PACKET0_EXACT_NORMAL_ROI_OPEN",
        "parent_git_revision": "21431304bd491f324121d0af85580aae499a631b",
        "active_rear_crop": [4064, 2286],
        "packet0_selector1_exact_records": 25,
        "packet0_selector1_exact_bytes": 300,
        "normal_packet_mismatch_counts_by_field": {
            label: mismatch[label] for label in ("startup1", "startup2", "startup3")
        },
        "normal_phase1_to_phase2_uniform_position_shift": True,
        "normal_phase2_phase3_steady_equal": True,
        "normal_roi_finalizer_source_implementation_complete": False,
        "final_four_packet_selector1_parity_claimed": False,
        "captured_windows_payload_values_emitted": False,
        "captured_windows_payload_hashes_emitted": False,
        "runtime_actions_performed": False,
    }
    (HERE / "RESULT.json").write_text(json.dumps(safe, indent=2, sort_keys=True) + "\n")
    print("E008U_PRIVATE_AUDIT_PASS packet0=25/25 exact, normal ROI finalizer open")


if __name__ == "__main__":
    main()
