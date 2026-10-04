#!/usr/bin/env python3
"""Review isolated initializer publication and forbid an unproved camera-state join."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2];P=R/"experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock"
STATUS="PASS_BOUNDED_ORIGINAL_ISOLATED_STREAM_INITIALIZER_PUBLICATION"
FALSE=("original_stream_initializer_return_qualified","stream_initializer_and_camera_state_join_qualified","native_allocator_implementation_qualified",
 "source_result_fixture_used","native_rear_runtime_allowed","native_CRT_resource_initialization_qualified","native_runtime_scalar_and_pointer_selection_qualified",
 "pointed_standard_stream_contents_qualified","stream_runtime_pointer_read_qualified","file_open_or_contents_qualified","full_outer_callee_return_qualified",
 "full_factory_or_first_helper_return_qualified","new_kernel_build","production_code_changed","private_raw_material_exported")
TRUE=("original_stream_initializer_publication_prefix_qualified","initializer_isolated_from_camera_parent","camera_caller_memory_permissions_and_frontier_unchanged")
PER={"original_instruction_visits":51,"exact_source_store_chunks":16,"independent_initializer_store_contracts":16,"rejected_owned_requests":141,
 "exact_dependency_reads":4,"original_nested_ABI_returns_exact":2,"exact_original_nested_callee_entries":2,"owned_allocation_calls":1,"owned_zeroed_allocation_bytes":4096,"owned_OS_API_calls":1}
BOOL=("first_resource_owned_model_ready","isolated_initializer_memory_and_permissions_exact","redzones_exact",
 "camera_caller_memory_permissions_and_frontier_unchanged","initializer_isolated_from_camera_parent")
ROW_FALSE=("original_initializer_return_qualified","stream_initializer_and_camera_state_join_qualified","native_CRT_resource_initialization_qualified","pointed_standard_stream_contents_qualified")
EXPECTED={"published_table_slots":512,"published_first_standard_stream_slots":1,"remaining_table_zero_bytes":4088,
 "stop_before_RVA":"0xcb3338","next_dependency_RVA":"0x16a2a90","next_dependency_bytes":8,"current_SP_relative_initializer_entry":-80}
INITIAL=[{'RVA': '0x16a2a50', 'bytes': 4, 'section_writable': True, 'virtual_zero_fill': True, 'file_backed': False, 'accepted_owned_initial_value': 0, 'native_runtime_selection_qualified': False}, {'RVA': '0x16a2a58', 'bytes': 8, 'section_writable': True, 'virtual_zero_fill': True, 'file_backed': False, 'accepted_owned_initial_value': 0, 'native_runtime_selection_qualified': False}]
PROVIDERS={'allocator_request_RVA': '0xcb75e0', 'allocator_return_RVA': '0xcb32ac', 'count': 512, 'element_bytes': 8, 'allocation_bytes': 4096, 'zeroed_allocation_provider_is_owned_model': True, 'native_allocator_implementation_qualified': False, 'resource_initializer_wrapper_RVA': '0xcba4b0', 'resource_initializer_return_RVA': '0xcb3328', 'import_cell_RVA': '0xf7e230', 'first_standard_stream_pointer_RVA': '0x1607060', 'first_resource_RVA': '0x1607090', 'spin_count': 4000, 'flags': 0, 'resource_success_return_is_owned_model': True, 'native_CRT_resource_initialization_qualified': False, 'pointed_standard_stream_contents_qualified': False}
EXTRA={'0xcb3260': {'body_bytes': 296, 'ranges': [['0xcb3260', '0xcb3387']], 'sha256': '7aa827ad2e4914dd30c14c91bb6e27fce3eb3c9863194934ebf524b164c6ab19'}, '0xcba4b0': {'body_bytes': 12, 'ranges': [['0xcba4b0', '0xcba4bb']], 'sha256': '737b4eb9b5e218a973a49f6712fbd440755a2cfd690d39721d3cdc2def43018d'}}
def contract(s):
 ec=json.loads((P/"SOURCE-SAFE.json").read_text())
 assert s["experiment"]=="E011ED" and s["status"]==STATUS and s["scenarios"]==256 and s["next_experiment"]=="E011EE"
 for k in FALSE:assert s[k] is False,k
 for k in TRUE:assert s[k] is True,k
 assert s["new_camera_starts"]==s["new_reboots"]==0 and s["initializer_owned_cold_initial_value_authority"]==INITIAL and s["initializer_owned_provider_authority"]==PROVIDERS
 assert s["runtime_initial_value_model_authority"]==ec["runtime_initial_value_model_authority"]
 assert s["source_pins"]==dict(ec["source_pins"],**EXTRA) and len(s["source_pins"])==46 and s["image_sha256"]==ec["image_sha256"]
 rows=s["details"];assert len(rows)==256 and [r["EC"] for r in rows]==ec["details"]
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 wanted=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 assert {tuple(r["EC"]["EB"]["EA"]["DZ"]["DY"]["DX"]["DW"]["DV"]["DU"]["DT"]["DS"][k] for k in axes) for r in rows}==wanted
 for row in rows:
  a=row["added"];assert all(a[k]==v for k,v in PER.items()) and all(a[k] is True for k in BOOL) and all(a[k] is False for k in ROW_FALSE) and all(a[k]==v for k,v in EXPECTED.items())
 assert s["added_totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(r["added"][k] for r in rows) for k in PER}
 assert s["inherited_EC_totals"]==ec["added_totals"]
 for k in ("EB","EA","DZ","DY","DX","DW","DV","DU","DT","DS"):assert s["inherited_"+k+"_totals"]==ec["inherited_"+k+"_totals"]
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s);result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="d2fdd2729b7c581fe57c6ab65d3a7481a2dea891" and result["qualification_exit_code"]==0
 assert result["added_original_instruction_visits"]==13056 and result["combined_original_instruction_visits"]==1250816
 assert result["camera_chain_original_instruction_visits"]==1237760 and result["aggregate_spans_isolated_contexts"] is True and len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011ED" and f["next_experiment"]==n["experiment"]=="E011EE"
 for k in TRUE:assert f[k] is True
 for k in ("original_stream_initializer_return_qualified","stream_initializer_and_camera_state_join_qualified","native_CRT_resource_initialization_qualified","stream_runtime_pointer_read_qualified","native_rear_runtime_allowed","actual_loader_CRT_startup_caller_qualified"):assert f[k] is False
 assert n["resume_context"]=="isolated_initializer" and n["resume_source_RVA"]=="0xcb3338" and n["next_dependency_RVA"]=="0x16a2a90" and n["next_dependency_bytes"]==8
 assert n["next_dependency_read_and_continuation_qualified"] is False and n["current_SP_relative_initializer_entry"]==-80
 assert n["camera_resume_source_RVA"]=="0xcc6120" and n["camera_current_SP_relative_outer_entry"]==-1648
 assert n["camera_parent_callee_RVA"]=="0x600368" and n["camera_outer_pending_return_RVA"]=="0x5f8ea8" and n["camera_stream_lock_owned_model_held"] is True
 assert n["camera_next_dependency_RVA"]=="0x16a2a58" and n["stream_initializer_and_camera_state_join_qualified"] is False
 assert n["initializer_parent_callee_RVA"]=="0xcb3260" and n["initializer_return_is_owned_fixture"] is True and n["actual_loader_CRT_startup_caller_qualified"] is False
 assert n["initializer_owned_cold_initial_value_authority"]==INITIAL and n["initializer_owned_provider_authority"]==PROVIDERS
 assert n["initializer_owned_table_slots"]==512 and n["initializer_published_standard_stream_slots"]==1 and n["initializer_remaining_zero_table_bytes"]==4088
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
  put(["initializer_owned_cold_initial_value_authority",0,"accepted_owned_initial_value"],512)
  put(["initializer_owned_cold_initial_value_authority",1,"native_runtime_selection_qualified"],True)
  put(["initializer_owned_provider_authority","allocation_bytes"],4088)
  put(["initializer_owned_provider_authority","resource_success_return_is_owned_model"],False)
  put(["initializer_owned_provider_authority","native_allocator_implementation_qualified"],True)
  put(["source_pins","0xcb3260","body_bytes"],300)
  put(["added_totals","original_instruction_visits"],13057)
  put(["details",0,"EC","EB","EA","DZ","DY","DX","DW","DV","DU","DT","DS","allocation_poison"],0)
  for bad in mutations:
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence or context join admitted")
 print(json.dumps({"status":"PASS_E011ED_REVIEW","scenarios":256,"added_original_visits":13056,"combined_original_visits":1250816,"camera_chain_original_visits":1237760,
 "aggregate_spans_isolated_contexts":True,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
