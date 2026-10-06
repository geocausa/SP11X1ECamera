#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(x):return json.loads((H/x).read_text())
def S(x):return hashlib.sha256((H/x).read_bytes()).hexdigest()
def check():
 s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
 assert s["experiment"]=="E011HV" and s["status"]=="PASS_CA6280_COOKIE_EPILOGUE_TO_CAD940_FRONTIER" and s["case_count"]==4 and s["rejected_altered_contracts"]==28
 assert s["cookie_check_success_all_axes"] and not s["cookie_failure_executed"] and s["saved_registers_restored"] and s["SP_restored_to_CA6280_entry"] and s["return_w0_u32"]==26 and s["next_camera_source_RVA"]=="0xcad940" and not s["next_camera_source_executed"]
 for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
 assert r["next_experiment"]=="E011HW" and not f["caller_frontier"]["executed"] and n["expected_path"]["target_RVA"]=="0xcad9a4"
 return {"status":"PASS_E011HV_PORTABLE_REVIEW","cases":4,"rejects":28,"next":"E011HW"}
if __name__=="__main__":print(json.dumps(check(),sort_keys=True))
