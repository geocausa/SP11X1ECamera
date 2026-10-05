#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(n): return json.loads((H/n).read_text())
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def check():
 s=L("SOURCE-SAFE.json"); r=L("RESULT.json"); f=L("FRONTIER-SAFE.json"); n=L("NEXT-SOURCE.json")
 assert s["experiment"]=="E011GE" and s["status"]=="PASS_DISPATCH_MINUS52_TO_CA9718_CASE_FRONTIER" and s["case_count"]==4 and s["rejected_altered_contracts"]==16
 assert s["dispatch_table_RVA"]=="0xca98ec" and s["dispatch_index_u32"]==1 and s["dispatch_entry_RVA"]=="0xca98f0" and s["dispatch_entry_s32"]==-52
 assert s["dispatch_read_RVA"]=="0xca95f4" and s["dispatch_read_executed"] and s["dispatch_target_RVA"]=="0xca9718" and s["dispatch_branch_RVA"]=="0xca9600" and s["dispatch_branch_executed"] and not s["selected_case_executed"]
 for k,nm in [("source_script_sha256","source-private.py"),("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json")]: assert r[k]==sha(nm)
 assert not r["new_front_camera_starts"] and not r["new_reboots"] and r["returned_to_Golden_Linux"] and not r["native_rear_runtime_allowed"]
 assert n["experiment"]=="E011GF" and n["current_camera_frontier"]["source_RVA"]=="0xca9718" and n["current_camera_frontier"]["next_dependency_read_RVA"]=="0x1370761" and not n["current_camera_frontier"]["next_dependency_read_executed"]
 assert f["camera_frontier"]["next_source_RVA"]=="0xca9718" and not f["camera_frontier"]["selected_case_executed"]
 return {"status":"PASS_E011GE_PORTABLE_REVIEW","cases":4,"rejects":16,"next":"E011GF"}
if __name__=="__main__": print(json.dumps(check(),sort_keys=True))
