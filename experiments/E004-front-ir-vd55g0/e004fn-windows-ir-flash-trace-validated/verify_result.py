#!/usr/bin/env python3
"""Verify bounded Windows flash requests and recovery without hardware access."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent

def main():
    evidence = HERE / "evidence"
    log = (evidence / "KD-TRACE.log").read_text()
    win = json.loads((evidence / "WINDOWS.json").read_text())
    golden = (evidence / "GOLDEN-RETURN.txt").read_text()
    assert win["DriverHash"].lower() == "6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b"
    assert win["ScriptHash"].lower() == hashlib.sha256((HERE / "capture.ps1").read_bytes()).hexdigest()
    dry = log.split("\nE004FN_DRY_BEGIN\n", 1)[1].split("\nE004FN_DRY_END_RESUMING\n", 1)[0]
    assert dry.count("\nE004FN_DRY_CASE_DONE") == 7
    assert len(re.findall(r"^E004FN_DRY_REQUEST", dry, re.M)) == 7
    assert len(re.findall(r"^[0-9a-f`]+  4d 5a", dry, re.M)) == 4
    after = log.split("\nE004FN_ARMED_RESUMING\n", 1)[1]
    for error in ("Numeric expression missing", "Range error", "Syntax error"):
        assert error not in dry and error not in after
    pattern = r"^E004FN_REQUEST hit=(\d+) code=([0-9a-f]+) bytes=(\d+)\n"
    matches = list(re.finditer(pattern, after, re.M))
    assert len(matches) == 5
    requests = []
    for i, match in enumerate(matches):
        hit, code, size = match.groups()
        block = after[match.end():matches[i+1].start() if i+1 < len(matches) else len(after)]
        data = bytearray()
        for line in block.splitlines():
            row = re.match(r"^[0-9a-f`]+  (.*)$", line)
            if not row:
                break
            column = row.group(1).split("  ", 1)[0].replace("-", " ")
            data.extend(bytes.fromhex(column))
        assert len(data) == int(size)
        requests.append({"hit": int(hit), "command": "0x" + code,
                         "bytes": int(size), "payload_hex": data.hex()})
    expected = [
        ("0x802f0fb0", "bc0200000000"),
        ("0x802f0fcc", "00000000"),
        ("0x802f0fd0", "0100000001000000000000000100000000000000"),
        ("0x802f0fc8", "01000001"),
        ("0x802f0fc8", "00000000"),
    ]
    assert [(r["command"], r["payload_hex"]) for r in requests] == expected
    assert [r["hit"] for r in requests] == list(range(1, 6))
    assert re.search(r"\nE004FN_CLEANUP\n\s*E004FN_BREAKPOINT_REMOVED_RESUMING\n", after)
    assert "Shutdown occurred" in after
    capture = "\n".join(win["CaptureLines"])
    assert "E004FN_START=Success" in capture and "E004FN_STOP_PASS" in capture
    assert "E004FN_ACQUIRED=12" in capture and "E004FN_END " in capture
    frames = re.findall(r"^E004FN_FRAME n=(\d+) timestamp=", capture, re.M)
    assert list(map(int, frames)) == list(range(1, 13))
    readings = re.findall(r"^E004FN_EXPOSURE phase=([^ ]+) auto=True min_ticks=(\d+) max_ticks=(\d+) step_ticks=(\d+) value_ticks=(\d+)$", capture, re.M)
    assert len(readings) == 13
    assert all(tuple(map(int, row[1:])) == (5000, 2000000, 10, 5000) for row in readings)
    assert "OVERLAP_GUARD=PASS" in golden
    assert "saved_entry=sp11-audio-fullio-v19c next_entry=" in golden
    assert "nodes=no modules=none active_processes=no" in golden
    assert "BootOrder: 0005,0004,0000,0001,0002,0006" in golden
    result = {
        "status": "PASS_BOUNDED_WINDOWS_FLASH_REQUEST_SEQUENCE",
        "identity_consumed": True, "same_boot_retry": False,
        "idle_parser_cases_passed": 7, "frames": 12, "normal_teardown": True,
        "observed_requests": requests,
        "observed_led_current_requests_ma": [700, 0, 0],
        "observed_input_selector": 0,
        "observed_trigger_mode_words": [1, 1, 0, 1, 0],
        "static_handler_interpretation": {
            "logical_led": 1, "sources_one_based": [1, 4],
            "trigger": "hardware, level-sensitive, active-high",
            "common_ee67_bit0_requested": 0,
            "native_trigger_selector_matches": True,
        },
        "timer_command_observed": False,
        "effective_hardware_timeout_proven": False,
        "standard_exposure_api_us": 500,
        "actual_sensor_exposure_proven": False,
        "physical_pulse_or_current_measured": False,
        "linux_illumination_activated": False,
        "golden_boot_id": re.search(r"boot_id=([^ ]+)", golden).group(1),
        "evidence_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(evidence.iterdir()) if p.name != "RESULT.json"
        },
        "next_gate": "Establish actual pulse envelope and PMIC timeout/common-bit state; keep native illumination off.",
    }
    (evidence / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
