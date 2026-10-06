#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_FIRST_DESCRIPTOR_RETURN_TO_SECOND_DESCRIPTOR_CALL_FRONTIER" and s["case_count"]==4
assert s["descriptor_count_u32"]==164 and s["descriptor_index_after_u32"]==1 and s["completed_count_after_u32"]==1 and s["loop_back_branch_taken"]
assert s["source_table_RVA"]=="0x1624140" and s["source_entry_RVA"]=="0x1624160" and s["destination_offset_u64"]==32 and s["copy_call_RVA"]=="0x5b8344" and not s["copy_call_executed"]
assert s["rejected_altered_contracts"]==16 and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011LA" and not n["current_frontier"]["copy_call_executed"]
print(json.dumps({"status":"PASS_E011KZ_PORTABLE_REVIEW","cases":4,"next":"E011LA"},sort_keys=True))
