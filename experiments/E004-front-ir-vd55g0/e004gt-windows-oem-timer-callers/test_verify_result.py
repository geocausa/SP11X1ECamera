#!/usr/bin/env python3
"""E004gt: reject changed original logs, fictitious callbacks or hardware claims."""
from pathlib import Path
from hashlib import sha256
import importlib.util,json,zipfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("verify_gt",HERE/"verify_result.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
result=json.loads(m.RESULT.read_text());prepared=json.loads(m.PREPARED.read_text())
with zipfile.ZipFile(m.ZIP) as z:
    kd=z.read("ORIGINAL-SP7-KD.log")
    cap=z.read("ORIGINAL-WINDOWS-CAPTURE-UTF16LE.log")
source=m.CAPTURE_SCRIPT.read_bytes()
m.validate(kd,cap,result,prepared,source)
mutations=(
    (kd+b"unapproved",cap,result,prepared,source,"altered KD"),
    (kd,cap+b"unapproved",result,prepared,source,"altered capture"),
    (kd,cap,result,prepared,source+b"unapproved","altered capture script"),
    (kd,cap,result|{"kd_callback_hits_during_bounded_oem_session":
        {"pmic_four_timer":1,"pmic_single_timer":0,
         "flash_timer_wrapper":0,"flash_config":0}},prepared,source,
         "invented callback hit"),
    (kd,cap,result|{"preboot_or_early_init_timer_programming_excluded":True},
         prepared,source,"invented early-boot coverage"),
    (kd,cap,result|{"hardware_timer_active_or_autonomous_cutoff_proven":True},
         prepared,source,"invented hardware autonomy"),
    (kd,cap,result|{"linux_native_ir_emitter_enabled":True},
         prepared,source,"misreported Linux emitter"),
    (kd,cap,result,prepared|{"normal_oem_preview_max_frames":64},source,
         "changed approved preview limit"),
)
for args in mutations:
    try:m.validate(*args[:5])
    except AssertionError:pass
    else:raise AssertionError("E004GT_FAIL_CLOSED negative accepted: "+args[5])
print("E004GT_ORIGINAL_LOG_AND_BOUNDARY_NEGATIVE_CASES=PASS COUNT=8")
print("NO_CAPTURE_OR_KERNEL_OR_EMITTER_EXECUTED_BY_NEGATIVE_TEST=YES")
