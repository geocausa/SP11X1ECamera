#!/usr/bin/env python3
"""Review exact constant-data authority, retained setup effects and bounded scope."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
STATUS="PASS_BOUNDED_ORIGINAL_CONSTANT_DATA_CONSUMER_SETUP"
FALSE=("source_result_fixture_used","native_rear_runtime_allowed","full_constant_consumer_return_qualified","full_outer_callee_return_qualified",
"full_factory_or_first_helper_return_qualified","next_runtime_dependency_qualified","constant_pointed_strings_or_format_contents_qualified",
"native_CRT_runtime_scalar_selection_qualified","stack_growth_guard_page_OS_qualified","new_kernel_build","production_code_changed","private_raw_material_exported")
PER={"original_instruction_visits":75,"exact_source_store_chunks":33,"rejected_owned_requests":204,"exact_opaque_constant_reads":1,
"original_leaf_returns_ABI_exact":1,"exact_active_consumer_entries":5,"independent_setup_store_contracts":33,"owned_allocation_calls":0,"owned_OS_API_calls":0}
DATA={"RVA":"0x10f03a0","bytes":8,"sha256":"a2fb00d4cf5a726758f3b5d24abbf631cccc4da72abd78c7e7556755fce7d726","file_backed":True,"section_nonwritable":True,"opaque":True}
EXTRA={
"0x7ac38":{"body_bytes":104,"ranges":[["0x7ac38","0x7ac9f"]],"sha256":"e116b84a78df86ea5e6e25179a5cd2acca434f07365cf00d0c249b97f28ea611"},
"0x7aca0":{"body_bytes":84,"ranges":[["0x7aca0","0x7acf3"]],"sha256":"6b302c4ecbc82135952ef5bb6e58184338b7fda2b1fdd9ef14a7d535cfbec4e4"},
"0x6bdd0":{"body_bytes":80,"ranges":[["0x6bdd0","0x6be1f"]],"sha256":"455b961625e30f926b1cee4e3979994807df131706393611c18e23617bb1ef06"},
"0x6bd48":{"body_bytes":132,"ranges":[["0x6bd48","0x6bdcb"]],"sha256":"3f73ed17e48df056ce5d481e0f27b003137b1ef73e5ad750d3a7d6bd95dd33ca"},
"0xedd0":{"body_bytes":12,"ranges":[["0xedd0","0xeddb"]],"sha256":"fccd30fe0400a87e1bee6601eac29919f8c78e65be18e9fabd5afa7982d92d44"}}
def contract(s):
 assert s["experiment"]=="E011DX" and s["status"]==STATUS and s["scenarios"]==256 and s["next_experiment"]=="E011DY"
 for k in FALSE:assert s[k] is False,k
 assert s["new_camera_starts"]==s["new_reboots"]==0 and s["constant_data_authority"]==DATA
 dw=json.loads((R/"experiments/E004-front-ir-vd55g0/e011dw-original-nested-enumeration-container/SOURCE-SAFE.json").read_text())
 assert s["source_pins"]==dict(dw["source_pins"],**EXTRA) and len(s["source_pins"])==30 and s["image_sha256"]==dw["image_sha256"]
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 expected=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 rows=s["details"];assert len(rows)==256 and [r["DW"] for r in rows]==dw["details"]
 assert {tuple(r["DW"]["DV"]["DU"]["DT"]["DS"][k] for k in axes) for r in rows}==expected
 for row in rows:
  a=row["added"];assert all(a[k]==v for k,v in PER.items())
  for k in ("nine_live_allocations_retained","whole_original_entry_to_frontier_memory_and_permissions_exact","stack_receiver_640_bytes_still_zero","outer_and_nested_registry_locks_held","CRT_and_SRW_released"):assert a[k] is True
  assert (a["stop_before_RVA"],a["next_dependency_RVA"],a["next_dependency_bytes"])==("0x6bd8c","0x17a1150",8)
  assert a["active_consumer_RVAs"]==["0x7ac38","0x7aca0","0x6bdd0","0x6bd48"] and a["outer_callee_return_not_reached_RVA"]=="0x5f8ea8"
 assert s["added_totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(row["added"][k] for row in rows) for k in PER}
 assert s["inherited_DW_totals"]==dw["added_totals"]
 for k in ("DV","DU","DT","DS"):assert s["inherited_"+k+"_totals"]==dw["inherited_"+k+"_totals"]
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s)
 result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="aab6cf3aa2a7970423eb73fe694052c044be0a43"
 assert result["qualification_exit_code"]==0 and result["native_rear_runtime_allowed"] is False
 assert result["added_original_instruction_visits"]==19200 and result["combined_original_instruction_visits"]==914432 and len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011DX" and f["next_experiment"]==n["experiment"]=="E011DY"
 assert f["original_constant_data_and_consumer_setup_qualified"] is True and f["latest_source_RS_query_checkpoint"]=="E011DM"
 assert f["full_constant_consumer_return_qualified"] is False and f["full_outer_callee_return_qualified"] is False
 assert n["resume_source_RVA"]=="0x6bd8c" and n["dependency_RVA"]=="0x17a1150" and n["dependency_bytes"]==8
 assert n["current_active_consumer_RVAs"]==["0x7ac38","0x7aca0","0x6bdd0","0x6bd48"]
 assert n["completed_leaf_RVA"]=="0xedd0" and n["completed_leaf_return_RVA"]=="0x6bd70" and n["completed_leaf_result_RVA"]=="0x17a1150"
 assert n["stack_receiver_640_bytes_still_zero"] is True and n["published_buffer_bytes"]==18832
 assert n["encoded_exit_table_used_entries"]==2 and n["encoded_exit_table_capacity"]==32 and n["nine_live_allocation_bytes"]==[24,128,256,48,48,18832,16,64,8192]
 count=0
 if "--selfcheck" in sys.argv:
  mutations=[]
  def put(path,value):
   bad=copy.deepcopy(s);at=bad
   for k in path[:-1]:at=at[k]
   at[path[-1]]=value;mutations.append(bad)
  for k in FALSE:put([k],True)
  for k,v in (("scenarios",255),("new_camera_starts",1),("new_reboots",1)):put([k],v)
  for k,v in PER.items():put(["details",0,"added",k],v+1)
  for k in ("nine_live_allocations_retained","whole_original_entry_to_frontier_memory_and_permissions_exact","stack_receiver_640_bytes_still_zero","outer_and_nested_registry_locks_held","CRT_and_SRW_released"):put(["details",0,"added",k],False)
  put(["details",0,"added","stop_before_RVA"],"0x6bd90")
  put(["details",0,"added","active_consumer_RVAs"],[])
  put(["constant_data_authority","bytes"],64);put(["constant_data_authority","section_nonwritable"],False);put(["constant_data_authority","sha256"],"0"*64)
  put(["source_pins","0xedd0","body_bytes"],16)
  put(["added_totals","original_instruction_visits"],19201)
  put(["details",0,"DW","DV","DU","DT","DS","allocation_poison"],0)
  for bad in mutations:
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence or scope admitted")
 print(json.dumps({"status":"PASS_E011DX_REVIEW","scenarios":256,"added_original_visits":19200,"combined_original_visits":914432,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
