#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_FACTORY_EPILOGUE_RETURN_OBJECT_TO_5B826C_FRONTIER" and s["case_count"]==4
assert s["factory_entry_RVA"]=="0x5bde08" and s["factory_return_RVA"]=="0x5be390" and s["factory_return_executed"]
assert s["caller_call_RVA"]=="0x5b8268" and s["caller_resume_RVA"]=="0x5b826c" and not s["caller_resume_executed"] and s["return_x0_RVA"]=="0x17a70d0"
assert s["restored_nonvolatile_registers"] and s["restored_SP_bytes"]=="0x60" and s["rejected_altered_contracts"]==12
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and s["returned_to_Golden_Linux"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KB" and not n["current_frontier"]["executed"]
print(json.dumps({"status":"PASS_E011KA_PORTABLE_REVIEW","cases":4,"next":"E011KB"},sort_keys=True))
