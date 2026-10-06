#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_POST_DESCRIPTOR_SIZE_TO_ALLOCATOR_FRONTIER" and s["case_count"]==4
assert s["function_return_u32"]==0 and s["descriptor_size_u32"]==0xa4 and not s["return_one_branch_taken"] and not s["zero_size_branch_taken"]
assert s["caller_x19_RVA"]=="0x17a4230" and s["caller_x19_plus_0x20_u32"]==0 and s["allocation_size_u64"]=="0x1480"
assert s["allocator_call_RVA"]=="0x5b82c8" and s["allocator_target_RVA"]=="0xcae740" and not s["allocator_call_executed"] and s["rejected_altered_contracts"]==16
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KF" and not n["expected_next_frontier"]["result_branch_executed"]
print(json.dumps({"status":"PASS_E011KE_PORTABLE_REVIEW","cases":4,"next":"E011KF"},sort_keys=True))
