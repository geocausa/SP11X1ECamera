#!/usr/bin/env python3
"""Offline audit of E004ga aborted Windows one-shot; never run camera or KD."""
import hashlib, json
from pathlib import Path

here=Path(__file__).resolve().parent
e=here/"evidence"
prepared=json.loads((e/"PREPARED.json").read_text())
aborted=json.loads((e/"ABORTED.json").read_text())
post=(e/"POSTBOOT.txt").read_text()
assert prepared["status"]=="OFFLINE_PREPARED_NOT_ARMED_NOT_CONSUMED"
assert prepared["branch"]=="experiment/e004-front-ir-vd55g0"
for name,expected in prepared["files_sha256"].items():
    if name=="README.md":
        continue  # amended only after the consumed abort, not capture code
    assert hashlib.sha256((here/name).read_bytes()).hexdigest()==expected,name
assert aborted["experiment"]=="E004ga" and aborted["identity_consumed"]
assert aborted["status"]=="ABORTED_DURING_KD_DRY_VALIDATION_NO_CAPTURE"
assert aborted["prepared_checkpoint"]=="7b19ffc0064ce71d62d79b437979558de608c8ab"
assert aborted["sp7_original_kd_log_bytes"]==7539
assert aborted["sp7_original_kd_log_sha256"]=="3229becbccffc774c9b2a4026661278135fff1f6ab5dd36f557f52e75c8e4ace"
assert aborted["windows_preview_frames"]==0 and not aborted["pmic_trace_collected"]
dry=aborted["kd_dry_observed"]
assert all(dry[k] for k in ("target_ee3e","skip_ee46","skip_ee4e","dry_complete",
                               "breakpoints_cleared","target_resumed_before_reboot",
                               "kd_process_stopped"))
assert not dry["arm_script_executed"] and not dry["capture_started"]
assert not aborted["emitter_activation_authorized"]
for marker in ("E004GA_ABORT_GOLDEN_POSTBOOT","c017bcd7-4e86-45ed-8453-224646b6cc8e",
               "saved_entry=sp11-audio-fullio-v19c","next_entry=\n",
               "BootCurrent: 0005","BootOrder: 0005,0004,0000,0001,0002,0006",
               "nodes=no modules=none active_processes=no","OVERLAP_GUARD=PASS"):
    assert marker in post,marker
assert hashlib.sha256((e/"POSTBOOT.txt").read_bytes()).hexdigest()=="7a0df8d104fb07e88f59c0b8279ade3bd6275c3e08881c0631271c69c7657067"
print("E004GA=ABORTED_AND_CONSUMED KD_DRY_REQUIRED_ENABLE_REGS=SKIPPED CAMERA_PREVIEW=NOT_RUN")
print("GOLDEN_POSTBOOT=PASS PMIC_TRACE=NOT_COLLECTED NO_E004GA_RETRY=YES")
