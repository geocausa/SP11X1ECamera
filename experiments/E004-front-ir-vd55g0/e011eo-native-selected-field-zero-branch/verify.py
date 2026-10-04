#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(n): return json.loads((H/n).read_text())
def check():
 s=L("SOURCE-SAFE.json");r=L("RESULT.json");f=L("FRONTIER-SAFE.json");n=L("NEXT-SOURCE.json");w=L("WINDOWS-SAFE.json")
 assert s["status"]=="PASS_NATIVE_QUALIFIED_SELECTED_FIELD_ZERO_BRANCH" and s["case_count"]==4
 assert s["pointed_object_field_read_executed"] and s["selected_field_zero_branch_taken"]
 assert s["native_front_selected_field_authority_joined"] and s["rejected_altered_contracts"]==448
 assert not s["broad_file_initial_state_persistence_qualified"] and not s["exact_CFD46C_native_instruction_breakpoint_observed"]
 assert w["independent_KD_read_confirmed_selected_field_zero"] and w["native_prestart_after_initialize_before_start"]["selected_field_value_u32"]==0
 assert w["native_prestart_after_initialize_before_start"]["second_pointer_not_file_static_0x1607650"]
 assert r["source_script_sha256"]==sha(H/"source-private.py") and r["source_safe_sha256"]==sha(H/"SOURCE-SAFE.json") and r["windows_safe_sha256"]==sha(H/"WINDOWS-SAFE.json")
 assert f["camera_frontier"]["source_RVA"]=="0xcfd498" and n["experiment"]=="E011EP" and not n["native_rear_runtime_allowed"]
 return {"status":"PASS_E011EO_PORTABLE_REVIEW","cases":4,"rejects":448,"next":"E011EP"}
if __name__=="__main__": print(json.dumps(check(),sort_keys=True))
