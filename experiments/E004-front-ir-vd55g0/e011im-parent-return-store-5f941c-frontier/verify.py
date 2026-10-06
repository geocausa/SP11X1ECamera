#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_PARENT_RETURN_STORE_STATUS8_TO_5F941C_FRONTIER" and s["case_count"]==4 and s["returned_x0_nonzero"] and s["parent_store_aliases_return_pointer"] and s["selected_status_u32"]==8 and s["status_branch_taken"] and s["status_branch_target_RVA"]=="0x5f941c" and not s["next_call_executed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IN" and not f["next_frontier"]["executed"] and n["expected_frontier"]["dependency_RVA"]=="0x169fdf0"
print(json.dumps({"status":"PASS_E011IM_PORTABLE_REVIEW","cases":4,"next":"E011IN"},sort_keys=True))
