#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_ZERO_EXISTING_COUNT_TO_FIRST_DESCRIPTOR_COPY_FRONTIER" and s["case_count"]==4
assert s["caller_x19_RVA"]=="0x17a4230" and s["caller_x19_plus_0x20_u32"]==0 and s["zero_existing_count_branch_taken"]
assert s["descriptor_count_u32"]==164 and s["descriptor_pointer_RVA"]=="0x1624140" and s["entry_bytes"]==32
assert s["first_copy_destination_is_x24"] and s["first_copy_source_RVA"]=="0x1624140" and s["copy_call_RVA"]=="0x5b8344" and s["copy_target_RVA"]=="0x5b9888" and not s["copy_call_executed"]
assert s["rejected_altered_contracts"]==12 and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KI" and not n["current_frontier"]["copy_call_executed"]
print(json.dumps({"status":"PASS_E011KH_PORTABLE_REVIEW","cases":4,"next":"E011KI"},sort_keys=True))
