#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_CA34A0_WRAPPER_TO_CA3450_FRONTIER" and s["case_count"]==4 and s["callback_RVA"]=="0xf7b310"
assert s["caller_call_RVA"]=="0x5be660" and s["wrapper_RVA"]=="0xca34a0" and s["wrapper_entered"] and s["wrapper_SP_delta"]==-16
assert s["next_call_RVA"]=="0xca34ac" and s["next_call_target_RVA"]=="0xca3450" and s["next_call_x0_RVA"]=="0xf7b310" and not s["next_call_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JR" and not f["next_frontier"]["call_executed"] and n["accepted_registration_authority"]["authority_experiment"]=="E011DU"
print(json.dumps({"status":"PASS_E011JQ_PORTABLE_REVIEW","cases":4,"next":"E011JR"},sort_keys=True))
