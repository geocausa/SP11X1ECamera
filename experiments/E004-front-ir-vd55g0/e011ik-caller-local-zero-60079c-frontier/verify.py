#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_CALLER_LOCAL_ZERO_TO_60079C_EPILOGUE_FRONTIER" and s["case_count"]==4 and s["local_value_u32"]==0 and s["direct_local_stores_after_producer_before_consumer"]==0 and s["consumer_zero_branch_taken"] and s["consumer_zero_branch_target_RVA"]=="0x60079c" and not s["next_camera_source_executed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IL" and not f["next_frontier"]["executed"]
print(json.dumps({"status":"PASS_E011IK_PORTABLE_REVIEW","cases":4,"next":"E011IL"},sort_keys=True))
