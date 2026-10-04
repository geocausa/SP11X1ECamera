#!/usr/bin/env python3
"""Review three isolated contexts and reject unqualified native-state or join claims."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2];P=R/"experiments/E004-front-ir-vd55g0/e011ed-original-isolated-stream-initializer-publication"
STATUS="PASS_BOUNDED_ORIGINAL_ISOLATED_LOWIO_BLOCK_PUBLICATION"
FALSE=("original_lowIO_initializer_return_qualified","original_stream_initializer_return_qualified","all_initializer_and_camera_states_join_qualified",
 "stream_initializer_and_camera_state_join_qualified","actual_loader_CRT_startup_caller_qualified","native_allocator_implementation_qualified",
 "source_result_fixture_used","native_rear_runtime_allowed","native_CRT_resource_initialization_qualified","native_runtime_scalar_and_pointer_selection_qualified",
 "pointed_standard_stream_contents_qualified","stream_runtime_pointer_read_qualified","native_handles_or_file_contents_qualified","file_open_or_contents_qualified",
 "full_outer_callee_return_qualified","full_factory_or_first_helper_return_qualified","new_kernel_build","production_code_changed","private_raw_material_exported")
TRUE=("original_lowIO_block_construction_and_publication_qualified","original_lowIO_block_constructor_return_qualified","lowIO_initializer_isolated_from_other_contexts",
 "camera_caller_memory_permissions_and_frontier_unchanged","stream_initializer_memory_permissions_and_frontier_unchanged")
PER={"original_instruction_visits":2884,"exact_source_store_chunks":663,"independent_lowIO_store_contracts":663,"rejected_owned_requests":4714,
 "exact_dependency_reads":130,"original_nested_ABI_returns_exact":67,"exact_original_nested_callee_entries":67,"owned_allocation_calls":1,"owned_zeroed_allocation_bytes":4608,"owned_OS_API_calls":65}
BOOL=("lowIO_lock_owned_model_held","isolated_lowIO_memory_and_permissions_exact","redzones_exact","original_lowIO_block_constructor_return_qualified",
 "camera_caller_memory_permissions_and_frontier_unchanged","stream_initializer_memory_permissions_and_frontier_unchanged","lowIO_initializer_isolated_from_other_contexts")
ROW_FALSE=("original_lowIO_initializer_return_qualified","all_initializer_and_camera_states_join_qualified","native_CRT_resource_initialization_qualified","native_handles_or_file_contents_qualified")
EXPECTED={"published_lowIO_blocks":1,"records_per_block":64,"record_bytes":72,"owned_ready_record_resources":64,
 "stop_before_RVA":"0xcc0948","next_dependency_RVA":"0x16a2e90","next_dependency_bytes":4,"current_SP_relative_lowIO_entry":-96}
INITIAL=[{'RVA': '0x16a2a90', 'bytes': 8, 'section_writable': True, 'virtual_zero_fill': True, 'file_backed': False, 'accepted_owned_initial_value': 0, 'native_runtime_selection_qualified': False}]
PROVIDERS={'allocator_request_RVA': '0xcb75e0', 'allocator_return_RVA': '0xcc05dc', 'count': 64, 'element_bytes': 72, 'allocation_bytes': 4608, 'zeroed_allocation_provider_is_owned_model': True, 'native_allocator_implementation_qualified': False, 'lock_wrapper_RVA': '0xcb7300', 'lock_index': 7, 'lock_resource_RVA': '0x16a2fd8', 'lock_model_ready': True, 'lock_return_RVA': '0xcc090c', 'lock_import_cell_RVA': '0xf7e0b8', 'OS_void_return_is_owned_clobber_model': True, 'resource_initializer_wrapper_RVA': '0xcba4b0', 'resource_initializer_return_RVA': '0xcc061c', 'import_cell_RVA': '0xf7e230', 'record_resource_offset': 0, 'resource_bytes': 40, 'spin_count': 4000, 'flags': 0, 'resource_success_return_is_owned_model': True, 'native_CRT_resource_initialization_qualified': False, 'native_handles_or_file_contents_qualified': False}
EXTRA={'0xcc08e8': {'body_bytes': 332, 'ranges': [['0xcc08e8', '0xcc0a33']], 'sha256': '0fd5d934868e2d438d497d94de0922455cf909e3553a24833a1f8cf659c7893b'}, '0xcc05b8': {'body_bytes': 204, 'ranges': [['0xcc05b8', '0xcc0683']], 'sha256': '2e8f62889f5850eb5275da5b71bc43cf777b62913547526e8c8c2b5ab5b53b87'}}
def contract(s):
 ed=json.loads((P/"SOURCE-SAFE.json").read_text())
 assert s["experiment"]=="E011EE" and s["status"]==STATUS and s["scenarios"]==256 and s["next_experiment"]=="E011EF"
 for k in FALSE:assert s[k] is False,k
 for k in TRUE:assert s[k] is True,k
 assert s["new_camera_starts"]==s["new_reboots"]==0 and s["lowIO_owned_cold_initial_value_authority"]==INITIAL and s["lowIO_owned_provider_authority"]==PROVIDERS
 for k in ("runtime_initial_value_model_authority","initializer_owned_cold_initial_value_authority","initializer_owned_provider_authority"):assert s[k]==ed[k]
 assert s["source_pins"]==dict(ed["source_pins"],**EXTRA) and len(s["source_pins"])==48 and s["image_sha256"]==ed["image_sha256"]
 rows=s["details"];assert len(rows)==256 and [r["ED"] for r in rows]==ed["details"]
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 wanted=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 assert {tuple(r["ED"]["EC"]["EB"]["EA"]["DZ"]["DY"]["DX"]["DW"]["DV"]["DU"]["DT"]["DS"][k] for k in axes) for r in rows}==wanted
 for row in rows:
  a=row["added"];assert all(a[k]==v for k,v in PER.items()) and all(a[k] is True for k in BOOL) and all(a[k] is False for k in ROW_FALSE) and all(a[k]==v for k,v in EXPECTED.items())
 assert s["added_totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(r["added"][k] for r in rows) for k in PER}
 assert s["inherited_ED_totals"]==ed["added_totals"]
 for k in ("EC","EB","EA","DZ","DY","DX","DW","DV","DU","DT","DS"):assert s["inherited_"+k+"_totals"]==ed["inherited_"+k+"_totals"]
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s);result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="a448a50e2df4df36db3befb2ba74ba9fe34c57b1" and result["qualification_exit_code"]==0
 assert result["added_original_instruction_visits"]==738304 and result["combined_original_instruction_visits"]==1989120
 assert result["camera_chain_original_instruction_visits"]==1237760 and result["aggregate_spans_isolated_contexts"] is True and len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011EE" and f["next_experiment"]==n["experiment"]=="E011EF"
 for k in TRUE:assert f[k] is True
 for k in FALSE:
  if k in f:assert f[k] is False
 assert n["resume_context"]=="isolated_lowIO_initializer" and n["resume_source_RVA"]=="0xcc0948" and n["next_dependency_RVA"]=="0x16a2e90" and n["next_dependency_bytes"]==4
 assert n["next_dependency_read_and_continuation_qualified"] is False and n["current_SP_relative_lowIO_entry"]==-96
 assert n["lowIO_parent_callee_RVA"]=="0xcc08e8" and n["lowIO_return_is_owned_fixture"] is True and n["lowIO_initializer_isolated_from_other_contexts"] is True
 assert n["lowIO_owned_cold_initial_value_authority"]==INITIAL and n["lowIO_owned_provider_authority"]==PROVIDERS
 assert n["lowIO_owned_block_heap_offset"]==0x26000 and n["lowIO_block_heap_offset_adds_stack_bias"] is True and n["lowIO_block_bytes"]==4608
 assert n["lowIO_block_records"]==n["lowIO_ready_owned_resources"]==64 and n["lowIO_record_bytes"]==72 and n["lowIO_lock_owned_model_held"] is True
 assert n["original_lowIO_initializer_return_qualified"] is False and n["all_initializer_and_camera_states_join_qualified"] is False and n["stream_initializer_and_camera_state_join_qualified"] is False
 assert n["stream_initializer_resume_source_RVA"]=="0xcb3338" and n["stream_initializer_next_dependency_RVA"]=="0x16a2a90" and n["current_SP_relative_initializer_entry"]==-80
 assert n["camera_resume_source_RVA"]=="0xcc6120" and n["camera_current_SP_relative_outer_entry"]==-1648
 assert n["camera_parent_callee_RVA"]=="0x600368" and n["camera_outer_pending_return_RVA"]=="0x5f8ea8" and n["camera_stream_lock_owned_model_held"] is True
 assert n["camera_next_dependency_RVA"]=="0x16a2a58" and n["initializer_parent_callee_RVA"]=="0xcb3260" and n["initializer_return_is_owned_fixture"] is True
 ed=json.loads((P/"SOURCE-SAFE.json").read_text());assert n["initializer_owned_cold_initial_value_authority"]==ed["initializer_owned_cold_initial_value_authority"] and n["initializer_owned_provider_authority"]==ed["initializer_owned_provider_authority"]
 assert n["actual_loader_CRT_startup_caller_qualified"] is False and n["initializer_owned_table_slots"]==512 and n["initializer_published_standard_stream_slots"]==1 and n["initializer_remaining_zero_table_bytes"]==4088
 assert n["camera_current_active_stream_callee_RVAs"]==["0xced2f0","0xced0d8","0xcc6078","0xcc6108"] and n["camera_pending_stream_return_RVAs"]==["0x600454","0xced330","0xced150","0xcc60a0"]
 assert n["formatted_output_length"]==37 and n["destination_remaining_zero_bytes"]==603 and n["nine_live_allocation_bytes"]==[24,128,256,48,48,18832,16,64,8192]
 count=0
 if "--selfcheck" in sys.argv:
  mutations=[]
  def put(path,value):
   bad=copy.deepcopy(s);at=bad
   for k in path[:-1]:at=at[k]
   at[path[-1]]=value;mutations.append(bad)
  for k in FALSE:put([k],True)
  for k in TRUE:put([k],False)
  for k,v in (("scenarios",255),("new_camera_starts",1),("new_reboots",1)):put([k],v)
  for k,v in PER.items():put(["details",0,"added",k],v+1)
  for k in BOOL:put(["details",0,"added",k],False)
  for k in ROW_FALSE:put(["details",0,"added",k],True)
  for k,v in EXPECTED.items():put(["details",0,"added",k],v+1 if isinstance(v,int) else "unsupported")
  put(["lowIO_owned_cold_initial_value_authority",0,"accepted_owned_initial_value"],1)
  put(["lowIO_owned_cold_initial_value_authority",0,"native_runtime_selection_qualified"],True)
  put(["lowIO_owned_provider_authority","allocation_bytes"],4600)
  put(["lowIO_owned_provider_authority","resource_success_return_is_owned_model"],False)
  put(["lowIO_owned_provider_authority","native_allocator_implementation_qualified"],True)
  put(["source_pins","0xcc05b8","body_bytes"],208)
  put(["added_totals","original_instruction_visits"],738305)
  put(["details",0,"ED","EC","EB","EA","DZ","DY","DX","DW","DV","DU","DT","DS","allocation_poison"],0)
  for bad in mutations:
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported native evidence or state join admitted")
 print(json.dumps({"status":"PASS_E011EE_REVIEW","scenarios":256,"added_original_visits":738304,"combined_original_visits":1989120,"camera_chain_original_visits":1237760,
 "aggregate_spans_isolated_contexts":True,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
