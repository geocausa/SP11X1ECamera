#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, struct, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
E004A = REPO / "experiments/E004-front-ir-vd55g0/e004a-windows-authority"
sys.path.insert(0, str(E004A))
from extract_windows_vd55g0 import _largest_regsetting

PACKAGE = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamauxsensor_extension8380.inf_arm64_84ddd55dc933cac9/com.surface.sensormodule.aux_vd55g0_MSHW0492.bin")
PACKET = E004A / "E004_IR_4C74_PACKET_20260912.bin"

PACKAGE_SHA = "e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794"
PACKET_SHA = "81e96e0470cbfa58065eba12ea1a998349b306111f2edee296d7044a69146cdd"
PATCH_SHA = "5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321"


def sha(data_or_path):
    if isinstance(data_or_path, (str, Path)):
        data = Path(data_or_path).read_bytes()
    else:
        data = data_or_path
    return hashlib.sha256(data).hexdigest()


def u16(b, off):
    return struct.unpack_from("<H", b, off)[0]


def u32(b, off):
    return struct.unpack_from("<I", b, off)[0]


def parse_packet(blob: bytes):
    out = []
    off = 0
    while off < len(blob):
        if off + 4 > len(blob):
            raise ValueError(f"truncated command at 0x{off:x}")
        kind = (blob[off + 2], blob[off + 3])
        if kind == (1, 9):
            if off + 20 > len(blob):
                raise ValueError(f"truncated poll at 0x{off:x}")
            cmd = {
                "kind": "poll",
                "offset": off,
                "length": 20,
                "data_type": blob[off],
                "addr_type": blob[off + 1],
                "command_type": blob[off + 2],
                "opcode": blob[off + 3],
                "timeout_ms": u16(blob, off + 4),
                "reserved0": u16(blob, off + 6),
                "address": u16(blob, off + 8),
                "address_upper": u16(blob, off + 10),
                "expected": u32(blob, off + 12),
                "tail": u32(blob, off + 16),
            }
            out.append(cmd)
            off += 20
            continue

        if kind == (1, 5):
            if off + 8 > len(blob):
                raise ValueError(f"truncated write header at 0x{off:x}")
            count = u16(blob, off)
            length = 8 + count * 8
            if off + length > len(blob):
                raise ValueError(f"truncated write block at 0x{off:x}")
            entries = []
            p = off + 8
            for i in range(count):
                entries.append({
                    "index": i,
                    "address": u16(blob, p),
                    "address_upper": u16(blob, p + 2),
                    "data": u16(blob, p + 4),
                    "data_upper": u16(blob, p + 6),
                })
                p += 8
            cmd = {
                "kind": "write",
                "offset": off,
                "length": length,
                "count": count,
                "command_type": blob[off + 2],
                "opcode": blob[off + 3],
                "data_type": blob[off + 4],
                "addr_type": blob[off + 5],
                "reserved": u16(blob, off + 6),
                "entries": entries,
            }
            out.append(cmd)
            off += length
            continue

        raise ValueError(
            f"unknown packet command at 0x{off:x}: "
            + blob[off:off + 16].hex(" ")
        )

    return out


def map_to_package(commands, rows):
    row_i = 0
    mapped = []
    for ci, cmd in enumerate(commands):
        start = row_i
        if cmd["kind"] == "poll":
            if row_i >= len(rows):
                raise ValueError("packet has extra poll command")
            row = rows[row_i]
            checks = {
                "operation": row["operation"] == 4,
                "address": row["address"] == cmd["address"],
                "data": row["data"] == cmd["expected"],
                "addr_type": row["addr_type"] == cmd["addr_type"],
                "data_type": row["data_type"] == cmd["data_type"],
                "timeout": row["delay_us"] == cmd["timeout_ms"] * 1000,
                "slave_override": row["slave_override"] is None,
                "address_upper_zero": cmd["address_upper"] == 0,
                "reserved_zero": cmd["reserved0"] == 0,
                "tail_ffff": cmd["tail"] == 0xFFFF,
            }
            if not all(checks.values()):
                raise ValueError(f"poll command {ci} != package row {row_i}: {checks}")
            row_i += 1
        else:
            for entry in cmd["entries"]:
                if row_i >= len(rows):
                    raise ValueError("packet has extra write entry")
                row = rows[row_i]
                checks = {
                    "operation": row["operation"] == 0,
                    "address": row["address"] == entry["address"],
                    "data": row["data"] == entry["data"],
                    "addr_type": row["addr_type"] == cmd["addr_type"],
                    "data_type": row["data_type"] == cmd["data_type"],
                    "delay": (row["delay_us"] or 0) == 0,
                    "slave_override": row["slave_override"] is None,
                    "address_upper_zero": entry["address_upper"] == 0,
                    "data_upper_zero": entry["data_upper"] == 0,
                }
                if not all(checks.values()):
                    raise ValueError(
                        f"write command {ci} entry {entry['index']} != package row {row_i}: {checks}"
                    )
                row_i += 1
        mapped.append({
            "command_index": ci,
            "kind": cmd["kind"],
            "packet_offset": f"0x{cmd['offset']:04x}",
            "packet_length": cmd["length"],
            "package_row_start": start,
            "package_row_end": row_i - 1,
            "package_rows": row_i - start,
        })

    if row_i != len(rows):
        raise ValueError(f"packet consumed {row_i} package rows, expected {len(rows)}")
    return mapped


