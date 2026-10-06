#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_NONZERO_1480_CLEAR_TO_5B82E0_FRONTIER" and s["case_count"]==4
assert s["result_branch_RVA"]=="0x5b82d0" and s["result_nonzero_branch_taken"] and s["clear_call_RVA"]=="0x5b82dc" and s["clear_target_RVA"]=="0xf5e600" and s["clear_bytes"]==0x1480 and s["clear_executed"] and s["clear_exact"] and s["allocation_redzones_retained"]
assert s["resume_RVA"]=="0x5b82e0" and not s["resume_executed"] and s["next_x19_field_expected_u32"]==0 and s["rejected_altered_contracts"]==8
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KH" and not n["current_frontier"]["read_executed"]
print(json.dumps({"status":"PASS_E011KG_PORTABLE_REVIEW","cases":4,"next":"E011KH"},sort_keys=True))
