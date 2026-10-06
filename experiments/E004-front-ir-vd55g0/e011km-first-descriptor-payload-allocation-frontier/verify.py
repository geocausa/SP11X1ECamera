#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_FIRST_DESCRIPTOR_PAYLOAD_ALLOCATOR_RETURN_FRONTIER" and s["case_count"]==4
assert s["allocator_call_RVA"]=="0x5b9968" and s["allocator_thunk_RVA"]=="0xcae740" and s["underlying_allocator_RVA"]=="0xcb16c0" and s["allocation_bytes"]==48
assert s["owned_process_heap_handle_read_qualified"] and s["owned_HeapAlloc_contract_executed"] and s["allocator_return_qualified"] and s["returned_pointer_nonzero"] and s["x21_result_nonzero"] and s["x22_size_preserved_u64"]==48
assert s["descriptor_source_preserved"] and s["descriptor_destination_preserved"] and s["result_branch_RVA"]=="0x5b9970" and not s["result_branch_executed"] and s["rejected_altered_contracts"]==8
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KN" and not n["current_frontier"]["branch_executed"]
print(json.dumps({"status":"PASS_E011KM_PORTABLE_REVIEW","cases":4,"next":"E011KN"},sort_keys=True))
