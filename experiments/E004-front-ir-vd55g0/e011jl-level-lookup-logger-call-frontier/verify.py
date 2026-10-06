#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_LEVEL_LOOKUP_TO_LOGGER_CALL_FRONTIER" and s["case_count"]==4
assert s["lookup_selector_u64"]==131072 and s["lookup_call_RVA"]=="0x5bec98" and s["lookup_target_RVA"]=="0x5d0c0" and s["lookup_return_RVA"]=="0x135f200" and s["lookup_return_bytes"]==10
assert s["logger_call_RVA"]=="0x5becb8" and s["logger_target_RVA"]=="0x1aca8" and s["logger_w0_u32"]==2 and s["logger_w1_u32"]==65535 and not s["logger_call_executed"]
assert s["new_front_camera_starts"]==s["new_rear_camera_starts"]==s["new_reboots"]==0 and not s["new_kernel_build"] and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]: assert r[k]==S(x)
assert r["next_experiment"]=="E011JM" and not f["logger_frontier"]["call_executed"] and n["accepted_logger_authority"]["diagnostic_no_effect_dependency_is_owned_model"]
print(json.dumps({"status":"PASS_E011JL_PORTABLE_REVIEW","cases":4,"next":"E011JM"},sort_keys=True))
