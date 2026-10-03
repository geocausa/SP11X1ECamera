#!/usr/bin/env python3
"""Read-only E011DM evidence, matrix, source locks and scope verification."""
from pathlib import Path
from itertools import product
import copy,hashlib,json,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
STATUS="PASS_BOUNDED_ORIGINAL_RS_QUERY_EMPTY_SELECTED_SLOTS"
FALSE_FLAGS=("query_result_fixture_used","slot_helper_result_fixture_used",
 "runtime_tag_vector_result_fixture_used","original_guard_result_fixture_used",
 "actual_registry_content_qualified","populated_record_identity_and_lifetime_qualified",
 "metadata_registry_initialization_qualified","concurrent_wait_and_real_Windows_loader_qualified",
 "upstream_AFD_normal_count_policy_closed","complete_deterministic_source_bootstrap_closed",
 "independent_enabled_output_retirement_proven","native_rear_runtime_allowed",
 "new_kernel_build","private_bytes_exported")
REQUESTS=(0,1,17,0x100000007,0xffffffffffffffff)
def source_contract(source):
 assert source["experiment"]=="E011DM" and source["status"]==STATUS
 assert source["scenarios"]==640 and source["reader_phase_cases"]==1920
 for key in FALSE_FLAGS:assert source[key] is False,key
 for key in ("registry_settings_node_context_pools_empty_slots_and_OS_SRW_CV_are_owned_models",
  "whole_nonstack_memory_and_mapping_permissions_exact","stack_redzones_and_preserved_ABI_exact",
  "original_code_and_owned_pool_slot_objects_immutable","actual_empty_query_path_qualified"):
  assert source[key] is True,key
 assert source["new_camera_starts"]==source["new_reboots"]==0
 assert source["node_pool_offsets"]==["0x490","0x498","0x4a8","0x4b0"]
 assert source["selected_pool_offset"]=="0x490" and source["pool_capacity_offset"]=="0x278"
 assert source["inline_slot_array_offset"]=="0x298" and source["empty_slot_state_offset"]=="0x30"
 assert source["TLS_request_selector_offset"]=="0x138" and source["ninth_query_stack_argument"]==0
 assert source["source_pins"]["0x5d4d30"]==dict(bytes=2144,sha256="cb1f18cbcf4bf0c7dc34f9081c2d83b148e36a213ba92a0686ea3585698dcdff")
 assert source["source_pins"]["0x5c3758"]==dict(bytes=1340,sha256="0db48188ba17a0501542acc05e83a79d648f821ccbe32eddd6581bb98ffe4ff8")
 rows=source["details"];assert len(rows)==640
 actual={(r["placement"],r["loader_index"],r["initial_epoch"],r["registry_pattern"],r["pool_capacity"],r["request_selector"]) for r in rows}
 assert actual==set(product((0,16,128,512),(0,37),(0x80000000,0xffffff00),range(2),(1,3,5,9),REQUESTS))
 fields=None
 stores=[["0x740f58","0x2020",4],["0x740f68","0x2014",4],["0x740f78","0x200c",4],["0x740f88","0x2020",4],
         ["0x5d4d8c","0x2020",4],["0x5d4d9c","0x2014",4],["0x5d4dac","0x200c",4],["0x5d4dbc","0x2020",4]]
 for row in rows:
  assert row["record_state"]=="empty"
  assert [p["phase"] for p in row["phases"]]==["cold","warm","stale_thread"]
  queries=14 if row["request_selector"] in (0,0xffffffffffffffff) else 7
  for p in row["phases"]:
   phase=p["phase"];apis={"cold":5,"warm":0,"stale_thread":2}[phase]
   assert p["original_guard_instruction_visits"]=={"cold":61,"warm":0,"stale_thread":33}[phase]
   assert p["initializer_instruction_visits"]=={"cold":22,"warm":0,"stale_thread":6}[phase]
   assert p["tag_field_stores"]==(7 if phase=="cold" else 0)
   for key in ("actual_query_calls","actual_empty_slot_lookups","actual_null_results","zero_ninth_stack_arguments"):
    assert p[key]==queries
   assert p["query_instruction_visits"]==100*queries
   assert p["slot_helper_instruction_visits"]==55*queries
   assert p["owned_standard_API_calls"]==apis
   assert p["invalid_dependency_requests_rejected"]==18*queries+4*apis
   assert p["owned_settings_store_sites"]==stores and p["owned_settings_stores"]==4+4*queries
   assert p["all_original_instruction_visits"]>=sum(p[k] for k in ("reader_instruction_visits","original_guard_instruction_visits","query_instruction_visits","slot_helper_instruction_visits"))
   keys=set(p)-{"phase","owned_settings_store_sites"}
   assert fields is None or fields==keys;fields=keys
 totals={k:sum(p[k] for r in rows for p in r["phases"]) for k in fields}
 assert source["totals"]==totals
 assert totals["actual_query_calls"]==18816 and totals["invalid_dependency_requests_rejected"]==356608
 assert totals["tag_field_stores"]==4480 and totals["original_guard_instruction_visits"]==60160
def verify():
 source=json.loads((HERE/"SOURCE-SAFE.json").read_text());source_contract(source)
 result=json.loads((HERE/"RESULT.json").read_text())
 assert result["experiment"]=="E011DM" and result["status"]==STATUS
 assert result["base_commit"]=="e6e58dda8759f97f3110dbd5fad44f7262121611"
 assert result["qualification_exit_code"]==0 and result["next_experiment"]=="E011DN"
 assert result["latest_factory_enumeration_checkpoint"]=="E011DI"
 assert result["native_rear_runtime_allowed"] is False
 assert result["populated_record_identity_and_lifetime_qualified"] is False
 assert len(result["source_locks"])>=10
 for rel,pin in result["source_locks"].items():
  path=(ROOT/rel).resolve();assert path.is_relative_to(ROOT)
  assert hashlib.sha256(path.read_bytes()).hexdigest()==pin,rel
 rejected=0
 if "--selfcheck" in sys.argv:
  for key in FALSE_FLAGS:
   bad=copy.deepcopy(source);bad[key]=True
   try:source_contract(bad)
   except AssertionError:rejected+=1
   else:raise AssertionError("scope promotion admitted")
  for key,value in (("reader_phase_cases",1919),("selected_pool_offset","0x498"),("ninth_query_stack_argument",1)):
   bad=copy.deepcopy(source);bad[key]=value
   try:source_contract(bad)
   except AssertionError:rejected+=1
   else:raise AssertionError("boundary mutation admitted")
  assert rejected==17
 print(json.dumps({"status":"PASS_E011DM","reader_phase_cases":1920,
  "actual_query_calls":18816,"added_query_and_slot_helper_instruction_visits":2916480,
  "invalid_dependency_requests_rejected":356608,"scope_negative_mutations_rejected":rejected,
  "populated_record_identity_and_lifetime_qualified":False,"native_rear_runtime_allowed":False}))
if __name__=="__main__":verify()
