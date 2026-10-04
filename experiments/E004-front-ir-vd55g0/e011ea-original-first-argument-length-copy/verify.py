#!/usr/bin/env python3
"""Review first-argument length/copy, returned frames and retained scope."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2];P=R/"experiments/E004-front-ir-vd55g0/e011dz-original-parser-dispatch-variadic-argument"
STATUS="PASS_BOUNDED_ORIGINAL_FIRST_ARGUMENT_LENGTH_AND_COPY"
FALSE=("source_result_fixture_used","native_rear_runtime_allowed","full_constant_consumer_return_qualified","full_outer_callee_return_qualified",
"full_factory_or_first_helper_return_qualified","native_runtime_scalar_and_pointer_selection_qualified","alternate_nonzero_runtime_flag_paths_qualified",
"pointed_locale_tables_qualified","cookie_leaf_has_SP_preserving_ABI","stack_growth_guard_page_OS_qualified",
"remaining_format_or_argument_continuation_qualified","new_kernel_build","production_code_changed","private_raw_material_exported")
PER={"original_instruction_visits":179,"exact_source_store_chunks":25,"independent_argument_store_contracts":25,"rejected_owned_requests":195,
"exact_immutable_argument_reads":7,"original_callee_ABI_returns_exact":4,"original_argument_consumer_ABI_returns_exact":2,
"cookie_pop_convention_returns_exact":1,"exact_original_callee_entries":4,"owned_allocation_calls":0,"owned_OS_API_calls":0}
BOOL=("first_argument_complete_source_length_and_copy_qualified","nine_live_allocations_retained","whole_original_entry_to_frontier_memory_and_permissions_exact",
"outer_and_nested_registry_locks_held","CRT_and_SRW_released")
EXPECTED={"first_argument_length":12,"exact_private_argument_bytes_copied":12,"destination_remaining_zero_bytes":628,"retained_active_consumer_frames":7,
"stop_before_RVA":"0xca984c","next_dependency_RVA":"0x1370762","next_dependency_bytes":1,"current_SP_relative_outer_entry":-3200,
"variadic_cursor_relative_outer_entry":-1488,"output_cursor_relative_outer_entry":-1380,"outer_callee_return_not_reached_RVA":"0x5f8ea8"}
AUTH={'RVA': '0x10f0380', 'bytes': 16, 'file_backed': True, 'section_nonwritable': True, 'sha256': 'c1092551461cd5ac0ad08f8fae02ab47447e1fd1c0b5d3bc068c969e57053a95', 'literal_bytes_including_NUL': 13, 'literal_sha256': '3072831f71eeaba699423425c497fac7b56a1657abae573e8ac18b073018fb77', 'terminator_at_last_literal_byte': True, 'original_literal_contents_exported': False}
EXTRA={'0xf5e3e0': {'body_bytes': 184, 'ranges': [['0xf5e3e0', '0xf5e497']], 'sha256': 'ce5ad5d84ac2a5ff6ef3bf2de15ffb746b4d31ef4a73c941101e906506a749cf'}, '0xcad1f0': {'body_bytes': 200, 'ranges': [['0xcad1f0', '0xcad2b7']], 'sha256': '7c090b8f136c3934fd4da97aa8de33dcd52259357c6bb6f81d34892bd4705d05'}, '0xf5d480': {'body_bytes': 664, 'ranges': [['0xf5d480', '0xf5d4c7'], ['0xf5d4e0', '0xf5d5c3'], ['0xf5d5e0', '0xf5d62b'], ['0xf5d640', '0xf5d75f']], 'sha256': 'b7d952b2014e55260ce44226d14da79db6ec60e9d7d6756fafcb106340871dc3'}}
def contract(s):
 dz=json.loads((P/"SOURCE-SAFE.json").read_text())
 assert s["experiment"]=="E011EA" and s["status"]==STATUS and s["scenarios"]==256 and s["next_experiment"]=="E011EB"
 for k in FALSE:assert s[k] is False,k
 assert s["new_camera_starts"]==s["new_reboots"]==0 and s["first_argument_length_and_copy_qualified"] is True
 assert s["argument_data_authority"]==AUTH and s["runtime_initial_value_model_authority"]==dz["runtime_initial_value_model_authority"]
 assert s["source_pins"]==dict(dz["source_pins"],**EXTRA) and len(s["source_pins"])==39 and s["image_sha256"]==dz["image_sha256"]
 rows=s["details"];assert len(rows)==256 and [r["DZ"] for r in rows]==dz["details"]
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 wanted=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 assert {tuple(r["DZ"]["DY"]["DX"]["DW"]["DV"]["DU"]["DT"]["DS"][k] for k in axes) for r in rows}==wanted
 for row in rows:
  a=row["added"];assert all(a[k]==v for k,v in PER.items()) and all(a[k] is True for k in BOOL) and all(a[k]==v for k,v in EXPECTED.items())
 assert s["added_totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(row["added"][k] for row in rows) for k in PER}
 assert s["inherited_DZ_totals"]==dz["added_totals"]
 for k in ("DY","DX","DW","DV","DU","DT","DS"):assert s["inherited_"+k+"_totals"]==dz["inherited_"+k+"_totals"]
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s);result=json.loads((H/"RESULT.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="5977c2cf9e09a3868e9692ab85e77c6c739994f0" and result["qualification_exit_code"]==0
 assert result["added_original_instruction_visits"]==45824 and result["combined_original_instruction_visits"]==1024256 and len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert f["experiment"]=="E011EA" and f["next_experiment"]==n["experiment"]=="E011EB" and f["original_first_argument_length_and_copy_qualified"] is True
 assert f["remaining_format_or_argument_continuation_qualified"] is False and f["native_rear_runtime_allowed"] is False
 assert n["resume_source_RVA"]=="0xca984c" and n["next_dependency_RVA"]=="0x1370762" and n["next_dependency_bytes"]==1
 assert n["next_dependency_read_and_continuation_qualified"] is False and n["argument_data_authority"]==AUTH
 assert n["current_active_consumer_RVAs"]==["0x7ac38","0x7aca0","0x6bdd0","0x6bd48","0xcad868","0xca6280","0xca94e8"]
 assert n["pending_consumer_return_RVAs"]==["0x600440","0x7ac7c","0x7acdc","0x6be0c","0x6bd94","0xcad940","0xca634c"]
 assert n["current_SP_relative_outer_entry"]==-3200 and n["first_argument_length"]==12 and n["destination_remaining_zero_bytes"]==628
 assert n["output_cursor_relative_outer_entry"]==-1380 and n["variadic_cursor_relative_outer_entry"]==-1488
 assert n["stack_receiver_640_bytes_still_zero"] is False and n["nine_live_allocation_bytes"]==[24,128,256,48,48,18832,16,64,8192]
 count=0
 if "--selfcheck" in sys.argv:
  mutations=[]
  def put(path,value):
   bad=copy.deepcopy(s);at=bad
   for k in path[:-1]:at=at[k]
   at[path[-1]]=value;mutations.append(bad)
  for k in FALSE:put([k],True)
  for k,v in (("scenarios",255),("new_camera_starts",1),("new_reboots",1),("first_argument_length_and_copy_qualified",False)):put([k],v)
  for k,v in PER.items():put(["details",0,"added",k],v+1)
  for k in BOOL:put(["details",0,"added",k],False)
  for k,v in EXPECTED.items():put(["details",0,"added",k],v+1 if isinstance(v,int) else "unsupported")
  put(["argument_data_authority","bytes"],13);put(["argument_data_authority","literal_bytes_including_NUL"],12)
  put(["argument_data_authority","original_literal_contents_exported"],True);put(["source_pins","0xf5d480","body_bytes"],668)
  put(["added_totals","original_instruction_visits"],45825)
  put(["details",0,"DZ","DY","DX","DW","DV","DU","DT","DS","allocation_poison"],0)
  for bad in mutations:
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence or scope admitted")
 print(json.dumps({"status":"PASS_E011EA_REVIEW","scenarios":256,"added_original_visits":45824,"combined_original_visits":1024256,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
