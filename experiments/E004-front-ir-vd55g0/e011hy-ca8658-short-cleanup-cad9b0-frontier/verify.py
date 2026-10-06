#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def L(x):return json.loads((H/x).read_text())
def S(x):return hashlib.sha256((H/x).read_bytes()).hexdigest()
def check():
 s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
 assert s["experiment"]=="E011HY" and s["status"]=="PASS_CA8658_SHORT_CLEANUP_TO_CAD9B0_EPILOGUE_FRONTIER" and s["case_count"]==4 and s["rejected_altered_contracts"]==28
 assert s["object_plus_0x28_u8"]==1 and s["object_plus_0x30_u8"]==0 and s["object_plus_0x38_u8"]==0
 assert s["call_RVA"]=="0xcad9a8" and s["call_target_RVA"]=="0xca8658" and s["call_executed"] and s["cleanup_short_path"] and s["cleanup_returned"]
 assert s["cleanup_ret_RVA"]=="0xca8778" and s["cleanup_return_target_RVA"]=="0xcad9ac" and s["w0_after_u32"]==26
 assert s["next_camera_source_RVA"]=="0xcad9b0" and not s["next_camera_source_executed"]
 assert [x["axis"] for x in s["details"]]==[0,1,40,1230] and all(x["object_plus_0x28_u8"]==1 and x["object_plus_0x30_u8"]==0 and x["object_plus_0x38_u8"]==0 and x["cleanup_returned"] and x["w0_after_u32"]==26 and not x["next_executed"] for x in s["details"])
 for k,x in [("source_safe_sha256","SOURCE-SAFE.json"),("frontier_safe_sha256","FRONTIER-SAFE.json"),("next_source_sha256","NEXT-SOURCE.json")]:assert r[k]==S(x)
 assert r["next_experiment"]=="E011HZ" and not r["new_front_camera_starts"] and not r["new_rear_camera_starts"] and not r["new_reboots"] and not r["new_kernel_build"] and r["returned_to_Golden_Linux"] and not r["native_rear_runtime_allowed"]
 assert not f["epilogue_frontier"]["executed"] and n["experiment"]=="E011HZ" and n["expected_return"]["return_target_RVA"]=="0x6bd94" and not n["expected_return"]["return_target_executed"]
 return {"status":"PASS_E011HY_PORTABLE_REVIEW","cases":4,"rejects":28,"next":"E011HZ"}
if __name__=="__main__":print(json.dumps(check(),sort_keys=True))
