#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(n): return json.loads((H/n).read_text())
def check():
 s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
 assert s["status"]=="PASS_JOINED_CFD550_CFCC18_VALIDATION_PREFIX" and s["case_count"]==4
 assert s["CFD550_register_reshape_qualified"] and s["CFCC18_validation_prefix_qualified"] and s["CFCC98_CFD410_arguments_qualified"]
 assert not s["CFD410_executed"] and s["exact_wrapper_key_stores"]==20 and s["rejected_altered_contracts"]==220
 assert s["next_source_RVA"]=="0xcfcc98" and s["next_call_target_RVA"]=="0xcfd410"
 assert r["source_script_sha256"]==sha(H/"source-private.py") and r["source_safe_sha256"]==sha(H/"SOURCE-SAFE.json")
 assert f["camera_frontier"]["call_not_executed"] and n["experiment"]=="E011EN" and not n["native_rear_runtime_allowed"]
 return {"status":"PASS_E011EM_PORTABLE_REVIEW","cases":4,"rejects":220,"next":"E011EN"}
if __name__=="__main__": print(json.dumps(check(),sort_keys=True))
