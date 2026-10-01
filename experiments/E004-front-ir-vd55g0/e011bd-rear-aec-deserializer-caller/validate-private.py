#!/usr/bin/env python3
"""Independently recheck the live named source/cache joins on the same SP11."""
from pathlib import Path
import hashlib,importlib.util,json,re,struct,argparse
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
p=argparse.ArgumentParser();p.add_argument("identity");a=p.parse_args()
assert re.fullmatch(r"E011BD-\d{8}-\d{4}[A-Z]",a.identity)
private=ROOT.parent/"private"/(a.identity+"-captured");cap=private/"capture"
def read(n):return json.loads((private/n).read_text(encoding="utf-8-sig"))
ps=read("VALIDATION-SAFE.json");prep=json.loads((HERE/"PREPARE-SAFE.json").read_text())
raw=(private/"cdb-observer.raw").read_text(errors="replace")
assert not re.search(r"Syntax error|Memory access error|Couldn.t resolve|E011BD_AUTHORITY_FAIL",raw)
def events(n):
 out=[]
 for m in re.finditer(r"^E011BD_"+n+r" ([^\r\n]+)",raw,re.M):
  e=dict(re.findall(r"([A-Za-z]+)=([0-9a-fA-F\x60]+)",m.group(1)));e["_pos"]=m.start();out.append(e)
 return out
def ptr(s):return int(s.replace(chr(96),""),16)
def rec(n,s):
 b=(cap/(n+".bin")).read_bytes();assert len(b)==s;return b
def q(b,o=0):return struct.unpack_from("<Q",b,o)[0]
mb=ptr(events("MODULE_BASE")[0]["base"])
for c in prep["code_ranges"]:assert hashlib.sha256(rec("CODE_"+c["name"],c["bytes"])).hexdigest()==c["sha256"]
for t in prep["tables"]:
 b=rec("TABLE_"+t["name"],8*len(t["target_rvas"]))
 assert [q(b,i*8)-mb for i in range(len(t["target_rvas"]))]==t["target_rvas"]
inventory={r["name"]:r for r in ps["record_hashes"]}
assert set(inventory)=={f.name for f in cap.iterdir() if f.is_file()}
for n,r in inventory.items():
 b=(cap/n).read_bytes();assert len(b)==r["bytes"] and hashlib.sha256(b).hexdigest()==r["sha256"]
names=events("NAME");returns=events("NAMERET");stores=events("NAMESTORE")
configs=events("CONFIG");cr=events("CONFIGRET");inits=events("INIT");ia=events("INITAFTER")
assert 1<=len(names)<=4 and len(names)==len(returns)==len(stores)
assert 1<=len(configs)<=4 and len(configs)==len(cr)
assert 1<=len(inits)<=4 and len(inits)==len(ia)
for i,e in enumerate(names,1):
 assert int(e["n"])==i
 r,s=returns[i-1],stores[i-1]
 assert all(r[k]=="1" for k in ["tidMatch","bankMatch"])
 assert all(s[k]=="1" for k in ["tidMatch","bankMatch","payloadMatch"])
 assert e["_pos"]<r["_pos"]<s["_pos"] and e["bank"]==s["bank"]
 assert rec(f"NAME{i:02}_TEXT",32).split(b"\0")[0]==b"aecxhwstatsconfig"
 assert ptr(r["object"])+0x120==ptr(r["payload"])==ptr(s["payload"])
 pay=rec(f"NAMERET{i:02}_PAYLOAD",96)
 assert pay==rec(f"NAMESTORE{i:02}_PAYLOAD",96)==rec(f"NAMERET{i:02}_OBJECT",384)[288:384]
 assert q(pay,56)==ptr(s["cache"]) and q(rec(f"NAMESTORE{i:02}_HOLDER",8))==ptr(s["payload"])
for i,e in enumerate(configs,1):
 r=cr[i-1];assert int(e["n"])==i
 assert ptr(e["bank"])==ptr(e["core"])+8
 assert all(ptr(e[k])-mb==v for k,v in [("target",0x3a8730),("publicSlot",0x3a8730),("coreSlot",0x3af540),("bankSlot",0x3aebb0),("coreTable",0x1338428),("bankTable",0x13383b8)])
 iface=rec(f"CONFIG{i:02}_INTERFACE",320);core=rec(f"CONFIG{i:02}_CORE",16)
 assert q(iface)==ptr(e["core"]) and q(iface,312)==ptr(e["publicSlot"])
 assert q(core)==ptr(e["coreTable"]) and q(core,8)==ptr(e["bankTable"])
 assert q(rec(f"CONFIG{i:02}_CORE_SLOT",8))==ptr(e["coreSlot"])
 assert q(rec(f"CONFIG{i:02}_BANK_SLOT",8))==ptr(e["bankSlot"])
 assert all(r[k]=="1" for k in ["tidMatch","dataMatch","payloadMatch"])
 assert e["_pos"]<r["_pos"] and r["bank"]==e["bank"] and r["payload"]==e["named"]
 assert ptr(r["data"])==ptr(e["bank"])+0xef8
 joined=[s for s in stores if s["bank"]==e["bank"] and s["payload"]==r["payload"] and s["cache"]==r["cache"] and s["_pos"]<e["_pos"]]
 assert joined
 n=int(joined[-1]["n"]);pay=rec(f"CONFIGRET{i:02}_PAYLOAD",96)
 assert q(rec(f"CONFIGRET{i:02}_DATA",248),240)==ptr(r["payload"])
 assert q(pay,56)==ptr(r["cache"])
 assert rec(f"CONFIGRET{i:02}_GRID",120)[20:32]==rec(f"NAMERET{n:02}_GRID",120)[20:32]
