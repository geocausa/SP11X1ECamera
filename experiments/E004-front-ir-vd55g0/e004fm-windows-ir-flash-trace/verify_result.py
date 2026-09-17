#!/usr/bin/env python3
"""Verify E004fm's partial trace, successful preview and recovery; no hardware I/O."""
import hashlib
import json
from pathlib import Path
import re
import struct

HERE = Path(__file__).resolve().parent

def main():
    evidence = HERE / "evidence"
    win = json.loads((evidence / "WINDOWS.json").read_text())
    log = (evidence / "KD-TRACE.log").read_text()
    golden = (evidence / "GOLDEN-RETURN.txt").read_text()
    capture = "\n".join(win["CaptureLines"])
    assert win["DriverHash"].lower() == "6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b"
    assert win["ScriptHash"].lower() == hashlib.sha256((HERE / "capture.ps1").read_bytes()).hexdigest()
    assert "E004FM_START=Success" in capture and "E004FM_STOP_PASS" in capture
    assert "E004FM_ACQUIRED=12" in capture and "E004FM_END " in capture
    frames = re.findall(r"^E004FM_FRAME n=(\d+) timestamp=([^\n]+)$", capture, re.M)
    assert [int(n) for n, _ in frames] == list(range(1, 13))
    readings = re.findall(r"^E004FM_EXPOSURE phase=([^ ]+) auto=True min_ticks=(\d+) max_ticks=(\d+) step_ticks=(\d+) value_ticks=(\d+)$", capture, re.M)
    assert len(readings) == 13
    assert all(tuple(map(int, row[1:])) == (5000, 2000000, 10, 5000) for row in readings)
    hits = re.findall(r"^E004FM_REQUEST hit=(\d+) code=([0-9a-f]+) bytes=(\d+)$", log, re.M)
    assert hits == [("1", "802f0fb0", "6")]
    assert "Numeric expression missing" in log and "Range error" in log
    recovery = log.split("\nE004FM_FIRST_PAYLOAD_RECOVERY\n", 1)[1]
    row = re.search(r"^[0-9a-f`]+\s+((?:[0-9a-f]{2} ){5}[0-9a-f]{2})", recovery, re.M)
    assert row
    request = struct.unpack("<3H", bytes.fromhex(row.group(1)))
    assert request == (700, 0, 0)
    assert "\nE004FM_BREAKPOINT_REMOVED_RESUMING\n" in recovery
    assert re.search(r"\nE004FM_VERIFY_NO_BREAKPOINTS\n\s*E004FM_NESTED_CONDITION_PASS", log)
    assert "E004FM_FINAL_RESUME" in log and "Shutdown occurred" in log
    assert "OVERLAP_GUARD=PASS" in golden
    assert "saved_entry=sp11-audio-fullio-v19c next_entry=" in golden
    assert "nodes=no modules=none active_processes=no" in golden
    assert "BootOrder: 0005,0004,0000,0001,0002,0006" in golden
    result = {
        "status": "PARTIAL_TRACE_WITH_SUCCESSFUL_WINDOWS_PREVIEW",
        "identity_consumed": True, "same_boot_stream_retry": False,
        "frames": 12, "normal_windows_teardown": True,
        "observed_current_request_ma": list(request),
        "observed_current_command": "0x802f0fb0",
        "standard_exposure_api": {
            "auto": True, "readings": 13, "value_us": 500,
            "min_us": 500, "max_us": 200000, "step_us": 1,
            "actual_sensor_exposure_proven": False,
        },
        "instrumentation_failures": [
            "Initial bp 0 spelling caused a range error; resumed and corrected before capture.",
            "MASM did not accept the compound && expression on first hit; captured the six-byte payload manually, removed breakpoint, resumed.",
        ],
        "full_selector_and_timer_trace_complete": False,
        "physical_current_or_pulse_measurement": False,
        "linux_illumination_activated": False,
        "golden_boot_id": re.search(r"boot_id=([^ ]+)", golden).group(1),
        "evidence_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(evidence.iterdir()) if p.name != "RESULT.json"
        },
        "next_gate": "Validate logger syntax before a fresh Windows stream identity.",
    }
    (evidence / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
