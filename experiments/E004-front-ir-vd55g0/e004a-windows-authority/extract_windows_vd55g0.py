#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import sys

REPO = Path(__file__).resolve().parents[3]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))

import qti_parameter_bin as qti
import qti_sensor_summary as qs


PATCH_START = 0x2000
PATCH_END = 0x2227


def _largest_regsetting(path: Path):
    parsed = qti.parse(path)
    ids = {entry["id"]: entry for entry in parsed["entries"]}
    regsets = []
    for entry in parsed["entries"]:
        if entry["name"] != "regSetting" or not entry["payload_size"]:
            continue
        try:
            rows = qs.reg_list(entry, ids)
        except Exception:
            continue
        regsets.append((entry["id"], rows))
    if not regsets:
        raise ValueError("no decodable regSetting entries")
    return max(regsets, key=lambda item: len(item[1]))


def _unique_byte(by_addr, address: int):
    rows = by_addr.get(address, [])
    if len(rows) != 1 or rows[0]["data"] is None:
        raise ValueError(f"expected one byte write at 0x{address:04x}, got {len(rows)}")
    return rows[0]["data"] & 0xFF


def extract_patch_bytes(path: Path) -> bytes:
    _, init = _largest_regsetting(path)
    by_addr = {}
    for row in init:
        by_addr.setdefault(row["address"], []).append(row)
    return bytes(_unique_byte(by_addr, address) for address in range(PATCH_START, PATCH_END + 1))


def extract(path: Path):
    path = Path(path)
    init_id, init = _largest_regsetting(path)
    by_addr = {}
    for row in init:
        by_addr.setdefault(row["address"], []).append(row)

    def le_value(start: int, size: int) -> int:
        return int.from_bytes(bytes(_unique_byte(by_addr, a) for a in range(start, start + size)), "little")

    patch_rows = [row for row in init if PATCH_START <= row["address"] <= PATCH_END]
    patch_addresses = [row["address"] for row in patch_rows]
    expected_addresses = list(range(PATCH_START, PATCH_END + 1))
    duplicates = sorted({a for a in patch_addresses if patch_addresses.count(a) > 1})
    contiguous = sorted(set(patch_addresses)) == expected_addresses and not duplicates
    patch = extract_patch_bytes(path) if contiguous else b""

    target_addrs = (
        list(range(0x0220, 0x0228))
        + list(range(0x0300, 0x0304))
        + list(range(0x0458, 0x045C))
    )
    target_rows = {f"0x{a:04x}": by_addr.get(a, []) for a in target_addrs}

    return {
        "source_file": path.name,
        "source_size": path.stat().st_size,
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "largest_regsetting_id": init_id,
        "largest_regsetting_count": len(init),
        "target_rows": target_rows,
        "decoded_register_values": {
            "0x0220_le32": le_value(0x0220, 4),
            "0x0224_le32": le_value(0x0224, 4),
            "0x0300_le16": le_value(0x0300, 2),
            "0x0458_le16": le_value(0x0458, 2),
        },
        "patch": {
            "start": f"0x{PATCH_START:04x}",
            "end": f"0x{PATCH_END:04x}",
            "expected_bytes": len(expected_addresses),
            "rows_in_range": len(patch_rows),
            "unique_addresses": len(set(patch_addresses)),
            "duplicate_addresses": [f"0x{x:04x}" for x in duplicates],
            "contiguous_full_range": contiguous,
            "sha256": hashlib.sha256(patch).hexdigest() if contiguous else None,
        },
        "first_16_init_rows": init[:16],
        "last_16_init_rows": init[-16:],
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: extract_windows_vd55g0.py <exact Windows sensor .bin>")
    print(json.dumps(extract(Path(sys.argv[1])), indent=2))


if __name__ == "__main__":
    main()
