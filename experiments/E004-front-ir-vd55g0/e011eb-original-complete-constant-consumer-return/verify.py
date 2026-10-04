#!/usr/bin/env python3
"""Review complete selected formatter return, exact output and enclosing scope."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2];P=R/"experiments/E004-front-ir-vd55g0/e011ea-original-first-argument-length-copy"
STATUS="PASS_BOUNDED_ORIGINAL_COMPLETE_CONSTANT_CONSUMER_RETURN"
FALSE=("source_result_fixture_used","native_rear_runtime_allowed","full_outer_callee_return_qualified","full_factory_or_first_helper_return_qualified",
"native_runtime_scalar_and_pointer_selection_qualified","alternate_nonzero_runtime_flag_paths_qualified","pointed_locale_tables_qualified",
"cookie_leaf_has_SP_preserving_ABI","stack_growth_guard_page_OS_qualified","parent_after_consumer_continuation_qualified",
"new_kernel_build","production_code_changed","private_raw_material_exported")
TRUE=("full_constant_consumer_return_qualified","all_three_argument_length_copy_and_termination_qualified","cold_runtime_context_cleanup_qualified")
PER={"original_instruction_visits":780,"exact_source_store_chunks":119,"independent_formatter_store_contracts":119,"rejected_owned_requests":867,
"exact_immutable_data_reads":31,"original_callee_ABI_returns_exact":16,"inherited_consumer_ABI_returns_exact":7,
"cookie_push_convention_returns_exact":2,"cookie_pop_convention_returns_exact":3,"exact_original_callee_entries":16,"owned_allocation_calls":0,"owned_OS_API_calls":0}
BOOL=("all_three_argument_bytes_and_terminators_exact","seven_inherited_consumer_frames_returned","cold_runtime_context_cleanup_qualified",
"unsigned_write_observer_preserves_exact_words","nine_live_allocations_retained","whole_original_entry_to_frontier_memory_and_permissions_exact",
"outer_and_nested_registry_locks_held","CRT_and_SRW_released")
EXPECTED={"remaining_argument_lengths":[1,24],"formatted_output_length":37,"destination_remaining_zero_bytes":603,"retained_active_consumer_frames":0,
"stop_before_RVA":"0x600440","current_SP_relative_outer_entry":-1456,"variadic_cursor_relative_outer_entry":-1472,
"output_cursor_relative_outer_entry":-1355,"completed_consumer_result":37,"outer_callee_return_not_reached_RVA":"0x5f8ea8"}
AUTH=[{'RVA': '0x10f03b0', 'bytes': 16, 'literal_RVA': '0x10f03b0', 'literal_bytes_including_NUL': 2, 'sha256': 'dad2ac2c3a4b7d322405d01acbb713a7042ed906bb4ec81c01ccd4021e838901', 'literal_sha256': '1472d0645f552820b5472b91341c2d9a118c8a96f4a72758d6aeeb14c10a1107', 'file_backed': True, 'section_nonwritable': True, 'terminator_at_last_literal_byte': True, 'original_literal_contents_exported': False, 'literal_offset_in_window': 0}, {'RVA': '0x13f1f20', 'bytes': 48, 'literal_RVA': '0x13f1f28', 'literal_bytes_including_NUL': 25, 'sha256': '973753c7f15d0cf4a464c323cee1d3a83724994a71bdffc9813b5f1b8e2a65c3', 'literal_sha256': 'f6576fcf7a6d985d27efdd1f30e911cdfbe9d1e64a17a6e07a19d078789a2e28', 'file_backed': True, 'section_nonwritable': True, 'terminator_at_last_literal_byte': True, 'original_literal_contents_exported': False, 'literal_offset_in_window': 8}]
CELLS=[{'RVA': '0xf8b230', 'bytes': 1, 'sha256': '4bf5122f344554c53bde2ebb8cd2b7e3d1600ad631c385a5d7cce23c7785459a', 'file_backed': True, 'section_nonwritable': True, 'sparse_cell_authority_only': True}]
EXTRA={'0xca8658': {'body_bytes': 304, 'ranges': [['0xca8658', '0xca8787']], 'sha256': '81b50e4947531268083b5f3b4115ddff3323d0fc37e4f2672d694f3d6f087652'}}
def contract(s):
 ea=json.loads((P/"SOURCE-SAFE.json").read_text())
 assert s["experiment"]=="E011EB" and s["status"]==STATUS and s["scenarios"]==256 and s["next_experiment"]=="E011EC"
 for k in FALSE:assert s[k] is False,k
 for k in TRUE:assert s[k] is True,k
 assert s["new_camera_starts"]==s["new_reboots"]==0 and s["remaining_argument_data_authority"]==AUTH and s["new_sparse_cell_authority"]==CELLS
 assert s["runtime_initial_value_model_authority"]==ea["runtime_initial_value_model_authority"]
 assert s["source_pins"]==dict(ea["source_pins"],**EXTRA) and len(s["source_pins"])==40 and s["image_sha256"]==ea["image_sha256"]
 rows=s["details"];assert len(rows)==256 and [r["EA"] for r in rows]==ea["details"]
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 wanted=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 assert {tuple(r["EA"]["DZ"]["DY"]["DX"]["DW"]["DV"]["DU"]["DT"]["DS"][k] for k in axes) for r in rows}==wanted
 for row in rows:
  a=row["added"];assert all(a[k]==v for k,v in PER.items()) and all(a[k] is True for k in BOOL) and all(a[k]==v for k,v in EXPECTED.items())
 assert s["added_totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(row["added"][k] for row in rows) for k in PER}
 assert s["inherited_EA_totals"]==ea["added_totals"]
 for k in ("DZ","DY","DX","DW","DV","DU","DT","DS"):assert s["inherited_"+k+"_totals"]==ea["inherited_"+k+"_totals"]
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s);result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="cbf8b66ce23219a99892a934923c9aa0a1799553" and result["qualification_exit_code"]==0
 assert result["added_original_instruction_visits"]==199680 and result["combined_original_instruction_visits"]==1223936 and len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011EB" and f["next_experiment"]==n["experiment"]=="E011EC"
 for k in TRUE:assert f[k] is True
 assert f["full_outer_callee_return_qualified"] is False and f["native_rear_runtime_allowed"] is False
 assert n["resume_source_RVA"]=="0x600440" and n["parent_callee_RVA"]=="0x600368" and n["outer_pending_return_RVA"]=="0x5f8ea8"
 assert n["parent_after_consumer_continuation_qualified"] is False and n["remaining_argument_data_authority"]==AUTH and n["new_sparse_cell_authority"]==CELLS
 assert n["current_active_consumer_RVAs"]==n["pending_consumer_return_RVAs"]==[]
 assert n["completed_consumer_RVAs"]==["0x7ac38","0x7aca0","0x6bdd0","0x6bd48","0xcad868","0xca6280","0xca94e8"]
 assert n["completed_consumer_return_RVAs"]==["0x600440","0x7ac7c","0x7acdc","0x6be0c","0x6bd94","0xcad940","0xca634c"]
 assert n["current_SP_relative_outer_entry"]==-1456 and n["completed_consumer_result"]==37
 assert n["formatted_output_length"]==37 and n["destination_remaining_zero_bytes"]==603 and n["stack_receiver_640_bytes_still_zero"] is False
 assert n["nine_live_allocation_bytes"]==[24,128,256,48,48,18832,16,64,8192] and n["cookie_leaf_has_SP_preserving_ABI"] is False
 assert "retained_cookie_slot_relative_outer_entry_SP" not in n and "retained_prior_cookie_slot_relative_outer_entry_SP" not in n
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
  for k,v in EXPECTED.items():put(["details",0,"added",k],v+1 if isinstance(v,int) else "unsupported")
  put(["remaining_argument_data_authority",1,"RVA"],"0x13f1f28")
  put(["remaining_argument_data_authority",1,"bytes"],32)
  put(["remaining_argument_data_authority",1,"literal_offset_in_window"],0)
  put(["remaining_argument_data_authority",0,"original_literal_contents_exported"],True)
  put(["new_sparse_cell_authority",0,"sparse_cell_authority_only"],False)
  put(["source_pins","0xca8658","body_bytes"],308)
  put(["added_totals","original_instruction_visits"],199681)
  put(["details",0,"EA","DZ","DY","DX","DW","DV","DU","DT","DS","allocation_poison"],0)
  for bad in mutations:
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence or scope admitted")
 print(json.dumps({"status":"PASS_E011EB_REVIEW","scenarios":256,"added_original_visits":199680,"combined_original_visits":1223936,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
