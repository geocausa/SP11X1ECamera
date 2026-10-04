#!/usr/bin/env python3
"""Review cached-object/nested-lock/large-clear evidence without widening runtime claims."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
STATUS="PASS_BOUNDED_ORIGINAL_CACHED_OBJECT_NESTED_LOCK_AND_BUFFER_CLEAR"
FALSE=("cache_or_nested_lock_or_clear_result_fixture_used","full_inline_object_initialization_qualified","factory_callee_executed_in_this_parent","first_helper_complete_return_qualified","full_metadata_descriptor_registry_publication_qualified","selected_runtime_profile_qualified","populated_RS_lifetime_qualified","deterministic_bootstrap_closed","independent_enabled_output_retirement_proven","native_rear_runtime_allowed","native_OS_CRT_allocator_construction_or_failure_paths_qualified","new_kernel_build","production_code_changed","private_raw_material_exported")
PER={"original_instruction_visits":1302,"added_source_instruction_visits":674,"added_clear_instruction_visits":589,"added_nested_callback_returns_ABI_exact":1,"added_CFG_returns_exact":1,"added_clear_returns_ABI_exact":1,"owned_extra_OS_calls":1,"owned_extra_diagnostic_calls":3,"original_registration_publication_returns_ABI_exact":11,"stack_store_chunks":96,"nonstack_field_store_chunks":130,"large_clear_store_chunks":1478,"invalid_owned_dependency_requests_rejected":169}
LITERAL={"window_RVA":"0xf5e600","window_bytes":428,"sha256":"d25748e9674f7a7b1505aff0e9b9517c5dc96221e1e0b6f37fcc0eef2b22d4f3","permitted_read_RVA":"0xf5e64c","permitted_read_bytes":1}
def contract(s):
 assert s["experiment"]=="E011DS" and s["status"]==STATUS and s["scenarios"]==512 and s["next_experiment"]=="E011DT"
 for k in FALSE:assert s[k] is False,k
 for k in ("source_memory_and_permissions_exact","ready_OS_and_loader_and_CRT_resources_are_owned_models","cold_zero_control_cells_and_disabled_trace_are_owned_models","buffer_poison_and_padding_are_robustness_fixtures"):assert s[k] is True
 assert s["new_camera_starts"]==s["new_reboots"]==0
 fields={"stop_before_RVA":"0x5b8268","next_factory_RVA":"0x5bde08","actual_factory_caller_return_RVA":"0x5b826c","cached_pointer_RVA":"0x1731880","source_inline_object_RVA":"0x17a4230","nested_lock_object_RVA":"0x1623598","nested_lock_resource_RVA":"0x16235a0","original_buffer_clear_RVA":"0xf5e600","original_buffer_clear_return_RVA":"0x5b8250","clear_destination_RVA":"0x17a4268","clear_bytes":11808}
 assert all(s[k]==v for k,v in fields.items()) and s["clear_literal_data_authority"]==LITERAL
 dr=json.loads((R/"experiments/E004-front-ir-vd55g0/e011dr-original-cleanup-registration-publication/SOURCE-SAFE.json").read_text())
 assert s["source_pins"]==dr["source_pins"] and len(s["source_pins"])==20 and s["image_sha256"]==dr["image_sha256"]
 rows=s["details"];assert len(rows)==512
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison","initial_global_epoch")
 expected=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a),(0x80000040,41)))
 assert {tuple(r[k] for k in axes) for r in rows}==expected
 for r in rows:
  assert all(r[k]==v for k,v in PER.items())
  for k in ("whole_mapped_memory_and_permissions_exact","immutable_source_and_unmodified_loader_regions","thread_epoch_update_exact","registry_logical_lock_held","nested_registry_logical_lock_held","allocation_redzones_and_relations_exact","cache_pointer_is_actual_inline_object","large_clear_exact","large_clear_padding_redzones_and_constructed_container_exact"):assert r[k] is True
  for k in ("SRW_logical_lock_held","CRT_logical_lock_held","parent_returned","first_helper_returned"):assert r[k] is False
  assert r["published_epoch"]==(r["initial_global_epoch"]+1)&0xffffffff
  assert r["stop_before_RVA"]=="0x5b8268" and r["next_factory_caller_return_RVA"]=="0x5b826c" and r["actual_pre_factory_call_X0_RVA"]=="0x17a4268"
  assert r["clear_literal_data_reads"]==1 and r["inherited_E011DR_source_visits"]==628 and r["original_CRT_registration_instruction_visits"]==338
  assert r["exit_table_used_pointer_entries"]==1 and r["exit_table_capacity_pointer_entries"]==32 and r["owned_allocation_bytes"]==152
 assert s["totals"]=={k:v*512 for k,v in PER.items()}=={k:sum(r[k] for r in rows) for k in PER}
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s)
 result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="42b939af54083f38555ee9ad90db3483ad1b5099" and result["qualification_exit_code"]==0 and result["native_rear_runtime_allowed"] is False
 assert len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011DS" and f["next_experiment"]==n["experiment"]=="E011DT"
 assert f["cached_inline_pointer_source_publication_qualified"] is True and f["nested_lock_original_callback_qualified"] is True and f["original_11808_byte_buffer_clear_qualified"] is True
 assert f["factory_callee_executed_in_this_parent"] is False and n["resume_source_call_RVA"]=="0x5b8268" and n["target_RVA"]=="0x5bde08" and n["actual_caller_return_RVA"]=="0x5b826c"
 assert f["latest_source_RS_query_checkpoint"]=="E011DM" and f["latest_factory_enumeration_checkpoint"]=="E011DI"
 count=0
 if "--selfcheck" in sys.argv:
  muts=[(k,True) for k in FALSE]+[("scenarios",511),("clear_bytes",11807),("stop_before_RVA","0x5b826c"),("source_inline_object_RVA","0x17a4268"),("ready_OS_and_loader_and_CRT_resources_are_owned_models",False),("cold_zero_control_cells_and_disabled_trace_are_owned_models",False),("buffer_poison_and_padding_are_robustness_fixtures",False),("new_camera_starts",1),("new_reboots",1)]
  for label,key,value in (("ABI","added_clear_returns_ABI_exact",0),("epoch","published_epoch",0),("matrix","allocation_poison",0),("lock","nested_registry_logical_lock_held",False),("literal","clear_literal_data_reads",0),("count","large_clear_store_chunks",1476),("X0","actual_pre_factory_call_X0_RVA","0x17a4230")):
   bad=copy.deepcopy(s);bad["details"][0][key]=value;muts.append(("__"+label,bad))
  bad=copy.deepcopy(s);bad["clear_literal_data_authority"]["window_bytes"]=308;muts.append(("__literal_authority",bad))
  bad=copy.deepcopy(s);bad["totals"]["original_instruction_visits"]+=1;muts.append(("__totals",bad))
  for key,value in muts:
   bad=value if key.startswith("__") else copy.deepcopy(s)
   if not key.startswith("__"):bad[key]=value
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence/scope admitted: "+key)
 print(json.dumps({"status":"PASS_E011DS_REVIEW","scenarios":512,"total_original_visits":666624,"added_original_visits":345088,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
