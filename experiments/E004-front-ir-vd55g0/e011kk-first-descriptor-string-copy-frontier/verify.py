#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_FIRST_DESCRIPTOR_STRING_CLEAR_TO_BOUNDED_COPY_FRONTIER" and s["case_count"]==4
assert s["result_branch_RVA"]=="0x5b9910" and s["result_nonzero_branch_taken"] and s["clear_call_RVA"]=="0x5b991c" and s["clear_target_RVA"]=="0xf5e600" and s["clear_bytes"]==42 and s["clear_executed"] and s["clear_exact"] and s["allocation_redzones_retained"]
assert s["source_entry_RVA"]=="0x1624140" and s["source_name_RVA"]=="0x13d9678" and s["source_name_length_u64"]==41 and s["source_name_span_bytes"]==42
assert s["copy_call_RVA"]=="0x5b9940" and s["copy_target_RVA"]=="0xcae7c0" and s["copy_x1_u64"]==42 and s["copy_x2_RVA"]=="0x13d9678" and s["copy_x3_u64"]=="U64_MAX" and not s["copy_call_executed"]
assert s["rejected_altered_contracts"]==12 and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KL" and not n["current_frontier"]["copy_call_executed"]
print(json.dumps({"status":"PASS_E011KK_PORTABLE_REVIEW","cases":4,"next":"E011KL"},sort_keys=True))
