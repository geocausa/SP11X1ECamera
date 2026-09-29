#!/usr/bin/env python3
"""Generate bounded BPC tuning-ID/selector observer; private SP11 output."""
import argparse,pathlib,re
p=argparse.ArgumentParser();p.add_argument("identity");p.add_argument("output",type=pathlib.Path);a=p.parse_args()
if not re.fullmatch(r"E011AC-[0-9]{8}-[0-9]{4}[A-Z]",a.identity):p.error("fresh identity required")
if a.output.exists():p.error("output exists; audit rather than overwrite")
a.output.mkdir(parents=True)
win="C:\\Users\\Geoca\\Documents\\SP11CameraPrivate\\"+a.identity
cap=win+"\\capture"
def write(n,s):(a.output/n).write_text("\n".join(s)+"\n")
def bounded(name,counter,first,items,last,guards=(),bid=None):
 lines=list(first)
 for condition in guards:lines.append(f".if ({condition}) {{")
 for n in range(1,4):
  for label,start,size in items:
   end=f"{start}+0x{size-1:x}" if isinstance(size,int) else size
   lines.append(f".if (@{chr(36)}{counter} == {n}) {{ .writemem {cap}\\{name}{n:02}_{label}.bin {start} {end} }}")
 lines+=list(last)
 for condition in reversed(guards):lines.append('} .else { .printf "E011AC_BOUND_REJECT\\n"; bd '+str(bid)+'; g }')
 write(name.lower()+".cmd",lines)
bounded("COMMON","t1",
 ['.printf "E011AC_COMMON n=%I64u req=%I64u root=%x reserve_relation=%d\\n",@$t1,@$t9,dwo(poi(@x0+8)),(@x3 == poi(@x0+8)+0xa0)'],
 [("ROOT","poi(@x0+8)",0xb8),("REGION","@x1",0x1ac),("RESERVE","@x3",0x18)],
 ["r @$t1=@$t1+1","g"])
bounded("SELECT","t2",
 ['.printf "E011AC_SELECT n=%I64u req=%I64u count=%I64u\\n",@$t2,@$t9,@x3'],
 [("MODES","@x2","@x2+(@x3*8)-1")],
 ["r @$t2=@$t2+1","g"],guards=("@x3 > 0","@x3 <= 0n16"),bid=2)
bounded("INTERP","t3",
 ['.printf "E011AC_INTERP n=%I64u req=%I64u root=%x vector_bytes=%I64u\\n",@$t3,@$t9,dwo(poi(@x0+8)),poi(@x2+8)-poi(@x2)'],
 [("VECTOR","poi(@x2)","poi(@x2+8)-1")],
 ["r @$t3=@$t3+1","g"],guards=("poi(@x2+8) > poi(@x2)","poi(@x2+8)-poi(@x2) <= 0x180"),bid=3)
o=["r @$t0=0","r @$t1=1","r @$t2=1","r @$t3=1","r @$t4=1","r @$t9=0"]
o.append('bp0 QcDeviceMFT8380+0x746f18 ".if (@$t0 < 8) { r @$t9=qwo(@x26+0x3ef0); .printf \\"E011AC_REQ n=%I64u req=%I64u\\n\\",@$t0,@$t9; r @$t0=@$t0+1 } .else { bd 0 }; g"')
for bid,rva,counter,file in [(1,"0x9c16b0","t1","common.cmd"),(2,"0xa09524","t2","select.cmd"),(3,"0x94e2f0","t3","interp.cmd")]:
 cmd=f"$$><{win}\\{file}".replace("\\","\\\\")
 o.append(f'bp{bid} QcDeviceMFT8380+{rva} ".if (@{chr(36)}{counter} <= 3) {{ {cmd} }} .else {{ bd {bid}; g }}"')
o.append('bp4 QcDeviceMFT8380+0xa09528 ".if (@$t4 <= 3) { .if (@x0 != 0) { .printf \\"E011AC_SELECTED n=%I64u req=%I64u root=%x\\n\\",@$t4,@$t9,dwo(@x0+0x120) }; r @$t4=@$t4+1 } .else { bd 4 }; g"')
o+=['.printf "E011AC_ARMED_REQ8_OTHER3\\n"',"bl"]
write("oracle.cmd",o);print("OWN_OBSERVER_FILES_GENERATED=4")
