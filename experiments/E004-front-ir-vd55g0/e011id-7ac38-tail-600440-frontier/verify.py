#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_7AC38_TAIL_RETURN26_TO_600440_FRONTIER" and s["case_count"]==4 and s["return_w0_u32"]==26 and s["next_camera_source_RVA"]=="0x600440" and not s["next_camera_source_executed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
print(json.dumps({"status":"PASS_E011ID_PORTABLE_REVIEW","next":"E011IE"},sort_keys=True))
