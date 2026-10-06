#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(x):return json.loads((H/x).read_text())
def S(x):return hashlib.sha256((H/x).read_bytes()).hexdigest()
def check():
 s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
 assert s["experiment"]=="E011IA" and s["status"]=="PASS_6BD94_RETURN26_PROPAGATION_TO_6BDC0_EPILOGUE_FRONTIER" and s["case_count"]==4 and s["rejected_altered_contracts"]==28
 assert s["input_w0_u32"]==26 and s["local_plus_0x10_after_u32"]==26 and s["result_branch_RVA"]=="0x6bda4" and s["result_branch_target_RVA"]=="0x6bdb4" and s["result_branch_taken"]
 assert s["local_plus_0x14_after_u32"]==26 and s["output_w0_u32"]==26 and s["next_camera_source_RVA"]=="0x6bdc0" and not s["next_camera_source_executed"]
 assert [x["axis"] for x in s["details"]]==[0,1,40,1230] and all(x["input_w0_u32"]==26 and x["result_branch_taken"] and x["output_w0_u32"]==26 and not x["next_executed"] for x in s["details"])
 for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
 assert r["next_experiment"]=="E011IB" and not r["new_front_camera_starts"] and not r["new_rear_camera_starts"] and not r["new_reboots"] and not r["new_kernel_build"] and r["returned_to_Golden_Linux"] and not r["native_rear_runtime_allowed"]
 assert not f["epilogue_frontier"]["executed"] and n["experiment"]=="E011IB" and n["expected_return"]["return_target_RVA"]=="0x6be0c"
 return {"status":"PASS_E011IA_PORTABLE_REVIEW","cases":4,"rejects":28,"next":"E011IB"}
if __name__=="__main__":print(json.dumps(check(),sort_keys=True))
