#!/usr/bin/env python3
"""Independent read-only consumed live validation on SP11; no camera access."""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,re,struct
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
TAGS=["NAMED","INIT","INITAFTER","ENVELOPE","QUERY","QUERYAFTER","GETTER","GETTERAFTER","FIRST","FIRSTAFTER","PUBLISH"]
def readtext(p):
 b=p.read_bytes();return b.decode("utf-16" if b[:2] in [b"\xff\xfe",b"\xfe\xff"] else "utf-8-sig")
def parse(raw):
 assert not re.search(r"Syntax error|Malformed|Numeric expression missing|Couldn.t resolve|Unable to|Command file execution failed",raw,re.I),"observer diagnostics"
 raw=raw.replace(chr(96),"");out={}
 for tag in TAGS:
  rows=re.findall(r"(?m)^E011BX_"+tag+r" (.+)$",raw)
  out[tag]=[{k:v for k,v in re.findall(r"([A-Za-z][A-Za-z0-9]*)=([0-9a-fA-F]+)",row)} for row in rows]
 return out
def hx(e,k):return int(e[k],16)
def dc(e,k):return int(e[k],10)
def u32(b,at):return struct.unpack_from("<I",b,at)[0]
def u64(b,at):return struct.unpack_from("<Q",b,at)[0]
def validate(events,data,manifest,expected,base,holder,bounded=False):
 for r in manifest["ranges"]:
  b=data["CODE_"+r["name"]];assert len(b)==r["bytes"] and hashlib.sha256(b).hexdigest()==r["sha256"],"loaded code"
 assert [v-base for v in struct.unpack("<3Q",data["TABLE_GRID"])]==manifest["tables"][0]["target_rvas"],"loaded table"
 for tag in ["ENVELOPE","FIRST","FIRSTAFTER","PUBLISH"]:assert len(events[tag])==1,"one first envelope"
 for tag in ["NAMED","INIT","INITAFTER"]:assert len(events[tag])==4,"four source/retention events"
 nq=len(events["QUERY"]);assert nq in [2,4],"bounded query count"
 for tag in ["QUERYAFTER","GETTER","GETTERAFTER"]:assert len(events[tag])==nq,"complete query/getter pairs"
 env=events["ENVELOPE"][0];first=events["FIRST"][0];after=events["FIRSTAFTER"][0];pub=events["PUBLISH"][0]
 assert hx(env,"processor")==hx(first,"processor")==hx(after,"processor"),"processor identity"
 assert hx(env,"tid")==hx(first,"tid")==hx(after,"tid")==hx(pub,"tid"),"first thread"
 for key in ["frameStackMatch","outStackMatch","sameProcessor","sameTid"]:assert dc(first,key)==1,"first arguments"
 assert dc(first,"queryCount")==dc(first,"getterCount")==nq
 assert hx(first,"frame")==hx(after,"frame") and hx(first,"out")==hx(after,"out")==hx(pub,"src"),"first pointers"
 assert dc(after,"sameTid")==1
 # First converter return register is recorded, but its status ABI is unqualified.
 assert hx(pub,"tag")==0x5000001c and dc(pub,"bytes")==2072 and dc(pub,"firstStackMatch")==dc(pub,"sameTid")==1
 assert len(data["FRAME"])==len(data["FRAME_AFTER"])==1880
 assert data["FRAME"]==data["FRAME_AFTER"],"input frame changed"
 assert data["FRAME_STATS"]==data["FRAME"][424:516] and len(data["FRAME_STATS"])==92
 assert len(data["FIRST_OUT"])==2072 and data["FIRST_OUT"]==data["PUBLISH_OUT"],"first publication payload"
 assert len(data["FIRST_BEFORE"])==2072
 arrays={};root_matches=set()
 for i,e in enumerate(events["NAMED"],1):
  assert dc(e,"n")==i and dc(e,"count")==4
  prefix=f"NAMED{i:02}_";obj=data[prefix+"OBJECT"];payload=data[prefix+"PAYLOAD"];arr=data[prefix+"ARRAY"]
  assert len(obj)==384 and len(payload)==96 and len(arr)==480 and obj[288:]==payload,"named shape"
  assert u32(payload,44)==4 and u64(payload,56)==hx(e,"array"),"named array"
  matches=[x for x in expected if all(obj[int(off):int(off)+len(bytes.fromhex(v))]==bytes.fromhex(v) for off,v in x["fields"].items() if not bounded or off!="72")]
  assert matches,"typed source module metadata"
  if bounded:
   assert all(u32(obj,72)==u32(bytes.fromhex(x["fields"]["72"]),0) for x in matches),"source numeric low word"
   assert all(u32(obj,76)!=u32(bytes.fromhex(x["fields"]["72"]),4) for x in matches),"retain known numeric high mismatch"
  weights=bytes.fromhex(matches[0]["weights"])
  assert hashlib.sha256(weights).hexdigest()==manifest["source_weight_sha256"]
  assert all(arr[j*120+20:j*120+32]==weights for j in range(4)),"source weights"
  arrays[hx(e,"array")]=arr;root_matches.update(x["source_sha256"] for x in matches)
 retained={}
 for i,(e,a) in enumerate(zip(events["INIT"],events["INITAFTER"]),1):
  assert dc(e,"n")==dc(a,"n")==i
  assert hx(e,"table")-base==0x13381a0
  assert hx(e,"tid")==hx(a,"tid") and hx(e,"self")==hx(a,"self") and hx(e,"cache")==hx(a,"cache")
  assert all(dc(a,k)==1 for k in ["sameTid","sameSelf","sameCache"])
  prefix=f"INIT{i:02}_";post=f"INITAFTER{i:02}_"
  cache=data[prefix+"CACHE"];assert len(cache)==120 and cache==data[post+"CACHE"]
  assert len(data[prefix+"SELF"])==len(data[post+"SELF"])==48
  assert u64(data[post+"SELF"],24)==hx(e,"cache")
  assert any(hx(e,"cache")==start+120*j and cache==arr[120*j:120*(j+1)] for start,arr in arrays.items() for j in range(4)),"source retention pointer"
  retained[hx(e,"self")]=(hx(e,"cache"),cache)
 primary=[];selectors=[]
 for i,(q,a,g,ga) in enumerate(zip(events["QUERY"],events["QUERYAFTER"],events["GETTER"],events["GETTERAFTER"]),1):
  assert all(dc(e,"n")==i for e in [q,a,g,ga])
  assert dc(g,"query")==dc(ga,"query")==i
  selector=dc(q,"selector");kind=10 if selector==12 else 21
  assert selector in [12,20] and dc(q,"count")==1 and dc(q,"allocated")==92 and dc(q,"type")==kind
  assert hx(q,"callerRVA")==({12:0x8528f0,20:0x852988}[selector])
  assert hx(q,"callbackRVA")== (0x36e460 if bounded else 0x372e40)
  assert hx(q,"tid")==hx(a,"tid")==hx(g,"tid")==hx(ga,"tid")==hx(first,"tid")
  assert dc(a,"sameTid")==dc(ga,"sameTid")==1 and hx(a,"status")==0 and hx(ga,"result")==1
  assert dc(a,"written")==92 and dc(a,"type")==kind
  assert hx(q,"desc")==hx(a,"desc") and hx(q,"out")==hx(a,"out")==hx(g,"out")==hx(ga,"out")
  assert hx(g,"table")-base==0x13381a0 and dc(g,"bytes")==92
  assert hx(g,"callerRVA") in [0x39eb18,0x39eb9c,0x39ec20,0x39ec70,0x39ece4],"source manager caller"
  assert hx(g,"self")==hx(ga,"self") in retained
  sourceptr,sourcecache=retained[hx(g,"self")]
  assert hx(g,"cache")==hx(ga,"cache")==sourceptr
  gp=f"GETTER{i:02}_";ap=f"GETTERAFTER{i:02}_";qp=f"QUERY{i:02}_";rp=f"QUERYAFTER{i:02}_"
  assert data[gp+"CACHE"]==data[ap+"CACHE"]==sourcecache,"unchanged source cache"
  assert len(data[gp+"SELF"])==48 and u64(data[gp+"SELF"],24)==sourceptr
  interface=data[qp+"INTERFACE"];assert len(interface)==48 and u64(interface,8)-base==(0x36e460 if bounded else 0x372e40) and u64(interface,40)==hx(q,"manager")
  desc=data[qp+"DESC"];post=data[rp+"DESC"]
  assert len(desc)==len(post)==24
  assert u64(desc,0)==u64(post,0)==hx(q,"out") and u32(desc,8)==u32(post,8)==92
  assert u32(post,12)==92 and u32(desc,16)==u32(post,16)==kind
  assert desc[:12]==post[:12] and desc[16:]==post[16:],"descriptor identity"
  produced=data[rp+"OUT"];assert len(produced)==92 and produced==data[ap+"OUT"]
  assert produced[68:80]==sourcecache[20:32],"original getter source weights"
  assert len(data[qp+"BEFORE"])==len(data[gp+"BEFORE"])==92
  if hx(q,"out")==hx(first,"frame")+424:
   primary.append(produced);selectors.append(selector)
 assert sorted(selectors)==[12,20],"both full queries target first frame"
 assert all(out==data["FRAME_STATS"] for out in primary),"typed payload first-frame equality"
 assert data["FIRST_OUT"][48:60]==data["FRAME_STATS"][68:80],"original primary conversion"
 assert holder.count("START_BEGIN")==1 and "START_STATUS=Success" in holder and "STOP_PASS" in holder and "E011BX_HOLDER_END" in holder
 handles=int(re.search(r"STOP_PASS valid_4k_handles=(\d+)",holder).group(1));assert handles>=10
 return {"queries":nq,"source_metadata_candidate_matches":len(root_matches),"valid_4k_handles":handles}
