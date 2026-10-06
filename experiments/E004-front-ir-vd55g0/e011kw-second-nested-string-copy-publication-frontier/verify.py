#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_SECOND_NESTED_STRING_COPY_TO_PUBLICATION_FRONTIER" and s["case_count"]==4
assert s["copy_call_RVA"]=="0x5b9a08" and s["copy_target_RVA"]=="0xcae7c0" and s["copy_source_RVA"]=="0x1362938" and s["copy_bound_u64"]==16 and s["copied_bytes_including_nul"]==16 and s["copy_return_u32"]==0 and s["destination_x25_preserved"]
assert s["resume_RVA"]=="0x5b9a0c" and s["publication_store_RVA"]=="0x5b9a10" and not s["publication_executed"] and s["rejected_altered_contracts"]==12
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KX" and not n["current_frontier"]["publication_executed"]
print(json.dumps({"status":"PASS_E011KW_PORTABLE_REVIEW","cases":4,"next":"E011KX"},sort_keys=True))
