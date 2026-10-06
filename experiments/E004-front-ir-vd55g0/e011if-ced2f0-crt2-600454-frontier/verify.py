#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_JOIN_CED2F0_CRT2_RETURN_TO_600454_FRONTIER" and s["case_count"]==4 and s["call_instruction_executed"] and s["same_thread_CRT_error_u32"]==2 and s["CED2F0_complete_return_inherited"] and s["CED2F0_return_u32"]==2 and s["next_camera_source_RVA"]=="0x600454" and not s["next_camera_source_executed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IG" and not f["caller_frontier"]["executed"] and n["expected_frontier"]["read_RVA"]=="0x60046c"
print(json.dumps({"status":"PASS_E011IF_PORTABLE_REVIEW","cases":4,"next":"E011IG"},sort_keys=True))
