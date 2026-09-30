#!/usr/bin/env python3
"""Fresh one-shot user-mode observation of actual AWB SetParam retained BG."""
import argparse,pathlib,re
p=argparse.ArgumentParser();p.add_argument("identity");p.add_argument("output",type=pathlib.Path);a=p.parse_args()
if not re.fullmatch(r"E011AT-[0-9]{8}-[0-9]{4}[A-Z]",a.identity):p.error("fresh identity required")
if a.output.exists():p.error("identity exists; never reuse")
a.output.mkdir(parents=True)
win="C:\\Users\\Geoca\\Documents\\SP11CameraPrivate\\"+a.identity;cap=win+"\\capture"
def save(n,lines):(a.output/(n+".cmd")).write_text("\n".join(lines)+"\n")
def dump(n,addr,size):return f".writemem {cap}\\{n}.bin {addr} {addr}+0x{size-1:x}"
def script(n):return '"$$><'+(win+"\\"+n+".cmd").replace("\\","\\\\")+'"'
save("set-outer",[
 '.printf "E011AT_OUTER tid=%x wrapper=%p actor=%p callback=%p io=%p\\n",@$tid,@x0,poi(poi(@x0+0x28)),poi(poi(poi(@x0+0x28))+8),@$t0',
 'r $t1=@$tid; r $t2=@x0; r $t6=poi(poi(@x0+0x28)); r $t7=poi(@$t6); r $t8=poi(@$t7+8)',
 dump("OUTER_IO_BG","@$t0+0xcb4",92),dump("OUTER_RETAINED_BG","@$t6+0xfb744",92),
 dump("OUTER_PARAM","@x1",40),dump("OUTER_WRAPPER","@x0",64),dump("OUTER_ACTOR","@$t6",64),
 dump("OUTER_VTABLE","@$t7",48),dump("OUTER_CALLBACK_CODE","@$t8",128),
 'lm a @$t8',
 'bp2 /1 @$t8 '+script("set-entry"),
 'ba w4 /1 @$t6+0xfb798 '+script("quad-write"),
 '.printf "E011AT_INNER_AND_QUAD_WATCH_ARMED\\n"',"g"])
save("set-entry",[
 '.printf "E011AT_SET_ENTRY tid=%x tidMatch=%u actorMatch=%u callbackMatch=%u rva=%I64x lr=%p\\n",@$tid,(@$tid==@$t1),(@x0==@$t6),(@pc==@$t8),@pc-QcDeviceMFT8380,@lr',
 dump("SET_ENTRY_RETAINED_BG","@x0+0xfb744",92),dump("SET_ENTRY_PARAM","@x1",40),
 'r $t9=@lr','bp3 /1 @$t9 '+script("set-return"),
 'bp4 /1 QcDeviceMFT8380+0x689228 '+script("tuning-helper"),"g"])
save("set-return",[
 '.printf "E011AT_SET_RETURN tid=%x tidMatch=%u actor=%p result=%x rva=%I64x\\n",@$tid,(@$tid==@$t1),@$t6,(@x0&0xffffffff),@pc-QcDeviceMFT8380',
 dump("SET_RETURN_RETAINED_BG","@$t6+0xfb744",92),"g"])
save("tuning-helper",[
 '.printf "E011AT_TUNING_HELPER tid=%x tidMatch=%u actorArgMatch=%u rva=%I64x\\n",@$tid,(@$tid==@$t1),(@x0==@$t6),@pc-QcDeviceMFT8380',
 dump("HELPER_RETAINED_BG","@$t6+0xfb744",92),dump("HELPER_ARG0","@x0",64),"g"])
save("quad-write",[
 '.printf "E011AT_QUAD_WRITE tid=%x sameThread=%u pcRva=%I64x actor=%p quad=%x\\n",@$tid,(@$tid==@$t1),@pc-QcDeviceMFT8380,@$t6,dwo(@$t6+0xfb798)',
 dump("QUAD_WRITE_RETAINED_BG","@$t6+0xfb744",92),
 'ub @pc L8','u @pc L8',"g"])
save("outer-return",[
 '.printf "E011AT_OUTER_RETURN tid=%x tidMatch=%u result=%x\\n",@$tid,(@$tid==@$t1),(@x0&0xffffffff)',
 dump("OUTER_RETURN_IO_BG","@$t0+0xcb4",92),dump("OUTER_RETURN_RETAINED_BG","@$t6+0xfb744",92),"g"])
save("get2-before",[
 '.printf "E011AT_GET2_BEFORE tid=%x sameThread=%u actor=%p quad=%x\\n",@$tid,(@$tid==@$t1),@$t6,dwo(@$t6+0xfb798)',
 dump("GET2_BEFORE_RETAINED_BG","@$t6+0xfb744",92),dump("GET2_BEFORE_IO_BG","@$t0+0xcb4",92),"g"])
save("publish",[
 '.printf "E011AT_PUBLISH tid=%x property=%x size=%x\\n",@$tid,(@x2&0xffffffff),(@x3&0xffffffff)',
 dump("PUBLISH_REC","@x4",128),"g"])
save("consumer",[
 '.printf "E011AT_CONSUMER tid=%x req=%I64u\\n",@$tid,qwo(@x1+0x1ff8)',
 dump("CONSUMER_REC","poi(@x1+0xf20)+0xcf8",128),"g"])
save("oracle",[
 ".logopen "+win+"\\cdb-observer.raw",
 'bp0 /1 QcDeviceMFT8380+0x83180c '+script("set-outer"),
 'bp1 /1 QcDeviceMFT8380+0x831810 '+script("outer-return"),
 'bp5 /1 QcDeviceMFT8380+0x831920 '+script("get2-before"),
 'bp6 /1 QcDeviceMFT8380+0x831e00 '+script("publish"),
 'bp7 /1 QcDeviceMFT8380+0x9fdf60 '+script("consumer"),
 '.printf "E011AT_ARMED_5_OUTER_ONESHOT_BP\\n"',"bl","g"])
print("E011AT generated: actual SetParam entry/return, tuning helper and retained-quad watch")
