#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_CALLER_RETURN_OBJECT_STORE_TO_C0_READ_FRONTIER" and s["case_count"]==4
assert s["caller_x26_source_RVA"]=="0x5b80d0" and s["caller_x26_is_SP"] and s["caller_resume_RVA"]=="0x5b826c"
assert s["return_x0_RVA"]=="0x17a70d0" and s["returned_object_store_RVA"]=="0x5b8270" and s["returned_object_store_SP_relative"]=="0x70" and s["returned_object_store_executed"]
assert s["next_object_field_read_RVA"]=="0x5b8274" and s["next_object_field_offset"]=="0xc0" and not s["next_object_field_read_executed"] and s["rejected_altered_contracts"]==8
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KC" and not n["current_frontier"]["read_executed"]
print(json.dumps({"status":"PASS_E011KB_PORTABLE_REVIEW","cases":4,"next":"E011KC"},sort_keys=True))
