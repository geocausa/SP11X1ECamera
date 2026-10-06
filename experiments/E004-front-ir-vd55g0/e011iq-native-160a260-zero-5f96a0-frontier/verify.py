#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_NATIVE_160A260_ZERO_TO_5F96A0_FRONTIER" and s["case_count"]==4
assert s["native_dependency_RVA"]=="0x160a260" and s["native_value_before_reader_start_u64"]==0 and s["native_value_after_successful_reader_start_u64"]==0 and s["data_section_writable"]
assert s["zero_branch_RVA"]=="0x5f9690" and s["zero_branch_taken"] and s["zero_branch_target_RVA"]=="0x5f96a0" and s["next_camera_source_RVA"]=="0x5f96a0" and not s["next_camera_source_executed"]
assert s["new_front_camera_starts"]==1 and s["new_rear_camera_starts"]==0 and s["new_reboots"]==1 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IR" and f["frontier"]["source_RVA"]=="0x5f96a0" and not f["frontier"]["executed"] and n["current_frontier"]["RVA"]=="0x5f96a0"
print(json.dumps({"status":"PASS_E011IQ_PORTABLE_REVIEW","cases":4,"next":"E011IR"},sort_keys=True))