def decode():
    if sha(PACKAGE) != PACKAGE_SHA:
        raise ValueError("Surface sensor package identity drift")
    if sha(PACKET) != PACKET_SHA:
        raise ValueError("captured InitialConfig packet identity drift")

    regsetting_id, rows = _largest_regsetting(PACKAGE)
    blob = PACKET.read_bytes()
    commands = parse_packet(blob)
    mapping = map_to_package(commands, rows)

    waits = [c for c in commands if c["kind"] == "poll"]
    writes = [c for c in commands if c["kind"] == "write"]
    flat_writes = [e for c in writes for e in c["entries"]]
    patch = bytes(
        e["data"] & 0xff
        for e in flat_writes
        if 0x2000 <= e["address"] <= 0x2227
    )

    if len(patch) != 552 or sha(patch) != PATCH_SHA:
        raise ValueError("Surface patch extraction mismatch")

    # Exact expected partition of the 601 Surface package rows.
    expected_partition = [
        ("poll", 0, 0),
        ("write", 1, 553),
        ("poll", 554, 554),
        ("write", 555, 555),
        ("poll", 556, 556),
        ("poll", 557, 557),
        ("write", 558, 600),
    ]
    got_partition = [
        (m["kind"], m["package_row_start"], m["package_row_end"]) for m in mapping
    ]
    if got_partition != expected_partition:
        raise ValueError(f"unexpected command partition {got_partition}")

    timeline = [
        {
            "step": 1,
            "windows_fact": "poll 0x002c == 0x01",
            "timeout_ms": 6,
            "package_rows": [0, 0],
            "reference_name_only": "ST calls state 0x01 READY_TO_BOOT",
        },
        {
            "step": 2,
            "windows_fact": "write 0x2000..0x2227 (552 bytes), then write 0x0200=0x02",
            "package_rows": [1, 553],
            "write_count": 553,
            "surface_patch_sha256": PATCH_SHA,
            "reference_name_only": "ST calls 0x0200=2 PATCH_SETUP",
        },
        {
            "step": 3,
            "windows_fact": "poll 0x0200 == 0x00",
            "timeout_ms": 28,
            "package_rows": [554, 554],
        },
        {
            "step": 4,
            "windows_fact": "write 0x0200=0x01",
            "package_rows": [555, 555],
            "write_count": 1,
            "reference_name_only": "ST calls 0x0200=1 BOOT",
        },
        {
            "step": 5,
            "windows_fact": "poll 0x0200 == 0x00",
            "timeout_ms": 6,
            "package_rows": [556, 556],
        },
        {
            "step": 6,
            "windows_fact": "poll 0x002c == 0x02",
            "timeout_ms": 4,
            "package_rows": [557, 557],
            "reference_name_only": "ST calls state 0x02 SW_STBY",
        },
        {
            "step": 7,
            "windows_fact": "write 43 post-boot timing/config registers",
            "package_rows": [558, 600],
            "write_count": 43,
        },
    ]

    final = writes[-1]["entries"]
    by_addr = {e["address"]: e["data"] & 0xff for e in final}
    def le(start, n):
        return int.from_bytes(bytes(by_addr[start+i] for i in range(n)), "little")

    compact_commands = []
    for c, m in zip(commands, mapping):
        q = {k: v for k, v in c.items() if k != "entries"}
        if c["kind"] == "write":
            q["first_write"] = {
                "address": f"0x{c['entries'][0]['address']:04x}",
                "data": f"0x{c['entries'][0]['data']:02x}",
            }
            q["last_write"] = {
                "address": f"0x{c['entries'][-1]['address']:04x}",
                "data": f"0x{c['entries'][-1]['data']:02x}",
            }
        q.update(m)
        compact_commands.append(q)

    return {
        "schema": "sp11-camera-e004d-windows-initialconfig-decode-v1",
        "authority": "same-machine Windows exact package + live captured InitialConfig packet",
        "sensor_package": {
            "path": str(PACKAGE),
            "sha256": PACKAGE_SHA,
            "largest_regsetting_id": regsetting_id,
            "rows": len(rows),
        },
        "live_initialconfig_packet": {
            "path": str(PACKET),
            "sha256": PACKET_SHA,
            "bytes": len(blob),
            "commands": len(commands),
            "poll_commands": len(waits),
            "write_commands": len(writes),
            "write_entries": len(flat_writes),
        },
        "packet_command_format_observed": {
            "poll": {
                "fixed_bytes": 20,
                "signature_bytes_2_3": ["0x01", "0x09"],
                "fields_used_by_exact_driver": "data_type byte0; addr_type byte1; timeout_ms u16@+4; register u16@+8; expected u32@+12",
            },
            "write": {
                "signature_bytes_2_3": ["0x01", "0x05"],
                "header_bytes": 8,
                "count": "u16@+0",
                "data_type": "byte@+4",
                "addr_type": "byte@+5",
                "entry_bytes": 8,
                "entry_fields_used_by_exact_driver": "register u16@+0; data u16@+4",
            },
        },
        "commands": compact_commands,
        "package_replay": {
            "rows_matched_exactly": len(rows),
            "rows_unmatched": 0,
            "packet_extra_operations": 0,
            "partition": mapping,
        },
        "surface_patch": {
            "start": "0x2000",
            "end": "0x2227",
            "bytes": len(patch),
            "sha256": sha(patch),
            "followed_immediately_by": "write 0x0200=0x02 in same 553-write Windows command",
        },
        "timeline": timeline,
        "post_boot_config": {
            "writes": len(final),
            "raw_writes": [
                {"address": f"0x{e['address']:04x}", "data": f"0x{e['data'] & 0xff:02x}"}
                for e in final
            ],
            "decoded_windows_values": {
                "ext_clock_hz": le(0x0220, 4),
                "mipi_data_rate_bps": le(0x0224, 4),
                "line_length": le(0x0300, 2),
                "orientation": by_addr[0x0302],
                "darkcal_pedestal": by_addr[0x0416],
                "frame_length": le(0x0458, 2),
                "exposure_mode": by_addr[0x044c],
                "manual_analog_gain": by_addr[0x044d],
                "manual_coarse_exposure": le(0x044e, 2),
                "manual_digital_gain": le(0x0450, 2),
                "gpio_ctrl": [by_addr[a] for a in range(0x0467, 0x046b)],
                "roi_x_start": le(0x045e, 2),
                "roi_x_end": le(0x0460, 2),
                "roi_y_start": le(0x0462, 2),
                "roi_y_end": le(0x0464, 2),
                "y_start": le(0x045a, 2),
                "y_end": le(0x045c, 2),
            },
            "reference_only_interpretation": {
                "source": "public ST driver naming only; not SP11 parity authority",
                "0x0200=0x02": "PATCH_SETUP",
                "0x0200=0x01": "BOOT",
                "0x002c=0x01": "READY_TO_BOOT",
                "0x002c=0x02": "SW_STBY",
                "0x044c=0x02": "manual exposure mode",
                "gpio_ctrl_1_2_1_1": "GPIO1 uses ST's STROBE selector value 0x02; GPIO0/2/3 use DISABLED selector value 0x01",
            },
        },
        "linux_authorization": {
            "sensor_data_write_authorized": False,
            "reason": "E004d is Windows sequence reconstruction only; Linux write experiment requires a separately checkpointed bounded plan.",
        },
    }


def main():
    print(json.dumps(decode(), indent=2))


if __name__ == "__main__":
    main()
