#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_HWENVLOCK_COPY_TO_IMPORT_CALL_FRONTIER" and s["case_count"]==4 and s["source_RVA"]=="0x13dbc80" and s["source_ascii"]=="HwEnvLock" and s["source_first_nul_offset"]==9
assert s["copy_return_w0_u32"]==0 and s["copied_bytes_including_nul"]==10 and s["allocated_pointer_preserved_in_x24"] and s["next_import_read_RVA"]=="0x5be3c0" and s["next_import_call_RVA"]=="0x5be3c8" and not s["next_import_call_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IZ" and f["frontier"]["import_slot_RVA"]=="0xf7e0c8" and f["frontier"]["import_name"]=="InitializeCriticalSection" and not f["frontier"]["call_executed"] and n["accepted_contract_authority"]=="E011DC"
print(json.dumps({"status":"PASS_E011IY_PORTABLE_REVIEW","cases":4,"next":"E011IZ"},sort_keys=True))
