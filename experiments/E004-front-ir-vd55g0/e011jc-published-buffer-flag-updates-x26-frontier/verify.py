#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_PUBLISHED_BUFFER_FLAG_UPDATES_TO_X26_FRONTIER" and s["case_count"]==4 and s["published_buffer_bytes"]==18832 and s["qualified_zero_offsets_before"]==["0x0c","0x14","0x20"]
assert s["buffer_plus_0x20_after_u32"]==0x08000000 and s["buffer_plus_0x14_after_u32"]==0 and s["buffer_plus_0x0c_after_u32"]==0 and s["published_buffer_reloaded_nonzero"] and not s["x20_zero_branch_taken"]
assert s["next_camera_source_RVA"]=="0x5be424" and s["next_dependency_expression"]=="[x26+0x6c]" and not s["next_dependency_read_executed"] and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JD" and f["frontier"]["source_RVA"]=="0x5be424" and not f["frontier"]["dependency_read_executed"]
print(json.dumps({"status":"PASS_E011JC_PORTABLE_REVIEW","cases":4,"next":"E011JD"},sort_keys=True))
