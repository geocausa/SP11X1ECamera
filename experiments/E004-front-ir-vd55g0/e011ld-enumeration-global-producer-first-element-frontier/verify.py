#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_ENUMERATION_GLOBAL_PRODUCER_TO_FIRST_ELEMENT_CALL_FRONTIER" and s["case_count"]==4
assert s["enumeration_global_pair_RVA"]=="0x1766540" and s["producer_RVA"]=="0x5beba8" and s["producer_allocation_bytes"]==16
assert s["producer_source_pair_RVA"]=="0x1618498" and s["producer_source_table_RVA"]=="0x1617b40" and s["producer_source_count_u32"]==62 and s["all_62_source_descriptor_preconditions_valid"]
assert s["producer_global_pointer_nonzero_owned"] and s["producer_global_count_u32"]==1 and s["method_output_count_u32"]==1 and s["status_zero_branch_taken"] and s["count_u32"]==1 and not s["count_zero_branch_taken"]
assert s["first_element_call_RVA"]=="0x5b8778" and s["first_element_call_target_RVA"]=="0x5b9c80" and s["first_element_call_x0_object_RVA"]=="0x17a4230" and s["first_element_call_x1_owned_entry"] and not s["first_element_call_executed"]
assert s["rejected_altered_contracts"]==16 and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011LE" and n["expected_closure"]["replacement_count_u32"]==231 and n["expected_closure"]["replacement_bytes"]==7392
print(json.dumps({"status":"PASS_E011LD_PORTABLE_REVIEW","cases":4,"next":"E011LE"},sort_keys=True))
