#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_SECOND_ITERATION_NONZERO_CLEANUP_TO_60046C_FRONTIER" and s["case_count"]==4 and s["caller_return_u32"]==2 and s["caller_x20_cleared"] and s["caller_output_slot_value_u64"]==0 and s["loop_counter_w26_u32"]==1 and s["x23_RVA"]=="0x10f03b0" and s["next_camera_source_RVA"]=="0x60046c" and not s["next_dependency_read_executed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IH" and not f["accepted_frontier"]["executed"] and n["expected_frontier"]["read_RVA"]=="0x600474"
print(json.dumps({"status":"PASS_E011IG_PORTABLE_REVIEW","cases":4,"next":"E011IH"},sort_keys=True))
