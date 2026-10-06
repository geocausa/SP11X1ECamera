#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_HWENVLOCK_CRITSEC_TO_PUBLICATION_FRONTIER" and s["case_count"]==4 and s["import_slot_RVA"]=="0xf7e0c8" and s["import_name"]=="InitializeCriticalSection"
assert s["typed_owned_logical_ownership_model_only"] and not s["native_critical_section_bytes_or_concurrency_qualified"] and s["InitializeCriticalSection_call_executed"] and s["critical_section_receiver_alloc_plus"]=="0x8"
assert s["resume_RVA"]=="0x5be3cc" and not s["publication_executed"] and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JA" and f["frontier"]["resume_RVA"]=="0x5be3cc" and not f["frontier"]["publication_executed"] and n["source_owner"]["x22_RVA"]=="0x1b30170"
print(json.dumps({"status":"PASS_E011IZ_PORTABLE_REVIEW","cases":4,"next":"E011JA"},sort_keys=True))
