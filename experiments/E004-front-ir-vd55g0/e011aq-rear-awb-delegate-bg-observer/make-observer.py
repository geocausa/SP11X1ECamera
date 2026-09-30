#!/usr/bin/env python3
"""Correctly dereferenced one-shot AWB delegate and retained BG observation."""
import argparse,pathlib,re
p=argparse.ArgumentParser();p.add_argument("identity");p.add_argument("output",type=pathlib.Path);a=p.parse_args()
if not re.fullmatch(r"E011AQ-[0-9]{8}-[0-9]{4}[A-Z]",a.identity):p.error("fresh identity required")
if a.output.exists():p.error("identity already exists; never reuse")
a.output.mkdir(parents=True)
win="C:\\Users\\Geoca\\Documents\\SP11CameraPrivate\\"+a.identity;cap=win+"\\capture"
def save(name,lines):(a.output/(name+".cmd")).write_text("\n".join(lines)+"\n")
def dump(name,addr,size):return f".writemem {cap}\\{name}.bin {addr} {addr}+0x{size-1:x}"
save("init",['.printf "E011AQ_INIT tid=%x owner=%p io=%p\\n",@$tid,@x0,poi(@x0+8)',dump("INIT_BG","poi(@x0+8)+0xcb4",92),"g"])
save("get2-before",['.printf "E011AQ_BEFORE tid=%x owner=%p io=%p wrapper=%p target=%p actor=%p vtable=%p callback=%p\\n",@$tid,@x19,@$t0,@x0,@x15,@$t6,@$t7,@$t8',
 "lm a @$t8",dump("BEFORE_BG","@$t0+0xcb4",92),dump("BEFORE_PARAM","@x1",40),dump("WRAPPER","@x0",64),
 dump("ACTOR","@$t6",64),dump("VTABLE","@$t7",48),dump("CALLBACK_CODE","@$t8",128),dump("RETAINED_BG","@$t6+0xfb744",92),
 dump("INPUT_LIST","poi(@x1+8)",80),dump("OUTPUT_LIST","poi(@x1+0x18)",264),
 dump("NESTED_PAYLOAD","poi(poi(@x1+8)+0x20)",12),
 dump("NESTED_DESCS","poi(poi(poi(@x1+8)+0x20))",360),'.printf "E011AQ_BEFORE_CAPTURED\\n"'])
save("delegate",['.printf "E011AQ_DELEGATE tid=%x tidMatch=%u actorMatch=%u selector=%u rva=%I64x\\n",@$tid,(@$tid==@$t1),(@x0==@$t6),dwo(@x1),@pc-QcDeviceMFT8380',
 dump("DELEGATE_BG","@x0+0xfb744",92),dump("DELEGATE_PARAM","@x1",40),dump("DELEGATE_CODE","@pc",128),"g"])
save("populate",['.printf "E011AQ_POPULATE tid=%x tidMatch=%u actorMatch=%u payloadMatch=%u count=%u\\n",@$tid,(@$tid==@$t1),(@x0==@$t6),(@x1==@$t0+0xb70),dwo(@x1+8)',
 dump("POP_SOURCE_BG","@x0+0xfb744",92),dump("POP_BEFORE_BG","@$t0+0xcb4",92),dump("POP_PAYLOAD","@x1",12),dump("POP_DESCS","poi(@x1)",360),"g"])
save("populate-after",['.printf "E011AQ_POP_RETURN tid=%x tidMatch=%u result=%x rva=%I64x\\n",@$tid,(@$tid==@$t1),(@x0&0xffffffff),@pc-QcDeviceMFT8380',
 dump("POP_AFTER_BG","@$t0+0xcb4",92),dump("POP_AFTER_SOURCE_BG","@$t6+0xfb744",92),"g"])
save("outer-after",['.printf "E011AQ_RETURN tid=%x tidMatch=%u ownerMatch=%u result=%x\\n",@$tid,(@$tid==@$t1),(@x19==@$t2),(@x0&0xffffffff)',
 dump("RETURN_BG","@$t0+0xcb4",92),"g"])
save("publish",['.printf "E011AQ_PUBLISH tid=%x property=%x size=%x\\n",@$tid,(@x2&0xffffffff),(@x3&0xffffffff)',dump("PUBLISH_REC","@x4",128),"g"])
save("consumer",['.printf "E011AQ_CONSUMER tid=%x req=%I64u\\n",@$tid,qwo(@x1+0x1ff8)',dump("CONSUMER_REC","poi(@x1+0xf20)+0xcf8",128),"g"])
def bp(bid,rva,name):
 cmd=(' "$$><'+(win+"\\"+name+".cmd").replace("\\","\\\\")+'"') if name else ""
 return f"bp{bid} /1 QcDeviceMFT8380+0x{rva:x}"+cmd
save("oracle",[".logopen "+win+"\\cdb-observer.raw"]+[bp(*t) for t in [(0,0x831510,"init"),(1,0x831920,None),(5,0x831924,"outer-after"),(6,0x831e00,"publish"),(7,0x9fdf60,"consumer")]]+['.printf "E011AQ_ARMED_5_OUTER_ONESHOT_BP\\n"',"bl"])
save("late-arm",[bp(*t) for t in [(2,0x68e5a0,"delegate"),(3,0x68f490,"populate"),(4,0x68e8d8,"populate-after")]]+['.printf "E011AQ_ARMED_3_INNER_ONESHOT_BP\\n"',"bl","g"])
print("E011AQ_GENERATED initial_sites=5 late_qualified_sites=3 scripts=10")
