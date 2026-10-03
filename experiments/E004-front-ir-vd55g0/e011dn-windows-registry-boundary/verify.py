#!/usr/bin/env python3
"""Check derived E011DN observation scope and evidence/source hash bindings."""
from pathlib import Path
import copy,hashlib,json,sys
import yaml
H=Path(__file__).resolve().parent
R=H.parents[2]
STATUS="PASS_BOUNDED_READY_REGISTRY_SNAPSHOT_RS_COPY_UNOBSERVED"
FALSE=("original_metadata_initializer_execution_qualified","selected_runtime_tag_initialization_qualified",
"populated_RS_identity_generation_lifetime_qualified","live_query_or_reader_execution_proven",
"absence_of_RS_across_other_processes_or_profiles_proven","normal_AFD_input_authority_closed",
"complete_deterministic_source_bootstrap_closed","independent_enabled_output_retirement_proven",
"native_rear_runtime_allowed","optical_material_saved","production_code_changed","private_raw_material_exported")
def contract(o):
 assert o["experiment"]=="E011DN" and o["status"]==STATUS
 for k in FALSE:assert o[k] is False,k
 assert o["registry_snapshot_qualified"] and o["same_Windows_boot"] and o["platform_callbacks_match_file_default"]
 assert o["snapshot_bytes"]==dict(runtime_tags=28,metadata_registry=64,platform_callbacks=24)
 assert o["runtime_tag_cell_count"]==7 and o["runtime_tag_nonzero_count"]==0
 assert o["selected_RS_tag_initialized"] is False
 assert o["metadata_bound_nonzero"] and o["metadata_descriptor_pointer_nonnull"]
 assert o["metadata_bound_RVA"]=="0x17350e0" and o["metadata_descriptor_pointer_RVA"]=="0x1735118"
 assert o["platform_callback_RVAs"]==["0x1de30","0x1df30","0x1df90"]
 assert o["GuardCFCheckFunctionPointer_cell_RVA"]=="0xf7e7b8" and o["cold_CFG_check_is_not_resource_constructor"]
 assert o["metadata_bound_writer_reference"]==dict(field_RVA="0x17350e0",site_RVA="0x5de9d8",function_RVA="0x5de700",access="write")
 assert o["source_function_pins"]["0x5de700"]==dict(bytes=4188,sha256="776092eab939986d2258713b25723c3ad4c1ddcdc8231881da140e25a9960533")
 assert len(o["source_function_pins"])==5
 assert o["Windows_boots"]==1 and o["reboots"]==2 and o["camera_starts"]==2 and o["kernel_debugger_halts"]==0
 assert o["RS_copy_samples"]==0 and o["next_experiment"]=="E011DO"
 assert o["Golden_guard_status"]=="PASS_GOLDEN_RETURN_EFI_GRUB_HASHES_HISTORY_EXACT"
 assert len(o["attempts"])==2
 for i,(a,n) in enumerate(zip(o["attempts"],(69,449))):
  assert a["identity"]=="E011DN-20261003-1926"+("A" if i==0 else "B")
  assert a["status"]==("EXCLUDED_NO_RS_CAPTURE" if i==0 else "REGISTRY_SNAPSHOT_ONLY_NO_RS_COPY")
  assert a["camera_starts"]==1 and a["valid_4k_handle_acquisitions"]==n and a["RS_copy_samples"]==0
  for k in ("stop_dispose_done","camera_task_removed","debugger_process_absent","target_service_process_absent"):assert a[k]
 assert o["accepted_observation_identity"]==o["attempts"][1]["identity"] and o["excluded_RS_attempt_identity"]==o["attempts"][0]["identity"]
 assert len(o["private_nonoptical_evidence_hashes"])>=20
def main():
 o=json.loads((H/"OBSERVATION-SAFE.json").read_text());contract(o)
 result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="f9669dd0809f2188232174fd30478101fe7d1e34"
 assert result["next_experiment"]=="E011DO" and result["RS_copy_samples"]==0
 assert result["native_rear_runtime_allowed"] is False
 assert result["metadata_registry_original_initializer_execution_qualified"] is False
 assert len(result["source_locks"])>=8
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R)
  assert hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 state=yaml.safe_load((R/"state/project.yaml").read_text())
 assert state["current_experiment"]=="E011DN" and state["next_experiment"]=="E011DO"
 assert state["e011dn_Windows_registry_boundary"]["RS_copy_samples"]==0
 readiness=json.loads((R/"src/sp11-camera-stack/READINESS.json").read_text())
 assert readiness["latest_Windows_registry_boundary"]==state["e011dn_Windows_registry_boundary"]
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["latest_source_RS_checkpoint"]=="E011DM" and f["latest_factory_enumeration_checkpoint"]=="E011DI"
 assert n["experiment"]=="E011DO" and n["native_rear_runtime_allowed"] is False
 rejected=0
 if "--selfcheck" in sys.argv:
  mutations=[(k,True) for k in FALSE]+[("RS_copy_samples",1),("Windows_boots",2),("selected_RS_tag_initialized",True),("runtime_tag_nonzero_count",1),("platform_callback_RVAs",["0x1de30","0x1df34","0x1df90"]),("registry_snapshot_qualified",False),("accepted_observation_identity",o["attempts"][0]["identity"])]
  for k,v in mutations:
   bad=copy.deepcopy(o);bad[k]=v
   try:contract(bad)
   except AssertionError:rejected+=1
   else:raise AssertionError("scope or evidence mutation admitted: "+k)
  assert rejected==len(mutations)
 print(json.dumps({"status":"PASS_E011DN_REVIEW","snapshot_bytes":116,"source_locks":len(result["source_locks"]),"scope_evidence_mutations_rejected":rejected,"RS_copy_samples":0,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
