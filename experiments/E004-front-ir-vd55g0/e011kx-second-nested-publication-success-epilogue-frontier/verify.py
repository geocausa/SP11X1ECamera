#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_SECOND_NESTED_ELEMENT_PUBLICATION_TO_HELPER_SUCCESS_EPILOGUE_FRONTIER" and s["case_count"]==4
assert s["destination_payload_count_u32"]==2 and s["published_second_source_byte_u8"]==1 and s["published_second_source_qword_u64"]==7 and s["completed_w21_u32"]==2 and s["source_count_u32"]==2
assert s["loop_back_branch_RVA"]=="0x5b9aa4" and not s["loop_back_branch_taken"] and s["success_branch_RVA"]=="0x5b9aa8" and s["success_branch_taken"] and s["success_w23_u32"]==0 and s["success_epilogue_RVA"]=="0x5b9b80" and not s["epilogue_executed"]
assert s["rejected_altered_contracts"]==12 and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KY" and not n["current_frontier"]["epilogue_executed"]
print(json.dumps({"status":"PASS_E011KX_PORTABLE_REVIEW","cases":4,"next":"E011KY"},sort_keys=True))
