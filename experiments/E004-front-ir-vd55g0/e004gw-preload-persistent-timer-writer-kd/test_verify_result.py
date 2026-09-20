#!/usr/bin/env python3
"""Reject tampering or unjustified claims from the E004gw original KD trace."""
from pathlib import Path
import importlib.util
import json
import zipfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gw_verify",HERE/"verify_result.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
with zipfile.ZipFile(mod.ZIP) as z:
    raw=z.read("ORIGINAL-SP7-PRELOAD-KD.log")
result=json.loads(mod.RESULT.read_text())
prep=json.loads(mod.PREP.read_text())
mod.validate(raw,result,prep)
mutations=(
    (raw+b"tamper",result,prep,"original KD hash drift"),
    (raw.replace(b"E004GW_ALL_KD_BP_DISARMED",b"E004GW_NOT_DISARMED"),
     result,prep,"missing KD cleanup"),
    (raw,result|{"breakpoint_still_resolved_active_at_final_pause":False},
     prep,"missing persistent hook at teardown"),
    (raw,result|{"original_log_actual_matching_timer_request_markers":1},
     prep,"invented matching request"),
    (raw,result|{"actual_first_timer_register_writer_identified":True},
     prep,"fabricated first writer"),
    (raw,result|{"all_pmic_timer_writers_or_uefi_firmware_excluded":True},
     prep,"unjustified all-writer absence"),
    (raw,result|{"pre_first_kd_pause_timer_writes_excluded":True},
     prep,"unobservable pre-KD period"),
    (raw,result|{"deferred_hook_resolved_before_first_pmic_driver_entry_proven":True},
     prep,"unproven driver-entry timing"),
    (raw,result|{"native_linux_ir_emitter_enabled":True},
     prep,"unapproved Linux IR activity"),
    (raw,result|{"golden_return_boot_id":"wrong-boot"},
     prep,"Golden return identity mismatch"),
    (raw,result,prep|{"persistent_breakpoint_required_for_valid_no_hit_conclusion":False},
     "preparation boundary changed"),
)
count=0
for corrupted,metadata,preparation,reason in mutations:
    try:
        mod.validate(corrupted,metadata,preparation)
    except AssertionError:
        count+=1
    else:
        raise AssertionError("E004GW_NEGATIVE_ACCEPTED "+reason)
assert count==len(mutations)
print("E004GW_ORIGINAL_TRACE_AND_NO_FALSE_TIMER_OR_EMITTER_CLAIM_TESTS=PASS COUNT=11")
print("E004GW_MUTATED_FILES_ONLY_IN_MEMORY=YES NO_WINDOWS_CAMERA_OR_PMIC_ACTIVITY=YES")
