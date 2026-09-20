#!/usr/bin/env python3
"""E004hb: reject tampered KD evidence and unsupported no-hit interpretation."""
from pathlib import Path
import importlib.util
import json
import zipfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hb_verify",HERE/"verify_result.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
with zipfile.ZipFile(v.ZIP) as z:
    raw=z.read("ORIGINAL-SP7-GENERIC-KD.log")
result=json.loads(v.RESULT.read_text())
prepared=json.loads(v.PREP.read_text())
v.validate(raw,result,prepared)
mutations=(
    (raw+b"tamper",result,prepared,"raw log identity"),
    (raw.replace(b"E004HB_ALL_HW_BREAKPOINTS_CLEARED",b"E004HB_NOT_CLEARED"),
     result,prepared,"missing KD cleanup"),
    (raw,result|{"third_hardware_breakpoint_programming_failed":False},
     prepared,"hidden three-slot resource failure"),
    (raw,result|{"three_hardware_breakpoints_simultaneously_installed_in_cpu":True},
     prepared,"invented third installed breakpoint"),
    (raw,result|{"type_0x4a_descriptor_monitored_during_bounded_boot":True},
     prepared,"unmonitored descriptor promoted to observed"),
    (raw,result|{"hardware_callback_positive_control_obtained_this_session":True},
     prepared,"invented callback positive control"),
    (raw,result|{"no_generic_callback_executed_anywhere_proven":True},
     prepared,"invalid inference from no-hit markers"),
    (raw,result|{"physical_led_current_irradiance_pulse_or_autonomous_fault_off_proven":True},
     prepared,"invented physical output"),
    (raw,result|{"golden_return_boot_id":"not-the-return-boot"},
     prepared,"wrong protected boot identity"),
    (raw,result,prepared|{"native_linux_ir_enabled":True},
     "incorrect native emitter state"),
)
for changed,metadata,preflight,description in mutations:
    try:v.validate(changed,metadata,preflight)
    except AssertionError:pass
    else:raise AssertionError("E004HB_UNREJECTED_MUTATION "+description)
print("E004HB_ORIGINAL_KD_SCOPE_AND_RESOURCE_LIMIT_NEGATIVES=PASS COUNT="+str(len(mutations)))
print("E004HB_NEGATIVE_TESTS_ARE_MEMORY_ONLY=YES")
