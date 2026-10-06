#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_FIRST_DESCRIPTOR_PAYLOAD_CLEAR_TO_FIRST_NESTED_STRING_FRONTIER" and s["case_count"]==4
assert s["result_branch_RVA"]=="0x5b9970" and s["result_nonzero_branch_taken"] and s["clear_call_RVA"]=="0x5b997c" and s["clear_target_RVA"]=="0xf5e600" and s["clear_bytes"]==48 and s["clear_executed"] and s["clear_exact"]
assert s["published_payload_pointer_store_RVA"]=="0x5b9980" and s["published_payload_pointer_nonzero"] and s["source_count_u32"]==2 and s["source_pointer_array_RVA"]=="0x16170d8" and s["source_pointer_array_bytes"]==48
assert s["first_element_offset_u64"]==0 and s["first_string_pointer_load_RVA"]=="0x5b9998" and s["first_string_RVA"]=="0x1362948" and s["first_string_span_bytes"]==23 and s["first_string_read_RVA"]=="0x5b999c" and not s["first_string_read_executed"]
assert s["rejected_altered_contracts"]==8 and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KO" and not n["current_frontier"]["first_string_read_executed"]
print(json.dumps({"status":"PASS_E011KN_PORTABLE_REVIEW","cases":4,"next":"E011KO"},sort_keys=True))
