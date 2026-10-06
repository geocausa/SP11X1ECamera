#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_READY_DESCRIPTOR_AGGREGATE_TO_5E81B8_CALL_FRONTIER" and s["case_count"]==4 and s["descriptor_count_u32"]==231 and s["ready_value_u32"]==1
assert s["tail_ff_descriptor_count_u32"]==147 and s["tail_ff_nested_count_u32"]==350 and s["input_SP_relative"]=="0x80" and s["input_bytes"]==24 and s["input_aggregate_u32"]==350
assert s["input_tag_u64"]=="0x8000000000" and s["input_stride_u64"]==4 and s["input_tail_u32"]==0 and s["call_RVA"]=="0x5b8bc4" and s["call_target_RVA"]=="0x5e81b8" and not s["call_executed"]
assert s["rejected_altered_contracts"]==16 and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011LH" and n["expected_closure"]["entry_array_bytes"]==2800 and n["expected_closure"]["stop_RVA"]=="0x5b8bcc"
print(json.dumps({"status":"PASS_E011LG_PORTABLE_REVIEW","cases":4,"next":"E011LH"},sort_keys=True))
