#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(x):return json.loads((H/x).read_text())
def S(x):return hashlib.sha256((H/x).read_bytes()).hexdigest()
def check():
 s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
 assert s["experiment"]=="E011HU" and s["status"]=="PASS_SP478_ZERO_CB1650_FASTPATH_TO_CA63E4_FRONTIER" and s["case_count"]==4 and s["rejected_altered_contracts"]==28
 assert s["frame_slot_u64"]==0 and s["frame_read_executed"] and s["call_x0_u64"]==0 and s["zero_fast_path_taken"] and s["w0_after_u32"]==26 and s["next_camera_source_RVA"]=="0xca63e4" and not s["next_camera_source_executed"]
 for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
 assert r["next_experiment"]=="E011HV" and not f["next"]["executed"] and n["expected_return"]["target_RVA"]=="0xcad940"
 return {"status":"PASS_E011HU_PORTABLE_REVIEW","cases":4,"rejects":28,"next":"E011HV"}
if __name__=="__main__":print(json.dumps(check(),sort_keys=True))
