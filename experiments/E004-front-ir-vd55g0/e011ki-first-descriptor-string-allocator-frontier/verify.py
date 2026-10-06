#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_FIRST_DESCRIPTOR_PREFIX_TO_STRING_ALLOCATOR_FRONTIER" and s["case_count"]==4
assert s["copy_call_RVA"]=="0x5b8344" and s["copy_target_RVA"]=="0x5b9888" and s["copy_call_executed"]
assert s["source_entry_RVA"]=="0x1624140" and s["entry_bytes"]==32 and s["name_pointer_RVA"]=="0x13d9678" and s["name_length_u64"]==41
assert s["source_plus_0x8_u32"]==0 and s["source_plus_0xc_u32"]==2 and s["source_plus_0x18_u32"]==0xffffffff
assert s["nested_allocation_bytes"]==42 and s["nested_allocator_call_RVA"]=="0x5b9908" and not s["nested_allocator_call_executed"]
assert s["rejected_altered_contracts"]==12 and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KJ" and not n["current_frontier"]["allocator_call_executed"]
print(json.dumps({"status":"PASS_E011KI_PORTABLE_REVIEW","cases":4,"next":"E011KJ"},sort_keys=True))
