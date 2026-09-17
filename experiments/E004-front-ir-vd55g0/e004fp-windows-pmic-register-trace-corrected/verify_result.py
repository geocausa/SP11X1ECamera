#!/usr/bin/env python3
"""Verify the accepted E004fp bounded Windows PMIC trace and Golden return."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"


def parse_db_byte(line: str) -> int:
    m = re.match(r"^[0-9a-f`]+\s+([0-9a-f]{2})\b", line.strip(), re.I)
    if not m:
        raise AssertionError(f"not a one-byte db line: {line!r}")
    return int(m.group(1), 16)


def main() -> None:
    log = (EVIDENCE / "WINDOWS-KD.log").read_text()
    capture = (EVIDENCE / "WINDOWS-CAPTURE.txt").read_text()
    post = (EVIDENCE / "POSTBOOT.txt").read_text()

    assert "E004FP_DRY_BEGIN" in log
    assert "E004FP_DRY_END_STAY_BROKEN" in log
    for reg in ("ee3e", "ee41", "ee4a", "ee4d", "ee67"):
        assert f"E004FP_DRY_TARGET reg={reg}" in log
    for reg in ("ee42", "ee68"):
        assert f"E004FP_DRY_SKIP reg={reg}" in log
    assert "E004FP_DRY_POSTREG raw=1234ee4a reg=ee4a" in log
    for error in ("Numeric expression missing", "Range error", "Syntax error"):
        assert error not in log

    armed = log.split("E004FP_ARMED_RESUMING", 1)[1]
    pre_pat = re.compile(
        r"^E004FP_PRE hit=(\d+) reg=([0-9a-f]+) mask=([0-9a-f]+) read_rc=([0-9a-f]+)\n"
        r"([^\n]+)\n([^\n]+)$", re.M | re.I)
    post_pat = re.compile(
        r"^E004FP_POST hit=(\d+) reg=([0-9a-f]+) mask=([0-9a-f]+) write_rc=([0-9a-f]+)\n"
        r"([^\n]+)$", re.M | re.I)
    pres = list(pre_pat.finditer(armed))
    posts = list(post_pat.finditer(armed))
    assert len(pres) == len(posts) == 7

    operations = []
    for pre, post_match in zip(pres, posts):
        phit, preg, pmask, prc, old_line, req_line = pre.groups()
        qhit, qreg, qmask, qrc, final_line = post_match.groups()
        assert phit == qhit and preg.lower() == qreg.lower() and pmask.lower() == qmask.lower()
        operations.append({
            "hit": int(phit),
            "register": "0x" + preg.lower(),
            "mask": int(pmask, 16),
            "read_rc": int(prc, 16),
            "old": parse_db_byte(old_line),
            "requested": parse_db_byte(req_line),
            "write_rc": int(qrc, 16),
            "final": parse_db_byte(final_line),
        })

    expected = [
        ("0xee4a", 0x70, 0x01, 0x00, 0x01),
        ("0xee4b", 0x70, 0x01, 0x00, 0x01),
        ("0xee4c", 0x70, 0x01, 0x00, 0x01),
        ("0xee4d", 0x70, 0x01, 0x00, 0x01),
        ("0xee4a", 0x07, 0x01, 0x05, 0x05),
        ("0xee4d", 0x07, 0x01, 0x05, 0x05),
        ("0xee67", 0x01, 0x01, 0x00, 0x00),
    ]
    actual = [(o["register"], o["mask"], o["old"], o["requested"], o["final"]) for o in operations]
    assert actual == expected
    assert all(o["read_rc"] == 0 and o["write_rc"] == 0 for o in operations)
    assert [o["hit"] for o in operations] == list(range(1, 8))
    assert not any(0xEE3E <= int(o["register"], 16) <= 0xEE41 for o in operations)
    assert "E004FP_BREAKPOINTS_CLEARED" in log
    assert "Shutdown occurred" in log

    assert "E004FP_INIT_PASS" in capture
    assert "E004FP_START=Success" in capture
    assert "E004FP_ACQUIRED=12" in capture
    assert "E004FP_STOP_PASS" in capture
    frames = [int(x) for x in re.findall(r"^E004FP_FRAME n=(\d+) timestamp=", capture, re.M)]
    assert frames == list(range(1, 13))
    exposure = re.findall(
        r"^E004FP_EXPOSURE phase=([^ ]+) auto=True min_ticks=(\d+) max_ticks=(\d+) step_ticks=(\d+) value_ticks=(\d+)$",
        capture, re.M)
    assert len(exposure) == 13
    assert all(tuple(map(int, row[1:])) == (5000, 2000000, 10, 5000) for row in exposure)

    assert "saved_entry=sp11-audio-fullio-v19c" in post
    assert "next_entry=" in post
    assert "BootOrder: 0005,0004,0000,0001,0002,0006" in post
    assert "OVERLAP_GUARD=PASS" in post
    assert "nodes=no modules=none active_processes=no" in post
    boot_ids = re.findall(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", post, re.I)
    assert boot_ids

    result = {
        "status": "PASS_BOUNDED_WINDOWS_PMIC_REGISTER_TRACE",
        "identity": "E004fp",
        "identity_consumed": True,
        "same_boot_retry": False,
        "frames": 12,
        "normal_capture_teardown": True,
        "breakpoints_cleared": True,
        "operations": operations,
        "timer_register_access_observed": False,
        "timer_absence_scope": "this one bounded 12-frame Windows IR preview only",
        "trigger_sources_programmed": [1, 4],
        "trigger_low3_final": 5,
        "trigger_interpretation_from_E004fl": "hardware, level-sensitive, active-high",
        "common_ee67_bit0_old": 1,
        "common_ee67_bit0_final": 0,
        "common_ee67_bit0_live_write_proven": True,
        "standard_exposure_api_us": 500,
        "actual_sensor_exposure_proven": False,
        "physical_current_or_optical_power_measured": False,
        "linux_illumination_activated": False,
        "golden_boot_id": boot_ids[0],
        "raw_windows_capture_file_sha256": "7a477318d8ad43f56f214ba0a7e6dc3e5cd6278fedfc56488f53ad573b9521d4",
        "evidence_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(EVIDENCE.iterdir()) if p.is_file() and p.name != "RESULT.json"
        },
        "next_gate": "Resolve actual VD55G0 sensor exposure/strobe envelope and determine whether any separate PMIC timer programming is required before native emitter activation.",
    }
    (EVIDENCE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
