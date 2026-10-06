#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_NATIVE_FUNCTION_BLOCK_C0_CFG_CHECK_TO_CALL_FRONTIER" and s["case_count"]==4
assert s["function_block_base_RVA"]=="0x17a70d0" and s["field_offsets"]==["0xa0","0xa8","0xb0","0xb8","0xc0","0xc8","0xd0"]
assert s["native_function_target_RVAs"]==["0x5ba750","0x5ba6b0","0x5ba880","0x5fdb90","0x5ba820","0x5bcc00","0x5ba850"] and s["native_function_vector_stable_across_successful_front_reader_start"] and s["cold_zero_model_distinct_from_native_front_context"]
assert s["object_field_read_RVA"]=="0x5b8274" and s["object_field_offset"]=="0xc0" and s["object_field_target_RVA"]=="0x5ba820" and s["object_field_read_executed"]
assert s["guard_cf_check_cell_RVA"]=="0xf7e7b8" and s["guard_cf_check_target_RVA"]=="0x1a8c0" and s["guard_cf_check_call_RVA"]=="0x5b8288" and s["guard_cf_check_call_executed"]
assert s["next_function_call_RVA"]=="0x5b828c" and s["next_function_target_RVA"]=="0x5ba820" and not s["next_function_call_executed"]
assert s["new_front_camera_starts"]==1 and s["new_rear_camera_starts"]==0 and s["new_reboots"]==1 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KD" and n["expected_effects"]["function_return_u32"]==0 and not n["expected_effects"]["resume_executed"]
print(json.dumps({"status":"PASS_E011KC_PORTABLE_REVIEW","cases":4,"next":"E011KD"},sort_keys=True))
