#!/usr/bin/env python3
"""Explicitly bounded cache/frame checks; keeps seven-field source/receiver qualification OPEN."""
from pathlib import Path
import importlib.util,copy,json,hashlib,re,datetime
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
ID="E011BX-20261002-0030A";PRIVATE=ROOT.parent/"private"/(ID+"-captured")
s=importlib.util.spec_from_file_location("bx_strict",HERE/"validate-private.py");V=importlib.util.module_from_spec(s);s.loader.exec_module(V)
def main():
 m=json.loads((HERE/"PRE-RUNTIME-SAFE.json").read_text())
 raw=V.readtext(PRIVATE/"cdb-observer.raw");events=V.parse(raw)
 base=int(re.findall(r"(?m)^E011BX_MODULE_BASE base=([0-9a-fA-F]+)",raw.replace(chr(96),""))[0],16)
 expected=json.loads(V.readtext(PRIVATE/"SOURCE-EXPECTED.private.json"))
 data={f.stem:f.read_bytes() for f in (PRIVATE/"capture").glob("*.bin")};holder=V.readtext(PRIVATE/"holder.log")
 corrected=copy.deepcopy(events);fixes=0
 for i in range(1,3):
  for tag,prefix in [("QUERY","QUERY"),("QUERYAFTER","QUERYAFTER")]:
   descriptor=data[f"{prefix}{i:02}_DESC"]
   for key,off,wrong in [("written",12,0x12),("type",16,0x16)]:
    # Original log uses MASM hex +12/+16; only written (wrong+18) lies within24.
    if wrong+4<=len(descriptor):assert int(events[tag][i-1][key])==V.u32(descriptor,wrong)
    corrected[tag][i-1][key]=str(V.u32(descriptor,off));fixes+=1
 try:V.validate(corrected,data,m,expected,base,holder)
 except AssertionError as e:strict=str(e)
 else:raise AssertionError("strict source unexpectedly accepted")
 assert strict=="typed source module metadata"
 facts=V.validate(corrected,data,m,expected,base,holder,bounded=True)
 rejected=[]
 cases=[
 ("short_written",lambda e,d:e["QUERYAFTER"][0].update(written="0")),
 ("wrong_type",lambda e,d:e["QUERY"][0].update(type="99")),
 ("changed_callback_identity",lambda e,d:e["QUERY"][0].update(callbackRVA="36e464")),
 ("wrong_first_pointer",lambda e,d:e["FIRST"][0].update(frame=format(V.hx(e["FIRST"][0],"frame")+8,"x"))),
 ("changed_publication",lambda e,d:d.update(PUBLISH_OUT=bytes([d["PUBLISH_OUT"][0]^1])+d["PUBLISH_OUT"][1:])),
 ("changed_retained_cache",lambda e,d:d.update(GETTER01_CACHE=bytes(120))),
 ("changed_source_metadata",lambda e,d:d.update(NAMED01_OBJECT=bytes(384))),
 ("changed_loaded_code",lambda e,d:d.update(CODE_QUERY=bytes(len(d["CODE_QUERY"]))))]
 for name,fn in cases:
  ee=copy.deepcopy(corrected);dd=dict(data);fn(ee,dd)
  try:V.validate(ee,dd,m,expected,base,holder,bounded=True)
  except AssertionError:rejected.append(name)
  else:raise AssertionError("negative accepted: "+name)
 clean=json.loads(V.readtext(PRIVATE/"CLEANUP-WINDOWS-SAFE.json"));qual=json.loads(V.readtext(PRIVATE/"LOADED-QUALIFICATION-SAFE.json"));release=json.loads(V.readtext(PRIVATE/"START-RELEASE-SAFE.json"))
 assert clean["CDB_exit_code"]==clean["holder_task_exit_code"]==0 and clean["manual_only_task_removed"]
 def dt(v):return datetime.datetime.fromisoformat(v.replace("Z","+00:00"))
 assert dt(clean["code_capture_latest_UTC"])<dt(qual["qualified_UTC"])<dt(release["Start_release_UTC"])
 inventory=[{"name":str(p.relative_to(PRIVATE)),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(PRIVATE.rglob("*")) if p.is_file()]
 inventory_path=PRIVATE.parent/(ID+"-Linux-inventory.private.json")
 if inventory_path.exists():
  previous=json.loads(inventory_path.read_text());assert previous==inventory,"private snapshot inventory changed; audit before rebaseline"
 else:inventory_path.write_text(json.dumps(inventory,indent=2)+"\n")
 snapshot=json.loads((HERE/"PRIVATE-SNAPSHOT-SAFE.json").read_text())
 assert snapshot["same_SP11_readonly_Windows_snapshot_files_rechecked"]==len(inventory)
 assert snapshot["snapshot_bytes"]==sum(x["bytes"] for x in inventory)
 out={"experiment":"E011BX","attempt":ID,"status":"PARTIAL_SOURCE_PROFILE_AND_RECEIVER_SCOPE_PASS_LIVE_CACHE_FIRST_FRAME_JOIN",
  **facts,"source_named_modules":4,"retained_grid_initializations":4,"source_metadata_fields_match":6,
  "source_numeric_profile_high_word_mismatch_modules":4,"strict_seven_field_source_validation_accepted":False,
  "live_direct_callback_RVA":"0x36E460","owned_E011BW_callback_RVA":"0x372E40",
  "live_callback_code_range_source_qualified_before_Start":False,"interface_fixture_matches_actual_live_receiver":False,
  "actual_GetParam_receiver_bootstrap_closed":False,"observed_callback_pointer_only":True,
  "source_weight_bytes_match_independent_Default_sources":True,"captured_weights_used_as_producer_constants":False,
  "descriptor_allocated_bytes":92,"descriptor_written_bytes_each":92,"descriptor_types":[10,21],
  "printf_scalar_fields_corrected_from_complete_retained_descriptors":fixes,
  "original_printf_log_preserved":True,"original_metadata_mismatch_retained":True,
  "source_cache_to_first_frame_pointer_join_closed":True,"first_conversion_publication_bytes_equal":2072,
  "named_array_retention_getter_query_frame_weights_pointer_byte_joins_pass":True,
  "full_original_live_callback_source_chain_claimed":False,"cold_numeric_profile_policy_closed":False,
  "loaded_code_ranges_qualified":11,"loaded_tables_qualified":1,"pre_Start_qualification_chronology_verified":True,
  "private_record_files":len(data),"private_record_bytes":sum(map(len,data.values())),
  "private_inventory_files":len(inventory),"private_inventory_bytes":sum(x["bytes"] for x in inventory),
  "private_snapshot_same_SP11_readonly_source_recheck_files":len(inventory),
  "converter_return_register_status_ABI_unqualified":True,"converter_return_register_used_as_success_status":False,
  "Windows_private_inventory_file_absent":True,"same_SP11_Linux_inventory_created":True,
  "tamper_fixtures_rejected":len(rejected),"tamper_families":rejected,"camera_Starts":1,"successful_stop":True,
  "CDB_diagnostics":0,"cleanup_verified":True,"native_rear_runtime_allowed":False,
  "actual_opened_filename_closed":False,"new_Linux_front_back_image_test":False,
  "original_bytes_exported":False,"optical_images_saved":False}
 (HERE/"VALIDATION-SAFE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out))
if __name__=="__main__":main()
