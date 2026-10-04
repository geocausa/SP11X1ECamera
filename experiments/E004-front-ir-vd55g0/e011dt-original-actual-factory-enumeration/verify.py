#!/usr/bin/env python3
"""Review original factory/enum integration, retained ownership, signed epoch and bounded scope."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
STATUS="PASS_BOUNDED_ACTUAL_FACTORY_ENUMERATION_IN_COLD_HELPER"
EXTRA={'0x5bde08': {'body_bytes': 4004, 'ranges': [['0x5bde08', '0x5bedab']], 'sha256': '6ac0077e8b76bd1301294aab6e24517b3c62e84f1046cde686e18620fbd2b84b'}, '0x5f8dc0': {'body_bytes': 1776, 'ranges': [['0x5f8dc0', '0x5f94af']], 'sha256': 'd6509a3050729b92fb3a89e93c334e04eb4316ea2ff4af082f56e02de1a6af29'}, '0x1440': {'body_bytes': 48, 'ranges': [['0x1440', '0x146f']], 'sha256': 'f63f52748e3065341e8e73a6fb2abab1f5af2e25a17f3b0d627034c7341c9b5b'}}
FALSE=("source_result_fixture_used","native_rear_runtime_allowed","full_factory_or_first_helper_return_qualified","full_descriptor_registry_publication_qualified","callback_registration_with_existing_encoded_table_qualified","native_OS_CRT_allocator_construction_and_failure_paths_qualified","stack_growth_guard_page_OS_qualified","new_kernel_build","production_code_changed","private_raw_material_exported")
PER={"original_instruction_visits":499,"factory_clear_instruction_visits":117,"factory_clear_store_chunks":130,"exact_source_store_chunks":401,"nonstack_field_store_chunks":222,"rejected_owned_requests":59,"guard_returns_ABI_exact":2,"probe_returns_ABI_exact":1,"clear_returns_ABI_exact":1,"owned_OS_API_calls":4,"owned_allocation_calls":2,"owned_allocation_bytes":96}
def contract(s):
 assert s["experiment"]=="E011DT" and s["status"]==STATUS and s["scenarios"]==256 and s["next_experiment"]=="E011DU"
 for k in FALSE:assert s[k] is False,k
 for k in ("factory_nodes_are_distinct_from_ancestor_allocations","actual_published_TLS_epoch_retained","already_committed_stack_bounds_are_owned_model"):assert s[k] is True
 assert s["cold_global_epoch"]=="0x80000040" and s["actual_published_thread_epoch"]=="0x80000041" and s["new_camera_starts"]==s["new_reboots"]==0
 ds=json.loads((R/"experiments/E004-front-ir-vd55g0/e011ds-original-cached-object-nested-lock-clear/SOURCE-SAFE.json").read_text())
 assert s["source_pins"]==dict(ds["source_pins"],**EXTRA) and len(s["source_pins"])==23 and s["image_sha256"]==ds["image_sha256"]
 assert s["clear_literal_window_authority"]==ds["clear_literal_data_authority"] and s["added_clear_literal_read_RVA"]=="0xf5e644" and s["added_clear_literal_read_bytes"]==1
 assert s["factory_zero_field_plan_sha256"]=="0f62dedc35657a133d2f1e4e9b5736fde52d69c78bfc6d0800e9498df3e93389"
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 expected=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 rows=s["details"];assert len(rows)==256 and {tuple(r["DS"][k] for k in axes) for r in rows}==expected
 prior={tuple(r[k] for k in axes):r for r in ds["details"] if r["initial_global_epoch"]==0x80000040};assert len(prior)==256
 for r in rows:
  d=r["DS"];a=r["added"];assert d==prior[tuple(d[k] for k in axes)]
  assert all(a[k]==v for k,v in PER.items())
  for k in ("factory_and_enumeration_guards_in_progress","outer_and_nested_registry_locks_held","whole_entry_to_frontier_memory_and_permissions_exact","ancestor_live_allocations_redzones_TLS_and_container_retained"):assert a[k] is True
  assert a["clear_literal_data_reads"]==[["0xf5e644",1]] and a["stop_before_RVA"]=="0x5f94a0" and a["next_callback_RVA"]=="0xf7b5e0"
 assert s["added_totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(r["added"][k] for r in rows) for k in PER}
 keys=("original_instruction_visits","invalid_owned_dependency_requests_rejected","stack_store_chunks","nonstack_field_store_chunks","large_clear_store_chunks")
 assert s["inherited_DS_totals"]=={k:sum(r["DS"][k] for r in rows) for k in keys}
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s)
 result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="6ac3a74ee3b599c10b359bb6b20ae1454bbaba8b" and result["qualification_exit_code"]==0 and result["native_rear_runtime_allowed"] is False
 assert len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011DT" and f["next_experiment"]==n["experiment"]=="E011DU" and f["actual_parent_factory_enumeration_bootstrap_qualified"] is True
 assert f["full_factory_or_first_helper_return_qualified"] is False and f["latest_source_RS_query_checkpoint"]=="E011DM" and f["latest_separate_factory_enumeration_checkpoint"]=="E011DI"
 assert n["resume_source_call_RVA"]=="0x5f94a0" and n["target_RVA"]=="0xca34a0" and n["actual_caller_return_RVA"]=="0x5f94a4" and n["actual_callback_argument_RVA"]=="0xf7b5e0"
 assert n["encoded_exit_table_used_entries"]==1 and n["encoded_exit_table_capacity"]==32
 count=0
 if "--selfcheck" in sys.argv:
  muts=[(k,True) for k in FALSE]+[("scenarios",255),("cold_global_epoch","0x29"),("actual_published_thread_epoch","0x2a"),("factory_nodes_are_distinct_from_ancestor_allocations",False),("actual_published_TLS_epoch_retained",False),("already_committed_stack_bounds_are_owned_model",False),("new_camera_starts",1),("new_reboots",1)]
  for label,key,value in (("ABI","guard_returns_ABI_exact",1),("nodes","owned_allocation_bytes",48),("lock","outer_and_nested_registry_locks_held",False),("clear","factory_clear_store_chunks",129),("frontier","stop_before_RVA","0x5f94a4"),("literal","clear_literal_data_reads",[])):
   bad=copy.deepcopy(s);bad["details"][0]["added"][key]=value;muts.append(("__"+label,bad))
  bad=copy.deepcopy(s);bad["details"][0]["DS"]["initial_global_epoch"]=41;muts.append(("__epoch",bad))
  bad=copy.deepcopy(s);bad["details"][0]["DS"]["allocation_poison"]=0;muts.append(("__matrix",bad))
  bad=copy.deepcopy(s);bad["added_totals"]["original_instruction_visits"]+=1;muts.append(("__totals",bad))
  bad=copy.deepcopy(s);bad["source_pins"]["0x5bde08"]["body_bytes"]=4008;muts.append(("__body",bad))
  for key,value in muts:
   bad=value if key.startswith("__") else copy.deepcopy(s)
   if not key.startswith("__"):bad[key]=value
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence/scope admitted: "+key)
 print(json.dumps({"status":"PASS_E011DT_REVIEW","scenarios":256,"added_original_visits":127744,"combined_original_visits":461056,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
