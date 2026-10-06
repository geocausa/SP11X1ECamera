#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_600440_RETURN26_TO_CED2F0_CALL_FRONTIER" and s["case_count"]==4 and s["input_w0_u32"]==26 and s["loop_counter_w26_u32"]==1 and s["x23_RVA"]=="0x10f03b0"
assert s["call_RVA"]=="0x600450" and s["call_target_RVA"]=="0xced2f0" and not s["call_executed"] and s["call_x0_SP_relative"]=="0x8" and s["call_x1_SP_relative"]=="0x40" and s["call_x2_RVA"]=="0x1363d40" and s["memory_reads_before_call"]==s["memory_writes_before_call"]==0
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IF" and not f["call_frontier"]["call_executed"] and n["expected_return"]["target_RVA"]=="0x600454"
print(json.dumps({"status":"PASS_E011IE_PORTABLE_REVIEW","cases":4,"next":"E011IF"},sort_keys=True))
