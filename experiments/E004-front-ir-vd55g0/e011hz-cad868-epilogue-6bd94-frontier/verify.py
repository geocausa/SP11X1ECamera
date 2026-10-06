#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(x):return json.loads((H/x).read_text())
def S(x):return hashlib.sha256((H/x).read_bytes()).hexdigest()
def check():
 s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
 assert s["experiment"]=="E011HZ" and s["status"]=="PASS_CAD868_EPILOGUE_RETURN26_TO_6BD94_FRONTIER" and s["case_count"]==4 and s["rejected_altered_contracts"]==32
 assert s["unique_callsite_RVA"]=="0x6bd90" and s["call_target_RVA"]=="0xcad868" and s["callsite_executed"] and s["architectural_return_RVA"]=="0x6bd94"
 assert s["epilogue_first_RVA"]=="0xcad9b0" and s["epilogue_return_RVA"]=="0xcad9c4" and s["epilogue_executed"] and s["saved_registers_restored"] and s["entry_SP_restored"] and s["return_w0_u32"]==26
 assert s["next_camera_source_RVA"]=="0x6bd94" and not s["next_camera_source_executed"]
 assert [x["axis"] for x in s["details"]]==[0,1,40,1230] and all(x["callsite_executed"] and x["saved_registers_restored"] and x["entry_SP_restored"] and x["w0_u32"]==26 and not x["return_target_executed"] for x in s["details"])
 for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
 assert r["next_experiment"]=="E011IA" and not r["new_front_camera_starts"] and not r["new_rear_camera_starts"] and not r["new_reboots"] and not r["new_kernel_build"] and r["returned_to_Golden_Linux"] and not r["native_rear_runtime_allowed"]
 assert not f["caller_frontier"]["executed"] and n["experiment"]=="E011IA" and n["current_camera_frontier"]["RVA"]=="0x6bd94"
 return {"status":"PASS_E011HZ_PORTABLE_REVIEW","cases":4,"rejects":32,"next":"E011IA"}
if __name__=="__main__":print(json.dumps(check(),sort_keys=True))
