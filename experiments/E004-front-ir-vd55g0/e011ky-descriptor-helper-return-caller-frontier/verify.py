#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L("SOURCE-SAFE.json");r=L("RESULT.json");n=L("NEXT-SOURCE.json")
assert s["status"]=="PASS_DESCRIPTOR_COPY_HELPER_EPILOGUE_RETURN_TO_CALLER_FRONTIER" and s["case_count"]==4
assert s["success_epilogue_RVA"]=="0x5b9b80" and s["helper_ret_RVA"]=="0x5b9ba0" and s["caller_resume_RVA"]=="0x5b8348" and s["return_w0_u32"]==0 and s["caller_SP_restored"] and s["nonvolatile_frame_restored"]
assert not s["caller_result_branch_executed"] and s["rejected_altered_contracts"]==12 and not s["native_rear_runtime_allowed"]
for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
assert r["next_experiment"]=="E011KZ" and not n["current_frontier"]["branch_executed"]
print(json.dumps({"status":"PASS_E011KY_PORTABLE_REVIEW","cases":4,"next":"E011KZ"},sort_keys=True))
