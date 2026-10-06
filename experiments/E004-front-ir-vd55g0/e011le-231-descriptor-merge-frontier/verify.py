#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_169_PLUS_62_NATIVE_DESCRIPTORS_MERGED_TO_5B87F8_FRONTIER" and s["case_count"]==4
assert s["old_descriptor_count_u32"]==169 and s["source_descriptor_count_u32"]==62 and s["source_nested_element_count"]==68 and s["replacement_count_u32"]==231 and s["replacement_bytes"]==7392
assert s["descriptor_copy_calls"]==231 and s["owned_heap_allocations"]==982 and s["exact_clear_calls"]==982 and s["bounded_string_copy_calls"]==750 and s["superseded_owned_frees"]==790
assert s["all_169_inherited_descriptors_exact"] and s["all_62_source_descriptors_exact"] and s["all_231_outputs_exact"] and s["published_count_u32"]==231
assert s["enumeration_global_pointer_freed"] and s["enumeration_global_count_after_u32"]==0 and s["caller_output_pointer_after_u64"]==0 and s["stop_RVA"]=="0x5b87f8" and not s["stop_executed"]
assert s["rejected_altered_contracts"]==16 and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011LF" and n["expected_closure"]["nested_element_count_u32"]==519 and n["expected_closure"]["stop_RVA"]=="0x5b8b68"
print(json.dumps({"status":"PASS_E011LE_PORTABLE_REVIEW","cases":4,"next":"E011LF"},sort_keys=True))
