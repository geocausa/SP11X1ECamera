#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest()
s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_OUTER_EPILOGUE_COOKIE_RETURN_TO_5F8EA8_FRONTIER" and s["case_count"]==4 and not s["cookie_failure_path_executed"] and s["saved_frame_restored"] and s["entry_SP_restored"] and s["architectural_return_RVA"]=="0x5f8ea8" and s["return_x0_kind"]=="nonzero_owned_object_pointer" and not s["next_camera_source_executed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011IM" and not f["return"]["executed"]
print(json.dumps({"status":"PASS_E011IL_PORTABLE_REVIEW","cases":4,"next":"E011IM"},sort_keys=True))
