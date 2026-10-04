#!/usr/bin/env python3
"""Review bounded parser dependencies, retained state and unqualified string frontier."""
from pathlib import Path
import copy,hashlib,itertools,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
STATUS="PASS_BOUNDED_ORIGINAL_PARSER_DISPATCH_AND_VARIADIC_ARGUMENT"
FALSE=("source_result_fixture_used","native_rear_runtime_allowed","pointed_argument_string_contents_or_length_qualified",
"full_constant_consumer_return_qualified","full_outer_callee_return_qualified","full_factory_or_first_helper_return_qualified",
"native_runtime_scalar_and_pointer_selection_qualified","alternate_nonzero_runtime_flag_paths_qualified","pointed_locale_tables_qualified",
"cookie_leaf_has_SP_preserving_ABI","stack_growth_guard_page_OS_qualified","next_string_helper_qualified",
"new_kernel_build","production_code_changed","private_raw_material_exported")
PER={"original_instruction_visits":168,"exact_source_store_chunks":38,"independent_parser_store_contracts":38,"rejected_owned_requests":277,
"exact_immutable_data_reads":9,"cookie_frame_returns_convention_exact":1,"scalar_helper_ABI_returns_exact":1,
"exact_nested_consumer_entries":3,"owned_allocation_calls":0,"owned_OS_API_calls":0}
BOOL=("first_variadic_argument_pointer_acquired","variadic_cursor_advanced_by_8","nine_live_allocations_retained","stack_destination_640_bytes_still_zero",
"whole_original_entry_to_frontier_memory_and_permissions_exact","outer_and_nested_registry_locks_held","CRT_and_SRW_released")
EXPECTED={"retained_active_consumer_frames":9,"stop_before_RVA":"0xcace90","next_callee_RVA":"0xf5e3e0","next_callee_return_RVA":"0xcace94",
"current_SP_relative_outer_entry":-3360,"next_argument_pointer_RVA":"0x10f0380","next_string_limit":2147483647,
"variadic_cursor_relative_outer_entry":-1488,"outer_callee_return_not_reached_RVA":"0x5f8ea8"}
EXTRA={
"0xca94e8":{"body_bytes":1028,"ranges":[["0xca94e8","0xca98eb"]],"sha256":"8e1aa3dcf0d019df157030034475dc1fe87defc61d765e4f5deecac6b56b150a"},
"0xcab178":{"body_bytes":1252,"ranges":[["0xcab178","0xcab65b"]],"sha256":"dd3ea3cf979b2411d9dabcce803e553a9f29929dcce44a6f623b0666de57835f"},
"0xcacdf8":{"body_bytes":184,"ranges":[["0xcacdf8","0xcaceaf"]],"sha256":"e4e3964e1c8eb7a8fb470069d381b057652975b02ac2450c7249b715cf068a3c"},
"0xca65a8":{"body_bytes":64,"ranges":[["0xca65a8","0xca65e7"]],"sha256":"73db5979ec481e935a61010e1c9120f40197182accea2442c026aabdba25957c"}}
NEXT={"entry_RVA":"0xf5e3e0","body_bytes":184,"ranges":[["0xf5e3e0","0xf5e497"]],"sha256":"ce5ad5d84ac2a5ff6ef3bf2de15ffb746b4d31ef4a73c941101e906506a749cf"}
AUTH=[{'RVA': '0x1370760', 'bytes_including_NUL': 7, 'sha256': '3c6150311763e7162e56773dd3a25a716f251c11cd14f9a4ebc57531ecb50430', 'file_backed': True, 'section_nonwritable': True, 'terminator_at_last_byte': True, 'original_literal_contents_exported': False}, {'RVA': '0xf8b21b', 'bytes': 1, 'sha256': '4bf5122f344554c53bde2ebb8cd2b7e3d1600ad631c385a5d7cce23c7785459a', 'file_backed': True, 'section_nonwritable': True, 'sparse_cell_authority_only': True}, {'RVA': '0xf8b222', 'bytes': 1, 'sha256': '4bf5122f344554c53bde2ebb8cd2b7e3d1600ad631c385a5d7cce23c7785459a', 'file_backed': True, 'section_nonwritable': True, 'sparse_cell_authority_only': True}, {'RVA': '0xca98f0', 'bytes': 4, 'sha256': '25cb28d3768e2a7055eeedc507751889495fc6131f85dab1ce0ce72ff303b324', 'file_backed': True, 'section_nonwritable': True, 'sparse_cell_authority_only': True}, {'RVA': '0xf8b2b7', 'bytes': 1, 'sha256': 'beead77994cf573341ec17b58bbf7eb34d2711c993c1d976b128b3188dc1829a', 'file_backed': True, 'section_nonwritable': True, 'sparse_cell_authority_only': True}, {'RVA': '0xf8b2a2', 'bytes': 1, 'sha256': 'ca358758f6d27e6cf45272937977a748fd88391db679ceda7dc7bf1f005ee879', 'file_backed': True, 'section_nonwritable': True, 'sparse_cell_authority_only': True}, {'RVA': '0xca9908', 'bytes': 4, 'sha256': '447e12701a0d03cf90a4ad7f02f1a045b35d284e26fe520440edb116d76bf700', 'file_backed': True, 'section_nonwritable': True, 'sparse_cell_authority_only': True}, {'RVA': '0xcab724', 'bytes': 4, 'sha256': 'fcd04ecb4a5b36f9f092c7c47141908f25c274f1a1758e78731a16d0fd4897d7', 'file_backed': True, 'section_nonwritable': True, 'sparse_cell_authority_only': True}]
PARENT=R/"experiments/E004-front-ir-vd55g0/e011dy-original-cold-runtime-context-receiver"
def contract(s):
 dy=json.loads((PARENT/"SOURCE-SAFE.json").read_text())
 assert s["experiment"]=="E011DZ" and s["status"]==STATUS and s["scenarios"]==256 and s["next_experiment"]=="E011EA"
 for k in FALSE:assert s[k] is False,k
 assert s["new_camera_starts"]==s["new_reboots"]==0 and s["bounded_literal_and_sparse_parser_cells_qualified"] is True
 assert s["immutable_data_authority"]==AUTH and s["runtime_initial_value_model_authority"]==dy["runtime_initial_value_model_authority"]
 assert s["source_pins"]==dict(dy["source_pins"],**EXTRA) and len(s["source_pins"])==36 and s["image_sha256"]==dy["image_sha256"]
 axes=("stack_bias","loader_index","thread_epoch","initial_bound_sentinel","diagnostic_X0","OS_void_X0","allocation_poison")
 expected=set(itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)))
 rows=s["details"];assert len(rows)==256 and [r["DY"] for r in rows]==dy["details"]
 assert {tuple(r["DY"]["DX"]["DW"]["DV"]["DU"]["DT"]["DS"][k] for k in axes) for r in rows}==expected
 for row in rows:
  a=row["added"];assert all(a[k]==v for k,v in PER.items()) and all(a[k] is True for k in BOOL) and all(a[k]==v for k,v in EXPECTED.items())
 assert s["added_totals"]=={k:v*256 for k,v in PER.items()}=={k:sum(row["added"][k] for row in rows) for k in PER}
 assert s["inherited_DY_totals"]==dy["added_totals"]
 for k in ("DX","DW","DV","DU","DT","DS"):assert s["inherited_"+k+"_totals"]==dy["inherited_"+k+"_totals"]
