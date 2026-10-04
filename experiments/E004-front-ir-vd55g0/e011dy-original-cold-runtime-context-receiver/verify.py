#!/usr/bin/env python3
"""Review cold runtime models, original receiver effects and retained scope."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
STATUS="PASS_BOUNDED_ORIGINAL_COLD_RUNTIME_CONTEXT_AND_RECEIVER_SETUP"
FALSE=("source_result_fixture_used","native_rear_runtime_allowed","full_constant_consumer_return_qualified","full_outer_callee_return_qualified",
"full_factory_or_first_helper_return_qualified","native_runtime_scalar_and_pointer_selection_qualified","alternate_nonzero_runtime_flag_paths_qualified",
"pointed_locale_tables_or_format_strings_qualified","cookie_leaf_has_SP_preserving_ABI","stack_growth_guard_page_OS_qualified","next_original_consumer_qualified",
"new_kernel_build","production_code_changed","private_raw_material_exported")
PER={"original_instruction_visits":82,"exact_source_store_chunks":44,"independent_setup_store_contracts":44,"rejected_owned_requests":268,
"exact_runtime_dependency_reads":4,"cookie_frame_returns_convention_exact":1,"exact_nested_consumer_entries":2,"owned_allocation_calls":0,"owned_OS_API_calls":0}
EXTRA={
"0xcad868":{"body_bytes":352,"ranges":[["0xcad868","0xcad9c7"]],"sha256":"3bd3cec587501af57ce2c37f82c3834b4737d5f346181f65571a801b3dcde393"},
"0xca6280":{"body_bytes":384,"ranges":[["0xca6280","0xca63ff"]],"sha256":"80573b1c868f55f5acbd0a1a62ecd1fc390fff39aee2275e161a64ab85cc8a1e"}}
AUTH=[
{"RVA":"0x17a1150","bytes":8,"section_writable":True,"virtual_zero_fill":True,"file_backed":False,"accepted_owned_initial_value":0,"native_runtime_selection_qualified":False},
{"RVA":"0x16a2a84","bytes":4,"section_writable":True,"virtual_zero_fill":True,"file_backed":False,"accepted_owned_initial_value":0,"native_runtime_selection_qualified":False},
{"RVA":"0x16072d8","bytes":16,"section_writable":True,"virtual_zero_fill":False,"file_backed":True,
"file_initial_sha256":"507987659945beb7bcd11ae53dece55517a2979fc4e3ea4c9683bdceb5fd0f3f","initial_pointer_targets_RVA":["0x1607180","0x1607650"],"native_runtime_selection_qualified":False}]
def contract(s):
 assert s["experiment"]=="E011DY" and s["status"]==STATUS and s["scenarios"]==256 and s["next_experiment"]=="E011DZ"
 for k in FALSE:assert s[k] is False,k
 assert s["new_camera_starts"]==s["new_reboots"]==0 and s["runtime_initial_value_model_authority"]==AUTH
 dx=json.loads((R/"experiments/E004-front-ir-vd55g0/e011dx-original-constant-data-consumer-setup/SOURCE-SAFE.json").read_text())
 assert s["source_pins"]==dict(dx["source_pins"],**EXTRA) and len(s["source_pins"])==32 and s["image_sha256"]==dx["image_sha256"]
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 expected=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 rows=s["details"];assert len(rows)==256 and [r["DX"] for r in rows]==dx["details"]
 assert {tuple(r["DX"]["DW"]["DV"]["DU"]["DT"]["DS"][k] for k in axes) for r in rows}==expected
 for row in rows:
  a=row["added"];assert all(a[k]==v for k,v in PER.items())
  for k in ("runtime_context_and_nested_receiver_fields_constructed","nine_live_allocations_retained","stack_destination_640_bytes_still_zero",
   "whole_original_entry_to_frontier_memory_and_permissions_exact","outer_and_nested_registry_locks_held","CRT_and_SRW_released"):assert a[k] is True
  assert a["retained_active_consumer_frames"]==6 and a["stop_before_RVA"]=="0xca6348" and a["next_callee_RVA"]=="0xca94e8" and a["next_callee_return_RVA"]=="0xca634c"
  assert (a["next_receiver_relative_outer_entry_SP"],a["next_runtime_context_relative_outer_entry_SP"],a["current_SP_relative_outer_entry"])==(-3104,-1888,-3136)
  assert a["outer_callee_return_not_reached_RVA"]=="0x5f8ea8"
 assert s["added_totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(row["added"][k] for row in rows) for k in PER}
 assert s["inherited_DX_totals"]==dx["added_totals"]
 for k in ("DW","DV","DU","DT","DS"):assert s["inherited_"+k+"_totals"]==dx["inherited_"+k+"_totals"]
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s);result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="aa47c6defe3e5d13665a40d2fb13c7ce285779a9" and result["qualification_exit_code"]==0 and result["native_rear_runtime_allowed"] is False
 assert result["added_original_instruction_visits"]==20992 and result["combined_original_instruction_visits"]==935424 and len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011DY" and f["next_experiment"]==n["experiment"]=="E011DZ" and f["original_cold_runtime_context_receiver_setup_qualified"] is True
 assert f["native_runtime_scalar_and_pointer_selection_qualified"] is False and f["full_constant_consumer_return_qualified"] is False
 assert n["resume_source_RVA"]=="0xca6348" and n["next_callee_RVA"]=="0xca94e8" and n["next_callee_return_RVA"]=="0xca634c"
 assert n["next_callee_exact_metadata"]=={"entry_RVA":"0xca94e8","body_bytes":1028,"ranges":[["0xca94e8","0xca98eb"]],"sha256":"8e1aa3dcf0d019df157030034475dc1fe87defc61d765e4f5deecac6b56b150a"}
 assert n["runtime_initial_value_model_authority"]==AUTH and n["next_callee_execution_qualified"] is False
 assert n["current_active_consumer_RVAs"]==["0x7ac38","0x7aca0","0x6bdd0","0x6bd48","0xcad868","0xca6280"]
 assert n["current_SP_relative_outer_entry"]==-3136 and n["next_receiver_relative_outer_entry_SP"]==-3104 and n["next_runtime_context_relative_outer_entry_SP"]==-1888
 assert n["cookie_frame_leaf_return_relative_SP"]==-16 and n["cookie_leaf_has_SP_preserving_ABI"] is False
 assert n["stack_receiver_640_bytes_still_zero"] is True and n["published_buffer_bytes"]==18832 and n["nine_live_allocation_bytes"]==[24,128,256,48,48,18832,16,64,8192]
 count=0
 if "--selfcheck" in sys.argv:
  mutations=[]
  def put(path,value):
   bad=copy.deepcopy(s);at=bad
   for k in path[:-1]:at=at[k]
   at[path[-1]]=value;mutations.append(bad)
  for k in FALSE:put([k],True)
  for k,v in (("scenarios",255),("new_camera_starts",1),("new_reboots",1)):put([k],v)
  for k,v in PER.items():put(["details",0,"added",k],v+1)
  for k in ("runtime_context_and_nested_receiver_fields_constructed","nine_live_allocations_retained","stack_destination_640_bytes_still_zero",
   "whole_original_entry_to_frontier_memory_and_permissions_exact","outer_and_nested_registry_locks_held","CRT_and_SRW_released"):put(["details",0,"added",k],False)
  put(["details",0,"added","stop_before_RVA"],"0xca634c");put(["details",0,"added","retained_active_consumer_frames"],5)
  put(["runtime_initial_value_model_authority",0,"accepted_owned_initial_value"],1)
  put(["runtime_initial_value_model_authority",0,"file_backed"],True)
  put(["runtime_initial_value_model_authority",2,"native_runtime_selection_qualified"],True)
  put(["source_pins","0xca6280","body_bytes"],388)
  put(["added_totals","original_instruction_visits"],20993)
  put(["details",0,"DX","DW","DV","DU","DT","DS","allocation_poison"],0)
  for bad in mutations:
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence or scope admitted")
 print(json.dumps({"status":"PASS_E011DY_REVIEW","scenarios":256,"added_original_visits":20992,"combined_original_visits":935424,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
