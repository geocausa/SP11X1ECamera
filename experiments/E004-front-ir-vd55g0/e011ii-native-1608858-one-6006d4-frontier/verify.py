#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_NATIVE_1608858_ONE_TO_SECOND_6006D4_FRONTIER" and s["case_count"]==4 and s["native_dependency_value_u32"]==1 and s["field_nonzero_branch_taken"] and s["field_nonzero_branch_target_RVA"]=="0x6006d4" and s["loop_counter_w26_u32"]==1 and not s["next_loop_counter_instruction_executed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IJ" and not f["next_frontier"]["executed"] and n["expected_frontier"]["RVA"]=="0x6006dc"
print(json.dumps({"status":"PASS_E011II_PORTABLE_REVIEW","cases":4,"next":"E011IJ"},sort_keys=True))