def main():
 s=json.loads((H/"SOURCE-SAFE.json").read_text());contract(s)
 result=json.loads((H/"RESULT.json").read_text());f=json.loads((H/"FRONTIER-SAFE.json").read_text());n=json.loads((H/"NEXT-SOURCE.json").read_text())
 assert result["status"]==STATUS and result["base_commit"]=="5f8d03785406985df05420f81ea1bcf2720d268a" and result["qualification_exit_code"]==0
 assert result["added_original_instruction_visits"]==43008 and result["combined_original_instruction_visits"]==978432 and len(result["source_locks"])==11
 for rel,pin in result["source_locks"].items():
  p=(R/rel).resolve();assert p.is_relative_to(R) and hashlib.sha256(p.read_bytes()).hexdigest()==pin,rel
 assert f["experiment"]=="E011DZ" and f["next_experiment"]==n["experiment"]=="E011EA" and f["original_parser_dispatch_variadic_argument_qualified"] is True
 for k in FALSE:
  if k in f:assert f[k] is False
 assert n["resume_source_RVA"]=="0xcace90" and n["next_callee_RVA"]=="0xf5e3e0" and n["next_callee_return_RVA"]=="0xcace94"
 assert n["next_callee_exact_metadata"]==NEXT and n["next_callee_execution_qualified"] is False
 assert n["immutable_data_authority"]==AUTH and n["pointed_argument_string_contents_or_length_qualified"] is False
 assert n["current_active_consumer_RVAs"]==["0x7ac38","0x7aca0","0x6bdd0","0x6bd48","0xcad868","0xca6280","0xca94e8","0xcab178","0xcacdf8"]
 assert n["pending_consumer_return_RVAs"]==["0x600440","0x7ac7c","0x7acdc","0x6be0c","0x6bd94","0xcad940","0xca634c","0xca9840","0xcab1f8"]
 assert n["current_SP_relative_outer_entry"]==-3360 and n["next_argument_pointer_RVA"]=="0x10f0380" and n["next_string_limit"]==2147483647
 assert n["variadic_cursor_relative_outer_entry"]==-1488 and n["parser_cursor_RVA"]=="0x1370762" and n["stack_receiver_640_bytes_still_zero"] is True
 assert n["nine_live_allocation_bytes"]==[24,128,256,48,48,18832,16,64,8192] and n["cookie_leaf_has_SP_preserving_ABI"] is False
 count=0
 if "--selfcheck" in sys.argv:
  mutations=[]
  def put(path,value):
   bad=copy.deepcopy(s);at=bad
   for k in path[:-1]:at=at[k]
   at[path[-1]]=value;mutations.append(bad)
  for k in FALSE:put([k],True)
  for k,v in (("scenarios",255),("new_camera_starts",1),("new_reboots",1),("bounded_literal_and_sparse_parser_cells_qualified",False)):put([k],v)
  for k,v in PER.items():put(["details",0,"added",k],v+1)
  for k in BOOL:put(["details",0,"added",k],False)
  for k,v in EXPECTED.items():put(["details",0,"added",k],v+1 if isinstance(v,int) else "unsupported")
  put(["immutable_data_authority",0,"bytes_including_NUL"],8)
  put(["immutable_data_authority",1,"sparse_cell_authority_only"],False)
  put(["source_pins","0xca65a8","body_bytes"],68)
  put(["added_totals","original_instruction_visits"],43009)
  put(["details",0,"DY","DX","DW","DV","DU","DT","DS","allocation_poison"],0)
  for bad in mutations:
   try:contract(bad)
   except AssertionError:count+=1
   else:raise AssertionError("unsupported evidence or scope admitted")
 print(json.dumps({"status":"PASS_E011DZ_REVIEW","scenarios":256,"added_original_visits":43008,"combined_original_visits":978432,"source_locks":11,"scope_evidence_mutations_rejected":count,"native_rear_runtime_allowed":False}))
if __name__=="__main__":main()
