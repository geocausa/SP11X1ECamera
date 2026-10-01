#!/usr/bin/env python3
"""Prepare a bounded same-SP11 observer; no original bytes leave this machine."""
from pathlib import Path
import argparse,hashlib,json,struct,re,pefile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
p=argparse.ArgumentParser();p.add_argument("identity");a=p.parse_args()
assert re.fullmatch(r"E011BA-\d{8}-\d{4}[A-Z]",a.identity)
priv=ROOT.parent/"private"/a.identity
assert not priv.exists(),"identity already exists"
dll=ROOT.parents[1]/"00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"
raw=dll.read_bytes();sha=hashlib.sha256(raw).hexdigest()
assert sha=="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase
ranges=[("NAME",0x3ca970,48),("CONFIG",0x39f070,384),
 ("PUBLIC",0x3a8730,64),("CORE",0x3af540,48),("BANK",0x3aebb0,8),
 ("INIT",0x3a0d70,64),("CACHECALL",0x39f340,48)]
tables=[("GRID",0x13381a0,[0x3a0d70,0x3a1140,0x3a0db0]),
 ("CORE",0x1338428+0x138,[0x3af540]),("BANK",0x13383b8+0x68,[0x3aebb0])]
for _,r,targets in tables:assert [x-base for x in struct.unpack("<"+"Q"*len(targets),pe.get_data(r,8*len(targets)))]==targets
prepare={"experiment":"E011BA","identity":a.identity,"base_commit":"823b8bb84733e8a3572376cae1c4ea9bc404f959",
 "original_DLL_sha256":sha,"code_ranges":[{"name":n,"rva":r,"bytes":s,"sha256":hashlib.sha256(pe.get_data(r,s)).hexdigest()} for n,r,s in ranges],
 "tables":[{"name":n,"rva":r,"target_rvas":t} for n,r,t in tables],
 "max_events_per_boundary":4,"original_code_modified":False,"runtime_armed":False,
 "native_rear_runtime_allowed":False,"private_bytes_exported":False}
priv.mkdir();(priv/"capture").mkdir()
(HERE/"PREPARE-SAFE.json").write_text(json.dumps(prepare,indent=2,sort_keys=True)+"\n")
win="C:\\Users\\Geoca\\Documents\\SP11CameraPrivate\\"+a.identity;cap=win+"\\capture"
def save(n,lines):(priv/(n+".cmd")).write_text("\n".join(lines)+"\n")
def dump(n,ptr,s):return f".writemem {cap}\\{n}.bin {ptr} {ptr}+0x{s-1:x}"
def include(n):return '"$$><'+(win+"\\"+n+".cmd").replace("\\","\\\\")+'"'
def bounded(n,counter,items):
 return [f".if ({counter} == 0n{i}) {{ "+dump(f"{n}{i:02}_{label}",ptr,s)+" }" for i in range(1,5) for label,ptr,s in items]
save("name",[
 '.printf "E011BA_NAME n=%I64u tid=%x bank=%p name=%p\n",@$t0,@$tid,@x22,@x1'.replace("\n",r"\n"),
 'r $t8=@x22; r $t9=@$tid',
 *bounded("NAME","@$t0",[("TEXT","@x1",32)]),
 'bp1 /1 QcDeviceMFT8380+0x3ca988 '+include("name-return"),"g"])
save("name-return",[
 r'.printf "E011BA_NAMERET n=%I64u tidMatch=%u bankMatch=%u object=%p payload=%p\n",@$t0,(@$tid==@$t9),(@x22==@$t8),@x0,@x0+0x120',
 'r $t10=@x0+0x120',
 *bounded("NAMERET","@$t0",[("OBJECT","@x0",384),("PAYLOAD","@x0+0x120",96),("GRID","poi(@x0+0x158)",120)]),
 'bp2 /1 QcDeviceMFT8380+0x3ca99c '+include("name-store"),"g"])
save("name-store",[
 r'.printf "E011BA_NAMESTORE n=%I64u tidMatch=%u bankMatch=%u payloadMatch=%u bank=%p payload=%p cache=%p\n",@$t0,(@$tid==@$t9),(@x22==@$t8),(poi(@x22+0xfe8)==@$t10),@x22,poi(@x22+0xfe8),poi(poi(@x22+0xfe8)+0x38)',
 *bounded("NAMESTORE","@$t0",[("HOLDER","@x22+0xfe8",8),("PAYLOAD","@$t10",96)]),
 'r $t0=@$t0+1',"g"])
