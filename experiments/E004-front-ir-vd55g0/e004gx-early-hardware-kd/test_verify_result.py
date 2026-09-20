#!/usr/bin/env python3
"""E004gx: reject modified raw KD bytes and fabricated timer, no-write or safety claims."""
from pathlib import Path
import importlib.util
import json
import zipfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gx_verifier",HERE/"verify_result.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
with zipfile.ZipFile(v.ZIP) as z:
    raw=z.read("ORIGINAL-SP7-HARDWARE-KD.log")
result=json.loads(v.RESULT.read_text())
prepared=json.loads(v.PREPARED.read_text())
v.validate(raw,result,prepared)
cases=(
    (raw+b"tamper",result,prepared,"original log mutation"),
    (raw.replace(b"E004GX_ALL_HW_BP_CLEARED",b"E004GX_BP_NOT_CLEARED"),
     result,prepared,"removed cleanup"),
    (raw,result|{"raw_hardware_execute_helper_entry_records_logged":105},
     prepared,"invented hardware positive-control count"),
    (raw,result|{"hardware_logged_ee3e_through_ee41_entry_requests":1},
     prepared,"invented timer address hit"),
    (raw,result|{"complete_windows_boot_or_other_cores_writer_absence_proven":True},
     prepared,"invented global no-write coverage"),
    (raw,result|{"pmic_reset_default_or_earliest_timer_register_writer_identified":True},
     prepared,"invented initial timer writer"),
    (raw,result|{"hardware_optical_current_irradiance_pulse_or_autonomous_cutoff_proven":True},
     prepared,"invented physical LED safety"),
    (raw,result|{"golden_return_boot_id":"wrong-boot"},
     prepared,"wrong Golden return"),
    (raw,result,prepared|{"native_linux_emitter_authorized":True},
     "unauthorized native LED enabled in preboot evidence"),
)
for modified,metadata,preflight,name in cases:
    try:v.validate(modified,metadata,preflight)
    except AssertionError:pass
    else:raise AssertionError("E004GX_NEGATIVE_TEST_FAILED "+name)
print(f"E004GX_MUTATED_ORIGINAL_TRACE_AND_SCOPE_NEGATIVES=PASS COUNT={len(cases)}")
print("E004GX_TESTS_ARE_IN_MEMORY_ONLY_NO_KD_CAMERA_LED=YES")
