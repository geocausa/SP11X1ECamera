#!/usr/bin/env python3
"""Review bounded original cleanup-registration/publication evidence and its scope."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
STATUS="PASS_BOUNDED_ORIGINAL_CLEANUP_REGISTRATION_AND_GUARD_PUBLICATION"
EXTRA={'0xcb7300': {'body_bytes': 28, 'ranges': [['0xcb7300', '0xcb731b']], 'sha256': 'e1f73058a5d75230088e8935971d1150dff0eb2a2335a632e38dda91ba8c7d18'}, '0xcb99c0': {'body_bytes': 168, 'ranges': [['0xcb99c0', '0xcb9a67']], 'sha256': 'fd618aea90fe77c003d9c147f84bd1fe81d6bb7d27208f3cda07eb58cb7d9834'}, '0xf5e600': {'body_bytes': 308, 'ranges': [['0xf5e600', '0xf5e633'], ['0xf5e680', '0xf5e6fb'], ['0xf5e70c', '0xf5e733'], ['0xf5e750', '0xf5e7ab']], 'sha256': '21fadd27bc73e835f042764cb723485997912b08c24a2875478282404cd7602e'}, '0xcb0388': {'body_bytes': 68, 'ranges': [['0xcb0388', '0xcb03cb']], 'sha256': 'bff698be3287759eac54712fb2c528995d703d76e67f55f6ec27ec02a2c5af80'}, '0xce7a48': {'body_bytes': 140, 'ranges': [['0xce7a48', '0xce7ad3']], 'sha256': '6f84e7a29bab93d10f7570516c2e5be4717e748b87314a6c75857f05ce4455d2'}, '0xca3450': {'body_bytes': 80, 'ranges': [['0xca3450', '0xca349f']], 'sha256': '717580a7ffc8be6182551d6786c5be03612c46a4d15c5f6fb737b6dfdacd2b20'}, '0xcaff90': {'body_bytes': 76, 'ranges': [['0xcaff90', '0xcaffdb']], 'sha256': '42a74d7a75333d2ecb174ba5db0c58029be541a07ee1e572e923f8119ad990ab'}, '0xcb0030': {'body_bytes': 392, 'ranges': [['0xcb0030', '0xcb01b7']], 'sha256': '186196a5d4a09c5c096ac0dbd01b74d0d18a023012dd52d76b9fe01c27d9c7ce'}, '0xcb7398': {'body_bytes': 28, 'ranges': [['0xcb7398', '0xcb73b3']], 'sha256': 'ba0fb2d4a1e1a1d1effa82370b5d86970cbf56048020dfd66c1702bb8237af60'}, '0xcb1650': {'body_bytes': 96, 'ranges': [['0xcb1650', '0xcb16af']], 'sha256': '791d78b8cb56ad9d29749ab08270ed56583998fee4b4e5f9e8ea2e1397841047'}}
FALSE=("CRT_native_initialization_qualified","cleanup_registration_or_guard_result_fixture_used","cleanup_callback_execution_or_teardown_qualified","native_allocator_failure_or_existing_table_growth_qualified","first_helper_complete_return_qualified","cold_parent_return_or_unlock_qualified","full_cold_registry_initialization_qualified","full_metadata_descriptor_construction_allocation_and_publication_qualified","native_Windows_OS_resources_qualified","selected_runtime_reader_profile_qualified","populated_RS_identity_generation_lifetime_qualified","normal_AFD_input_authority_closed","complete_deterministic_source_bootstrap_closed","independent_enabled_output_retirement_proven","native_rear_runtime_allowed","new_kernel_build","production_code_changed","private_raw_material_exported")
PER={"original_instruction_visits":628,"constructor_instruction_visits":103,"registration_wrapper_instruction_visits":9,"first_helper_instruction_visits":40,"guard_instruction_visits":26,"frame_helper_instruction_visits":12,"original_CRT_registration_instruction_visits":338,"publication_instruction_visits":35,"callback_returns_ABI_exact":1,"guard_returns_ABI_exact":1,"constructor_returns_ABI_exact":1,"original_registration_publication_returns_ABI_exact":11,"owned_OS_API_calls":8,"owned_diagnostic_calls":1,"owned_allocation_calls":2,"owned_allocation_bytes":152,"owned_exit_reallocation_calls":1,"owned_exit_reallocation_bytes":256,"owned_wake_calls":1,"stack_store_chunks":85,"nonstack_field_store_chunks":122,"invalid_owned_dependency_requests_rejected":123}
def contract(s):
 assert s["experiment"]=="E011DR" and s["status"]==STATUS and s["scenarios"]==512
 for k in FALSE:assert s[k] is False,k
 for k in ("loader_TLS_OS_readiness_and_fresh_allocation_are_owned_models","CRT_empty_encoded_exit_table_readiness_is_owned_model","whole_mapped_memory_and_permissions_exact","immutable_source_and_unmodified_loader_regions","thread_epoch_update_exact","all_declared_callee_return_ABIs_exact","original_cleanup_registration_qualified","original_helper_guard_publication_qualified"):assert s[k] is True,k
 assert s["new_camera_starts"]==s["new_reboots"]==0 and s["next_experiment"]=="E011DS"
 fields={"original_cleanup_callback_RVA":"0xf7b120","original_exit_table_RVA":"0x16a2760","original_exit_table_words":3,"exit_used_entries":1,"exit_capacity_entries":32,"original_registration_wrapper_RVA":"0xca34a0","registration_wrapper_caller_return_RVA":"0x5b90a0","original_registration_RVA":"0xca3450","registration_caller_return_RVA":"0xca34b0","original_guard_publication_RVA":"0xce7a48","guard_publication_caller_return_RVA":"0x5b90ac","guard_field_RVA":"0x17a4220","global_epoch_RVA":"0x1607b04","TLS_thread_epoch_offset":"0x10","owned_exit_allocator_RVA":"0xcc2a50","owned_exit_allocator_caller_return_RVA":"0xcb9a30","owned_exit_allocator_arguments":[0,256],"stop_before_RVA":"0x5b8104","next_factory_pointer_RVA":"0x1731880","next_factory_pointer_read_RVA":"0x5b8108"}
 assert all(s[k]==v for k,v in fields.items())
 dq=json.loads((R/"experiments/E004-front-ir-vd55g0/e011dq-original-cold-container-construction/SOURCE-SAFE.json").read_text())
 assert s["source_pins"]==dict(dq["source_pins"],**EXTRA) and len(s["source_pins"])==20 and s["image_sha256"]==dq["image_sha256"]
 rows=s["details"];assert len(rows)==512
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison","initial_global_epoch")
 expected=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a),(0x80000040,41)))
 assert {tuple(r[k] for k in axes) for r in rows}==expected
 for r in rows:
  assert all(r[k]==v for k,v in PER.items())
  for k in ("whole_mapped_memory_and_permissions_exact","immutable_source_and_unmodified_loader_regions","thread_epoch_update_exact","registry_logical_lock_held","allocation_redzones_and_relations_exact"):assert r[k] is True
  for k in ("SRW_logical_lock_held","CRT_logical_lock_held","parent_returned","first_helper_returned"):assert r[k] is False
  assert r["published_epoch"]==(r["initial_global_epoch"]+1)&0xffffffff
  assert r["exit_table_used_pointer_entries"]==1 and r["exit_table_capacity_pointer_entries"]==32
  assert r["stop_before_RVA"]=="0x5b8104" and r["next_factory_pointer_RVA"]=="0x1731880"
 assert s["totals"]=={k:v*512 for k,v in PER.items()}=={k:sum(r[k] for r in rows) for k in PER}
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s)
 result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="8e554d94fb05c7a6b082f46935bc7f0c9fa88048" and result["qualification_exit_code"]==0
 assert result["native_rear_runtime_allowed"] is False and len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011DR" and f["next_experiment"]==n["experiment"]=="E011DS"
 assert f["original_cleanup_registration_qualified"] is True and f["original_helper_guard_publication_qualified"] is True and f["first_helper_complete_return_qualified"] is False
 assert f["latest_source_RS_query_checkpoint"]=="E011DM" and f["latest_factory_enumeration_checkpoint"]=="E011DI"
 assert n["resume_source_RVA"]=="0x5b8104" and n["factory_pointer_RVA"]=="0x1731880" and n["factory_pointer_read_RVA"]=="0x5b8108" and n["factory_pointer_write_RVA"]=="0x5b8138"
 count=0
 if "--selfcheck" in sys.argv:
  muts=[(k,True) for k in FALSE]+[("scenarios",511),("stop_before_RVA","0x5b8108"),("CRT_empty_encoded_exit_table_readiness_is_owned_model",False),("thread_epoch_update_exact",False),("new_camera_starts",1),("new_reboots",1),("exit_capacity_entries",16)]
  for label,field,value in (("ABI","original_registration_publication_returns_ABI_exact",10),("epoch","published_epoch",0),("matrix","initial_global_epoch",0),("callback","next_factory_pointer_RVA","0x1731888"),("capacity","exit_table_capacity_pointer_entries",16)):
   bad=copy.deepcopy(s);bad["details"][0][field]=value;muts.append(("__"+label,bad))
  bad=copy.deepcopy(s);bad["totals"]["original_instruction_visits"]+=1;muts.append(("__counts",bad))
  for key,value in muts:
   bad=value if key.startswith("__") else copy.deepcopy(s)
   if not key.startswith("__"):bad[key]=value
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence or scope mutation admitted: "+key)
 print(json.dumps({"status":"PASS_E011DR_REVIEW","scenarios":512,"original_instruction_visits":321536,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
