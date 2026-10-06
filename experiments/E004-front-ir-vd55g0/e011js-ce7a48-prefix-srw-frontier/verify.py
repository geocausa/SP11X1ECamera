#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_CE7A48_PREFIX_TO_SRW_ACQUIRE_FRONTIER" and s["case_count"]==4 and s["publication_helper_entered"]
assert s["lock_dependency_name"]=="AcquireSRWLockExclusive" and s["lock_call_RVA"]=="0xce7a70" and s["lock_resource_RVA"]=="0x16a3738" and not s["lock_call_executed"]
assert s["next_epoch_read_RVA"]=="0xce7a78" and s["next_epoch_cell_RVA"]=="0x1607b04" and not s["next_epoch_read_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JT" and n["expected_epoch_authority"]["epoch_u32"]=="0x80000042"
print(json.dumps({"status":"PASS_E011JS_PORTABLE_REVIEW","cases":4,"next":"E011JT"},sort_keys=True))
