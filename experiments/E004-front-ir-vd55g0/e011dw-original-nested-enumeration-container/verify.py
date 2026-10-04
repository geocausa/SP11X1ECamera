#!/usr/bin/env python3
"""Review nested enumeration container construction, retained ownership and bounded scope."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
STATUS="PASS_BOUNDED_ACTUAL_NESTED_ENUMERATION_CONTAINER_CONSTRUCTION"
EXTRA={"0x600368":{"body_bytes":1120,"ranges":[["0x600368","0x6007c7"]],"sha256":"18d45d94302157df5a5ce15d232191f9fca4a63bc1c910af535a9dc24b4b7e43"},
 "0x5e81b8":{"body_bytes":540,"ranges":[["0x5e81b8","0x5e83d3"]],"sha256":"ec5c36864ecc63597070f754e40553dfe358c067243ceb4b44b8390ca757dd16"}}
FALSE=("source_result_fixture_used","native_rear_runtime_allowed","full_factory_or_first_helper_return_qualified","full_descriptor_registry_publication_qualified",
 "native_OS_CRT_allocator_construction_and_failure_paths_qualified","native_runtime_scalar_selection_qualified","alternate_nonzero_scalar_branch_qualified",
 "full_outer_callee_return_qualified","next_constant_data_dependency_qualified","stack_growth_guard_page_OS_qualified","new_kernel_build","production_code_changed","private_raw_material_exported")
TRUE=("original_nested_constructor_and_two_clear_returns_qualified","actual_nested_owner_relations_constructed","prior_callback_table_epochs_and_six_allocations_retained")
PER={"original_instruction_visits":592,"clear_instruction_visits":479,"heap_clear_store_chunks":1024,"stack_clear_store_chunks":80,
 "exact_source_store_chunks":1147,"nonstack_field_store_chunks":21,"rejected_owned_requests":104,"original_nested_constructor_returns_ABI_exact":1,
 "original_heap_clear_returns_ABI_exact":1,"original_stack_clear_returns_ABI_exact":1,"owned_allocation_calls":3,"owned_allocation_bytes":8272,"owned_OS_API_calls":0}
READS=[["0x5e8200",0,4],["0x5e8210",4,4],["0x5e8258",8,4],["0x5e8274",12,4],["0x5e8290",16,4]]
def contract(s):
 assert s["experiment"]=="E011DW" and s["status"]==STATUS and s["scenarios"]==256 and s["next_experiment"]=="E011DX"
 for k in FALSE:assert s[k] is False,k
 for k in TRUE:assert s[k] is True,k
 assert s["new_camera_starts"]==s["new_reboots"]==0
 dv=json.loads((R/"experiments/E004-front-ir-vd55g0/e011dv-original-cold-enumeration-buffer/SOURCE-SAFE.json").read_text())
 assert s["source_pins"]==dict(dv["source_pins"],**EXTRA) and len(s["source_pins"])==25 and s["image_sha256"]==dv["image_sha256"]
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 expected=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 rows=s["details"];assert len(rows)==256 and {tuple(r["DV"]["DU"]["DT"]["DS"][k] for k in axes) for r in rows}==expected
 prior={tuple(r["DU"]["DT"]["DS"][k] for k in axes):r for r in dv["details"]};assert len(prior)==256
 for r in rows:
  d=r["DV"];a=r["added"];assert d==prior[tuple(d["DU"]["DT"]["DS"][k] for k in axes)]
  assert all(a[k]==v for k,v in PER.items())
  for k in ("nine_distinct_live_allocations_retained","nested_header_and_zero_1024_slot_array_constructed","original_640_byte_stack_clear_exact",
   "whole_entry_to_frontier_memory_and_permissions_exact","ancestor_callbacks_epochs_nodes_redzones_container_and_buffer_retained","factory_guard_in_progress",
   "outer_and_nested_registry_locks_held","CRT_and_SRW_released"):assert a[k] is True
  assert a["exact_owned_header_read_contracts"]==READS
  assert a["stop_before_RVA"]=="0x600420" and a["next_dependency_RVA"]=="0x10f03a0" and a["next_dependency_bytes"]==8
  assert a["nested_actual_return_RVA"]=="0x6003cc" and a["heap_clear_actual_return_RVA"]=="0x5e8258" and a["stack_clear_actual_return_RVA"]=="0x6003f0"
  assert a["outer_callee_return_not_reached_RVA"]=="0x5f8ea8"
 assert s["added_totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(r["added"][k] for r in rows) for k in PER}
 assert s["inherited_DV_totals"]==dv["added_totals"] and s["inherited_DU_totals"]==dv["inherited_DU_totals"] and s["inherited_DT_totals"]==dv["inherited_DT_totals"] and s["inherited_DS_totals"]==dv["inherited_DS_totals"]
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s)
 result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="8adbe7b266f29d12e90d15abb5608161d7d71f5c" and result["qualification_exit_code"]==0 and result["native_rear_runtime_allowed"] is False
 assert result["added_original_instruction_visits"]==151552 and result["combined_original_instruction_visits"]==895232 and len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011DW" and f["next_experiment"]==n["experiment"]=="E011DX"
 assert f["original_nested_constructor_and_two_clear_returns_qualified"] is True and f["actual_nested_owner_relations_constructed"] is True
 assert f["full_outer_callee_return_qualified"] is False and f["latest_source_RS_query_checkpoint"]=="E011DM"
 assert n["resume_source_RVA"]=="0x600420" and n["dependency_RVA"]=="0x10f03a0" and n["dependency_bytes"]==8
 assert n["encoded_exit_table_used_entries"]==2 and n["encoded_exit_table_capacity"]==32
 assert n["published_buffer_bytes"]==18832 and n["nine_live_allocation_bytes"]==[24,128,256,48,48,18832,16,64,8192]
 assert n["nested_header_slots"]==1024 and n["nested_header_array_bytes"]==8192
 assert n["published_enumeration_global_TLS_epoch"]=="0x80000042" and n["retained_helper_epoch"]=="0x80000041" and n["factory_guard_in_progress"] is True
 assert n["active_callee_RVA"]=="0x600368" and n["active_callee_return_not_reached_RVA"]=="0x5f8ea8" and n["completed_nested_constructor_RVA"]=="0x5e81b8"
 count=0
 if "--selfcheck" in sys.argv:
  muts=[(k,True) for k in FALSE]+[(k,False) for k in TRUE]+[("scenarios",255),("new_camera_starts",1),("new_reboots",1)]
  for label,key,value in (("nestedABI","original_nested_constructor_returns_ABI_exact",0),("heapABI","original_heap_clear_returns_ABI_exact",0),
   ("stackABI","original_stack_clear_returns_ABI_exact",0),("allocation","owned_allocation_bytes",8256),("heapclear","heap_clear_store_chunks",1023),
   ("stackclear","stack_clear_store_chunks",79),("fields","nonstack_field_store_chunks",20),("reads","exact_owned_header_read_contracts",[]),
   ("lock","outer_and_nested_registry_locks_held",False),("factory","factory_guard_in_progress",False),("frontier","stop_before_RVA","0x600424"),
   ("memory","whole_entry_to_frontier_memory_and_permissions_exact",False),("return","nested_actual_return_RVA","0x5f8ea8"),("leases","nine_distinct_live_allocations_retained",False)):
   bad=copy.deepcopy(s);bad["details"][0]["added"][key]=value;muts.append(("__"+label,bad))
  bad=copy.deepcopy(s);bad["details"][0]["DV"]["DU"]["DT"]["DS"]["initial_global_epoch"]=41;muts.append(("__parent",bad))
  bad=copy.deepcopy(s);bad["details"][0]["DV"]["DU"]["DT"]["DS"]["allocation_poison"]=0;muts.append(("__matrix",bad))
  bad=copy.deepcopy(s);bad["added_totals"]["original_instruction_visits"]+=1;muts.append(("__totals",bad))
  bad=copy.deepcopy(s);bad["source_pins"]["0x5e81b8"]["body_bytes"]=544;muts.append(("__body",bad))
  for key,value in muts:
   bad=value if key.startswith("__") else copy.deepcopy(s)
   if not key.startswith("__"):bad[key]=value
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence/scope admitted: "+key)
 print(json.dumps({"status":"PASS_E011DW_REVIEW","scenarios":256,"added_original_visits":151552,"combined_original_visits":895232,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
