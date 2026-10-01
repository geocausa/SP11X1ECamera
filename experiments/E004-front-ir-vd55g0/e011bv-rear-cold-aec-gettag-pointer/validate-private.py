#!/usr/bin/env python3
"""Read-only independent same-SP11 validation of consumed E011BV; never runs a camera."""
from pathlib import Path
import json,re,hashlib,copy,datetime
HERE=Path(__file__).resolve().parent
PRIVATE=HERE.parents[2].parent/"private/E011BV-20261001-2310A-captured"
TAGS=["FIRST","SECOND","PUBLISH","PUBLISH_AFTER","WRITE","WRITE_AFTER","READER","READ","READ_AFTER","COLD","COLD_AFTER"]
SIZES={"FIRST_OUT":2072,"SECOND_OUT":2072,"PUBLISH_OUT":2072,"PUBLISH_NODE":1280,"PUBLISH_POOL":720,"WRITE_OUT":2072,"WRITE_STORE":128,"WRITE_STORE_AFTER":128,"READER_NODE":1280,"READER_POOL":720,"READ_STORE":128,"READ_OUT":2072,"COLD_SOURCE":2072,"COLD_BEFORE":2072,"COLD_AFTER":2072,"COLD_SOURCE_AFTER":2072}
def textfile(p):
 b=p.read_bytes();return b.decode("utf-16" if b.startswith(bytes([255,254])) or b.startswith(bytes([254,255])) else "utf-8-sig")
def hx(e,t,k):return int(e[t][k],16)
def dc(e,t,k):return int(e[t][k],10)
def check(e,data,code,manifest,holder):
 for n,s in SIZES.items():assert len(data[n])==s,("size",n)
 for f in manifest["ranges"]:assert len(code[f["name"]])==f["bytes"] and hashlib.sha256(code[f["name"]]).hexdigest()==f["sha256"],("code",f["name"])
 assert len(manifest["ranges"])==12
 assert hx(e,"PUBLISH","tag")==hx(e,"WRITE","tag")==hx(e,"READ","tag")==hx(e,"READER","tag")==0x5000001c
 assert dc(e,"PUBLISH","bytes")==dc(e,"WRITE","bytes")==dc(e,"COLD","bytes")==2072
 assert hx(e,"FIRST","out")==hx(e,"PUBLISH","src")==hx(e,"WRITE","src")
 assert hx(e,"FIRST","tid")==hx(e,"PUBLISH","tid")==hx(e,"WRITE","tid")
 assert dc(e,"PUBLISH","firstPtrMatch")==dc(e,"PUBLISH","firstTidMatch")==dc(e,"WRITE","sameTid")==1
 assert hx(e,"WRITE","store")==hx(e,"READ","store") and dc(e,"READ","sameStore")==1
 assert hx(e,"READ","tid")==hx(e,"READ_AFTER","tid")==hx(e,"READER","tid")==hx(e,"COLD","tid")==hx(e,"COLD_AFTER","tid")
 assert dc(e,"READ","sameReaderTid")==dc(e,"READ_AFTER","sameTid")==dc(e,"COLD","readerTidMatch")==dc(e,"COLD_AFTER","sameTid")==1
 assert hx(e,"READ_AFTER","src")==hx(e,"COLD","src") and dc(e,"COLD","metadataSrcMatch")==dc(e,"COLD_AFTER","returnedDstMatch")==1
 assert hx(e,"WRITE","callerRVA")==0x5d6ef8 and hx(e,"READ","callerRVA")==0x5d54d0
 assert hx(e,"WRITE_AFTER","result")==hx(e,"PUBLISH_AFTER","result")==0
 pubPool=int.from_bytes(data["PUBLISH_NODE"][1200:1208],"little");readPool=int.from_bytes(data["READER_NODE"][1200:1208],"little")
 assert pubPool==readPool==hx(e,"READER","pool")
 for name in ["PUBLISH_OUT","WRITE_OUT","READ_OUT","COLD_SOURCE","COLD_AFTER","COLD_SOURCE_AFTER"]:assert data[name]==data["FIRST_OUT"],("payload",name)
 assert holder.count("START_BEGIN")==1 and "START_STATUS=Success" in holder and "STOP_PASS" in holder and "E011BV_HOLDER_END" in holder
 handles=int(re.search(r"STOP_PASS valid_4k_handles=([0-9]+)",holder).group(1));assert handles>=10
 return handles
