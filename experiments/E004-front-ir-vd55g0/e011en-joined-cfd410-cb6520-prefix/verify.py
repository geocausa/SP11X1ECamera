#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(n): return json.loads((H/n).read_text())
def check():
 s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json")
 assert s["status"]=="PASS_JOINED_CFD410_CB6520_PREFIX" and s["case_count"]==4
 assert s["CFD410_local_setup_qualified"] and s["CB6520_owned_cold_zero_path_qualified"] and s["CB6520_return_qualified"]
 assert s["runtime_dependency_reads_qualified"]==12 and s["exact_EN_local_store_chunks"]==36 and s["rejected_altered_contracts"]==428
 assert not s["pointed_object_field_read_executed"] and s["next_source_RVA"]=="0xcfd46c" and s["next_dependency_RVA"]=="0x160718c"
 assert r["source_script_sha256"]==sha(H/"source-private.py") and r["source_safe_sha256"]==sha(H/"SOURCE-SAFE.json")
 assert not f["camera_frontier"]["dependency_read_executed"] and n["experiment"]=="E011EO" and not n["native_rear_runtime_allowed"]
 return {"status":"PASS_E011EN_PORTABLE_REVIEW","cases":4,"rejects":428,"next":"E011EO"}
if __name__=="__main__": print(json.dumps(check(),sort_keys=True))
