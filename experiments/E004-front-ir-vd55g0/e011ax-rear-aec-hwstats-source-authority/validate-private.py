#!/usr/bin/env python3
"""Recheck same-SP11 private Windows AEC captures and emit derived evidence only."""
from pathlib import Path
import hashlib,json,re,struct
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
ATTEMPT="E011AX-20261001-0055A";CAPTURE=ROOT.parent/"private"/(ATTEMPT+"-captured")
def main():
 c=CAPTURE/"capture";source=json.loads((CAPTURE/"VALIDATION-SAFE.json").read_text(encoding="utf-8-sig"))
 prepare=json.loads((HERE/"PREPARE-SAFE.json").read_text())
 raw=(CAPTURE/"cdb-observer.raw").read_text(errors="replace")
 def events(name):
  out=[]
  for m in re.finditer(r"^E011AX_"+name+r" ([^\r\n]+)",raw,re.M):
   e=dict(re.findall(r"([A-Za-z]+)=([0-9a-fA-F`]+)",m.group(1)));e["_position"]=m.start();out.append(e)
  return out
 def pointer(s):return int(s.replace("`",""),16)
 def record(name,size):
  b=(c/(name+".bin")).read_bytes();assert len(b)==size;return b
 recorded={r["name"]:r for r in source["record_hashes"]};assert len(recorded)==67
 assert set(recorded)=={f.name for f in c.iterdir()}
 for name,r in recorded.items():
  b=(c/name).read_bytes();assert len(b)==r["bytes"] and hashlib.sha256(b).hexdigest()==r["sha256"]
 for code in prepare["code_ranges"]:
  b=record("CODE_"+code["name"],code["bytes"]);assert hashlib.sha256(b).hexdigest()==code["sha256"]
 module=pointer(events("MODULE_BASE")[0]["base"])
 assert [p-module for p in struct.unpack("<3Q",record("CODE_TABLE",24))]==prepare["grid_vtable_first_three_target_rvas"]
 init=events("INIT");after=events("INIT_AFTER");get=events("GETTER");ga=events("GETTER_AFTER");consumer=events("CONSUMER");ca=events("CONSUMER_AFTER")
 callback=events("CALLBACK");cold=events("COLD");coldAfter=events("COLD_AFTER");engine=events("ENGINE_QUERY")
 assert tuple(map(len,[init,after,get,ga,consumer,ca,callback,cold,coldAfter,engine]))==(4,4,4,4,4,4,1,1,1,1)
 for i,e in enumerate(init,1):
  assert int(e["n"])==i
  old=record(f"INIT{i:02}_CACHE",96);new=record(f"INITAFTER{i:02}_CACHE",96)
  obj=record(f"INITAFTER{i:02}_SELF",48)
  assert old==new and struct.unpack_from("<Q",obj,24)[0]==pointer(e["cache"])
  assert all(after[i-1][k]=="1" for k in ["tidMatch","selfMatch","cacheMatch"])
 for i,e in enumerate(get,1):
  assert int(e["n"])==i and int(e["bytes"])==92
  obj=record(f"GETTER{i:02}_SELF",48);src=record(f"GETTER{i:02}_CACHE",96);out=record(f"GETTERAFTER{i:02}_OUT",92)
  assert struct.unpack_from("<Q",obj)[0]-module==prepare["grid_vtable_rva"]
  assert struct.unpack_from("<Q",obj,24)[0]==pointer(e["cache"])
  assert src==record(f"GETTERAFTER{i:02}_CACHE",96) and src[20:32]==out[68:80]
  assert ga[i-1]["tidMatch"]==ga[i-1]["outputMatch"]=="1"
  matches=[a for a in init if a["self"]==e["self"] and a["cache"]==e["cache"]]
  assert len(matches)==1 and record("INIT"+f'{int(matches[0]["n"]):02}'+"_CACHE",96)[20:32]==src[20:32]
 query=record("CALLBACK01_QUERY",40);desc=record("CALLBACK01_DESC",24)
 assert struct.unpack_from("<I",query)[0]==12 and struct.unpack_from("<I",query,32)[0]==1
 payload,allocated=struct.unpack_from("<2Q",desc);kind=struct.unpack_from("<I",desc,16)[0];assert (allocated,kind)==(92,10)
 joined=[e for e in get if pointer(e["output"])==payload and e["tid"]==callback[0]["tid"]]
 assert len(joined)==2
 primary=[e for e in consumer if pointer(e["frame"])+0x1a8==payload and e["tid"]==callback[0]["tid"]]
 assert len(primary)==1
 first,last=joined;pe=primary[0]
 assert engine[0]["_position"]<callback[0]["_position"]<first["_position"]<last["_position"]<pe["_position"]<cold[0]["_position"]
 primary_frame=record(f'CONSUMER{int(pe["n"]):02}_FRAME',92)
 assert primary_frame==record(f'GETTERAFTER{int(last["n"]):02}_OUT',92)
 assert first["self"]==last["self"] and first["cache"]==last["cache"]
 for i,e in enumerate(consumer,1):
  frame=record(f"CONSUMER{i:02}_FRAME",92);stats=record(f"CONSUMERAFTER{i:02}_STATS",128)
  assert frame==record(f"CONSUMERAFTER{i:02}_FRAME",92) and frame[68:80]==stats[48:60]
  assert all(ca[i-1][k]=="1" for k in ["tidMatch","frameMatch","statsMatch"])
 assert cold[0]["bytes"]=="2072" and coldAfter[0]["returnedDstMatch"]=="1"
 cs=record("COLD_SOURCE",2072);assert cs==record("COLD_SOURCE_AFTER",2072)==record("COLD_AFTER",2072)
 assert cs[48:60]==record(f'CONSUMERAFTER{int(pe["n"]):02}_STATS',128)[48:60]
 assert pointer(cold[0]["src"])!=pointer(pe["stats"]) and cold[0]["tid"]==pe["tid"]
 cleanup=json.loads((CAPTURE/"CLEANUP-SAFE.json").read_text(encoding="utf-8-sig"))
 assert cleanup["task_removed"] and cleanup["debugger_exited"] and cleanup["task_last_result"]==0
 assert cleanup["start_count"]==cleanup["stop_count"]==1 and cleanup["capture_files"]==67
 assert source["code_qualification_before_Start_verified"] and source["valid_4k_frame_handles"]==710
 safe=dict(source);safe.update({"independent_Linux_private_recheck":"PASS","primary_same_output_getter_same_object_and_cache":True,
 "first_BG_joined_getter_weight_fields_match_consumed_primary_frame":record(f'GETTERAFTER{int(first["n"]):02}_OUT',92)[68:80]==primary_frame[68:80],
 "whole_primary_output_matches_last_observed_getter":True,"second_same_output_getter_callback_selector_live_qualified":False,
 "second_same_output_getter_not_assigned_a_selector_by_timing":True,"cold_metadata_bridge_closed":False,
 "cold_source_pointer_same_as_primary_statistics":False,"cold_source_and_primary_same_thread":True,
 "entire_cold_copy_bytes_exact":2072,"private_records_same_SP11":True,"retained_values_promoted_to_policy":False,
 "original_runtime_executable_bytes_intentionally_instrumented_by_software_breakpoints":True,
 "original_disk_image_modified":False,"new_kernel_build_performed":False,"production_C_changed":False,
 "source_locks":[{"path":str((HERE/f).relative_to(ROOT)),"sha256":hashlib.sha256((HERE/f).read_bytes()).hexdigest()} for f in
 ["prepare-private.py","make-observer.py","holder.ps1","validate-private.py","validate-private.ps1","source-private.py"]]})
 (HERE/"VALIDATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
 (HERE/"LOADED-QUALIFICATION-SAFE.json").write_text(json.dumps(json.loads((CAPTURE/"LOADED-QUALIFICATION-SAFE.json").read_text(encoding="utf-8-sig")),indent=2,sort_keys=True)+"\n")
 (HERE/"CLEANUP-SAFE.json").write_text(json.dumps(cleanup,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in safe.items() if k not in ["record_hashes","source_locks"]},indent=2))
if __name__=="__main__":main()
