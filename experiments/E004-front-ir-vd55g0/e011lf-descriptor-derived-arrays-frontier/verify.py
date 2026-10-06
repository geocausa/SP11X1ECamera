#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_231_DESCRIPTOR_DERIVED_INDEX_ARRAYS_TO_5B8B68_FRONTIER" and s["case_count"]==4
assert s["replacement_count_u32"]==231 and s["preassigned_descriptor_count_u32"]==1 and s["prefix_array_bytes"]==924 and s["nested_element_count_u32"]==519 and s["scalar_array_bytes"]==4152
assert s["next_descriptor_id_u32"]==0x80e7 and s["ready_field_offset"]=="0x2c" and s["ready_value_u32"]==1 and s["all_derived_arrays_exact"] and s["all_231_outputs_exact"]
assert s["owned_heap_allocations"]==984 and s["exact_clear_calls"]==984 and s["bounded_string_copy_calls"]==750 and s["stop_RVA"]=="0x5b8b68" and not s["stop_executed"]
assert s["rejected_altered_contracts"]==16 and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011LG" and n["expected_call"]["tail_ff_nested_count_u32"]==350 and n["expected_call"]["target_RVA"]=="0x5e81b8"
print(json.dumps({"status":"PASS_E011LF_PORTABLE_REVIEW","cases":4,"next":"E011LG"},sort_keys=True))
