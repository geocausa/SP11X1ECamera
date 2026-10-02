#!/usr/bin/env python3
"""Prepare one bounded, source-qualified user-mode trace; original bytes stay on SP11."""
from pathlib import Path
import argparse,hashlib,json,re,struct,importlib.util,pefile,capstone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument("identity");a=p.parse_args()
 assert re.fullmatch(r"E011BX-\d{8}-\d{4}[A-Z]",a.identity)
 priv=ROOT.parent/"private"/a.identity
 assert not priv.exists(),"audit existing identity; never reuse"
 BB=load("bx_grid",EX/"e011bb-rear-aec-four-grid-deserialization/source-private.py")
 BL=load("bx_profile",EX/"e011bl-rear-aec-source-profile/source-private.py")
 dll=BB.AZ.DLL;raw=dll.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha==BB.AZ.SHA
 pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase
 ranges=[("NAME",0x3ca970,48),("INIT",0x3a0d70,64),("GETTER",0x3a0db0,900),
 ("MANAGER",0x39ea40,688),("GETPARAM",0x372e40,4524),("WRAPPER",0x852668,388),
 ("QUERY",0x8527f0,424),("ENVELOPE",0x83a7a0,64),("FIRST",0x83a998,140),
 ("CONVERTER",0x83df68,256),("PUBLISH",0x83abbc,32)]
 cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);cs.detail=True
 for r,target in [(0x8528ec,0x852668),(0x852984,0x852668),(0x83aa1c,0x83df68)]:
  ins=next(cs.disasm(pe.get_data(r,4),r));assert ins.mnemonic=="bl" and ins.operands[0].imm==target
 table=0x13381a0;targets=[0x3a0d70,0x3a1140,0x3a0db0]
 assert [v-base for v in struct.unpack("<3Q",pe.get_data(table,24))]==targets
 expected=[];audit=[]
 for name,pin in BB.AZ.AV.FILES:
  blob=(BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  h,sy,wire,info=BB.source(blob);_,_,_,records=BL.describe(blob)
  sid=info["root_symbol_id"];s=sy[sid];selector=s["mode_id"]
  off=s["record_offset"];record=blob[off:off+56]
  assert s["type"]=="aecxhwstatsconfig" and s["version_major"]==10 and s["version_minor"]==0
  assert len(set(wire[i*101+20:i*101+32] for i in range(4)))==1
  fields={16:record[4:36].split(b"\0",1)[0]+b"\0",56:record[:4],
   60:record[36:44],68:record[44:48],72:struct.pack("<2I",*records[selector][1:3]),
   80:BL.text(records,selector).encode()+b"\0",208:blob[88:].split(b"\0",1)[0][:64]+b"\0"}
  expected.append({"source_sha256":pin,"fields":{str(k):v.hex() for k,v in fields.items()},
   "weights":wire[20:32].hex()})
  audit.append({"sha256":pin,"qualified_Default_root":True,"root_symbol_id":sid,
   "selector_id":selector,"all_four_weights_equal":True})
 assert len({e["weights"] for e in expected})==1
 manifest={"experiment":"E011BX","identity":a.identity,
  "base_commit":"0c17c5385c305b1883e86a23c40b58f7bf0a4bd7",
  "original_DLL_sha256":sha,"ranges":[{"name":n,"rva":r,"bytes":z,
   "sha256":hashlib.sha256(pe.get_data(r,z)).hexdigest()} for n,r,z in ranges],
  "tables":[{"name":"GRID","rva":table,"target_rvas":targets}],
  "source_candidates":audit,"source_weight_sha256":hashlib.sha256(bytes.fromhex(expected[0]["weights"])).hexdigest(),
  "max_named_modules":4,"max_grid_initializations":4,"max_typed_queries":4,"max_getters":4,
  "max_camera_Starts":1,"max_first_producer_and_publication":1,
  "runtime_armed":False,"native_rear_runtime_allowed":False,
  "actual_opened_filename_claimed":False,"original_code_modified":False}
 priv.mkdir();(priv/"capture").mkdir()
 (priv/"SOURCE-EXPECTED.private.json").write_text(json.dumps(expected))
 (priv/"PRE-RUNTIME-SAFE.json").write_text(json.dumps(manifest,indent=2)+"\n")
 (HERE/"PRE-RUNTIME-SAFE.json").write_text(json.dumps(manifest,indent=2)+"\n")
 win="C:\\Users\\Geoca\\Documents\\SP11CameraPrivate\\"+a.identity;cap=win+"\\capture"
 def save(n,lines):(priv/(n+".cmd")).write_text("\n".join(lines)+"\n")
 def dump(n,ptr,z):return f".writemem {cap}\\{n}.bin {ptr} {ptr}+0x{z-1:x}"
 def include(n):return '"$$><'+(win+"\\"+n+".cmd").replace("\\","\\\\")+'"'
 def bounded(n,ct,items):
  return [f".if (@$t{ct}==0n{i}) {{ "+dump(f"{n}{i:02}_{label}",ptr,z)+" }"
   for i in range(1,5) for label,ptr,z in items]
 def log(tag,args):return '.printf "E011BX_'+tag+r'\n",'+args
 save("named",[
  log('NAMED n=%I64u tid=%x bank=%p payload=%p array=%p count=%u','@$t0,@$tid,@x22,poi(@x22+0xfe8),poi(poi(@x22+0xfe8)+0x38),dwo(poi(@x22+0xfe8)+0x2c)'),
  *bounded("NAMED",0,[("OBJECT","poi(@x22+0xfe8)-0x120",384),("PAYLOAD","poi(@x22+0xfe8)",96),
    ("ARRAY","poi(poi(@x22+0xfe8)+0x38)",480)]),
  "r $t0=@$t0+1; .if (@$t0>4) { bd 0 }; g"])
 save("init",[
  log('INIT n=%I64u tid=%x self=%p table=%p cache=%p','@$t1,@$tid,@x0,poi(@x0),@x1'),
  "r $t2=@x0; r $t3=@x1; r $t4=@$tid",
  *bounded("INIT",1,[("SELF","@x0",48),("CACHE","@x1",120)]),
  "bp2 /1 QcDeviceMFT8380+0x3a0d94 "+include("init-after"),"g"])
 save("init-after",[
  log('INITAFTER n=%I64u tid=%x self=%p cache=%p sameTid=%u sameSelf=%u sameCache=%u','@$t1,@$tid,@x19,poi(@x19+0x18),(@$tid==@$t4),(@x19==@$t2),(poi(@x19+0x18)==@$t3)'),
  *bounded("INITAFTER",1,[("SELF","@x19",48),("CACHE","poi(@x19+0x18)",120)]),
  "r $t1=@$t1+1; .if (@$t1>4) { bd 1 }; g"])
 save("envelope",[
  log('ENVELOPE tid=%x processor=%p','@$tid,@x0'),"r $t5=@x0; r $t6=@$tid; r $t7=1","g"])
 save("query",[
  log('QUERY n=%I64u tid=%x engine=%p selector=%u interface=%p callbackRVA=%I64x manager=%p desc=%p out=%p count=%u allocated=%u written=%u type=%u callerRVA=%I64x',
   '@$t8,@$tid,@x0,@w1,poi(@x0+0x1088),poi(poi(@x0+0x1088)+8)-QcDeviceMFT8380,poi(poi(@x0+0x1088)+0x28),@x3,poi(@x3),@w4,dwo(@x3+8),dwo(@x3+12),dwo(@x3+16),@lr-QcDeviceMFT8380'),
  "r $t9=@x0; r $t10=@x3; r $t11=poi(@x3); r $t12=@$tid; r $t13=@w1",
  *bounded("QUERY",8,[("INTERFACE","poi(@x0+0x1088)",48),("DESC","@x3",24),("BEFORE","poi(@x3)",92)]),
  "bp5 /1 @lr "+include("query-after"),"g"])
 save("query-after",[
  log('QUERYAFTER n=%I64u tid=%x status=%x desc=%p out=%p sameTid=%u written=%u type=%u','@$t8,@$tid,@w0,@$t10,poi(@$t10),(@$tid==@$t12),dwo(@$t10+12),dwo(@$t10+16)'),
  *bounded("QUERYAFTER",8,[("DESC","@$t10",24),("OUT","@$t11",92)]),
  "r $t8=@$t8+1; r $t10=0; r $t11=0; .if (@$t8>4) { bd 4 }; g"])
 save("getter",[
  log('GETTER n=%I64u query=%I64u tid=%x self=%p table=%p cache=%p out=%p bytes=%u callerRVA=%I64x','@$t14,@$t8,@$tid,@x0,poi(@x0),poi(@x0+0x18),@x1,@w2,@lr-QcDeviceMFT8380'),
  "r $t15=@x0; r $t16=poi(@x0+0x18); r $t17=@x1; r $t18=@$tid",
  *bounded("GETTER",14,[("SELF","@x0",48),("CACHE","poi(@x0+0x18)",120),("BEFORE","@x1",92)]),
  "bp7 /1 @lr "+include("getter-after"),"g"])
 save("getter-after",[
  log('GETTERAFTER n=%I64u query=%I64u tid=%x result=%x self=%p cache=%p out=%p sameTid=%u','@$t14,@$t8,@$tid,@w0,@$t15,@$t16,@$t17,(@$tid==@$t18)'),
  *bounded("GETTERAFTER",14,[("CACHE","@$t16",120),("OUT","@$t17",92)]),
  "r $t14=@$t14+1; .if (@$t14>4) { bd 6 }; g"])
 save("first",[
  log('FIRST tid=%x processor=%p frame=%p out=%p frameStackMatch=%u outStackMatch=%u sameProcessor=%u sameTid=%u queryCount=%I64u getterCount=%I64u',
   '@$tid,@x0,@x1,@x2,(@x1==@sp+0x4f0),(@x2==@sp+0xc50),(@x0==@$t5),(@$tid==@$t6),@$t8-1,@$t14-1'),
  "r $t19=@x1; r $t7=0; bd 4; bd 6",
  dump("FRAME","@x1",1880),dump("FRAME_STATS","@x1+0x1a8",92),dump("FIRST_BEFORE","@x2",2072),
  "bp9 /1 QcDeviceMFT8380+0x83aa20 "+include("first-after"),"g"])
 save("first-after",[
  log('FIRSTAFTER tid=%x processor=%p frame=%p out=%p result=%x sameTid=%u','@$tid,@x19,@$t19,@sp+0xc50,@w0,(@$tid==@$t6)'),
  dump("FIRST_OUT","@sp+0xc50",2072),dump("FRAME_AFTER","@$t19",1880),"g"])
 save("publish",[
  log('PUBLISH tid=%x tag=%x bytes=%u src=%p firstStackMatch=%u sameTid=%u','@$tid,@w2,@w3,@x4,(@x4==@sp+0xc50),(@$tid==@$t6)'),
  dump("PUBLISH_OUT","@x4",2072),"g"])
 def bp(slot,r,n,cond=None,once=False):
  command=include(n)
  if cond:command='".if ('+cond+') { '+command.strip('"')+' } .else { g }"'
  return f"bp{slot} "+("/1 " if once else "")+f"QcDeviceMFT8380+0x{r:x} "+command
 save("arm",[
  "; ".join(f"r $t{i}="+("1" if i in [0,1,8,14] else "0") for i in range(20)),
  bp(0,0x3ca99c,"named","(@$t0<=4)"),
  bp(1,0x3a0d70,"init","(@$t1<=4) and (poi(@x0)==QcDeviceMFT8380+0x13381a0)"),
  bp(3,0x83a7a0,"envelope",once=True),
  bp(4,0x852668,"query","(@$t7==1) and (@$tid==@$t6) and (@$t8<=4) and ((@w1==0n12) or (@w1==0n20)) and ((@lr==QcDeviceMFT8380+0x8528f0) or (@lr==QcDeviceMFT8380+0x852988))"),
  bp(6,0x3a0db0,"getter","(@$t7==1) and (@$t10!=0) and (@$tid==@$t12) and (@$t14<=4) and (@x1==@$t11)"),
  bp(8,0x83aa1c,"first",once=True),bp(10,0x83abd4,"publish",once=True),
  r'.printf "E011BX_ARMED_BOUNDED_SOURCE_QUERY\n"',"bl"])
 save("oracle",[".logopen "+win+"\\cdb-observer.raw","sxe ld:QcDeviceMFT8380.dll",r'.printf "E011BX_WAIT_OWNER_MODULE\n"',"g"])
 save("qualify",[r'.printf "E011BX_MODULE_BASE base=%p\n",QcDeviceMFT8380']+
  [dump("CODE_"+n,"QcDeviceMFT8380+0x"+format(r,"x"),z) for n,r,z in ranges]+
  [dump("TABLE_GRID","QcDeviceMFT8380+0x13381a0",24)])
 holder=(EX/"e011bv-rear-cold-aec-gettag-pointer/holder.ps1").read_text().replace("E011BV","E011BX")
 (HERE/"holder.ps1").write_text(holder);(priv/"holder.ps1").write_text(holder)
 print(json.dumps({"experiment":"E011BX","identity":a.identity,"scripts":len(list(priv.glob("*.cmd"))),
  "source_candidates":len(expected),"source_ranges":len(ranges),"runtime_armed":False}))
if __name__=="__main__":main()
