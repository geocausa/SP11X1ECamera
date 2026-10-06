#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_164_PLUS_5_NATIVE_DESCRIPTORS_REPUBLISHED_TO_5B8738_FRONTIER" and s["case_count"]==4
assert s["old_descriptor_count_u32"]==164 and s["extra_descriptor_count_u32"]==5 and s["replacement_count_u32"]==169 and s["replacement_bytes"]==0x1520
assert s["descriptor_copy_calls"]==169 and s["owned_heap_allocations"]==790 and s["exact_clear_calls"]==790 and s["bounded_string_copy_calls"]==620 and s["superseded_owned_frees"]==768
assert s["all_164_inherited_descriptors_exact"] and s["all_5_extra_descriptors_source_exact"] and s["all_169_outputs_exact"] and s["published_count_u32"]==169
assert s["stop_RVA"]=="0x5b8738" and not s["stop_executed"] and s["rejected_altered_contracts"]==16
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011LC" and n["stop_RVA"]=="0x5b875c" and not n["current_frontier"]["executed"]
print(json.dumps({"status":"PASS_E011LB_PORTABLE_REVIEW","cases":4,"next":"E011LC"},sort_keys=True))
