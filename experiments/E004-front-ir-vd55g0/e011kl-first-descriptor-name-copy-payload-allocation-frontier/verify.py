#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_FIRST_DESCRIPTOR_NAME_COPY_TO_PAYLOAD_ALLOCATOR_FRONTIER" and s["case_count"]==4
assert s["copy_call_RVA"]=="0x5b9940" and s["copy_target_RVA"]=="0xcae7c0" and s["copy_bound_u64"]==42 and s["copy_source_RVA"]=="0x13d9678" and s["copy_return_u32"]==0 and s["copied_bytes_including_nul"]==42
assert s["published_name_pointer_store_RVA"]=="0x5b9944" and s["published_name_pointer_nonzero"] and s["source_count_read_RVA"]=="0x5b9948" and s["source_count_u32"]==2 and s["element_bytes"]==24 and s["nested_allocation_bytes"]==48
assert s["allocator_call_RVA"]=="0x5b9968" and s["allocator_target_RVA"]=="0xcae740" and not s["allocator_call_executed"] and s["rejected_altered_contracts"]==12
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KM" and not n["current_frontier"]["allocator_call_executed"]
print(json.dumps({"status":"PASS_E011KL_PORTABLE_REVIEW","cases":4,"next":"E011KM"},sort_keys=True))
