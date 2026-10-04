#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n):return json.loads((H/n).read_text())
def check():
 s=load("SOURCE-SAFE.json");r=load("RESULT.json");f=load("FRONTIER-SAFE.json");n=load("NEXT-SOURCE.json")
 assert s["status"]=="PASS_JOINED_ORIGINAL_STREAM_ALLOCATOR_RETURN" and s["case_count"]==4
 assert s["exact_dependency_reads"]==8 and s["exact_source_store_chunks"]==24
 assert s["rejected_altered_contracts"]==220
 assert s["global_index8_lock_release_qualified"] and s["selected_object_lock_retained_held"]
 assert s["complete_CC6078_return_qualified"] and s["next_source_RVA"]=="0xced150"
 assert r["source_script_sha256"]==sha(H/"source-private.py") and r["source_safe_sha256"]==sha(H/"SOURCE-SAFE.json")
 assert f["camera_frontier"]["source_RVA"]=="0xced150" and f["lock_state"]["selected_object_lock_held"]
 assert n["experiment"]=="E011EL" and not n["native_rear_runtime_allowed"]
 return {"status":"PASS_E011EK_PORTABLE_REVIEW","cases":4,"rejects":220,"next":"E011EL"}
if __name__=="__main__":print(json.dumps(check(),sort_keys=True))
