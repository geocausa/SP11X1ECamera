#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_ZERO_ENUM_BUFFER_FIELDS_TO_160A260_FRONTIER" and s["case_count"]==4 and s["published_buffer_preserved_zero_through_600368_return"] and len(s["qualified_zero_field_offsets"])==12 and s["signed_byte_2828_u8"]==0 and s["branch_taken_to_RVA"]=="0x5f9684" and s["x20_after_branch_u64"]==0 and s["next_dependency_RVA"]=="0x160a260" and not s["next_dependency_read_executed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IQ" and not f["next_frontier"]["executed"]
print(json.dumps({"status":"PASS_E011IP_PORTABLE_REVIEW","cases":4,"next":"E011IQ"},sort_keys=True))
