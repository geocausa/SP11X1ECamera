#!/usr/bin/env python3
"""Check original constructor evidence, allocation contracts, matrix and bounded claims."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
STATUS="PASS_BOUNDED_ORIGINAL_COLD_CONTAINER_CONSTRUCTION"
FALSE=("constructor_or_first_helper_or_guard_result_fixture_used","first_helper_complete_return_qualified","cold_parent_return_or_unlock_qualified","full_cold_registry_initialization_qualified","full_metadata_descriptor_construction_allocation_and_publication_qualified","cleanup_registration_execution_qualified","helper_guard_publication_qualified","native_allocator_failure_cleanup_or_teardown_qualified","native_Windows_OS_resources_qualified","selected_runtime_reader_profile_qualified","populated_RS_identity_generation_lifetime_qualified","normal_AFD_input_authority_closed","complete_deterministic_source_bootstrap_closed","independent_enabled_output_retirement_proven","native_rear_runtime_allowed","new_kernel_build","production_code_changed","private_raw_material_exported")
PER={"original_instruction_visits":255,"constructor_instruction_visits":103,"registration_wrapper_prefix_visits":4,"first_helper_instruction_visits":36,"guard_instruction_visits":26,"frame_helper_instruction_visits":12,"callback_returns_ABI_exact":1,"guard_returns_ABI_exact":1,"constructor_returns_ABI_exact":1,"owned_OS_API_calls":3,"owned_diagnostic_calls":1,"owned_allocation_calls":2,"owned_allocation_bytes":152,"stack_store_chunks":48,"nonstack_field_store_chunks":51,"invalid_owned_dependency_requests_rejected":69}
def contract(s):
 assert s["experiment"]=="E011DQ" and s["status"]==STATUS and s["scenarios"]==256
 for key in FALSE:assert s[key] is False,key
 for key in ("loader_TLS_and_OS_resource_readiness_operations_are_owned_models","allocation_readiness_storage_provenance_and_liveness_are_owned_models","diagnostic_no_effect_dependency_is_owned_model","whole_mapped_memory_and_permissions_exact","immutable_source_and_loader_regions","constructor_callee_ABI_exact","allocation_redzones_and_relations_exact"):assert s[key] is True,key
 assert s["new_camera_starts"]==s["new_reboots"]==0 and s["next_experiment"]=="E011DR"
 fields={"constructor_RVA":"0x2ee1a0","constructor_caller_return_RVA":"0x5b9094","container_RVA":"0x17a7088","container_bytes":64,"constructor_input_scalar":65535,
 "owned_allocator_RVA":"0xcae740","constructed_array_pointer_entries":16,"constructed_mask":7,"constructed_bucket_count":8,"constructed_load_factor_bits":"0x3f800000",
 "stop_before_RVA":"0xca3450","next_caller_return_RVA":"0xca34b0","next_callback_RVA":"0xf7b120","registration_wrapper_RVA":"0xca34a0"}
 assert all(s[k]==v for k,v in fields.items())
 assert s["owned_allocations"]==[{"caller_return_RVA":"0x2ee1d0","bytes":24},{"caller_return_RVA":"0x2ee218","bytes":128}]
 pins=s["source_pins"];assert len(pins)==10
 assert pins["0x2ee1a0"]=={"body_bytes":260,"ranges":[["0x2ee1a0","0x2ee2a3"]],"sha256":"5540e74845b5dcd51626470a4315ad8b36c94eea910a4ac0c47e408965fd748b"}
 assert pins["0xca34a0"]=={"body_bytes":36,"ranges":[["0xca34a0","0xca34c3"]],"sha256":"0cd146a840c54743d0d3a2e3ecdacbbb619f7c9701bb605d498854f9ee0986f5"}
 dp=json.loads((R/"experiments/E004-front-ir-vd55g0/e011dp-original-cold-bounds-helper-guard/SOURCE-SAFE.json").read_text())
 assert all(pins[k]==v for k,v in dp["source_pins"].items()) and s["image_sha256"]==dp["image_sha256"]
 rows=s["details"];assert len(rows)==256
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 expected=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0xfffffffe),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 assert {tuple(r[k] for k in axes) for r in rows}==expected
 for r in rows:
  assert all(r[k]==v for k,v in PER.items())
  for key in ("whole_mapped_memory_and_permissions_exact","immutable_source_and_loader_regions","registry_logical_lock_held","allocation_redzones_and_relations_exact"):assert r[key] is True
  for key in ("SRW_logical_lock_held","parent_returned","first_helper_returned"):assert r[key] is False
  assert r["stop_before_RVA"]=="0xca3450" and r["caller_return_RVA"]=="0xca34b0" and r["next_callback_RVA"]=="0xf7b120"
 assert s["totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(r[k] for r in rows) for k in PER}
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s)
 result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="83bb34166854471e845f9e2f817b3e5725845a7d" and result["qualification_exit_code"]==0
 assert result["native_rear_runtime_allowed"] is False and result["full_cold_registry_initialization_qualified"] is False and len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011DQ" and f["next_experiment"]==n["experiment"]=="E011DR"
 assert f["original_cold_container_constructor_qualified"] is True and f["cleanup_registration_execution_qualified"] is False and f["helper_guard_publication_qualified"] is False
 assert f["latest_source_RS_query_checkpoint"]=="E011DM" and f["latest_factory_enumeration_checkpoint"]=="E011DI"
 assert n["resume_source_RVA"]=="0xca3450" and n["actual_caller_return_RVA"]=="0xca34b0" and n["actual_callback_argument_RVA"]=="0xf7b120"
 count=0
 if "--selfcheck" in sys.argv:
  muts=[(k,True) for k in FALSE]+[("scenarios",255),("stop_before_RVA","0xca3454"),("allocation_readiness_storage_provenance_and_liveness_are_owned_models",False),("whole_mapped_memory_and_permissions_exact",False),("new_camera_starts",1),("new_reboots",1),("constructed_array_pointer_entries",8)]
  bad=copy.deepcopy(s);bad["owned_allocations"][1]["bytes"]=127;muts.append(("__size",bad))
  bad=copy.deepcopy(s);bad["details"][0]["constructor_returns_ABI_exact"]=0;muts.append(("__ABI",bad))
  bad=copy.deepcopy(s);bad["details"][0]["allocation_poison"]=0;muts.append(("__matrix",bad))
  bad=copy.deepcopy(s);bad["totals"]["original_instruction_visits"]+=1;muts.append(("__counts",bad))
  bad=copy.deepcopy(s);bad["details"][0]["next_callback_RVA"]="0xf7b124";muts.append(("__callback",bad))
  for key,value in muts:
   bad=value if key.startswith("__") else copy.deepcopy(s)
   if not key.startswith("__"):bad[key]=value
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence or scope mutation admitted: "+key)
 print(json.dumps({"status":"PASS_E011DQ_REVIEW","scenarios":256,"original_instruction_visits":65280,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
