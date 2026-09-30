#!/usr/bin/env python3
"""Generate bounded auto-continue user-mode statistics semantic-input probes."""
import argparse,pathlib,re
p=argparse.ArgumentParser();p.add_argument("identity");p.add_argument("output",type=pathlib.Path);a=p.parse_args()
if not re.fullmatch(r"E011AK-[0-9]{8}-[0-9]{4}[A-Z]",a.identity):p.error("fresh identity required")
if a.output.exists():p.error("existing attempt must be audited, never reused")
a.output.mkdir(parents=True)
win="C:\\Users\\Geoca\\Documents\\SP11CameraPrivate\\"+a.identity
cap=win+"\\capture"
spec=[
 ("AEC",0xa060f0,0,[("REC","poi(@x1+0xf20)+0x3e0",128),("CROP","poi(@x1+0xf20)",16),("GAIN","poi(@x1+0x16d30)+0x44",4)],"qwo(@x1+0x1ff8)",["dwo(@x0+0x14) == 0n10"]),
 ("AWB",0x9fdf60,1,[("REC","poi(@x1+0xf20)+0xcf8",128),("CROP","poi(@x1+0xf20)",16),("GAIN","poi(@x1+0x16d30)+0x44",4)],"qwo(@x1+0x1ff8)",[]),
 ("RS",0xa0dfc0,2,[("REC","poi(@x1+0xf20)+0x2c50",132),("CROP","poi(@x1+0xf20)",16),("FORMAT","@x1+0xec",4)],"qwo(@x1+0x1ff8)",[]),
 ("AECPACK",0xb3f860,3,[("REC","poi(@x1+8)",128),("OPT","@x1",28)],"@$t9",[]),
 ("AWBPACK",0xb39950,4,[("REC","poi(@x1)",128),("OPT","@x1",24)],"@$t9",[]),
 ("RSPACK",0xb44930,5,[("REC","poi(@x1+8)",160),("OPT","@x1",24)],"@$t9",[]),
 ("AECPRODUCE",0x83df68,6,[("FRAME","@x1+0x1a8",88)],"@$t9",[]),
 ("AWBPRODUCE",0x846020,7,[("IO","@x0+0xcb4",88)],"@$t9",[])]
oracle=[".logopen "+win+"\\cdb-observer.raw","r @$t9=0"]
for name,rva,bid,items,req,filters in spec:
    counter=f"@$t{bid}";oracle.append(f"r {counter}=1")
    lines=[f'.printf "E011AK_{name} n=%I64u req=%I64u tid=%x\\n",{counter},{req},@$tid']
    for n in range(1,9):
        for label,start,size in items:
            lines.append(f".if ({counter} == 0n{n}) {{ .writemem {cap}\\{name}{n:02}_{label}.bin {start} {start}+0x{size-1:x} }}")
    lines.extend([f"r {counter}={counter}+1","g"])
    (a.output/(name.lower()+".cmd")).write_text("\n".join(lines)+"\n")
    cmd=("$$><"+win+"\\"+name.lower()+".cmd").replace("\\","\\\\")
    execute=f".if ({counter} <= 0n8) {{ {cmd} }} .else {{ bd {bid}; g }}"
    for filt in filters:execute=f".if ({filt}) {{ {execute} }} .else {{ g }}"
    oracle.append(f'bu{bid} QcDeviceMFT8380+0x{rva:x} "{execute}"')
oracle.append('bu8 QcDeviceMFT8380+0x746f18 ".if (@$t9 < 0n8) { r @$t9=qwo(@x26+0x3ef0); .printf \\"E011AK_REQ req=%I64u\\n\\",@$t9 }; g"')
oracle+=['.printf "E011AK_ARMED_9_BP\\n"',"bl"]
(a.output/"oracle.cmd").write_text("\n".join(oracle)+"\n")
print("E011AK_OBSERVER_GENERATED scripts=9 breakpoints=9 bounded_capture_only")