def main():
 manifest=json.loads((HERE/"PRE-RUNTIME-SAFE.json").read_text())
 raw=(PRIVATE/"cdb-observer.raw").read_text(errors="replace");e={}
 for tag in TAGS:
  rows=re.findall(r"(?m)^E011BV_"+tag+r" (.+)$",raw);assert len(rows)==1,(tag,len(rows))
  e[tag]={k:v.replace(chr(96),"") for k,v in re.findall(r"([A-Za-z][A-Za-z0-9]*)=([0-9a-fA-F"+chr(96)+r"]+)",rows[0])}
 assert not re.search(r"Syntax error|Malformed|Numeric expression missing|Couldn.t resolve|Unable to|Command file execution failed",raw,re.I)
 data={n:(PRIVATE/"capture"/(n+".bin")).read_bytes() for n in SIZES}
 code={f["name"]:(PRIVATE/"capture"/("CODE_"+f["name"]+".bin")).read_bytes() for f in manifest["ranges"]}
 holder=textfile(PRIVATE/"holder.log")
 handles=check(e,data,code,manifest,holder)
 cleanup=json.loads(textfile(PRIVATE/"CLEANUP-WINDOWS-SAFE.json"))
 assert cleanup["CDB_exit_code"]==cleanup["holder_task_exit_code"]==0 and cleanup["manual_only_task_removed"]
 def dt(v):return datetime.datetime.fromisoformat(v.replace("Z","+00:00"))
 assert dt(cleanup["code_capture_latest_UTC"])<dt(cleanup["initial_live_qualification_tool_UTC"])<dt(cleanup["Start_release_UTC"])
 inv=json.loads(textfile(PRIVATE/"PRIVATE-HASH-INVENTORY.json"));total=0
 for f in inv:
  p=PRIVATE.joinpath(*f["name"].split(chr(92)));b=p.read_bytes()
  assert len(b)==f["bytes"] and hashlib.sha256(b).hexdigest()==f["sha256"];total+=len(b)
 failures=[]
 for label,fn in [
 ("getter_pointer",lambda ee,dd,cc,hh:ee["READ_AFTER"].update(src=hex(hx(ee,"COLD","src")+16)[2:])),
 ("store_identity",lambda ee,dd,cc,hh:ee["READ"].update(store=hex(hx(ee,"WRITE","store")+16)[2:])),
 ("wrong_property",lambda ee,dd,cc,hh:ee["READ"].update(tag="5000001d")),
 ("wrong_caller",lambda ee,dd,cc,hh:ee["READ"].update(callerRVA="5d5180")),
 ("wrong_pool",lambda ee,dd,cc,hh:dd.update(READER_NODE=dd["READER_NODE"][:1200]+bytes(8)+dd["READER_NODE"][1208:])),
 ("changed_read_payload",lambda ee,dd,cc,hh:dd.update(READ_OUT=bytes([dd["READ_OUT"][0]^1])+dd["READ_OUT"][1:])),
 ("changed_source_after",lambda ee,dd,cc,hh:dd.update(COLD_SOURCE_AFTER=bytes([dd["COLD_SOURCE_AFTER"][0]^1])+dd["COLD_SOURCE_AFTER"][1:])),
 ("wrong_loaded_code",lambda ee,dd,cc,hh:cc.update(STOREREAD=bytes([cc["STOREREAD"][0]^1])+cc["STOREREAD"][1:])),
 ("second_Start",lambda ee,dd,cc,hh:None)]:
  ee=copy.deepcopy(e);dd=dict(data);cc=dict(code);hh=holder
  fn(ee,dd,cc,hh)
  if label=="second_Start":hh+=" START_BEGIN"
  try:check(ee,dd,cc,manifest,hh)
  except AssertionError:failures.append(label)
  else:raise AssertionError(("negative accepted",label))
 win=json.loads(textfile(PRIVATE/"VALIDATION-SAFE.json"));assert win["valid_4k_handles"]==handles==449
 out={**win,"independent_same_SP11_Linux_recheck":True,"private_hash_inventory_files":len(inv),"private_hash_inventory_bytes":total,"tamper_fixtures_rejected":len(failures),"tamper_families":failures,"loaded_code_qualification_chronology_verified":True,"CDB_diagnostics":0,"bounded_live_cold_metadata_pointer_bridge_closed":True,"numeric_source_initialization_closed":False,"whole_camera_stack_parity_closed":False,"first_pair_requires_full_catalogue":False}
 (HERE/"VALIDATION-SAFE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+chr(10));print(json.dumps(out))
if __name__=="__main__":main()
