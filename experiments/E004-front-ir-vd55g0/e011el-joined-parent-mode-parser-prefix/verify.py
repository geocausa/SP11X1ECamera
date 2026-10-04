#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n):return json.loads((H/n).read_text())
def check():
 s=load("SOURCE-SAFE.json");r=load("RESULT.json");f=load("FRONTIER-SAFE.json");n=load("NEXT-SOURCE.json");g=load("GLOBAL-REFS-SAFE.json")
 assert s["status"]=="PASS_JOINED_PARENT_MODE_PARSER_PREFIX" and s["case_count"]==4
 assert s["CFA2E0_mode_parser_return_qualified"] and s["parser_result_flags"]=="0x100000000" and s["parser_validity"]==1
 assert s["exact_cold_global_reads"]==4 and s["exact_mode_literal_reads"]==16 and s["rejected_altered_contracts"]==60
 assert s["next_source_RVA"]=="0xcfa9bc" and not s["deeper_CFD550_CFCC18_effects_qualified"]
 assert g["target_RVA"]=="0x16a382c" and all(x["type"]=="READ" for x in g["refs"])
 assert r["source_script_sha256"]==sha(H/"source-private.py") and r["source_safe_sha256"]==sha(H/"SOURCE-SAFE.json") and r["global_refs_safe_sha256"]==sha(H/"GLOBAL-REFS-SAFE.json")
 assert f["camera_frontier"]["call_not_executed"] and n["experiment"]=="E011EM" and not n["native_rear_runtime_allowed"]
 return {"status":"PASS_E011EL_PORTABLE_REVIEW","cases":4,"next":"E011EM"}
if __name__=="__main__":print(json.dumps(check(),sort_keys=True))
