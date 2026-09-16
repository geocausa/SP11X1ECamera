#!/usr/bin/env python3
"""Verify the bounded idle PMIC RAM snapshot and its Golden return."""
import hashlib
import json
from pathlib import Path
import re
import struct

def address(value):
    return int(value.replace("`", ""), 16)

def main():
    root = Path(__file__).resolve().parent
    evidence = root / "evidence"
    log = (evidence / "KD-IDLE-STATE.log").read_text()
    ready = (evidence / "WINDOWS-READY.txt").read_text()
    golden = (evidence / "GOLDEN-RETURN.txt").read_text()
    expected_hash = "756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e"
    assert expected_hash in ready.lower()
    module = re.search(r"^([0-9a-f`]+)\s+([0-9a-f`]+)\s+qcpmic8380\s", log, re.M)
    assert module
    base, end = map(address, module.groups())
    assert end > base + 0x3b8e8
    start = log.index("\nE004FJ_ACTUAL_IDLE_PMIC_STATE\n")
    tail = log[start:]
    rows = re.findall(r"^([0-9a-f`]+)\s+([0-9a-f]{8}`[0-9a-f]{8})\s+([0-9a-f]{8}`[0-9a-f]{8})$", tail, re.M)
    assert len(rows) == 2
    assert address(rows[0][0]) == base + 0x3b8c8
    assert address(rows[1][0]) == base + 0x3b8d8
    data = b"".join(struct.pack("<Q", address(value))
                    for row in rows for value in row[1:])
    assert len(data) == 32
    register_id, init_arg = struct.unpack_from("<II", data)
    old_table, active_table = struct.unpack_from("<QQ", data, 8)
    assert (register_id, init_arg, old_table) == (1, 1, 0)
    assert active_table == base + 0x39470
    assert data[24] == 1 and list(data[25:29]) == [3, 2, 4, 4]
    assert "E004FJ_END_RESUMING" in tail and "Shutdown occurred" in tail
    assert "OVERLAP_GUARD=PASS" in golden
    assert "nodes=no modules=none active_processes=no" in golden
    assert "saved_entry=sp11-audio-fullio-v19c next_entry=" in golden
    result = {
        "status": "PASS_IDLE_WINDOWS_FOUR_CHANNEL_MAPPING",
        "driver_sha256": expected_hash,
        "observed_register_access_identifier": register_id,
        "observed_initialization_argument": init_arg,
        "observed_active_table_rva": hex(active_table - base),
        "initialized": True, "paired_channel_bytes": list(data[25:29]),
        "led1_sources_one_based": [1, 4],
        "led2_sources_one_based": [2, 3],
        "camera_opened": False, "flash_commands_sent": False,
        "physical_current_or_optical_measurement": False,
        "golden_boot_id": re.search(r"boot_id=([^ ]+)", golden).group(1),
        "initial_symbol_lookup_failed": True,
        "recovery": "Resume, refresh module list, resume, read one 32-byte snapshot by verified live base, resume.",
        "pulse_limits_proven": False,
        "normalized_evidence_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(evidence.iterdir()) if p.name != "RESULT.json"
        },
    }
    (evidence / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
