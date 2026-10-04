#!/usr/bin/env python3
"""Review E011EF lowIO cold-count continuation/return and reject unqualified native-state or join claims."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
P=R/"experiments/E004-front-ir-vd55g0/e011ee-original-isolated-lowio-block-publication"
STATUS="PASS_BOUNDED_ORIGINAL_LOWIO_COUNT_ACTIVATION_RETURN"
TRUE=("original_lowIO_block_construction_and_publication_qualified","original_lowIO_block_constructor_return_qualified",
 "original_lowIO_count_transition_qualified","original_first_lowIO_record_lock_and_activation_qualified","original_lowIO_initializer_return_qualified",
 "lowIO_initializer_isolated_from_other_contexts","camera_caller_memory_permissions_and_frontier_unchanged","stream_initializer_memory_permissions_and_frontier_unchanged")
FALSE=("original_stream_initializer_return_qualified","all_initializer_and_camera_states_join_qualified","stream_initializer_and_camera_state_join_qualified",
 "actual_loader_CRT_startup_caller_qualified","native_allocator_implementation_qualified","source_result_fixture_used","native_rear_runtime_allowed",
 "native_CRT_resource_initialization_qualified","native_runtime_scalar_and_pointer_selection_qualified","native_runtime_count_selection_qualified",
 "pointed_standard_stream_contents_qualified","stream_runtime_pointer_read_qualified","native_handles_or_file_contents_qualified","file_open_or_contents_qualified",
 "full_outer_callee_return_qualified","full_factory_or_first_helper_return_qualified","new_kernel_build","production_code_changed","private_raw_material_exported")
PER={"original_instruction_visits":37,"exact_source_store_chunks":2,"rejected_owned_requests":55,"exact_dependency_reads":5,
 "exact_original_wrapper_entries":2,"owned_OS_API_calls":2,"original_lowIO_initializer_ABI_return_exact":1}
ROW_TRUE=("first_record_lock_owned_model_held","lowIO_global_lock_owned_model_released","isolated_lowIO_memory_and_permissions_exact","redzones_exact","original_lowIO_initializer_return_qualified")
ROW_FALSE=("all_initializer_and_camera_states_join_qualified","actual_loader_CRT_startup_caller_qualified","native_CRT_resource_initialization_qualified","native_runtime_count_selection_qualified")
SCALARS={"count_initial":0,"count_final":64,"count_increment":64,"first_record_active_byte":1}
COUNT=[{"RVA":"0x16a2e90","bytes":4,"section_writable":True,"virtual_zero_fill":True,"file_backed":False,"accepted_owned_initial_value":0,"native_runtime_selection_qualified":False}]
PROVIDER={"count_read_RVA":"0xcc0948","count_write_RVA":"0xcc0950","initial_count":0,"count_increment":64,"final_count":64,
 "record_lock_wrapper_RVA":"0xcc07b0","record_lock_return_RVA":"0xcc095c","record_index":0,"record_lock_resource_offset":0,
 "enter_import_cell_RVA":"0xf7e0b8","record_lock_owned_model_held_after_return":True,"global_unlock_wrapper_RVA":"0xcb7398",
 "global_unlock_return_RVA":"0xcc0978","global_lock_index":7,"global_lock_resource_RVA":"0x16a2fd8","leave_import_cell_RVA":"0xf7e0c0",
 "global_lock_owned_model_held_after_return":False,"OS_void_return_is_owned_clobber_model":True,"native_CRT_resource_initialization_qualified":False}
EXTRA={"0xcc07b0":{"body_bytes":40,"ranges":[["0xcc07b0","0xcc07d7"]],"sha256":"be7159a0f0c442885d5f7a5e3789c97b5890579c91d607448b651d13f4e2d17c"},
 "0xcb7398":{"body_bytes":28,"ranges":[["0xcb7398","0xcb73b3"]],"sha256":"ba0fb2d4a1e1a1d1effa82370b5d86970cbf56048020dfd66c1702bb8237af60"}}
def contract(s):
 parent=json.loads((P/"SOURCE-SAFE.json").read_text())
 assert s["experiment"]=="E011EF" and s["status"]==STATUS and s["scenarios"]==256 and s["next_experiment"]=="E011EG"
 for k in TRUE: assert s[k] is True,k
 for k in FALSE: assert s[k] is False,k
 assert s["new_camera_starts"]==s["new_reboots"]==0
 assert s["lowIO_count_owned_cold_initial_value_authority"]==COUNT and s["lowIO_continuation_owned_provider_authority"]==PROVIDER
 for k in ("lowIO_owned_cold_initial_value_authority","lowIO_owned_provider_authority","initializer_owned_cold_initial_value_authority",
           "initializer_owned_provider_authority","runtime_initial_value_model_authority"):
  assert s[k]==parent[k],k
 assert s["source_pins"]==dict(parent["source_pins"],**EXTRA) and len(s["source_pins"])==49 and s["image_sha256"]==parent["image_sha256"]
 rows=s["details"];assert len(rows)==256 and [r["EE"] for r in rows]==parent["details"]
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 wanted=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 got=set()
 for row in rows:
  p=row["EE"]
  for key in ("ED","EC","EB","EA","DZ","DY","DX","DW","DV","DU","DT","DS"): p=p[key]
  got.add(tuple(p[k] for k in axes))
  a=row["added"]
  assert all(a[k]==v for k,v in PER.items())
  assert all(a[k] is True for k in ROW_TRUE) and all(a[k] is False for k in ROW_FALSE)
  assert all(a[k]==v for k,v in SCALARS.items())
 assert got==wanted
 assert s["added_totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(r["added"][k] for r in rows) for k in PER}
 assert s["inherited_EE_totals"]==parent["added_totals"] and s["inherited_ED_totals"]==parent["inherited_ED_totals"]
 for k in ("EC","EB","EA","DZ","DY","DX","DW","DV","DU","DT","DS"): assert s["inherited_"+k+"_totals"]==parent["inherited_"+k+"_totals"]
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s)
 result_path=H/"RESULT.json"
 if result_path.exists():
  result=json.loads(result_path.read_text())
  assert result["status"]==STATUS and result["qualification_exit_code"]==0 and result["scenarios"]==256
  assert result["added_original_instruction_visits"]==9472 and result["combined_original_instruction_visits"]==1998592
  assert result["camera_chain_original_instruction_visits"]==1237760 and result["aggregate_spans_isolated_contexts"] is True
  for rel,pin in result.get("source_locks",{}).items():
   p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 count=0
 if "--selfcheck" in sys.argv:
  mutations=[]
  def put(path,value):
   bad=copy.deepcopy(s);at=bad
   for k in path[:-1]:at=at[k]
   at[path[-1]]=value;mutations.append(bad)
  for k in TRUE:put([k],False)
  for k in FALSE:put([k],True)
  for k,v in PER.items():put(["details",0,"added",k],v+1)
  for k in ROW_TRUE:put(["details",0,"added",k],False)
  for k in ROW_FALSE:put(["details",0,"added",k],True)
  for k,v in SCALARS.items():put(["details",0,"added",k],v+1)
  put(["lowIO_count_owned_cold_initial_value_authority",0,"accepted_owned_initial_value"],1)
  put(["lowIO_count_owned_cold_initial_value_authority",0,"native_runtime_selection_qualified"],True)
  put(["lowIO_continuation_owned_provider_authority","final_count"],63)
  put(["source_pins","0xcc07b0","body_bytes"],44)
  put(["added_totals","original_instruction_visits"],9473)
  for bad in mutations:
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence/state-join mutation admitted")
 print(json.dumps({"status":"PASS_E011EF_REVIEW","scenarios":256,"added_original_visits":9472,"combined_original_visits":1998592,
  "camera_chain_original_visits":1237760,"aggregate_spans_isolated_contexts":True,"source_pins":49,
  "scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
