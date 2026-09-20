#!/usr/bin/env python3
"""E004hd: reject altered original live pointer data and unsupported conclusions."""
from pathlib import Path
import importlib.util,json,zipfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hd_verify",HERE/"verify_result.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
with zipfile.ZipFile(v.ZIP) as z:
    raw=z.read("ORIGINAL-SP7-READONLY-PMIC-IOCTL-HANDLER-KD.log")
result=json.loads(v.RESULT.read_text())
prepared=json.loads(v.PREP.read_text())
v.verify_original_pmic_image()
v.validate(raw,result,prepared)
tick=bytes([96])
mutations=(
    (raw+b"tamper",result,prepared,"original KD byte mutation"),
    (raw.replace(b"fffff803"+tick+b"477db8d8  fffff803"+tick+b"477d9470",
                 b"fffff803"+tick+b"477db8d8  fffff803"+tick+b"477d9500"),
     result,prepared,"fabricated live table pointer"),
    (raw.replace(b"E004HD_BREAKPOINTS_CLEARED",b"E004HD_NOT_CLEARED"),
     result,prepared,"missing debugger cleanup"),
    (raw,result|{"final_handler_global_resolved_rva":"0x39500"},
     prepared,"invented live table RVA"),
    (raw,result|{"final_live_handler_target_oem_pmic_rva":"0x26d50"},
     prepared,"invented callback function RVA"),
    (raw,result|{"fresh_windows_camera_ioctl_preview_or_flash_command_executed":True},
     prepared,"fabricated flash command in read-only session"),
    (raw,result|{"four_channel_callback_executed_in_this_read_only_session":True},
     prepared,"confusing callback pointer with execution"),
    (raw,result|{"original_timer_register_0x93_first_writer_identified":True},
     prepared,"invented timer first writer"),
    (raw,result|{"hardware_emission_current_pulse_or_independent_fault_cutoff_proven":True},
     prepared,"invented physical safety"),
    (raw,result|{"golden_return_boot_id":"wrong-boot"},
     prepared,"wrong Golden rollback"),
    (raw,result,prepared|{"no_debugger_or_pmic_memory_writes":False},
     "altered read-only preboot contract"),
    (raw,result,prepared|{"native_ir_enabled":True},
     "invented native emitter approval"),
)
for changed,metadata,preflight,reason in mutations:
    try:v.validate(changed,metadata,preflight)
    except AssertionError:pass
    else:raise AssertionError("E004HD_UNREJECTED_NEGATIVE "+reason)
print("E004HD_ORIGINAL_LIVE_KD_AND_SCOPE_NEGATIVES=PASS COUNT="+str(len(mutations)))
print("E004HD_ALL_MUTATIONS_IN_MEMORY_ONLY_NO_NEW_WINDOWS_CAMERA_PMIC_LED=YES")
