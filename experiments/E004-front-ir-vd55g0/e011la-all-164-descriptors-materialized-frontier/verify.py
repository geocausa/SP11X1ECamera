#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_ALL_164_NATIVE_DESCRIPTORS_MATERIALIZED_TO_5B84B8_FRONTIER" and s["case_count"]==4
assert s["descriptor_count_u32"]==164 and s["descriptor_entry_bytes"]==32 and s["destination_bytes"]==0x1480 and s["nested_element_count"]==439 and s["maximum_nested_count_u32"]==37
assert s["descriptor_copy_calls"]==164 and s["owned_heap_allocations"]==767 and s["exact_clear_calls"]==767 and s["bounded_string_copy_calls"]==603
assert s["all_top_level_names_exact"] and s["all_nested_payload_elements_exact"] and s["all_nested_strings_exact"] and s["old_zero_table_cleanup_executed"]
assert s["published_count_u32"]==164 and s["published_table_nonzero"] and s["stop_RVA"]=="0x5b84b8" and not s["stop_executed"] and s["rejected_altered_contracts"]==16
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011LB" and n["expected_closure"]["replacement_count_u32"]==169 and n["expected_closure"]["replacement_bytes"]==0x1520 and not n["current_frontier"]["executed"]
print(json.dumps({"status":"PASS_E011LA_PORTABLE_REVIEW","cases":4,"next":"E011LB"},sort_keys=True))
