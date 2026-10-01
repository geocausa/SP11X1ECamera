#!/usr/bin/env python3
"""Generate a single-use, bounded AEC cache-lineage Windows observer."""
import argparse,pathlib,re,json
p=argparse.ArgumentParser();p.add_argument("identity");p.add_argument("output",type=pathlib.Path);a=p.parse_args()
if not re.fullmatch(r"E011AX-[0-9]{8}-[0-9]{4}[A-Z]",a.identity):p.error("fresh identity required")
if a.output.exists():p.error("existing identity must be audited; never reuse")
a.output.mkdir(parents=True)
win="C:\\Users\\Geoca\\Documents\\SP11CameraPrivate\\"+a.identity;cap=win+"\\capture"
def save(n,lines):(a.output/(n+".cmd")).write_text("\n".join(lines)+"\n")
def dump(n,addr,size):return f".writemem {cap}\\{n}.bin {addr} {addr}+0x{size-1:x}"
def script(n):return '"$$><'+(win+"\\"+n+".cmd").replace("\\","\\\\")+'"'
def bounded(n,counter,items):
 out=[]
 for i in range(1,5):
  for label,addr,size in items:out.append(f".if ({counter} == 0n{i}) {{ "+dump(f"{n}{i:02}_{label}",addr,size)+" }")
 return out
save("init",[
 '.printf "E011AX_INIT n=%I64u tid=%x self=%p cache=%p rva=%I64x\\n",@$t0,@$tid,@x0,@x1,@pc-QcDeviceMFT8380',
 'r $t8=@x0; r $t9=@x1; r $t10=@$tid',
 *bounded("INIT","@$t0",[("SELF","@x0",48),("CACHE","@x1",96)]),
 'bp1 /1 QcDeviceMFT8380+0x3a0d94 '+script("init-after"),"g"])
save("init-after",[
 '.printf "E011AX_INIT_AFTER n=%I64u tidMatch=%u selfMatch=%u cacheMatch=%u self=%p cache=%p\\n",@$t0,(@$tid==@$t10),(@x19==@$t8),(poi(@x19+0x18)==@$t9),@x19,poi(@x19+0x18)',
 *bounded("INITAFTER","@$t0",[("SELF","@x19",48),("CACHE","poi(@x19+0x18)",96)]),
 'r $t0=@$t0+1',"g"])
save("callback",[
 '.printf "E011AX_CALLBACK n=%I64u tid=%x self=%p manager=%p query=%p desc=%p count=%u\\n",@$t2,@$tid,@x0,poi(@x0+0x28),@x1,poi(@x1+0x18),dwo(@x1+0x20)',
 *bounded("CALLBACK","@$t2",[("SELF","@x0",48),("QUERY","@x1",40)]),
 '.if (dwo(@x1+0x20)==1) { '+ '; '.join(bounded("CALLBACK","@$t2",[("DESC","poi(@x1+0x18)",24)]))+' }',
 'r $t2=@$t2+1',"g"])
save("getter",[
 '.printf "E011AX_GETTER n=%I64u tid=%x self=%p cache=%p output=%p bytes=%I64u\\n",@$t3,@$tid,@x0,poi(@x0+0x18),@x1,@x2',
 'r $t11=@x0; r $t12=poi(@x0+0x18); r $t13=@x1; r $t14=@$tid',
 *bounded("GETTER","@$t3",[("SELF","@x0",48),("CACHE","poi(@x0+0x18)",96),("BEFORE","@x1",92)]),
 'bp4 /1 QcDeviceMFT8380+0x3a0ef8 '+script("getter-after"),"g"])
save("getter-after",[
 '.printf "E011AX_GETTER_AFTER n=%I64u tidMatch=%u outputMatch=%u self=%p cache=%p output=%p\\n",@$t3,(@$tid==@$t14),(@x19==@$t13),@$t11,@$t12,@x19',
 *bounded("GETTERAFTER","@$t3",[("CACHE","@$t12",96),("OUT","@x19",92)]),
 'r $t3=@$t3+1',"g"])
