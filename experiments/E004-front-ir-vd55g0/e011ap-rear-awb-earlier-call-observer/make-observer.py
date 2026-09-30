#!/usr/bin/env python3
"""One-shot AWB call boundaries; original binaries and records remain private."""
import argparse,pathlib,re
p=argparse.ArgumentParser();p.add_argument("identity");p.add_argument("output",type=pathlib.Path);a=p.parse_args()
if not re.fullmatch(r"E011AP-[0-9]{8}-[0-9]{4}[A-Z]",a.identity):p.error("fresh identity required")
if a.output.exists():p.error("existing identity must never be reused")
a.output.mkdir(parents=True)
win="C:\\Users\\Geoca\\Documents\\SP11CameraPrivate\\"+a.identity;cap=win+"\\capture"
def save(name,lines):(a.output/(name+".cmd")).write_text("\n".join(lines)+"\n")
def dump(tag,start,size):return f".writemem {cap}\\{tag}.bin {start} {start}+0x{size-1:x}"
save("init",['.printf "E011AP_INIT tid=%x owner=%p io=%p\\n",@$tid,@x0,poi(@x0+8)',dump("INIT_BG","poi(@x0+8)+0xcb4",92),"g"])
save("set-before",["r @$t0=poi(@x19+8)","r @$t1=@$tid","r @$t2=@x19",
 '.printf "E011AP_SET_BEFORE tid=%x owner=%p io=%p algo=%p target=%p\\n",@$tid,@x19,@$t0,@x0,@x15',"lm a @x15",
 dump("SET_BEFORE_BG","@$t0+0xcb4",92),dump("SET_PARAM","@x1",16),dump("SET_WRAPPER","@x0",64),dump("SET_TARGET","@x15",128),"g"])
save("set-after",['.printf "E011AP_SET_AFTER tid=%x tidMatch=%u ownerMatch=%u result=%x\\n",@$tid,(@$tid==@$t1),(@x19==@$t2),(@x0&0xffffffff)',dump("SET_AFTER_BG","@$t0+0xcb4",92),"g"])
# GetParam2 is deliberately stopped for target/owned-object qualification.
save("get2-before",["r @$t3=poi(@x19+8)","r @$t4=@$tid","r @$t5=@x19",
 '.printf "E011AP_GET2_BEFORE tid=%x owner=%p io=%p algo=%p target=%p selector=%x\\n",@$tid,@x19,@$t3,@x0,@x15,dwo(@x1)',
 "lm a @x15","r @$t6=poi(@x0+0x28)","r @$t7=poi(@$t6+0x10)",
 '.printf "E011AP_DELEGATE object=%p target=%p\\n",@$t6,@$t7',"lm a @$t7",
 dump("GET2_BEFORE_BG","@$t3+0xcb4",92),dump("GET2_PARAM","@x1",40),dump("GET2_WRAPPER","@x0",64),
 dump("GET2_TARGET","@x15",128),dump("DELEGATE_OBJECT","@$t6",64),dump("DELEGATE_TARGET","@$t7",128),"g"])
save("get2-after",['.printf "E011AP_GET2_AFTER tid=%x tidMatch=%u ownerMatch=%u result=%x\\n",@$tid,(@$tid==@$t4),(@x19==@$t5),(@x0&0xffffffff)',dump("GET2_AFTER_BG","@$t3+0xcb4",92),"g"])
save("get12",['.printf "E011AP_GET12_BEFORE tid=%x owner=%p io=%p selector=%x\\n",@$tid,@x19,poi(@x19+8),dwo(@x1)',dump("GET12_BG","poi(@x19+8)+0xcb4",92),"g"])
save("publish",['.printf "E011AP_PUBLISH tid=%x property=%x size=%x\\n",@$tid,(@x2&0xffffffff),(@x3&0xffffffff)',dump("PUBLISH_REC","@x4",128),"g"])
save("consumer",['.printf "E011AP_CONSUMER tid=%x req=%I64u\\n",@$tid,qwo(@x1+0x1ff8)',dump("CONSUMER_REC","poi(@x1+0xf20)+0xcf8",128),"g"])
oracle=[".logopen "+win+"\\cdb-observer.raw"]
spec=[(0,0x831510,"init"),(1,0x83180c,"set-before"),(2,0x831810,"set-after"),(3,0x831920,None),(4,0x831924,"get2-after"),(5,0x831964,"get12"),(6,0x831e00,"publish"),(7,0x9fdf60,"consumer")]
for bid,rva,name in spec:
    cmd=(' "$$><'+(win+"\\"+name+".cmd").replace("\\","\\\\")+'"') if name else ""
    oracle.append(f"bp{bid} /1 QcDeviceMFT8380+0x{rva:x}"+cmd)
oracle+=['.printf "E011AP_ARMED_8_ONESHOT_BP\\n"',"bl"]
save("oracle",oracle)
print("E011AP_GENERATED one_shot_sites=8 scripts=9 manual_GetParam2_qualification=true")
