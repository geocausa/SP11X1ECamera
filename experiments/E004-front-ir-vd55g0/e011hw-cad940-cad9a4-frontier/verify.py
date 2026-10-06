#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(x):return json.loads((H/x).read_text())
def S(x):return hashlib.sha256((H/x).read_bytes()).hexdigest()
def check():
 s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
 assert s["experiment"]=="E011HW" and s["status"]=="PASS_CAD940_RETURN26_TO_CAD9A4_CLEANUP_FRONTIER" and s["case_count"]==4 and s["rejected_altered_contracts"]==28
 assert s["x20_SP_relative"]=="0x200" and s["x22_u64"]==640 and s["terminator_SP_relative"]=="0x47f" and s["terminator_store_executed"] and s["return_w0_u32"]==26 and s["return_branch_taken"] and s["w19_after_u32"]==26 and s["sign_nonnegative_branch_taken"] and s["next_camera_source_RVA"]=="0xcad9a4" and not s["next_camera_source_executed"]
 for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
 assert r["next_experiment"]=="E011HX" and not f["cleanup_frontier"]["executed"] and n["expected_call_frontier"]["target_RVA"]=="0xca8658"
 return {"status":"PASS_E011HW_PORTABLE_REVIEW","cases":4,"rejects":28,"next":"E011HX"}
if __name__=="__main__":print(json.dumps(check(),sort_keys=True))
