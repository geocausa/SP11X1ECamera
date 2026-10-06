#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_D0_METHOD_CFG_TO_ENUMERATION_GLOBAL_PAIR_FRONTIER" and s["case_count"]==4
assert s["factory_object_RVA"]=="0x17a70d0" and s["caller_factory_object_SP_relative"]=="0x70" and s["method_field_offset"]=="0xd0" and s["method_target_RVA"]=="0x5ba850"
assert s["guard_cf_check_cell_RVA"]=="0xf7e7b8" and s["guard_cf_check_target_RVA"]=="0x1a8c0" and s["guard_check_executed"] and s["method_call_executed"] and s["method_return_u32"]==0
assert s["output_pair_SP_relative"]=="0x50" and s["output_count_SP_relative"]=="0x58" and s["enumeration_global_pair_RVA"]=="0x1766540" and s["output_pair_mirrors_global"]
assert not s["enumeration_global_pair_concrete_values_qualified"] and not s["enumeration_global_pair_values_exported"] and s["status_w23_u32"]==0 and s["status_branch_RVA"]=="0x5b875c" and not s["status_branch_executed"]
assert s["rejected_altered_contracts"]==12 and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011LD" and n["expected_next_call"]["call_RVA"]=="0x5b8778" and not n["current_frontier"]["executed"]
print(json.dumps({"status":"PASS_E011LC_PORTABLE_REVIEW","cases":4,"next":"E011LD"},sort_keys=True))
