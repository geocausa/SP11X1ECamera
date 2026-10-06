#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_SRW_RELEASE_TO_CONDITION_WAKE_FRONTIER" and s["case_count"]==4
assert s["release_import_RVA"]=="0xf7e518" and s["release_call_RVA"]=="0xce7ab0" and s["release_call_executed"] and s["release_resource_RVA"]=="0x16a3738"
assert s["srw_lock_held_before"] and not s["srw_lock_held_after"] and s["wake_import_RVA"]=="0xf7e410" and s["wake_call_RVA"]=="0xce7ac0" and s["wake_call_x0_RVA"]=="0x16a3730" and not s["wake_call_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JX" and not n["expected_return"]["caller_branch_executed"]
print(json.dumps({"status":"PASS_E011JW_PORTABLE_REVIEW","cases":4,"next":"E011JX"},sort_keys=True))
