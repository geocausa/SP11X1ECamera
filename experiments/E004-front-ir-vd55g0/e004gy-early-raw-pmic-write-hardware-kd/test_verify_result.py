#!/usr/bin/env python3
"""E004gy: reject tampered original KD and invented raw-write/timer/safety claims."""
from pathlib import Path
import importlib.util
import json
import zipfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gy_verify",HERE/"verify_result.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
with zipfile.ZipFile(v.ZIP) as z:
    raw=z.read("ORIGINAL-SP7-RAW-HARDWARE-KD.log")
result=json.loads(v.RESULT.read_text())
prep=json.loads(v.PREP.read_text())
v.validate(raw,result,prep)
cases=(
    (raw+b"tamper",result,prep,"changed raw transcript"),
    (raw.replace(b"E004GY_ALL_HW_BREAKPOINTS_CLEARED",b"E004GY_NOT_CLEARED"),
     result,prep,"missing debugger cleanup"),
    (raw,result|{"corrected_hardware_raw_helper_entry_records_logged":27},
     prep,"fabricated entry count"),
    (raw,result|{"raw_write_entry_spans_overlapping_ee3e_to_ee41":1},
     prep,"invented timer overlap"),
    (raw,result|{"raw_write_alternate_three_direct_callers_observed_in_this_window":True},
     prep,"invented bypass caller"),
    (raw,result|{"all_windows_boot_writers_and_firmware_excluded":True},
     prep,"invented global absence"),
    (raw,result|{"first_idle_timer_0x93_origin_identified":True},
     prep,"invented initialization owner"),
    (raw,result|{"autonomous_hardware_fault_cutoff_or_optical_output_proven":True},
     prep,"invented physical LED safety"),
    (raw,result|{"golden_return_boot_id":"wrong-boot"},prep,
     "incorrect Golden rollback identity"),
    (raw,result,prep|{"native_emitter_authorized":True},
     "unauthorized native emitter in preboot contract"),
)
for modified,metadata,preparation,why in cases:
    try:v.validate(modified,metadata,preparation)
    except AssertionError:pass
    else:raise AssertionError("E004GY_NEGATIVE_ACCEPTED "+why)
print(f"E004GY_ORIGINAL_HARDWARE_KD_AND_UNCERTAINTY_NEGATIVES=PASS COUNT={len(cases)}")
print("E004GY_ALL_NEGATIVE_MUTATIONS_IN_MEMORY_ONLY_NO_KD_LED_OR_CAMERA=YES")