element_offsets=[];first_grid_indices=[]
for i,e in enumerate(inits,1):
 r=ia[i-1];assert int(e["n"])==i
 assert ptr(e["table"])-mb==0x13381a0
 assert all(r[k]=="1" for k in ["tidMatch","selfMatch","cacheMatch"])
 assert e["_pos"]<r["_pos"]
 joins=[v for v in cr if 0<=ptr(e["cache"])-ptr(v["cache"])<480 and (ptr(e["cache"])-ptr(v["cache"]))%120==0 and v["_pos"]<e["_pos"]]
 assert joins;n=int(joins[-1]["n"]);offset=ptr(e["cache"])-ptr(joins[-1]["cache"]);element_offsets.append(offset)
 b=rec(f"INIT{i:02}_CACHE",120);obj=rec(f"INITAFTER{i:02}_SELF",48)
 assert b==rec(f"INITAFTER{i:02}_CACHE",120) and q(obj,24)==ptr(e["cache"])
 assert q(obj)-mb==0x13381a0
 if offset==0:
  assert b[20:32]==rec(f"CONFIGRET{n:02}_GRID",120)[20:32];first_grid_indices.append(i)
assert first_grid_indices and element_offsets==ps["grid_Init_array_element_byte_offsets"]
spec=importlib.util.spec_from_file_location("ba_source",HERE.parent/"e011ay-rear-aec-cache-construction/scalar-private.py")
ay=importlib.util.module_from_spec(spec);spec.loader.exec_module(ay)
inputs=[
 ("qccamplatform8380.inf_arm64_16d44e9aca3becfb/com.qti.tuned.default.bin","aa685fb55e528e717eaf115112dd08bffb5d15c7cd00c4570282163667008150"),
 ("surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.qti.tuned.default.bin","ca620fbcfd9bde3c25157289ac7172244fb39744b36d293ea53ab94422eea634"),
 ("surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin","4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635")]
sources=[]
for name,sha in inputs:
 b=(ROOT.parents[1]/"00-RE-archive/sp11-driverdump"/name).read_bytes()
 assert hashlib.sha256(b).hexdigest()==sha
 wire,info=ay.source(b)
 for i in first_grid_indices:assert rec(f"INIT{i:02}_CACHE",120)[20:32]==wire[20:32]
 sources.append({"path":name,"sha256":sha,"runtime_weights_match":True,"root_symbol_id":info["root_symbol_id"],"grid_symbol_id":info["grid_symbol_id"]})
for f in (ROOT.parent/"private"/a.identity).glob("*.cmd"):
 assert (private/f.name).read_bytes()==f.read_bytes(),"observer script changed"
holder_bytes=(private/"holder.log").read_bytes()
holder=holder_bytes.decode("utf-16" if holder_bytes.startswith(bytes([255,254])) else "utf-8-sig")
assert len(re.findall(r"START_BEGIN",holder))==1 and len(re.findall(r"STOP_PASS",holder))==1
qualification=read("LOADED-QUALIFICATION-SAFE.json")
from datetime import datetime
start=re.search(r"(?m)^(\S+) START_BEGIN",holder).group(1)
assert datetime.fromisoformat(qualification["UTC"].replace("Z","+00:00"))<datetime.fromisoformat(start.replace("Z","+00:00"))
cleanup=read("CLEANUP-SAFE.json")
assert cleanup["task_removed"] and cleanup["debugger_exited"] and cleanup["task_last_result"]==0
assert cleanup["start_count"]==cleanup["stop_count"]==1
safe=dict(ps);safe.update({"independent_Linux_private_recheck":"PASS","independent_tuning_weights_comparison":"PASS_3_SHA_PINNED_DEFAULT_ROOTS",
 "source_candidates":sources,"chronological_named_lookup_config_Init_joins":True,"full_profile_materialization_closed":False,
 "cold_weight_initialization_policy_closed":False,"captured_weights_used_as_producer_inputs":False,
 "original_disk_image_modified":False,"software_breakpoints_used":True,"production_C_changed":False,
 "new_kernel_build_performed":False,"WM16_retirement_closed":False,"Linux_optical_parity_closed":False})
for n,data in [("VALIDATION-SAFE.json",safe),("LOADED-QUALIFICATION-SAFE.json",read("LOADED-QUALIFICATION-SAFE.json")),("CLEANUP-SAFE.json",cleanup)]:
 (HERE/n).write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:v for k,v in safe.items() if k not in ["record_hashes","source_candidates"]},indent=2))
