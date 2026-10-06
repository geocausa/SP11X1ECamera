#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_RETURN_OBJECT_TO_B0_ALLOCATOR_CALL_FRONTIER" and s["case_count"]==4 and s["caller_resume_RVA"]=="0x5bea00" and s["returned_object_preserved_in_x20"]
assert s["allocation_bytes"]==176 and s["allocator_thunk_call_RVA"]=="0x5bea08" and s["allocator_thunk_RVA"]=="0xcae740" and s["underlying_allocator_RVA"]=="0xcb16c0" and not s["allocator_call_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IW" and f["allocator_frontier"]["call_RVA"]=="0x5bea08" and not f["allocator_frontier"]["call_executed"] and n["accepted_allocator_authority"]["authority_experiment"]=="E011ES"
print(json.dumps({"status":"PASS_E011IV_PORTABLE_REVIEW","cases":4,"next":"E011IW"},sort_keys=True))
