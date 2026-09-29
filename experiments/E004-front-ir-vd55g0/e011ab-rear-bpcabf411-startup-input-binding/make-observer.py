#!/usr/bin/env python3
"""Generate an eight-hit SP11 Windows observer; raw evidence stays on SP11."""
import argparse, pathlib, re
p=argparse.ArgumentParser()
p.add_argument("identity")
p.add_argument("output", type=pathlib.Path)
a=p.parse_args()
if not re.fullmatch(r"E011AB-[0-9]{8}-[0-9]{4}[A-Z]",a.identity): p.error("fresh identity required")
if a.output.exists(): p.error("output already exists; audit instead of overwriting")
a.output.mkdir(parents=True)
win="C:\\Users\\Geoca\\Documents\\SP11CameraPrivate\\"+a.identity
capture=win+"\\capture"
def write(name,lines): (a.output/name).write_text("\n".join(lines)+"\n")
def dumps(counter,prefix,items):
    lines=[f'.printf "E011AB_{prefix} n=%I64u req=%I64u\\n",@${counter},@$t9']
    for i in range(1,9):
        for label,start,length in items:
            lines.append(f".if (@${counter} == {i}) {{ .writemem {capture}\\{prefix}{i:02}_{label}.bin {start} {start}+0x{length-1:x} }}")
    lines += [f"r @${counter}=@${counter}+1","g"]
    return lines
write("common.cmd",dumps("t1","COMMON",[("REGION","@x1",0x1ac),("RESERVE","@x3",0x18),("DEP","@x0",0x160)]))
write("pack.cmd",dumps("t2","PACK",[("OUT","poi(@x1+0x10)",0x90)]))
oracle=["r @$t0=0","r @$t1=1","r @$t2=1","r @$t9=0"]
oracle.append('bu0 QcDeviceMFT8380+0x746f18 ".if (@$t0 < 8) { r @$t9=qwo(@x26+0x3ef0); .printf \\"E011AB_REQ n=%I64u req=%I64u\\n\\",@$t0,@$t9; r @$t0=@$t0+1 } .else { bd 0 }; g"')
for bid,rva,counter,script in [(1,"0x9c16b0","t1","common.cmd"),(2,"0xb41090","t2","pack.cmd")]:
    command=f"$$><{win}\\{script}".replace("\\","\\\\")
    oracle.append(f'bu{bid} QcDeviceMFT8380+{rva} ".if (@${counter} <= 8) {{ {command} }} .else {{ bd {bid}; g }}"')
oracle += ['.printf "E011AB_ARMED_MAX8\\n"',"bl"]
write("oracle.cmd",oracle)
print("GENERATED_OWN_OBSERVER_FILES=3")
