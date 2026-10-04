#!/usr/bin/env python3
"""Verify the cold-bound/first-helper guard evidence and its bounded scope."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
STATUS="PASS_BOUNDED_ORIGINAL_COLD_BOUNDS_AND_FIRST_HELPER_GUARD"
FALSE=("bound_or_helper_or_guard_result_fixture_used","first_helper_complete_return_qualified","cold_parent_return_or_unlock_qualified","full_cold_registry_initialization_qualified","descriptor_construction_allocation_and_publication_qualified","native_Windows_OS_resources_qualified","selected_runtime_reader_profile_qualified","populated_RS_identity_generation_lifetime_qualified","normal_AFD_input_authority_closed","complete_deterministic_source_bootstrap_closed","independent_enabled_output_retirement_proven","native_rear_runtime_allowed","new_kernel_build","production_code_changed","private_raw_material_exported")
PER={"original_instruction_visits":145,"first_helper_instruction_visits":33,"guard_instruction_visits":26,"frame_helper_instruction_visits":12,"callback_returns_ABI_exact":1,"guard_returns_ABI_exact":1,"owned_OS_API_calls":3,"owned_diagnostic_calls":1,"stack_store_chunks":39,"nonstack_field_store_chunks":3,"invalid_owned_dependency_requests_rejected":51}
def contract(s):
 assert s["experiment"]=="E011DP" and s["status"]==STATUS and s["scenarios"]==128
 for k in FALSE:assert s[k] is False,k
 for k in ("loader_TLS_and_OS_resource_readiness_operations_are_owned_models","diagnostic_no_effect_dependency_is_owned_model","whole_mapped_memory_and_permissions_exact","immutable_source_and_loader_regions"):assert s[k] is True,k
 assert s["new_camera_starts"]==s["new_reboots"]==0 and s["next_experiment"]=="E011DQ"
 for k,v in {"first_helper_RVA":"0x5b80a8","first_helper_caller_return_RVA":"0x5de844","guard_RVA":"0xce7ad8","guard_caller_return_RVA":"0x5b9074","stop_before_RVA":"0x2ee1a0","next_caller_return_RVA":"0x5b9094"}.items():assert s[k]==v,k
 assert s["literal_definitions"]==[{"definition_RVA":"0x5de82c","constant":239},{"definition_RVA":"0x5de834","constant":282},{"definition_RVA":"0xce7b10","constant":-1}]
 assert s["expected_nonstack_fields"]==[{"store_RVA":"0x5de830","field_RVA":"0x17350ec","bytes":4,"value":239},{"store_RVA":"0x5de838","field_RVA":"0x17350e4","bytes":4,"value":282},{"store_RVA":"0xce7b14","field_RVA":"0x17a4220","bytes":4,"value":0xffffffff}]
 assert s["standard_OS_IAT_RVAs"]=={"EnterCriticalSection":"0xf7e0b8","LeaveCriticalSection":"0xf7e0c0","AcquireSRWLockExclusive":"0xf7e520","ReleaseSRWLockExclusive":"0xf7e518"}
 pins=s["source_pins"];assert len(pins)==8
 assert pins["0x5b80a8"]=={"body_bytes":4104,"ranges":[["0x5b80a8","0x5b90af"]],"sha256":"26c3514bda9b9c1e8e91c5988c51fd336d0b77465699675d4935ab2219a0ca9b"}
 assert pins["0xce7ad8"]=={"body_bytes":188,"ranges":[["0xce7ad8","0xce7b93"]],"sha256":"d310e3f40e9666c9e47bb67e2bef87de0f68142b0413af59613ad85d362f6efc"}
 do=json.loads((R/"experiments/E004-front-ir-vd55g0/e011do-original-registry-lock-reuse/SOURCE-SAFE.json").read_text())
 assert all(pins[k]==v for k,v in do["source_pins"].items()) and s["image_sha256"]==do["image_sha256"]
 rows=s["details"];assert len(rows)==128
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0")
 expected=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0xfffffffe),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988)))
 assert {tuple(r[k] for k in axes) for r in rows}==expected
 for r in rows:
  assert all(r[k]==v for k,v in PER.items())
  for k in ("whole_mapped_memory_and_permissions_exact","immutable_source_and_loader_regions","registry_logical_lock_held"):assert r[k] is True
  for k in ("SRW_logical_lock_held","parent_returned","first_helper_returned"):assert r[k] is False
  assert r["stop_before_RVA"]=="0x2ee1a0" and r["caller_return_RVA"]=="0x5b9094" and r["next_object_RVA"]=="0x17a7088" and r["next_scalar_argument"]==65535
 assert s["totals"]=={k:v*128 for k,v in PER.items()}=={k:sum(r[k] for r in rows) for k in PER}
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s)
 result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="cc27048c7c5e852779740500572b6df369bdc3a8" and result["qualification_exit_code"]==0
 assert result["native_rear_runtime_allowed"] is False and result["full_cold_registry_initialization_qualified"] is False
 assert len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011DP" and f["next_experiment"]==n["experiment"]=="E011DQ"
 assert f["latest_source_RS_query_checkpoint"]=="E011DM" and f["latest_factory_enumeration_checkpoint"]=="E011DI"
 assert n["resume_source_RVA"]=="0x2ee1a0" and n["actual_caller_return_RVA"]=="0x5b9094"
 assert n["actual_pointer_argument_RVA"]=="0x17a7088" and n["actual_scalar_argument"]==65535
 count=0
 if "--selfcheck" in sys.argv:
  muts=[(k,True) for k in FALSE]+[("scenarios",127),("stop_before_RVA","0x2ee1a4"),("loader_TLS_and_OS_resource_readiness_operations_are_owned_models",False),("whole_mapped_memory_and_permissions_exact",False),("new_camera_starts",1),("new_reboots",1)]
  bad=copy.deepcopy(s);bad["expected_nonstack_fields"][0]["value"]=240;muts.append(("__fields",bad))
  bad=copy.deepcopy(s);bad["literal_definitions"][1]["constant"]=283;muts.append(("__literal",bad))
  bad=copy.deepcopy(s);bad["details"][0]["next_scalar_argument"]=65534;muts.append(("__arguments",bad))
  bad=copy.deepcopy(s);bad["details"][0]["loader_index"]=1;muts.append(("__matrix",bad))
  bad=copy.deepcopy(s);bad["totals"]["original_instruction_visits"]+=1;muts.append(("__counts",bad))
  for key,value in muts:
   bad=value if key.startswith("__") else copy.deepcopy(s)
   if not key.startswith("__"):bad[key]=value
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence or scope mutation admitted: "+key)
 print(json.dumps({"status":"PASS_E011DP_REVIEW","scenarios":128,"original_instruction_visits":18560,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
