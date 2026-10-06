#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_CONDITION_WAKE_HELPER_RETURN_TO_CALLER_BRANCH_FRONTIER" and s["case_count"]==4
assert s["wake_import_RVA"]=="0xf7e410" and s["wake_call_RVA"]=="0xce7ac0" and s["wake_call_x0_RVA"]=="0x16a3730" and s["wake_call_executed"] and s["wake_count"]==1 and not s["srw_lock_held_during_wake"]
assert s["helper_return_RVA"]=="0xce7ad0" and s["helper_return_executed"] and s["caller_resume_RVA"]=="0x5be674"
assert s["caller_branch_RVA"]=="0x5be674" and s["caller_branch_target_RVA"]=="0x5bdeb8" and not s["caller_branch_executed"] and s["rejected_altered_contracts"]==12
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JY" and n["retained_state"]["x25_plus_4_u32"]==0 and not n["expected_next_frontier"]["target_executed"]
print(json.dumps({"status":"PASS_E011JX_PORTABLE_REVIEW","cases":4,"next":"E011JY"},sort_keys=True))
