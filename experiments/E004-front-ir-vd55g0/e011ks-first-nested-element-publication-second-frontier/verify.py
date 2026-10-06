#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_FIRST_NESTED_ELEMENT_PUBLICATION_TO_SECOND_ELEMENT_FRONTIER" and s["case_count"]==4
assert s["published_pointer_store_RVA"]=="0x5b9a10" and s["destination_payload_count_u32"]==1 and s["published_source_byte_u8"]==1 and s["published_source_qword_u64"]==1
assert s["next_w21_u32"]==1 and s["next_element_offset_u64"]==24 and s["source_pointer_array_RVA"]=="0x16170d8" and s["second_source_element_read_RVA"]=="0x5b9998" and not s["second_source_element_read_executed"]
assert s["rejected_altered_contracts"]==12 and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KT" and not n["current_frontier"]["read_executed"]
print(json.dumps({"status":"PASS_E011KS_PORTABLE_REVIEW","cases":4,"next":"E011KT"},sort_keys=True))
