#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_EPOCH_80000043_TO_LOADER_INDEX_FRONTIER" and s["case_count"]==4 and s["lock_held_during_effects"]
assert s["epoch_cell_RVA"]=="0x1607b04" and s["epoch_before_u32"]=="0x80000042" and s["epoch_after_u32"]=="0x80000043"
assert s["guard_RVA"]=="0x1b302d0" and s["guard_before_u32"]=="0xffffffff" and s["guard_after_u32"]=="0x80000043"
assert s["next_loader_index_read_RVA"]=="0xce7a90" and s["next_loader_index_cell_RVA"]=="0x16a3740" and not s["next_loader_index_read_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011JV" and n["retained_state"]["epoch_u32"]=="0x80000043"
print(json.dumps({"status":"PASS_E011JU_PORTABLE_REVIEW","cases":4,"next":"E011JV"},sort_keys=True))
