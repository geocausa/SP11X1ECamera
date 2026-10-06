#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_NATIVE_C0_FUNCTION_DESCRIPTOR_TO_5B8290_FRONTIER" and s["case_count"]==4
assert s["function_call_RVA"]=="0x5b828c" and s["function_target_RVA"]=="0x5ba820" and s["function_call_executed"] and s["function_nonnull_branch_taken"]
assert s["descriptor_output_SP_relative"]=="0x60" and s["descriptor_pointer_RVA"]=="0x1624140" and s["descriptor_size_u32"]==0xa4 and s["function_return_u32"]==0
assert s["resume_RVA"]=="0x5b8290" and not s["resume_executed"] and s["rejected_altered_contracts"]==8
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KE" and not n["expected_next_frontier"]["read_executed"]
print(json.dumps({"status":"PASS_E011KD_PORTABLE_REVIEW","cases":4,"next":"E011KE"},sort_keys=True))
