#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_RETURNED_OBJECT_BUFFER_POINTER_TO_FIELD20_FRONTIER" and s["case_count"]==4 and s["returned_object_RVA"]=="0x169fde0" and s["pointer_slot_RVA"]=="0x169fdf0"
assert s["published_buffer_pointer_nonzero"] and s["published_buffer_bytes"]==18832 and s["pointer_read_executed"] and s["next_camera_source_RVA"]=="0x5be3dc" and not s["next_dependency_read_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JC" and f["frontier"]["source_RVA"]=="0x5be3dc" and not f["frontier"]["dependency_read_executed"] and n["expected_fields_after"]["plus_0x20_u32"]=="0x08000000"
print(json.dumps({"status":"PASS_E011JB_PORTABLE_REVIEW","cases":4,"next":"E011JC"},sort_keys=True))
