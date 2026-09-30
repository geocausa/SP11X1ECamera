#!/usr/bin/env python3
"""Generate a fresh pre-Init AWB bgStatsConfigV1 writer observer."""
import argparse,pathlib,re
p=argparse.ArgumentParser();p.add_argument("identity");p.add_argument("output",type=pathlib.Path);a=p.parse_args()
if not re.fullmatch(r"E011AU-[0-9]{8}-[0-9]{4}[A-Z]",a.identity):p.error("fresh identity required")
if a.output.exists():p.error("identity exists; never reuse")
a.output.mkdir(parents=True)
win="C:\\Users\\Geoca\\Documents\\SP11CameraPrivate\\"+a.identity;cap=win+"\\capture"
def save(n,lines):(a.output/(n+".cmd")).write_text("\n".join(lines)+"\n")
def dump(n,addr,size):return f".writemem {cap}\\{n}.bin {addr} {addr}+0x{size-1:x}"
def script(n):return '"$$><'+(win+"\\"+n+".cmd").replace("\\","\\\\")+'"'
save("create-call",[
 '.printf "E011AU_CREATE_CALL tid=%x actor=%p config=%p rva=%I64x\\n",@$tid,@x0,@x1,@pc-QcDeviceMFT8380',
 'r $t1=@$tid; r $t6=@x0; r $t5=@x1',
 dump("CREATE_PRE_RETAINED_BG","@x0+0xfb744",92),dump("CREATE_CONFIG_INPUT","@x1",128),
 'bp1 /1 QcDeviceMFT8380+0x687e48 '+script("writer-source"),
 '.printf "E011AU_WRITER_SOURCE_BP_ARMED\\n"',"g"])
save("writer-source",[
 '.printf "E011AU_WRITER_SOURCE tid=%x tidMatch=%u actorMatch=%u rva=%I64x lookup=%p\\n",@$tid,(@$tid==@$t1),(@x19==@$t6),@pc-QcDeviceMFT8380,@x0',
 'r $t7=@x0; .if (@$t7 != 0) { r $t7=@$t7+0x120}',
 dump("WRITER_PRE_RETAINED_BG","@x19+0xfb744",92),
 '.if (@$t7 != 0) { '+dump("BGSTATSCONFIG_SOURCE","@$t7",96)+'}',
 'bp2 /1 QcDeviceMFT8380+0x688434 '+script("writer-after"),
 '.printf "E011AU_WRITER_AFTER_BP_ARMED\\n"',"g"])
save("writer-after",[
 '.printf "E011AU_WRITER_AFTER tid=%x tidMatch=%u actorMatch=%u source=%p quad=%x rva=%I64x\\n",@$tid,(@$tid==@$t1),(@x19==@$t6),@$t7,dwo(@x19+0xfb798),@pc-QcDeviceMFT8380',
 dump("WRITER_AFTER_RETAINED_BG","@x19+0xfb744",92),
 '.if (@$t7 != 0) { '+dump("BGSTATSCONFIG_SOURCE_AFTER","@$t7",96)+'}',
 "g"])
save("oracle",[
 ".logopen "+win+"\\cdb-observer.raw",
 "sxe ld:QcDeviceMFT8380.dll",
 '.printf "E011AU_WAIT_OWNER_MODULE\\n"',"g"])
print("E011AU generated: pre-Init CreateAWBAlgorithm -> bgStatsConfigV1 writer")
