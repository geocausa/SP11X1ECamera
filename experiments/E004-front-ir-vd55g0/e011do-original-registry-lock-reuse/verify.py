#!/usr/bin/env python3
"""Verify E011DO evidence, complete matrix, source bindings and bounded scope."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent
R=H.parents[2]
STATUS="PASS_BOUNDED_ORIGINAL_REGISTRY_LOCK_AND_INITIALIZED_REUSE"
FALSE=("native_Windows_OS_resources_qualified","callback_result_fixture_used","cold_parent_return_or_unlock_qualified",
"full_cold_registry_initialization_qualified","descriptor_construction_allocation_and_publication_qualified",
"selected_runtime_reader_profile_qualified","populated_RS_identity_generation_lifetime_qualified",
"normal_AFD_input_authority_closed","complete_deterministic_source_bootstrap_closed","independent_enabled_output_retirement_proven",
"native_rear_runtime_allowed","new_kernel_build","production_code_changed","private_raw_material_exported")
TOTALS={"original_instruction_visits":6848,"callback_instruction_visits":2576,"original_CFG_nop_visits":112,
"original_frame_helper_visits":768,"callback_returns_ABI_exact":112,"owned_OS_API_calls":112,
"owned_diagnostic_calls":112,"stack_store_chunks":1232,"invalid_owned_dependency_requests_rejected":2512}
def contract(s):
 assert s["experiment"]=="E011DO" and s["status"]==STATUS
 assert (s["scenarios"],s["cold_prefix_cases"],s["initialized_reuse_cases"])==(64,16,48)
 for key in FALSE:assert s[key] is False,key
 for key in ("pre_existing_bound_values_are_owned_fixtures","OS_critical_section_readiness_and_operations_are_owned_models",
 "diagnostic_no_effect_dependency_is_owned_model","original_lock_callbacks_and_initialized_branch_executed",
 "whole_mapped_memory_and_permissions_exact","source_and_nonstack_memory_immutable","callback_callee_ABI_exact","initialized_parent_return_ABI_exact"):
  assert s[key] is True,key
 assert s["new_camera_starts"]==s["new_reboots"]==0
 assert s["cold_stop_before_RVA"]=="0x5de800" and s["next_cold_helper_RVA"]=="0x5b80a8"
 assert s["next_cold_helper_caller_return_RVA"]=="0x5de844" and s["next_experiment"]=="E011DP"
 assert s["default_callback_table_RVA"]=="0x1330a68" and s["resource_object_RVA"]=="0x1626898" and s["critical_section_offset"]=="0x8"
 assert s["standard_OS_IAT_RVAs"]=={"EnterCriticalSection":"0xf7e0b8","LeaveCriticalSection":"0xf7e0c0"}
 pins=s["source_pins"];assert len(pins)==6
 assert pins["0x5de700"]["body_bytes"]==4188 and pins["0x5de700"]["sha256"]=="776092eab939986d2258713b25723c3ad4c1ddcdc8231881da140e25a9960533"
 assert pins["0x1a8c0"]["body_bytes"]==4
 assert pins["0x11f0"]["body_bytes"]==60 and pins["0x11f0"]["ranges"]==[["0x11f0","0x120f"],["0x1214","0x121b"],["0x1220","0x1233"]]
 rows=s["details"];assert len(rows)==64
 bounds=sorted({r["initial_bound_fixture"] for r in rows});assert len(bounds)==4 and bounds[0]==0 and bounds[1]==1 and bounds[-1]==0xffffffff
 assert bounds==sorted((0,1,s["observed_ready_bound_fixture"],0xffffffff))
 assert s["observed_ready_bound_fixture"] not in (0,1,0xffffffff)
 expected=set(itertools.product((0,16,128,512),bounds,(0,0x8877665544332211),(0,0xffeeddccbbaa9988)))
 actual={(r["stack_bias"],r["initial_bound_fixture"],r["diagnostic_X0"],r["OS_void_X0"]) for r in rows};assert actual==expected
 for r in rows:
  cold=r["initial_bound_fixture"]==0
  assert r["path"]==("cold_prefix" if cold else "initialized_reuse")
  assert r["parent_returned"]==(not cold) and r["logical_lock_held_at_boundary"]==cold
  assert r["stop_before_RVA"]==("0x5de800" if cold else None) and r["source_and_nonstack_memory_immutable"]
  fields={"original_instruction_visits":65 if cold else 121,"callback_instruction_visits":23 if cold else 46,
  "original_CFG_nop_visits":1 if cold else 2,"original_frame_helper_visits":6 if cold else 14,
  "callback_returns_ABI_exact":1 if cold else 2,"owned_OS_API_calls":1 if cold else 2,
  "owned_diagnostic_calls":1 if cold else 2,"stack_store_chunks":17 if cold else 20,"invalid_owned_dependency_requests_rejected":28 if cold else 43}
  assert all(r[k]==v for k,v in fields.items())
 assert s["totals"]==TOTALS=={k:sum(r[k] for r in rows) for k in TOTALS}
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s)
 result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="d7013c0af2ef128b5df9424a3f110f0e590a4f38"
 assert result["qualification_exit_code"]==0 and result["next_experiment"]=="E011DP"
 assert result["full_cold_registry_initialization_qualified"] is False
 assert result["native_rear_runtime_allowed"] is False and len(result["source_locks"])>=8
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R)
  assert hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 authority=R/"experiments/E004-front-ir-vd55g0/e011dn-windows-registry-boundary/OBSERVATION-SAFE.json"
 a=json.loads(authority.read_text())
 assert s["input_evidence_locks"]["E011DN_OBSERVATION_SAFE"]==hashlib.sha256(authority.read_bytes()).hexdigest()
 assert s["input_evidence_locks"]["private_READY_META"]==a["private_nonoptical_evidence_hashes"]["E011DN-20261003-1926B/capture/READY_META.bin"]
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["next_experiment"]==n["experiment"]=="E011DP"
 assert f["latest_source_RS_query_checkpoint"]=="E011DM" and f["latest_factory_enumeration_checkpoint"]=="E011DI"
 count=0
 if "--selfcheck" in sys.argv:
  muts=[(k,True) for k in FALSE]+[("scenarios",63),("cold_stop_before_RVA","0x5de804"),("OS_critical_section_readiness_and_operations_are_owned_models",False),("whole_mapped_memory_and_permissions_exact",False),("new_camera_starts",1),("new_reboots",1),("observed_ready_bound_fixture",0)]
  for key,value in muts:
   bad=copy.deepcopy(s);bad[key]=value
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported scope or matrix mutation admitted: "+key)
  assert count==len(muts)
 print(json.dumps({"status":"PASS_E011DO_REVIEW","scenarios":64,"source_locks":len(result["source_locks"]),
 "scope_evidence_mutations_rejected":count,"initialized_parent_returns":48,"cold_prefix_stops":16,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
