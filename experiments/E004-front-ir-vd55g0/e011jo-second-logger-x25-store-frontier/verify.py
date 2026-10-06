#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_SECOND_OWNED_LOGGER_TO_X25_STORE_FRONTIER" and s["case_count"]==4 and s["accepted_diagnostic_no_effect_dependency_model"]
assert s["logger_call_RVA"]=="0x5beda0" and s["logger_resume_RVA"]=="0x5beda4" and s["logger_call_executed"]
assert s["next_instruction_RVA"]=="0x5beda4" and s["next_instruction"]=="str wzr, [x25]" and not s["next_instruction_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JP" and not f["next_frontier"]["executed"] and n["current_frontier"]["RVA"]=="0x5beda4"
print(json.dumps({"status":"PASS_E011JO_PORTABLE_REVIEW","cases":4,"next":"E011JP"},sort_keys=True))
