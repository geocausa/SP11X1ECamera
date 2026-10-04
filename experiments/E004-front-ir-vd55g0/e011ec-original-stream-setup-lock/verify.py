#!/usr/bin/env python3
"""Review bounded stream setup and distinguish owned lock readiness from native state."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2];P=R/"experiments/E004-front-ir-vd55g0/e011eb-original-complete-constant-consumer-return"
STATUS="PASS_BOUNDED_ORIGINAL_STREAM_SETUP_LOCK"
FALSE=("source_result_fixture_used","native_rear_runtime_allowed","full_outer_callee_return_qualified","full_factory_or_first_helper_return_qualified",
 "native_CRT_resource_initialization_qualified","native_runtime_scalar_and_pointer_selection_qualified","alternate_nonzero_runtime_flag_paths_qualified","pointed_locale_tables_qualified",
 "cookie_leaf_has_SP_preserving_ABI","stack_growth_guard_page_OS_qualified","stream_runtime_pointer_read_qualified","file_open_or_contents_qualified",
 "new_kernel_build","production_code_changed","private_raw_material_exported")
TRUE=("original_stream_wrapper_setup_qualified","owned_stream_lock_acquisition_qualified","bounded_parent_after_consumer_continuation_qualified",
 "full_constant_consumer_return_qualified","all_three_argument_length_copy_and_termination_qualified","cold_runtime_context_cleanup_qualified")
PER={"original_instruction_visits":54,"exact_source_store_chunks":18,"independent_stream_setup_store_contracts":18,"rejected_owned_requests":147,
 "exact_immutable_mode_reads":1,"exact_inherited_loader_binding_reads":1,"original_lock_wrapper_ABI_returns_exact":1,"exact_original_callee_entries":5,"owned_allocation_calls":0,"owned_OS_API_calls":1}
BOOL=("completed_output_retained_exact","stream_lock_owned_model_held","nine_live_allocations_retained","whole_original_entry_to_frontier_memory_and_permissions_exact",
 "outer_and_nested_registry_locks_held","inherited_publication_CRT_and_SRW_released")
ROW_FALSE=("native_CRT_resource_initialization_qualified","stream_runtime_pointer_read_qualified","file_open_or_contents_qualified")
EXPECTED={"formatted_output_length":37,"destination_remaining_zero_bytes":603,"active_stream_callee_frames":4,"stop_before_RVA":"0xcc6120",
 "next_dependency_RVA":"0x16a2a58","next_dependency_bytes":8,"current_SP_relative_outer_entry":-1648,"outer_callee_return_not_reached_RVA":"0x5f8ea8"}
MODE={'RVA': '0x1363d40', 'bytes_including_NUL': 2, 'sha256': '96229c0a1dcb79d7d50913f882e3144961b5616140ded9ab844bd685e08e3a30', 'file_backed': True, 'section_nonwritable': True, 'terminator_at_last_byte': True, 'original_literal_contents_exported': False}
LOCK={'owned_resource_RVA': '0x16a3000', 'modeled_ready': True, 'initial_logical_lock_held': False, 'inherited_import_cell_RVA': '0xf7e0b8', 'OS_void_return_is_owned_clobber_model': True, 'native_CRT_resource_initialization_qualified': False}
EXTRA={'0xced2f0': {'body_bytes': 104, 'ranges': [['0xced2f0', '0xced357']], 'sha256': '2f01c5c987420ed8a66fe9b598884e0769d591d030222e364df1936b0141db53'}, '0xced0d8': {'body_bytes': 196, 'ranges': [['0xced0d8', '0xced19b']], 'sha256': '3e7921b298228ceba63639c8ad5143816fa88e92741b9bf36543dcaaf5f176b2'}, '0xcc6078': {'body_bytes': 100, 'ranges': [['0xcc6078', '0xcc60db']], 'sha256': '7eca050b7b7a4284ed60cdb2a8d067cb2d4ecd964bbd9da560e5af2a15ff0fe8'}, '0xcc6108': {'body_bytes': 248, 'ranges': [['0xcc6108', '0xcc61ff']], 'sha256': '92392516a581bfd36da290b122fe121ec3da6715a050a19cb286dd14d7c573ff'}}
def contract(s):
 eb=json.loads((P/"SOURCE-SAFE.json").read_text())
 assert s["experiment"]=="E011EC" and s["status"]==STATUS and s["scenarios"]==256 and s["next_experiment"]=="E011ED"
 for k in FALSE:assert s[k] is False,k
 for k in TRUE:assert s[k] is True,k
 assert s["new_camera_starts"]==s["new_reboots"]==0 and s["mode_data_authority"]==MODE and s["stream_lock_owned_model_authority"]==LOCK
 assert s["runtime_initial_value_model_authority"]==eb["runtime_initial_value_model_authority"]
 assert s["source_pins"]==dict(eb["source_pins"],**EXTRA) and len(s["source_pins"])==44 and s["image_sha256"]==eb["image_sha256"]
 rows=s["details"];assert len(rows)==256 and [r["EB"] for r in rows]==eb["details"]
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 wanted=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 assert {tuple(r["EB"]["EA"]["DZ"]["DY"]["DX"]["DW"]["DV"]["DU"]["DT"]["DS"][k] for k in axes) for r in rows}==wanted
 for row in rows:
  a=row["added"];assert all(a[k]==v for k,v in PER.items()) and all(a[k] is True for k in BOOL) and all(a[k] is False for k in ROW_FALSE) and all(a[k]==v for k,v in EXPECTED.items())
 assert s["added_totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(r["added"][k] for r in rows) for k in PER}
 assert s["inherited_EB_totals"]==eb["added_totals"]
 for k in ("EA","DZ","DY","DX","DW","DV","DU","DT","DS"):assert s["inherited_"+k+"_totals"]==eb["inherited_"+k+"_totals"]
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s);result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="7983e1f771eb7a807aa1d5bf3b187bf431a2b71f" and result["qualification_exit_code"]==0
 assert result["added_original_instruction_visits"]==13824 and result["combined_original_instruction_visits"]==1237760 and len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011EC" and f["next_experiment"]==n["experiment"]=="E011ED"
 for k in TRUE:assert f[k] is True
 for k in ("native_CRT_resource_initialization_qualified","stream_runtime_pointer_read_qualified","file_open_or_contents_qualified","full_outer_callee_return_qualified","native_rear_runtime_allowed"):assert f[k] is False
 assert n["resume_source_RVA"]=="0xcc6120" and n["next_dependency_RVA"]=="0x16a2a58" and n["next_dependency_bytes"]==8
 assert n["next_dependency_read_and_continuation_qualified"] is False and n["current_SP_relative_outer_entry"]==-1648
 assert n["mode_data_authority"]==MODE and n["stream_lock_owned_model_authority"]==LOCK and n["stream_lock_owned_model_held"] is True
 assert n["current_active_stream_callee_RVAs"]==["0xced2f0","0xced0d8","0xcc6078","0xcc6108"]
 assert n["pending_stream_return_RVAs"]==["0x600454","0xced330","0xced150","0xcc60a0"]
 assert n["current_active_consumer_RVAs"]==n["pending_consumer_return_RVAs"]==[]
 assert n["formatted_output_length"]==37 and n["destination_remaining_zero_bytes"]==603 and n["nine_live_allocation_bytes"]==[24,128,256,48,48,18832,16,64,8192]
 assert n["outer_pending_return_RVA"]=="0x5f8ea8" and n["stream_runtime_pointer_read_qualified"] is False and n["file_open_or_contents_qualified"] is False
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
  put(["mode_data_authority","original_literal_contents_exported"],True)
  put(["mode_data_authority","bytes_including_NUL"],3)
  put(["stream_lock_owned_model_authority","native_CRT_resource_initialization_qualified"],True)
  put(["stream_lock_owned_model_authority","owned_resource_RVA"],"0x16a2960")
  put(["source_pins","0xcc6108","body_bytes"],252)
  put(["added_totals","owned_OS_API_calls"],0)
  put(["details",0,"EB","EA","DZ","DY","DX","DW","DV","DU","DT","DS","OS_void_X0"],1)
  for bad in mutations:
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence or scope admitted")
 print(json.dumps({"status":"PASS_E011EC_REVIEW","scenarios":256,"added_original_visits":13824,"combined_original_visits":1237760,"source_locks":11,
 "scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
