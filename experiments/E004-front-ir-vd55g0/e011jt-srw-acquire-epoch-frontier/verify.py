#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_SRW_ACQUIRE_TO_EPOCH_READ_FRONTIER" and s["case_count"]==4 and s["lock_call_executed"] and s["lock_held_after"]
assert s["lock_resource_RVA"]=="0x16a3738" and s["next_epoch_read_RVA"]=="0xce7a78" and s["next_epoch_cell_RVA"]=="0x1607b04" and s["next_epoch_expected_u32"]=="0x80000042" and not s["next_epoch_read_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JU" and n["expected_effects"]["epoch_after_u32"]=="0x80000043"
print(json.dumps({"status":"PASS_E011JT_PORTABLE_REVIEW","cases":4,"next":"E011JU"},sort_keys=True))