save("consumer",[
 '.printf "E011AX_CONSUMER n=%I64u tid=%x frame=%p stats=%p\\n",@$t5,@$tid,@x21,@x19',
 'r $t15=@x21; r $t16=@x19; r $t17=@$tid',
 *bounded("CONSUMER","@$t5",[("FRAME","@x21+0x1a8",92),("BEFORE","@x19",128)]),
 'bp6 /1 QcDeviceMFT8380+0x83e034 '+script("consumer-after"),"g"])
save("consumer-after",[
 '.printf "E011AX_CONSUMER_AFTER n=%I64u tidMatch=%u frameMatch=%u statsMatch=%u frame=%p stats=%p\\n",@$t5,(@$tid==@$t17),(@x21==@$t15),(@x19==@$t16),@x21,@x19',
 *bounded("CONSUMERAFTER","@$t5",[("FRAME","@x21+0x1a8",92),("STATS","@x19",128)]),
 'r $t5=@$t5+1',"g"])
save("cold",[
 '.printf "E011AX_COLD tid=%x dst=%p src=%p bytes=%I64u\\n",@$tid,@x0,@x1,@x2',
 'r $t18=@x0; r $t19=@x1',
 dump("COLD_SOURCE","@x1",2072),dump("COLD_BEFORE","@x0",2072),
 'bp8 /1 QcDeviceMFT8380+0x73c094 '+script("cold-after"),"g"])
save("cold-after",[
 '.printf "E011AX_COLD_AFTER dst=%p src=%p returnedDstMatch=%u\\n",@$t18,@$t19,(@x0==@$t18)',
 dump("COLD_AFTER","@$t18",2072),dump("COLD_SOURCE_AFTER","@$t19",2072),"g"])
save("query",[
 '.printf "E011AX_ENGINE_QUERY n=%I64u tid=%x engine=%p selector=%u outputs=%p\\n",@$t7,@$tid,@x0,@x1,@x2',
 *bounded("ENGINE","@$t7",[("OUTPUTS","@x2",24)]),
 'r $t7=@$t7+1',"g"])
save("arm",[
 'r $t0=1; r $t2=1; r $t3=1; r $t5=1; r $t7=1',
 'bp0 QcDeviceMFT8380+0x3a0d70 ".if (@$t0<=0n4) { '+script("init").strip('"')+' } .else { bd 0; g }"',
 'bp2 QcDeviceMFT8380+0x372e40 ".if (dwo(@x1)==0n12) { .if (@$t2<=0n4) { '+script("callback").strip('"')+' } .else { bd 2; g } } .else { g }"',
 'bp3 QcDeviceMFT8380+0x3a0db0 ".if (@$t3<=0n4) { '+script("getter").strip('"')+' } .else { bd 3; g }"',
 'bp5 QcDeviceMFT8380+0x83e01c ".if (@$t5<=0n4) { '+script("consumer").strip('"')+' } .else { bd 5; g }"',
 'bp7 /1 QcDeviceMFT8380+0x73c090 '+script("cold"),
 'bp9 QcDeviceMFT8380+0x8528ec ".if (@$t7<=0n4) { '+script("query").strip('"')+' } .else { bd 9; g }"',
 '.printf "E011AX_ARMED_BOUNDED_CACHE_LINEAGE\\n"',"bl"])
save("oracle",[".logopen "+win+"\\cdb-observer.raw","sxe ld:QcDeviceMFT8380.dll",'.printf "E011AX_WAIT_OWNER_MODULE\\n"',"g"])
save("qualify",['.printf "E011AX_MODULE_BASE base=%p\\n",QcDeviceMFT8380']+[dump("CODE_"+name,"QcDeviceMFT8380+0x"+format(rva,"x"),size) for name,rva,size in [
 ("INIT",0x3a0d70,64),("GETPARAM",0x372e40,64),("GETTER",0x3a0db0,336),("CONSUMER",0x83e01c,24),
 ("COLD",0x73c074,36),("QUERY",0x8528b4,60),("TABLE",0x13381a0,24)]])
print(json.dumps({"experiment":"E011AX","generated_scripts":len(list(a.output.glob("*.cmd"))),"max_cache_instances":4,"max_primary_queries":4,"cold_copies":1,"runtime_armed":False}))