def main():
 p=argparse.ArgumentParser();p.add_argument("identity");p.add_argument("--private",type=Path);p.add_argument("--allow-incomplete-cleanup",action="store_true");a=p.parse_args()
 assert re.fullmatch(r"E011BX-\d{8}-\d{4}[A-Z]",a.identity)
 priv=a.private or ROOT.parent/"private"/(a.identity+"-captured")
 m=json.loads((HERE/"PRE-RUNTIME-SAFE.json").read_text());assert m["identity"]==a.identity
 expected=json.loads((priv/"SOURCE-EXPECTED.private.json").read_text())
 raw=readtext(priv/"cdb-observer.raw");events=parse(raw)
 bases=re.findall(r"(?m)^E011BX_MODULE_BASE base=([0-9a-fA-F]+)",raw.replace(chr(96),""));assert len(bases)==1
 base=int(bases[0],16)
 data={f.stem:f.read_bytes() for f in (priv/"capture").glob("*.bin")}
 holder=readtext(priv/"holder.log");facts=validate(events,data,m,expected,base,holder)
 negatives=[]
 cases=[("short_written",lambda e,d:e["QUERYAFTER"][0].update(written="0")),
  ("wrong_type",lambda e,d:e["QUERY"][0].update(type="99")),
  ("wrong_callback",lambda e,d:e["QUERY"][0].update(callbackRVA="372e44")),
  ("wrong_first_pointer",lambda e,d:e["FIRST"][0].update(frame=format(hx(e["FIRST"][0],"frame")+8,"x"))),
  ("changed_payload",lambda e,d:d.update(PUBLISH_OUT=bytes([d["PUBLISH_OUT"][0]^1])+d["PUBLISH_OUT"][1:])),
  ("changed_source_cache",lambda e,d:d.update(GETTER01_CACHE=bytes(120))),
  ("wrong_source_metadata",lambda e,d:d.update(NAMED01_OBJECT=bytes(384))),
  ("wrong_code",lambda e,d:d.update(CODE_QUERY=bytes(len(d["CODE_QUERY"])))) ]
 for name,fn in cases:
  e=copy.deepcopy(events);d=dict(data);fn(e,d)
  try:validate(e,d,m,expected,base,holder)
  except AssertionError:negatives.append(name)
  else:raise AssertionError("tamper accepted: "+name)
 qual=json.loads(readtext(priv/"LOADED-QUALIFICATION-SAFE.json"));release=json.loads(readtext(priv/"START-RELEASE-SAFE.json"))
 def dt(v):return datetime.datetime.fromisoformat(v.replace("Z","+00:00"))
 assert dt(qual["qualified_UTC"])<dt(release["Start_release_UTC"]),"qualification chronology"
 if not a.allow_incomplete_cleanup:
  clean=json.loads(readtext(priv/"CLEANUP-WINDOWS-SAFE.json"))
  assert clean["CDB_exit_code"]==clean["holder_task_exit_code"]==0 and clean["manual_only_task_removed"]
 out={"experiment":"E011BX","attempt":a.identity,"status":"PASS_BOUNDED_LIVE_SOURCE_QUERY_FIRST_FRAME_JOIN",**facts,
  "named_modules":4,"grid_initializations":4,"loaded_code_ranges":len(m["ranges"]),"loaded_tables":1,
  "camera_Starts":1,"private_payload_records":len(data),"private_payload_bytes":sum(map(len,data.values())),
  "tamper_fixtures_rejected":len(negatives),"tamper_families":negatives,
  "typed_queries_written92_verified":True,"source_cache_to_first_frame_pointer_join_closed":True,
  "first_published_weight_source_closed_for_observed_Default_scope":True,
  "actual_opened_filename_closed":False,"whole_profile_policy_closed":False,
  "native_rear_runtime_allowed":False,"new_Linux_front_back_image_test":False,
  "optical_images_saved":False,"original_bytes_exported":False,"cleanup_verified":not a.allow_incomplete_cleanup}
 (HERE/"VALIDATION-SAFE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out))
if __name__=="__main__":main()
