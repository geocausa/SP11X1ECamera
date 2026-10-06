#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_HWENVLOCK_PUBLICATION_TO_RETURNED_OBJECT_FRONTIER" and s["case_count"]==4 and s["source_owner_RVA"]=="0x1b30170" and s["publication_target_RVA"]=="0x1b30288" and s["publication_executed"] and s["publication_pointer_nonzero"]
assert s["returned_object_x20_nonzero"] and not s["x20_zero_branch_taken"] and s["next_camera_source_RVA"]=="0x5be3d8" and s["next_dependency_expression"]=="[x20+0x10]" and not s["next_dependency_read_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JB" and f["frontier"]["source_RVA"]=="0x5be3d8" and not f["frontier"]["dependency_read_executed"]
print(json.dumps({"status":"PASS_E011JA_PORTABLE_REVIEW","cases":4,"next":"E011JB"},sort_keys=True))
