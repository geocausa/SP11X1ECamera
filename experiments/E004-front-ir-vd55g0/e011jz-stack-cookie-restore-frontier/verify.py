#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_STACK_COOKIE_CHECK_TO_NONVOLATILE_RESTORE_FRONTIER" and s["case_count"]==s["cookie_axis_count"]==4
assert s["cookie_contract"]=="opaque_process_cookie_value" and not s["cookie_native_value_qualified"] and s["cookie_global_RVA"]=="0x1607000"
assert s["x19_RVA"]=="0x17a70d0" and s["stack_adjust_RVA"]=="0x5be36c" and s["stack_adjust_u64"]=="0x480"
assert s["cookie_check_call_RVA"]=="0x5be370" and s["cookie_check_target_RVA"]=="0x11f0" and s["cookie_check_executed"] and s["cookie_check_success"] and s["resume_RVA"]=="0x5be374" and not s["resume_executed"]
assert s["rejected_altered_contracts"]==12 and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KA" and n["caller_authority"]["caller_resume_RVA"]=="0x5b826c"
print(json.dumps({"status":"PASS_E011JZ_PORTABLE_REVIEW","cases":4,"next":"E011KA"},sort_keys=True))
