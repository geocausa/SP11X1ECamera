#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_PARENT_STATUS1_TO_5F9438_COOKIE_CALL_FRONTIER" and s["case_count"]==4 and s["status_store_RVA"]=="0x5f9428" and s["status_target_RVA"]=="0x1731598" and s["status_u32"]==1
assert s["return_x0_matches_x21"] and s["stack_restore_instruction_RVA"]=="0x5f9434" and s["stack_restore_bytes"]==0x1720 and s["next_camera_source_RVA"]=="0x5f9438" and s["next_call_target_RVA"]=="0x11f0" and not s["next_call_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IU" and not f["frontier"]["executed"] and n["expected_frontier"]["architectural_return_RVA"]=="0x5bea00"
print(json.dumps({"status":"PASS_E011IT_PORTABLE_REVIEW","cases":4,"next":"E011IU"},sort_keys=True))
