#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_EXISTING_TABLE_THIRD_REGISTRATION_TO_CE7A48_FRONTIER" and s["case_count"]==4
assert s["callback_RVA"]=="0xf7b310" and s["existing_table_used_entries_before"]==2 and s["existing_table_used_entries_after"]==3 and s["existing_table_capacity_entries"]==32 and s["registration_used_existing_capacity_without_allocator"]
assert s["wrapper_return_w0_u32"]==0 and s["next_call_RVA"]=="0x5be670" and s["next_call_target_RVA"]=="0xce7a48" and s["next_call_x0_RVA"]=="0x1b302d0" and not s["next_call_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JS" and not f["next_frontier"]["call_executed"] and n["accepted_publication_authority"]["authority_experiment"]=="E011DU"
print(json.dumps({"status":"PASS_E011JR_PORTABLE_REVIEW","cases":4,"next":"E011JS"},sort_keys=True))
