#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_CALLER_BRANCH_ZERO_STATUS_TO_5BE368_FRONTIER" and s["case_count"]==4
assert s["caller_branch_RVA"]=="0x5be674" and s["caller_branch_target_RVA"]=="0x5bdeb8" and s["caller_branch_executed"]
assert s["x25_RVA"]=="0x18a2968" and s["x25_plus_4_u32"]==0 and s["status_load_RVA"]=="0x5bdeb8" and s["status_compare_RVA"]=="0x5bdebc"
assert s["conditional_branch_RVA"]=="0x5bdec0" and s["conditional_branch_taken"] and s["conditional_branch_target_RVA"]=="0x5be368" and s["next_camera_source_RVA"]=="0x5be368" and not s["next_camera_source_executed"]
assert s["rejected_altered_contracts"]==8 and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JZ" and not n["current_frontier"]["executed"]
print(json.dumps({"status":"PASS_E011JY_PORTABLE_REVIEW","cases":4,"next":"E011JZ"},sort_keys=True))
