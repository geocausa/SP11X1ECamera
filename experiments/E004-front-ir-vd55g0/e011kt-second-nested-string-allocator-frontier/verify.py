#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_SECOND_NESTED_STRING_SCAN_TO_ALLOCATOR_FRONTIER" and s["case_count"]==4
assert s["second_element_offset_u64"]==24 and s["source_pointer_array_RVA"]=="0x16170d8" and s["string_RVA"]=="0x1362938" and s["string_length_u64"]==15 and s["string_span_bytes"]==16 and s["allocation_bytes"]==16
assert s["allocator_call_RVA"]=="0x5b99cc" and s["allocator_target_RVA"]=="0xcae740" and not s["allocator_call_executed"] and s["rejected_altered_contracts"]==12
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KU" and not n["current_frontier"]["allocator_call_executed"]
print(json.dumps({"status":"PASS_E011KT_PORTABLE_REVIEW","cases":4,"next":"E011KU"},sort_keys=True))
