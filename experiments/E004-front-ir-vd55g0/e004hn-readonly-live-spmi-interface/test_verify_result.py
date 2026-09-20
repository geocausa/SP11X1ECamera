#!/usr/bin/env python3
"""E004hn: reject fabricated original Windows live SPMI callback or hit claims."""
from pathlib import Path
import copy,importlib.util,json,zipfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hn_verify",HERE/"verify_result.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
with zipfile.ZipFile(v.ZIP) as z:
    raw=z.read("ORIGINAL-SP7-READONLY-SPMI-LIVE-INTERFACE-KD.log")
result=json.loads(v.RESULT.read_text())
prepared=json.loads(v.PREP.read_text())
v.validate(raw,result,prepared)
v.previous()
TICK=bytes([96])
mutated_records=(
    (raw+b"tamper",result,prepared,"original trace altered"),
    (raw.replace(b"fffff803"+TICK+b"3de7d040  fffff803"+TICK+b"3dea1660",
                 b"fffff803"+TICK+b"3de7d040  fffff803"+TICK+b"3dea1920"),
     result,prepared,"fabricated callback target"),
    (raw.replace(b"E004HN_ALL_BP_CLEAR_NO_CAMERA",b"E004HN_BP_STILL_ARMED"),
     result,prepared,"breakpoint cleanup absent"),
    (raw.replace(b"Closing open log file",b"original log never closed"),
     result,prepared,"original SP7 log never closed"),
    (raw.replace(b"E004HN_PASSIVE_IDLE_WINDOW_ENDED_NO_SPMI_ENTRY",
                 b"E004HN_INVENTED_SPMI_IDLE_HIT"),
     result,prepared,"invented original bound"),
    (raw,result|{"one_shot_natural_idle_spmi_callback_entry_hit_observed":True},
     prepared,"false positive SPMI hit"),
    (raw,result|{"first_writer_of_original_pmic_idle_timer_byte_0x93_identified":True},
     prepared,"fabricated first timer writer"),
    (raw,result|{"actual_bus_sid_or_register_transaction_observed":True},
     prepared,"invented SPMI selector/payload"),
    (raw,result|{"hardware_register_or_physical_emitter_cutoff_proven":True},
     prepared,"invented autonomous hardware off"),
    (raw,result|{"native_linux_ir_or_login_modified":True},
     prepared,"false native emitter/auth flag"),
    (raw,result|{"golden_return_boot_id":"different-boot"},
     prepared,"fabricated Golden return"),
    (raw,result|{"pmic_live_callback_slot_value":"fffff8033dea1920"},
     prepared,"misidentified provider callback"),
    (raw,result|{"all_kd_breakpoints_cleared_original_log_closed_sp7_kd_stopped":False},
     prepared,"incorrect KD cleanup"),
    (raw,result,prepared|{"new_windows_boot_consumed":True},
     "historical preboot scope altered"),
    (raw,result,prepared|{"native_ir_or_login_enabled":True},
     "original preboot emitter authorization altered"),
)
for observed,metadata,preflight,why in mutated_records:
    try:v.validate(observed,metadata,preflight)
    except AssertionError:pass
    else:raise AssertionError("E004HN_UNREJECTED_NEGATIVE "+why)
print("E004HN_ORIGINAL_WINDOWS_LIVE_SPMI_POINTER_NONHIT_SCOPE_NEGATIVES=PASS COUNT="+str(len(mutated_records)))
print("E004HN_ALL_MUTATIONS_IN_MEMORY_NO_NEW_BOOT_CAMERA_PMIC_LED=PASS")
