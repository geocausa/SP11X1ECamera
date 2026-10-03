#!/usr/bin/env python3
"""Read-only E011DL source/evidence integrity, matrix and scope check."""
from pathlib import Path
from itertools import product
import copy,hashlib,json,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
STATUS="PASS_BOUNDED_ORIGINAL_RUNTIME_RS_TAG_INITIALIZATION_AND_REUSE"
FALSE_FLAGS=("runtime_tag_vector_result_fixture_used","original_guard_result_fixture_used",
 "concurrent_wait_and_real_Windows_loader_qualified","actual_registry_content_and_query_body_qualified",
 "upstream_AFD_normal_count_policy_closed","complete_deterministic_source_bootstrap_closed",
 "independent_enabled_output_retirement_proven","native_rear_runtime_allowed",
 "new_kernel_build","private_bytes_exported")
def source_contract(source):
 assert source["experiment"]=="E011DL" and source["status"]==STATUS
 assert source["tag_vector_RVA"]=="0x17a30e0"
 assert source["RS_tag_cell_RVA"]=="0x17a30f4" and source["guard_RVA"]=="0x1b303fc"
 assert source["registry_field_offsets"]==["0xc0","0xd8","0x48","0x60","0x78","0x90","0xa8"]
 assert source["property_namespace_mask"]=="0x08000000"
 assert source["scenarios"]==192 and source["reader_phase_cases"]==576
 assert source["cases_by_record_state"]==dict(present=192,absent=192,fallback=192)
 for key in FALSE_FLAGS:assert source[key] is False,key
 for key in ("whole_nonstack_memory_and_mapping_permissions_exact",
 "stack_redzones_and_preserved_ABI_exact","source_record_and_original_code_immutable",
 "cold_initialization_then_warm_and_stale_thread_reuse_checked",
 "registry_settings_metadata_query_and_OS_SRW_CV_are_owned_models"):
  assert source[key] is True,key
 assert source["new_camera_starts"]==source["new_reboots"]==0
 rows=source["details"]
 assert len(rows)==192
 actual={(r["placement"],r["loader_index"],r["initial_epoch"],r["registry_pattern"],r["record_state"]) for r in rows}
 assert actual==set(product((0,16,128,512),(0,37),(0x80000000,0xffffff00),range(4),("present","absent","fallback")))
 fields=None
 for row in rows:
  assert [p["phase"] for p in row["phases"]]==["cold","warm","stale_thread"]
  queries=13 if row["record_state"]=="present" else 14
  for p in row["phases"]:
   phase=p["phase"];apis={"cold":5,"warm":0,"stale_thread":2}[phase]
   assert p["original_guard_instruction_visits"]=={"cold":61,"warm":0,"stale_thread":33}[phase]
   assert p["initializer_instruction_visits"]=={"cold":22,"warm":0,"stale_thread":6}[phase]
   assert p["tag_field_stores"]==(7 if phase=="cold" else 0)
   assert p["query_callbacks"]==queries and p["owned_standard_API_calls"]==apis
   assert p["invalid_dependency_requests_rejected"]==9*queries+4*apis
   assert p["all_original_instruction_visits"]>=p["reader_instruction_visits"]+p["original_guard_instruction_visits"]
   assert p["owned_settings_store_sites"]==[["0x740f58","0x2020",4],["0x740f68","0x2014",4],["0x740f78","0x200c",4],["0x740f88","0x2020",4]]
   keys=set(p)-{"phase","owned_settings_store_sites"}
   assert fields is None or fields==keys;fields=keys
 totals={k:sum(p[k] for r in rows for p in r["phases"]) for k in fields}
 assert source["totals"]==totals
 assert totals["tag_field_stores"]==1344 and totals["invalid_dependency_requests_rejected"]==76224
 assert totals["original_guard_instruction_visits"]==18048
 assert totals["initializer_instruction_visits"]==5376
def verify():
 result=json.loads((HERE/"RESULT.json").read_text());source=json.loads((HERE/"SOURCE-SAFE.json").read_text())
 source_contract(source)
 assert result["experiment"]=="E011DL" and result["status"]==STATUS
 assert result["base_commit"]=="a78159254d8ad8e8781dbb4b5877103fb43eea77"
 assert result["next_experiment"]=="E011DM" and result["latest_factory_enumeration_checkpoint"]=="E011DI"
 assert result["qualification_exit_code"]==0 and result["native_rear_runtime_allowed"] is False
 assert result["independent_enabled_output_retirement_proven"] is False
 for rel,pin in result["source_locks"].items():
  path=(ROOT/rel).resolve();assert path.is_relative_to(ROOT)
  assert hashlib.sha256(path.read_bytes()).hexdigest()==pin,rel
 assert len(result["source_locks"])>=10
 rejected=0
 if "--selfcheck" in sys.argv:
  for key in FALSE_FLAGS:
   bad=copy.deepcopy(source);bad[key]=True
   try:source_contract(bad)
   except AssertionError:rejected+=1
   else:raise AssertionError("false scope promotion admitted")
  for key,value in (("reader_phase_cases",575),("RS_tag_cell_RVA","0x17a30f0"),("property_namespace_mask","0x08000001")):
   bad=copy.deepcopy(source);bad[key]=value
   try:source_contract(bad)
   except AssertionError:rejected+=1
   else:raise AssertionError("incorrect boundary admitted")
  assert rejected==13
 print(json.dumps({"status":"PASS_E011DL","reader_phase_cases":576,
  "original_guard_instruction_visits_reused":18048,"initializer_instruction_visits":5376,
  "tag_field_stores":1344,"invalid_dependency_requests_rejected":76224,
  "scope_negative_mutations_rejected":rejected,"actual_query_and_upstream_policy_open":True,
  "native_rear_runtime_allowed":False}))
if __name__=="__main__":verify()
