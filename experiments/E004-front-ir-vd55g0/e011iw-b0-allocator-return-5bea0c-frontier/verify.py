#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_B0_ALLOCATOR_RETURN_TO_5BEA0C_FRONTIER" and s["case_count"]==4 and s["allocation_bytes"]==176
assert s["owned_process_heap_handle_read_qualified"] and s["owned_HeapAlloc_contract_executed"] and s["allocator_return_qualified"] and s["returned_pointer_nonzero"] and s["returned_object_preserved_in_x20"]
assert s["resume_RVA"]=="0x5bea0c" and not s["resume_branch_executed"] and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IX" and f["frontier"]["source_RVA"]=="0x5bea0c" and not f["frontier"]["branch_executed"] and n["expected_frontier"]["target_RVA"]=="0xcae7c0"
print(json.dumps({"status":"PASS_E011IW_PORTABLE_REVIEW","cases":4,"next":"E011IX"},sort_keys=True))
