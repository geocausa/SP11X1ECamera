#!/usr/bin/env python3
"""Extract the SP11 IMX681 Windows stream/group-hold controls.

The proprietary QTI sensor binary is supplied by the operator and is never copied
into the repository.  This script accepts only the exact same-machine blob already
used by E003e, verifies its SHA-256, and emits derived register metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

EXPECTED_SHA = "f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c"
# Exact IDs in the SHA-pinned MSHW0490 / IMX681 sensorDriverData object.
CONTROL_IDS = {
    "stream_on": 1837,
    "stream_off": 1841,
    "group_hold_on": 1845,
    "group_hold_off": 1849,
}
EXPECTED = {
    "stream_on": (0x0100, 0x01),
    "stream_off": (0x0100, 0x00),
    "group_hold_on": (0x0104, 0x01),
    "group_hold_off": (0x0104, 0x00),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scalar(entry: dict) -> int | None:
    raw = bytes.fromhex(entry["raw_hex"])
    return int.from_bytes(raw, "little") if raw else None


def decode_single_reg_setting(entry: dict, ids: dict[int, dict]) -> dict:
    raw = bytes.fromhex(entry["raw_hex"])
    if len(raw) != 40:
        raise SystemExit(f"regSetting id={entry['id']} has {len(raw)} bytes, expected 40")
    w = struct.unpack("<10I", raw)
    data = scalar(ids[w[4]]) if w[4] in ids else None
    delay = scalar(ids[w[9]]) if w[9] in ids else None
    return {
        "regsetting_id": entry["id"],
        "address": f"0x{w[2]:04x}",
        "data": f"0x{data:02x}" if data is not None else None,
        "addr_type": w[5],
        "data_type": w[6],
        "operation": w[7],
        "delay_us": delay or 0,
        "slave_override": w[0] or None,
    }


def main() -> None:
    here = Path(__file__).resolve().parent
    repo = here.parents[2]
    ap = argparse.ArgumentParser()
    ap.add_argument("oracle", type=Path, help="exact local com.surface.sensormodule.ffc_imx681.bin")
    ap.add_argument("--out", type=Path, default=here / "sensor-lifecycle-oracle.json")
    args = ap.parse_args()

    got = sha256(args.oracle)
    if got != EXPECTED_SHA:
        raise SystemExit(f"oracle SHA mismatch: {got}")

    sys.path.insert(0, str(repo / "tools"))
    import qti_parameter_bin as qti  # type: ignore

    parsed = qti.parse(args.oracle)
    ids = {e["id"]: e for e in parsed["entries"]}
    controls = {}
    for name, ident in CONTROL_IDS.items():
        e = ids.get(ident)
        if not e or e["name"] != "regSetting":
            raise SystemExit(f"{name}: id {ident} is not regSetting")
        ctl = decode_single_reg_setting(e, ids)
        exp_addr, exp_data = EXPECTED[name]
        if (
            int(ctl["address"], 16) != exp_addr
            or int(ctl["data"], 16) != exp_data
            or ctl["addr_type"] != 2
            or ctl["data_type"] != 1
            or ctl["operation"] != 0
            or ctl["delay_us"] != 0
            or ctl["slave_override"] is not None
        ):
            raise SystemExit(f"{name}: unexpected control {ctl}")
        controls[name] = ctl

    fast = ids.get(1833)
    if not fast or fast["name"] != "isFastStandbyEnabled":
        raise SystemExit("isFastStandbyEnabled entry not found at expected id 1833")

    result = {
        "date": "2026-08-28",
        "device": "Surface Camera Front / Sony IMX681 / MSHW0490",
        "oracle_file": args.oracle.name,
        "oracle_sha256": got,
        "policy": "derived metadata only; proprietary blob is not committed",
        "controls": controls,
        "is_fast_standby_enabled_payload_size": fast["payload_size"],
        "conclusion": "Windows sensor data defines exact one-write 0x0100=1 stream-on and 0x0100=0 stream-off controls with zero delay; 0x0104 group hold is separate.",
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    print("E003G_SENSOR_LIFECYCLE_EXTRACTION=PASS")


if __name__ == "__main__":
    main()
