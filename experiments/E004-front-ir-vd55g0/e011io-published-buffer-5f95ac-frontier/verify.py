#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_PUBLISHED_ENUM_BUFFER_TO_5F95AC_FRONTIER" and s["case_count"]==4 and s["published_pointer_nonzero"] and s["published_buffer_bytes"]==18832 and s["published_buffer_initial_zero_authority"] and not s["zero_branch_taken"] and s["next_camera_source_RVA"]=="0x5f95ac" and not s["next_dependency_read_executed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IP" and not f["next_frontier"]["executed"]
print(json.dumps({"status":"PASS_E011IO_PORTABLE_REVIEW","cases":4,"next":"E011IP"},sort_keys=True))
