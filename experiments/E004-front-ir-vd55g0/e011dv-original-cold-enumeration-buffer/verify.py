#!/usr/bin/env python3
"""Review original cold enumeration buffer, zero-fill model and retained parent scope."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
STATUS="PASS_BOUNDED_ACTUAL_COLD_ENUMERATION_BUFFER_PUBLICATION"
FALSE=("source_result_fixture_used","native_rear_runtime_allowed","full_factory_or_first_helper_return_qualified","full_descriptor_registry_publication_qualified",
 "native_OS_CRT_allocator_construction_and_failure_paths_qualified","native_runtime_scalar_selection_qualified","alternate_nonzero_scalar_branch_qualified",
 "next_callee_execution_qualified","stack_growth_guard_page_OS_qualified","new_kernel_build","production_code_changed","private_raw_material_exported")
TRUE=("actual_cold_scalar_branch_qualified_under_loader_zero_model","original_allocation_clear_and_buffer_publication_qualified","prior_callback_table_epochs_and_five_allocations_retained")
ZERO={"RVA":"0x1731598","bytes":4,"section_virtual_start_RVA":"0x1607000","section_virtual_bytes":5429539,"section_raw_bytes":635904,
 "section_flags":"0xc0000040","outside_file_backed_span":True,"virtual_loader_zero_fill_model":True}
PER={"original_instruction_visits":928,"clear_instruction_visits":912,"clear_store_chunks":2354,"exact_source_store_chunks":2356,"nonstack_field_store_chunks":2,
 "rejected_owned_requests":43,"original_clear_returns_ABI_exact":1,"owned_allocation_calls":1,"owned_allocation_bytes":18832,"owned_OS_API_calls":0,"loader_zero_scalar_reads":1}
def contract(s):
 assert s["experiment"]=="E011DV" and s["status"]==STATUS and s["scenarios"]==256 and s["next_experiment"]=="E011DW"
 for k in FALSE:assert s[k] is False,k
 for k in TRUE:assert s[k] is True,k
 assert s["new_camera_starts"]==s["new_reboots"]==0 and s["scalar_zero_fill_authority"]==ZERO
 du=json.loads((R/"experiments/E004-front-ir-vd55g0/e011du-original-existing-table-registration-publication/SOURCE-SAFE.json").read_text())
 assert s["source_pins"]==du["source_pins"] and len(s["source_pins"])==23 and s["image_sha256"]==du["image_sha256"]
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 expected=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 rows=s["details"];assert len(rows)==256 and {tuple(r["DU"]["DT"]["DS"][k] for k in axes) for r in rows}==expected
 prior={tuple(r["DT"]["DS"][k] for k in axes):r for r in du["details"]};assert len(prior)==256
 for r in rows:
  d=r["DU"];a=r["added"];assert d==prior[tuple(d["DT"]["DS"][k] for k in axes)]
  assert all(a[k]==v for k,v in PER.items())
  for k in ("six_distinct_live_allocations_retained","whole_entry_to_frontier_memory_and_permissions_exact","ancestor_callbacks_epochs_nodes_redzones_and_container_retained",
   "factory_guard_in_progress","outer_and_nested_registry_locks_held","CRT_and_SRW_released"):assert a[k] is True
  assert a["clear_literal_data_reads"]==[["0xf5e644",1]] and a["original_clear_return_RVA"]=="0x5f8e54"
  assert a["published_pointer_RVA"]=="0x169fdf0" and a["published_reference_count_RVA"]=="0x169fde8" and a["published_reference_count"]==1 and a["published_buffer_bytes_zero"]==18832
  assert a["stop_before_RVA"]=="0x5f8ea4" and a["next_target_RVA"]=="0x600368" and a["next_actual_return_RVA"]=="0x5f8ea8"
 assert s["added_totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(r["added"][k] for r in rows) for k in PER}
 assert s["inherited_DU_totals"]==du["added_totals"] and s["inherited_DT_totals"]==du["inherited_DT_totals"] and s["inherited_DS_totals"]==du["inherited_DS_totals"]
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s)
 result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="0d8a0f93f12cfa2840c8613058a15f5cccfe90ea" and result["qualification_exit_code"]==0 and result["native_rear_runtime_allowed"] is False
 assert result["added_original_instruction_visits"]==237568 and result["combined_original_instruction_visits"]==743680 and len(result["source_locks"])==12
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text());b=json.loads((H/"BOUNDARY-AUTHORITY-SAFE.json").read_text())
 assert f["experiment"]=="E011DV" and f["next_experiment"]==n["experiment"]=="E011DW"
 assert f["actual_cold_scalar_branch_qualified_under_loader_zero_model"] is True and f["original_allocation_clear_and_buffer_publication_qualified"] is True
 assert f["full_factory_or_first_helper_return_qualified"] is False and f["latest_source_RS_query_checkpoint"]=="E011DM"
 assert n["resume_source_call_RVA"]=="0x5f8ea4" and n["target_RVA"]=="0x600368" and n["actual_caller_return_RVA"]=="0x5f8ea8"
 assert n["encoded_exit_table_used_entries"]==2 and n["encoded_exit_table_capacity"]==32 and n["published_reference_count"]==1 and n["published_buffer_bytes"]==18832
 assert n["published_enumeration_global_TLS_epoch"]=="0x80000042" and n["retained_helper_epoch"]=="0x80000041" and n["factory_guard_in_progress"] is True
 assert b["experiment"]=="E011DV" and b["status"]=="PASS_PRIVATE_STATIC_BOUNDARY_DERIVATION" and b["image_sha256"]==s["image_sha256"]
 assert b["next_function_executed_or_qualified"] is False and b["initial_pointer_and_refcount_file_values_zero"] is True
 assert b["original_calls"]==[{"source_call_RVA":"0x5f8e34","target_RVA":"0xcae740","actual_return_RVA":"0x5f8e38"},
  {"source_call_RVA":"0x5f8e50","target_RVA":"0xf5e600","actual_return_RVA":"0x5f8e54"},{"source_call_RVA":"0x5f8ea4","target_RVA":"0x600368","actual_return_RVA":"0x5f8ea8"}]
 assert b["next_function_metadata"]==n["next_function_metadata"]=={"entry_RVA":"0x600368","body_bytes":1120,"ranges":[["0x600368","0x6007c7"]],"sha256":"18d45d94302157df5a5ce15d232191f9fca4a63bc1c910af535a9dc24b4b7e43"}
 count=0
 if "--selfcheck" in sys.argv:
  muts=[(k,True) for k in FALSE]+[(k,False) for k in TRUE]+[("scenarios",255),("new_camera_starts",1),("new_reboots",1)]
  for label,key,value in (("ABI","original_clear_returns_ABI_exact",0),("allocation","owned_allocation_bytes",18816),("clear","clear_store_chunks",2353),
   ("refcount","published_reference_count",0),("buffer","published_buffer_bytes_zero",18816),("pointer","published_pointer_RVA","0x169fe00"),
   ("lock","outer_and_nested_registry_locks_held",False),("factory","factory_guard_in_progress",False),("frontier","stop_before_RVA","0x5f8ea8"),("memory","whole_entry_to_frontier_memory_and_permissions_exact",False),
   ("literal","clear_literal_data_reads",[]),("return","original_clear_return_RVA","0x5be9fc"),("leases","six_distinct_live_allocations_retained",False)):
   bad=copy.deepcopy(s);bad["details"][0]["added"][key]=value;muts.append(("__"+label,bad))
  bad=copy.deepcopy(s);bad["details"][0]["DU"]["DT"]["DS"]["initial_global_epoch"]=41;muts.append(("__parent",bad))
  bad=copy.deepcopy(s);bad["details"][0]["DU"]["DT"]["DS"]["allocation_poison"]=0;muts.append(("__matrix",bad))
  bad=copy.deepcopy(s);bad["added_totals"]["original_instruction_visits"]+=1;muts.append(("__totals",bad))
  bad=copy.deepcopy(s);bad["scalar_zero_fill_authority"]["virtual_loader_zero_fill_model"]=False;muts.append(("__loader",bad))
  bad=copy.deepcopy(s);bad["scalar_zero_fill_authority"]["section_raw_bytes"]+=4;muts.append(("__section",bad))
  for key,value in muts:
   bad=value if key.startswith("__") else copy.deepcopy(s)
   if not key.startswith("__"):bad[key]=value
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence/scope admitted: "+key)
 print(json.dumps({"status":"PASS_E011DV_REVIEW","scenarios":256,"added_original_visits":237568,"combined_original_visits":743680,"source_locks":12,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
