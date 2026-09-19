#!/usr/bin/env python3
"""ONE read-only SPMI PMIC timer snapshot. No retry even if interrupted."""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import re
import subprocess
import sys

from prepare import ADDRS, HERE, REGMAP, command, golden_preflight, need

PREPARED = HERE/"evidence/PREPARED.json"
CONSUMED = HERE/"evidence/CONSUMED.json"
RESULT = HERE/"evidence/RESULT.json"
ROOT_READ = r"""
import os,sys
p="/sys/kernel/debug/regmap/0-01/registers"
offset=548910
length=36
fd=os.open(p,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
try:
    blob=os.pread(fd,length,offset)
finally:
    os.close(fd)
if len(blob)!=length:
    raise SystemExit("PASSIVE_READ_INCOMPLETE")
sys.stdout.buffer.write(blob)
"""

def one_read() -> None:
    need(PREPARED.is_file() and not CONSUMED.exists() and not RESULT.exists(),
         "not prepared, already consumed or already recorded")
    prepared = json.loads(PREPARED.read_text())
    need(prepared["status"] == "PREPARED_SINGLE_PASSIVE_READ_NOT_CONSUMED"
         and prepared["target_seek_bytes"] == 548910
         and prepared["target_read_bytes"] == 36
         and prepared["target_addresses"] == [f"0x{x:04x}" for x in ADDRS],
         "prepared target drift")
    # Fail closed if another change/boot/camera run happened after preparation.
    fresh = golden_preflight()
    need(fresh["access_metadata_sha256"] == prepared["access_metadata_sha256"]
         and fresh["golden_boot"] == prepared["golden_boot"],
         "SPMI metadata or Golden boot changed after preparation")
    marker = {
        "experiment": "E004fx",
        "status": "ONE_PASSIVE_READ_CONSUMED_BEFORE_IO",
        "boot": prepared["golden_boot"],
        "addresses": prepared["target_addresses"],
        "prepared_sha256": sha256(PREPARED.read_bytes()).hexdigest(),
        "attempt_count": 1,
        "hardware_write_requested": False,
        "emitter_activation_requested": False,
    }
    # Commit the consumed identity on disk before the ONE privileged read.
    with CONSUMED.open("x") as f:
        json.dump(marker, f, indent=2)
        f.write("\n")
        f.flush()
        import os
        os.fsync(f.fileno())
    report = {
        "experiment": "E004fx",
        "boot": prepared["golden_boot"],
        "read_once_identity_consumed": True,
        "pmic_spmi": "0-01",
        "target_addresses": prepared["target_addresses"],
        "requested_debugfs_pread_bytes": 36,
        "kernel_module_loaded_or_flash_driver_installed": False,
        "spmi_register_write_requested": False,
        "emitter_activation_requested": False,
        "physical_led_wiring_verified": False,
        "physical_timer_interval_measured": False,
        "independent_stuck_trigger_shutdown_verified": False,
        "safe_optical_irradiance_verified": False,
        "emitter_enable_authorized": False,
    }
    try:
        read = subprocess.run(["sudo", "-n", sys.executable, "-c", ROOT_READ],
                              capture_output=True, timeout=18, check=False)
        need(read.returncode == 0, "bounded privileged read returned failure")
        need(len(read.stdout) == 36, "read was not exactly four register lines")
        rows = read.stdout.decode("ascii").splitlines()
        need(len(rows) == 4, "unexpected register line count")
        values = {}
        for address, line in zip(ADDRS, rows):
            match = re.fullmatch(rf"{address:04x}: ([0-9a-fA-F]{{2}}|XX)", line)
            need(match is not None, "unexpected regmap output label/format")
            values[f"0x{address:04x}"] = match.group(1).lower()
        readable = all(value != "xx" for value in values.values())
        report["status"] = ("PASS_SINGLE_PASSIVE_IDLE_TIMER_READ" if readable
                            else "INCONCLUSIVE_REGISTER_READ_RETURNED_XX")
        report["idle_timer_register_bytes"] = values
        report["idle_timer_enable_bits"] = {
            reg: None if value == "xx" else bool(int(value, 16) & 0x80)
            for reg, value in values.items()
        }
        report["timer_state_during_windows_capture_proven"] = False
        report["emitter_on_time_limit_proven"] = False
        report["interpretation"] = (
            "Idle-state PMIC config bytes only. Flash node disabled in Golden; "
            "no emission, timeout effectiveness, Windows-streaming timer state, "
            "physical wiring or optical safety is inferred."
        )
    except Exception as exc:
        report["status"] = "INCONCLUSIVE_SINGLE_PASSIVE_READ_CONSUMED"
        report["read_failure_type"] = type(exc).__name__
        report["same_boot_retry_permitted"] = False
    RESULT.write_text(json.dumps(report, indent=2)+"\n")
    print("E004FX_READ_RESULT=" + report["status"])
    print("ONE_READ_CONSUMED=YES SPMI_WRITES=ZERO EMITTER=OFF")
    print("TIMER_BYTES=" + json.dumps(report.get("idle_timer_register_bytes", {})))
    # Never repeat on failure. Postboot health is independently verified afterwards.

if __name__ == "__main__":
    one_read()
