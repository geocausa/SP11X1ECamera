#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_NATIVE_160A218_ZERO_TO_SECOND_600474_FRONTIER" and s["case_count"]==4 and s["native_dependency_value_u64"]==0 and not s["bit16_set"] and not s["bit16_branch_taken"] and s["loop_counter_w26_u32"]==1 and s["next_camera_source_RVA"]=="0x600474" and not s["next_dependency_read_executed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011II" and not f["next_frontier"]["executed"] and n["expected_frontier"]["RVA"]=="0x6006d4"
print(json.dumps({"status":"PASS_E011IH_PORTABLE_REVIEW","cases":4,"next":"E011II"},sort_keys=True))
