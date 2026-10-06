#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_1480_ALLOCATOR_RETURN_TO_X24_BRANCH_FRONTIER" and s["case_count"]==4
assert s["allocator_thunk_call_RVA"]=="0x5b82c8" and s["allocator_thunk_RVA"]=="0xcae740" and s["underlying_allocator_RVA"]=="0xcb16c0" and s["allocation_bytes"]==0x1480
assert s["owned_process_heap_handle_read_qualified"] and s["owned_HeapAlloc_contract_executed"] and s["allocator_return_qualified"] and s["returned_pointer_nonzero"]
assert s["x23_preserved_u64"]=="0x1480" and s["result_moved_to_x24_RVA"]=="0x5b82cc" and s["x24_result_nonzero"] and s["result_branch_RVA"]=="0x5b82d0" and not s["result_branch_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KG" and not n["current_frontier"]["result_branch_executed"]
print(json.dumps({"status":"PASS_E011KF_PORTABLE_REVIEW","cases":4,"next":"E011KG"},sort_keys=True))
