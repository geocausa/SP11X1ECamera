#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(x):return json.loads((H/x).read_text())
def S(x):return hashlib.sha256((H/x).read_bytes()).hexdigest()
def check():
 s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
 assert s["experiment"]=="E011HX" and s["status"]=="PASS_CAD9A4_TO_CA8658_CLEANUP_CALL_FRONTIER" and s["case_count"]==4 and s["rejected_altered_contracts"]==16 and s["call_x0_SP_relative"]=="0x10" and s["call_target_RVA"]=="0xca8658" and not s["call_executed"]
 for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
 assert r["next_experiment"]=="E011HY" and not f["call_frontier"]["call_executed"] and n["expected_cleanup"]["next_RVA"]=="0xcad9b0"
 return {"status":"PASS_E011HX_PORTABLE_REVIEW","cases":4,"rejects":16,"next":"E011HY"}
if __name__=="__main__":print(json.dumps(check(),sort_keys=True))
