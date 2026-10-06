#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_BRANCH_REPEAT_SEARCH_TO_SECOND_LOGGER_FRONTIER" and s["case_count"]==4 and s["branch_executed"]
assert s["search_call_RVA"]=="0x5bed74" and s["search_target_RVA"]=="0xce7c98" and s["search_return_source_offset"]==74
assert s["logger_call_RVA"]=="0x5beda0" and s["logger_target_RVA"]=="0x1aca8" and not s["logger_call_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JO" and not f["logger_frontier"]["call_executed"] and n["expected_frontier"]["resume_RVA"]=="0x5beda4"
print(json.dumps({"status":"PASS_E011JN_PORTABLE_REVIEW","cases":4,"next":"E011JO"},sort_keys=True))
