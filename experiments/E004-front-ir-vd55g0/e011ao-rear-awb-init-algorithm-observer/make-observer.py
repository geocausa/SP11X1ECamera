#!/usr/bin/env python3
"""Bounded, auto-continuing AWB initialization source probes; no optical payload."""
import argparse,pathlib,re
p=argparse.ArgumentParser();p.add_argument("identity");p.add_argument("output",type=pathlib.Path);a=p.parse_args()
if not re.fullmatch(r"E011AO-[0-9]{8}-[0-9]{4}[A-Z]",a.identity):p.error("fresh identity required")
if a.output.exists():p.error("existing attempt must be audited, never reused")
a.output.mkdir(parents=True)
win="C:\\Users\\Geoca\\Documents\\SP11CameraPrivate\\"+a.identity;cap=win+"\\capture"
def save(name,lines):
    (a.output/(name+".cmd")).write_text("\n".join(lines)+"\n")
def records(counter,tag,items):
    lines=[]
    for n in range(1,5):
        for label,start,size in items:
            lines.append(f".if ({counter} == 0n{n}) {{ .writemem {cap}\\{tag}{n:02}_{label}.bin {start} {start}+0x{size-1:x} }}")
    return lines
save("init",['.printf "E011AO_INIT n=%I64u tid=%x\\n",@$t5,@$tid']+
    records("@$t5","INIT",[("BG","poi(@x0+8)+0xcb4",92)])+["r @$t5=@$t5+1","g"])
save("before",[
    '.if (@$t1 != 0) { .printf "E011AO_OVERLAP_PAIR\\n"; g }',
    "r @$t1=1","r @$t2=poi(@x19+8)","r @$t3=@$tid","r @$t4=@x19",
    '.printf "E011AO_BEFORE n=%I64u tid=%x selector=%x target=%p io=%p\\n",@$t0,@$tid,dwo(@x1),@x15,@$t2',
    "ln @x15","lm a @x15"]+
    records("@$t0","BEFORE",[("BG","@$t2+0xcb4",92),("PARAM","@x1",40),("BGDESC","poi(@x1+0x18)+0xf0",24),("ALGO","@x0",32),("TARGET","@x15",128)])+["g"])
save("after",[
    '.if ((@$t1 != 1) || (@$t3 != @$tid) || (@$t4 != @x19)) { .printf "E011AO_INCOHERENT_PAIR\\n"; g }',
    '.printf "E011AO_AFTER n=%I64u tid=%x result=%x io=%p\\n",@$t0,@$tid,(@x0 & 0xffffffff),@$t2']+
    records("@$t0","AFTER",[("BG","@$t2+0xcb4",92)])+["r @$t1=0","r @$t0=@$t0+1","g"])
save("publish",['.printf "E011AO_PUBLISH n=%I64u tid=%x property=%x size=%x\\n",@$t6,@$tid,(@x2 & 0xffffffff),(@x3 & 0xffffffff)']+
    records("@$t6","PUBLISH",[("REC","@x4",128),("BG","@x0+0xcb4",92)])+["r @$t6=@$t6+1","g"])
save("consumer",['.printf "E011AO_CONSUMER n=%I64u tid=%x req=%I64u\\n",@$t7,@$tid,qwo(@x1+0x1ff8)']+
    records("@$t7","CONSUMER",[("REC","poi(@x1+0xf20)+0xcf8",128)])+["r @$t7=@$t7+1","g"])
oracle=[".logopen "+win+"\\cdb-observer.raw","r @$t0=1","r @$t1=0","r @$t5=1","r @$t6=1","r @$t7=1"]
spec=[
 (0,0x831510,"init","@$t5 <= 0n4"),
 (1,0x831964,"before","(@$t0 <= 0n4) && (dwo(@x1) == 0n12) && (dwo(poi(@x1+0x18)+0xf8) == 0n92) && (poi(poi(@x1+0x18)+0xf0) == poi(@x19+8)+0xcb4)"),
 (2,0x831968,"after","@$t0 <= 0n4"),
 (3,0x831e00,"publish","(@$t6 <= 0n4) && ((@x2 & 0xffffffff) == 0x5000001d) && ((@x3 & 0xffffffff) == 0x80)"),
 (4,0x9fdf60,"consumer","@$t7 <= 0n4")]
# 0nc is not decimal12: use explicit decimal, avoiding ambiguous CDB radix.
spec=[(b,r,n,c.replace("0nc","0n12")) for b,r,n,c in spec]
for bid,rva,name,condition in spec:
    cmd=("$$><"+win+"\\"+name+".cmd").replace("\\","\\\\")
    oracle.append(f'bu{bid} QcDeviceMFT8380+0x{rva:x} ".if ({condition}) {{ {cmd} }} .else {{ g }}"')
oracle += ['.printf "E011AO_ARMED_5_BP\\n"',"bl"]
save("oracle",oracle)
print("E011AO_GENERATED scripts=6 bounded_user_mode_only")
