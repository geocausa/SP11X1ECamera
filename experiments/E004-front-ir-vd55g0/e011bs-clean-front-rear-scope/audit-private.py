#!/usr/bin/env python3
"""E011BS bounded inventory for one-mode clean front/rear priority; no camera access."""
from pathlib import Path
import importlib.util,hashlib,json,collections,re
HERE=Path(__file__).resolve().parent;EX=HERE.parent
sp=importlib.util.spec_from_file_location("bs_module_inventory",EX/"e011br-rear-selected-module-metadata/source-private.py")
BR=importlib.util.module_from_spec(sp);sp.loader.exec_module(BR)
def members(path,tag):
 source=path.read_text();start=source.index(tag+" {");end=source.index("};",start)
 fields=re.findall(r"\bstruct\s+(\w+)\s+(\w+)\s*;",source[start:end])
 assert fields
 return [{"type":kind,"member":name} for kind,name in fields]
def main():
 cases=[];union=set()
 for filename,sha in BR.BQ.BP.BO.BO.BM.BL.BH.FIXTURE.AV.FILES[1:]:
  blob=(BR.BQ.BP.BO.BO.BM.BL.BH.FIXTURE.AV.ARCHIVE/filename).read_bytes()
  assert hashlib.sha256(blob).hexdigest()==sha
  f=BR.Production(blob,0);loader=f.run_full()
  names=collections.Counter(name for sid,selector,name in f.br_modules.values())
  owners=collections.Counter((owner-f.nodes)//160 for owner,module,selector,name,slot in f.br_stores)
  union.update(names)
  cases.append({"source_sha256":sha,"placement":0,"loaded_module_instances":len(f.br_modules),
   "distinct_embedded_source_names":len(names),"instances_repeating_a_source_name":len(f.br_modules)-len(names),
   "source_mode_nodes":len(f.records),"ordinary_unflagged_profile_nodes":sum(not row[2] for row in f.records.values()),
   "module_map_owners":len(owners),"original_loader_success":loader["original_loader_success_boolean"],
   "original_reader_returns":loader["source_reader_full_returns"],
   "all_module_dispatches_counted":len(f.br_modules)==loader["original_module_dispatches"]})
 regpath=EX/"e007d-rear-register-provider-integration/camss-e007d-register-integration.inc"
 reg=members(regpath,"struct e007d_rear_register_state")
 dmipath=EX/"e007v-rear-dsx101-clean-provider/camss-e007v-dsx101.inc"
 dmi=members(dmipath,"struct e007v_rear_dmi_state")
 result={"experiment":"E011BS","status":"PASS_BOUNDED_INVENTORY_AND_BASELINE_SCOPE_RECORDED",
  "base_commit":"c737828e7118600daf7ab2f8253862c303010255","source_cases":cases,
  "loaded_rear_module_instances_across_two_sources":sum(c["loaded_module_instances"] for c in cases),
  "distinct_embedded_source_names_across_two_sources":len(union),
  "distinct_name_count_is_not_feature_count_or_mandatory_set":True,
  "register_state_member_groups":reg,"register_state_member_groups_count":len(reg),
  "DMI_wrapper_member_groups":dmi,
  "current_composer_schema_members_are_not_individual_required_feature_proof":True,
  "minimal_enabled_module_dependency_closure_proven":False,
  "minimal_native_ISP_profile_deployed":False,"full_catalogue_port_required_before_first_image":False,
  "renamed_key_work_is_conditional_on_baseline_reachable_consumers":True,
  "first_milestone":"one normal colour mode per physical RGB camera, finite front then rear then off image test",
  "optional_feature_targets_deferred":["AI scene or face enhancement","beautification and effects","portrait blur","HDR and multi-frame processing","advanced stabilization","additional modes and resolutions"],
  "deferred_targets_are_scope_decisions_not_claims_that_the_OEM_uses_them":True,
  "first_image_may_use_explicit_manual_exposure_white_balance_or_focus_with_reported_limits":True,
  "runtime_hardware_dependency_gates_unchanged":True,
  "captured_scalars_as_producer_inputs":False,"originals_exported":False,
  "new_camera_starts":0,"new_reboots":0,"native_rear_runtime_allowed":False,
  "production_C_changed":False,"kernel_build_performed":False,"whole_camera_stack_parity_closed":False}
 (HERE/"INVENTORY-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in result.items() if k not in ["register_state_member_groups","DMI_wrapper_member_groups","optional_feature_targets_deferred"]}),flush=True)
if __name__=="__main__":main()
