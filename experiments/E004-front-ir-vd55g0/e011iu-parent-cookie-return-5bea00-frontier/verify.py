#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_PARENT_COOKIE_EPILOGUE_RETURN_TO_5BEA00_FRONTIER" and s["case_count"]==4 and s["cookie_contract"]=="opaque_process_cookie_value" and not s["cookie_failure_path_executed"]
assert s["parent_function_RVA"]=="0x5f8dc0" and s["parent_callsite_RVA"]=="0x5be9fc" and s["epilogue_return_RVA"]=="0x5f9458" and s["architectural_return_RVA"]=="0x5bea00" and s["return_object_preserved_in_x0"] and s["saved_frame_restored"] and s["entry_SP_restored"]
assert s["next_camera_source_RVA"]=="0x5bea00" and not s["next_camera_source_executed"] and s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IV" and f["frontier"]["source_RVA"]=="0x5bea00" and not f["frontier"]["executed"] and n["expected_frontier"]["target_RVA"]=="0xcae740"
print(json.dumps({"status":"PASS_E011IU_PORTABLE_REVIEW","cases":4,"next":"E011IV"},sort_keys=True))
