#!/usr/bin/env python3
"""Review original existing-table append/publication, retained parent effects and bounded scope."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
STATUS="PASS_BOUNDED_ACTUAL_EXISTING_TABLE_REGISTRATION_ENUMERATION_PUBLICATION"
FALSE=("source_result_fixture_used","native_rear_runtime_allowed","full_factory_or_first_helper_return_qualified","full_descriptor_registry_publication_qualified",
 "native_OS_CRT_allocator_construction_and_failure_paths_qualified","next_enumeration_dependency_qualified","stack_growth_guard_page_OS_qualified",
 "new_kernel_build","production_code_changed","private_raw_material_exported")
TRUE=("existing_nonempty_encoded_table_is_actual_parent_result","registration_used_existing_capacity_without_allocator","enumeration_epoch_publication_qualified","prior_factory_nodes_and_registry_locks_retained")
PER={"original_instruction_visits":176,"exact_source_store_chunks":37,"nonstack_field_store_chunks":7,"rejected_owned_requests":107,
 "original_registration_publication_returns_ABI_exact":8,"owned_OS_API_calls":5,"owned_exit_reallocation_calls":0,"owned_wake_calls":1}
def contract(s):
 assert s["experiment"]=="E011DU" and s["status"]==STATUS and s["scenarios"]==256 and s["next_experiment"]=="E011DV"
 for k in FALSE:assert s[k] is False,k
 for k in TRUE:assert s[k] is True,k
 assert s["new_camera_starts"]==s["new_reboots"]==0
 dt=json.loads((R/"experiments/E004-front-ir-vd55g0/e011dt-original-actual-factory-enumeration/SOURCE-SAFE.json").read_text())
 assert s["source_pins"]==dt["source_pins"] and len(s["source_pins"])==23 and s["image_sha256"]==dt["image_sha256"]
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 expected=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 rows=s["details"];assert len(rows)==256 and {tuple(r["DT"]["DS"][k] for k in axes) for r in rows}==expected
 prior={tuple(r["DS"][k] for k in axes):r for r in dt["details"]};assert len(prior)==256
 for r in rows:
  d=r["DT"];a=r["added"];assert d==prior[tuple(d["DS"][k] for k in axes)]
  assert all(a[k]==v for k,v in PER.items())
  for k in ("factory_guard_in_progress","outer_and_nested_registry_locks_held","CRT_and_SRW_released","whole_entry_to_frontier_memory_and_permissions_exact","ancestor_live_allocations_redzones_TLS_and_container_retained"):assert a[k] is True
  assert a["actual_return_RVAs"]==["0x5f94a4","0x5f94ac"]
  assert a["registration_publication_frame_entries"]==["0xca34a0","0xca3450","0xcb0388","0xcaff90","0xcb7300","0xcb0030","0xcb7398","0xce7a48"]
  assert a["exit_table_used_entries"]==2 and a["exit_table_capacity_entries"]==32
  assert a["published_enumeration_global_TLS_epoch"]=="0x80000042" and a["retained_helper_epoch"]=="0x80000041"
  assert a["stop_before_RVA"]=="0x5f8e24" and a["next_dependency_RVA"]=="0x1731598" and a["next_dependency_bytes"]==4
 assert s["added_totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(r["added"][k] for r in rows) for k in PER}
 assert s["inherited_DT_totals"]==dt["added_totals"] and s["inherited_DS_totals"]==dt["inherited_DS_totals"]
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s)
 result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="e2bbc66e4708a076a018120c03ef3c535cb765ce" and result["qualification_exit_code"]==0 and result["native_rear_runtime_allowed"] is False
 assert result["added_original_instruction_visits"]==45056 and result["combined_original_instruction_visits"]==506112 and len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011DU" and f["next_experiment"]==n["experiment"]=="E011DV"
 assert f["callback_registration_with_existing_encoded_table_qualified"] is True and f["enumeration_epoch_publication_qualified"] is True
 assert f["full_factory_or_first_helper_return_qualified"] is False and f["latest_source_RS_query_checkpoint"]=="E011DM" and f["latest_actual_parent_factory_enumeration_checkpoint"]=="E011DT"
 assert n["resume_source_RVA"]=="0x5f8e24" and n["dependency_RVA"]=="0x1731598" and n["dependency_bytes"]==4
 assert n["encoded_exit_table_used_entries"]==2 and n["encoded_exit_table_capacity"]==32
 assert n["published_enumeration_global_TLS_epoch"]=="0x80000042" and n["retained_helper_epoch"]=="0x80000041" and n["factory_guard_in_progress"] is True
 count=0
 if "--selfcheck" in sys.argv:
  muts=[(k,True) for k in FALSE]+[(k,False) for k in TRUE]+[("scenarios",255),("new_camera_starts",1),("new_reboots",1)]
  for label,key,value in (("ABI","original_registration_publication_returns_ABI_exact",7),("reallocation","owned_exit_reallocation_calls",1),("capacity","exit_table_capacity_entries",31),
   ("used","exit_table_used_entries",1),("epoch","published_enumeration_global_TLS_epoch","0x80000041"),("helper","retained_helper_epoch","0x80000042"),
   ("lock","outer_and_nested_registry_locks_held",False),("factory","factory_guard_in_progress",False),("frontier","stop_before_RVA","0x5f8e28"),("memory","whole_entry_to_frontier_memory_and_permissions_exact",False),
   ("returns","actual_return_RVAs",["0x5b90a0","0x5b90ac"]),("frames","registration_publication_frame_entries",[])):
   bad=copy.deepcopy(s);bad["details"][0]["added"][key]=value;muts.append(("__"+label,bad))
  bad=copy.deepcopy(s);bad["details"][0]["DT"]["DS"]["initial_global_epoch"]=41;muts.append(("__parent",bad))
  bad=copy.deepcopy(s);bad["details"][0]["DT"]["DS"]["allocation_poison"]=0;muts.append(("__matrix",bad))
  bad=copy.deepcopy(s);bad["added_totals"]["original_instruction_visits"]+=1;muts.append(("__totals",bad))
  bad=copy.deepcopy(s);bad["source_pins"]["0xca34a0"]["sha256"]="0"*64;muts.append(("__pin",bad))
  for key,value in muts:
   bad=value if key.startswith("__") else copy.deepcopy(s)
   if not key.startswith("__"):bad[key]=value
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence/scope admitted: "+key)
 print(json.dumps({"status":"PASS_E011DU_REVIEW","scenarios":256,"added_original_visits":45056,"combined_original_visits":506112,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