# Dynamic callback/table authority is checked before the actual dispatch is used.
save("config",[
 r'.printf "E011BA_CONFIG n=%I64u tid=%x owner=%p interface=%p core=%p bank=%p target=%p publicSlot=%p coreTable=%p coreSlot=%p bankTable=%p bankSlot=%p named=%p\n",@$t1,@$tid,@x23,@x0,poi(@x0),poi(@x0)+8,@x15,poi(@x0+0x138),poi(poi(@x0)),poi(poi(poi(@x0))+0x138),poi(poi(@x0)+8),poi(poi(poi(@x0)+8)+0x68),poi(poi(@x0)+0xff0)',
 '.if ((@x15!=QcDeviceMFT8380+0x3a8730) | (poi(@x0+0x138)!=QcDeviceMFT8380+0x3a8730) | (poi(poi(poi(@x0))+0x138)!=QcDeviceMFT8380+0x3af540) | (poi(poi(poi(@x0)+8)+0x68)!=QcDeviceMFT8380+0x3aebb0)) { .echo E011BA_AUTHORITY_FAIL; } .else { '+include("config-qualified").strip('"')+' }'])
save("config-qualified",[
 'r $t11=poi(@x0)+8; r $t12=@$tid; r $t13=poi(@$t11+0xfe8)',
 *bounded("CONFIG","@$t1",[("INTERFACE","@x0",320),("CORE","poi(@x0)",16),("CORE_SLOT","poi(poi(@x0))+0x138",8),("BANK_SLOT","poi(poi(@x0)+8)+0x68",8)]),
 'bp4 /1 QcDeviceMFT8380+0x39f0bc '+include("config-return"),"g"])
save("config-return",[
 r'.printf "E011BA_CONFIGRET n=%I64u tidMatch=%u dataMatch=%u payloadMatch=%u bank=%p data=%p payload=%p cache=%p\n",@$t1,(@$tid==@$t12),(@x0==@$t11+0xef8),(poi(@x0+0xf0)==@$t13),@$t11,@x0,poi(@x0+0xf0),poi(poi(@x0+0xf0)+0x38)',
 *bounded("CONFIGRET","@$t1",[("DATA","@x0",248),("PAYLOAD","poi(@x0+0xf0)",96),("GRID","poi(poi(@x0+0xf0)+0x38)",120)]),
 'r $t1=@$t1+1',"g"])
save("init",[
 r'.printf "E011BA_INIT n=%I64u tid=%x self=%p table=%p cache=%p\n",@$t2,@$tid,@x0,poi(@x0),@x1',
 '.if (poi(@x0)!=QcDeviceMFT8380+0x13381a0) { .echo E011BA_AUTHORITY_FAIL; } .else { '+include("init-qualified").strip('"')+' }'])
save("init-qualified",[
 'r $t14=@x0; r $t15=@x1; r $t16=@$tid',
 *bounded("INIT","@$t2",[("SELF","@x0",48),("CACHE","@x1",120)]),
 'bp6 /1 QcDeviceMFT8380+0x3a0d94 '+include("init-after"),"g"])
save("init-after",[
 r'.printf "E011BA_INITAFTER n=%I64u tidMatch=%u selfMatch=%u cacheMatch=%u self=%p cache=%p\n",@$t2,(@$tid==@$t16),(@x19==@$t14),(poi(@x19+0x18)==@$t15),@x19,poi(@x19+0x18)',
 *bounded("INITAFTER","@$t2",[("SELF","@x19",48),("CACHE","poi(@x19+0x18)",120)]),
 'r $t2=@$t2+1',"g"])
save("arm",["r $t0=1; r $t1=1; r $t2=1"]+[
 f'bp{slot} QcDeviceMFT8380+0x{r:x} ".if (@$t{ct}<=0n4) {{ '+include(n).strip('"')+f' }} .else {{ bd {slot}; g }}"'
 for slot,r,ct,n in [(0,0x3ca984,0,"name"),(3,0x39f0b8,1,"config"),(5,0x3a0d70,2,"init")]]+
 [r'.printf "E011BA_ARMED_BOUNDED_SOURCE_CACHE\n"',"bl"])
save("oracle",[".logopen "+win+"\\cdb-observer.raw","sxe ld:QcDeviceMFT8380.dll",r'.printf "E011BA_WAIT_OWNER_MODULE\n"',"g"])
save("qualify",[r'.printf "E011BA_MODULE_BASE base=%p\n",QcDeviceMFT8380']+
 [dump("CODE_"+n,"QcDeviceMFT8380+0x"+format(r,"x"),s) for n,r,s in ranges]+
 [dump("TABLE_"+n,"QcDeviceMFT8380+0x"+format(r,"x"),8*len(t)) for n,r,t in tables])
holder=(HERE.parent/"e011ax-rear-aec-hwstats-source-authority/holder.ps1").read_text().replace("E011AX","E011BA")
(HERE/"holder.ps1").write_text(holder)
(priv/"PREPARE-SAFE.json").write_text(json.dumps(prepare,indent=2)+"\n")
print(json.dumps({"experiment":"E011BA","identity":a.identity,"scripts":len(list(priv.glob("*.cmd"))),"runtime_armed":False}))
