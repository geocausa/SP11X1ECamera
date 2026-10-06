#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_5F941C_HELPER_PROLOGUE_TO_169FDF0_FRONTIER" and s["case_count"]==4 and s["call_executed"] and s["cookie_producer_executed"] and s["next_dependency_RVA"]=="0x169fdf0" and not s["next_dependency_read_executed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IO" and not f["next_frontier"]["executed"]
print(json.dumps({"status":"PASS_E011IN_PORTABLE_REVIEW","cases":4,"next":"E011IO"},sort_keys=True))
