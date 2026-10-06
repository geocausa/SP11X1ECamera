#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(x):return json.loads((H/x).read_text())
def S(x):return hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["experiment"]=="E011IC" and s["status"]=="PASS_6BDD0_TAIL_RETURN26_TO_7ACDC_FRONTIER" and s["case_count"]==4 and s["rejected_altered_contracts"]==32
assert s["source_callsite_RVA"]=="0x7acd8" and s["call_target_RVA"]=="0x6bdd0" and s["tail_executed"] and s["saved_frame_restored"] and s["return_w0_u32"]==26 and s["next_camera_source_RVA"]=="0x7acdc" and not s["next_camera_source_executed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011ID" and not f["frontier"]["executed"] and n["expected_return"]["return_target_RVA"]=="0x600440"
print(json.dumps({"status":"PASS_E011IC_PORTABLE_REVIEW","cases":4,"rejects":32,"next":"E011ID"},sort_keys=True))
