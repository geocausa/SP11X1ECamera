#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_B0_ZERO_INIT_TO_CAE7C0_CONSTRUCTION_FRONTIER" and s["case_count"]==4 and s["nonzero_allocation_branch_taken"] and s["allocation_bytes"]==s["zeroed_bytes"]==176
assert s["source_zero_store_instructions"]==6 and s["allocated_pointer_preserved_in_x24"] and s["construction_call_RVA"]=="0x5be3b8" and s["construction_target_RVA"]=="0xcae7c0" and not s["construction_call_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IY" and f["frontier"]["target_RVA"]=="0xcae7c0" and not f["frontier"]["call_executed"] and n["expected_source"]["ascii"]=="HwEnvLock"
print(json.dumps({"status":"PASS_E011IX_PORTABLE_REVIEW","cases":4,"next":"E011IY"},sort_keys=True))
