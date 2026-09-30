#!/usr/bin/env python3
"""Generate a bounded same-SP11 AEC/context -> shared vector -> BPC observer."""
import argparse,pathlib,re
p=argparse.ArgumentParser();p.add_argument("identity");p.add_argument("output",type=pathlib.Path);a=p.parse_args()
if not re.fullmatch(r"E011AF-[0-9]{8}-[0-9]{4}[A-Z]",a.identity):p.error("fresh identity required")
if a.output.exists():p.error("existing attempt must be audited")
a.output.mkdir(parents=True)
win="C:\\Users\\Geoca\\Documents\\SP11CameraPrivate\\"+a.identity
cap=win+"\\capture"
def write(name,lines):(a.output/name).write_text("\n".join(lines)+"\n")
def captures(name,counter,items,last,guards=(),bid=0,limit=3,header=(),filters=()):
    lines=[]
    for condition in filters:lines.append(f".if ({condition}) {{")
    lines+=list(header)
    for condition in guards:lines.append(f".if ({condition}) {{")
    for n in range(1,limit+1):
        for label,start,size in items:
            end=f"{start}+0x{size-1:x}" if isinstance(size,int) else size
            action=f".writemem {cap}\\{name}{n:02}_{label}.bin {start} {end}"
            if label == "AEC":
                action=f'.if ({start} > 0) {{ {action} }} .else {{ .printf "E011AF_AEC_ABSENT {name} n={n}\\n" }}'
            lines.append(f".if (@{chr(36)}{counter} == 0n{n}) {{ {action} }}")
    lines+=last
    for condition in reversed(guards):
        lines.append('} .else { .printf "E011AF_BOUND_REJECT bid='+str(bid)+'\\n"; bd '+str(bid)+'; g }')
    for condition in reversed(filters):lines.append("} .else { g }")
    write(name.lower()+".cmd",lines)
def isp_items(isp):
    return [("HEAD",isp,0x108),("CTX",isp+"+0x17120",0x20),
            ("FIXED",isp+"+0x2080",0xb8),("AEC","poi("+isp+")",0xc4)]
captures("CALC","t1",[("VECTOR","@x1",24),("CURRENT","poi(@x1)","poi(@x1+8)-1"),
    ("TYPES","poi(@x2)",12)], ["r @$t1=@$t1+1","g"],
    guards=("poi(@x1) > 0","poi(@x1+8)-poi(@x1) >= 0x18",
            "poi(@x1+8)-poi(@x1) <= 0x100","poi(@x1+0x10) >= poi(@x1+8)"),bid=1,limit=16,
    filters=("@x2 > 0","poi(@x2) > 0","poi(@x2+8)-poi(@x2) == 0xc",
             "dwo(poi(@x2)) == 2","dwo(poi(@x2)+4) == 5","dwo(poi(@x2)+8) == 1"),
    header=['.printf "E011AF_CALC n=%I64u req=%I64u shared=%p vector=%p tid=%x caller_rva=%I64x bytes=%I64u\\n",@$t1,@$t9,@x1,poi(@x1),@$tid,(@x30-QcDeviceMFT8380),poi(@x1+8)-poi(@x1)'])
# GAIN is immediately after the selected gain store; snapshot lookup return
# events are collected at each of its three call sites, with ISP/TID lineage.
captures("GAIN","t2",isp_items("@x19")+[("NODE","@x20+0x33ec",0xc)],
    ["r @$t2=@$t2+1","g"],guards=(),bid=2,limit=0x10,
    header=['.printf "E011AF_GAIN n=%I64u req=%I64u isp=%p tid=%x\\n",@$t2,@$t9,@x19,@$tid'])
captures("GEN","t6",isp_items("@x19")+[("VECTOR","@x19+0x17190",24),("CURRENT","poi(@x19+0x17190)","poi(@x19+0x17198)-1")],
    ["r @$t6=@$t6+1","g"],guards=("poi(@x19+0x17190) > 0",
      "poi(@x19+0x17198)-poi(@x19+0x17190) >= 0x18",
      "poi(@x19+0x17198)-poi(@x19+0x17190) <= 0x100"),bid=6,limit=0x10,
    header=['.printf "E011AF_GEN n=%I64u req=%I64u isp=%p shared=%p vector=%p tid=%x bytes=%I64u\\n",@$t6,@$t9,@x19,(@x19+0x17190),poi(@x19+0x17190),@$tid,poi(@x19+0x17198)-poi(@x19+0x17190)'])
captures("COMMON","t7",[("ROOT","poi(@x0+8)",0xb8),("REGION","@x1",0x1ac),("RESERVE","@x3",0x18)],
    ["r @$t7=@$t7+1","g"],bid=7,
    header=['.printf "E011AF_COMMON n=%I64u req=%I64u root=%x caller_rva=%I64x tid=%x\\n",@$t7,@$t9,dwo(poi(@x0+8)),(@x30-QcDeviceMFT8380),@$tid'])
captures("SELECT","t8",[("MODES","@x2","@x2+(@x3*8)-1")],["r @$t8=@$t8+1","g"],
    guards=("@x3 > 0","@x3 <= 0n16"),bid=8,
    header=['.printf "E011AF_SELECT n=%I64u req=%I64u count=%I64u\\n",@$t8,@$t9,@x3'])
items=[("VECTOR","poi(@x2)","poi(@x2+8)-1")];guards=["poi(@x2+8)-poi(@x2) == 0x48"]
for level in range(3):
    entry=f"poi(@x2)+0x{level*24:x}";begin=f"poi({entry})";end=f"poi({entry}+8)"
    guards.extend((begin+" > 0",end+"-"+begin+" == 8"))
    items.append((f"LEVEL{level+1}",begin,end+"-1"))
captures("INTERP","t10",items,["r @$t10=@$t10+1","g"],guards=guards,bid=9,
    header=['.printf "E011AF_INTERP n=%I64u req=%I64u caller_rva=%I64x tid=%x\\n",@$t10,@$t9,(@x30-QcDeviceMFT8380),@$tid'])
captures("PACK","t11",[("OUT","poi(@x1+0x10)",0x90)],["r @$t11=@$t11+1","g"],bid=10,
    header=['.printf "E011AF_PACK n=%I64u req=%I64u\\n",@$t11,@$t9'])
o=["r @$t0=0","r @$t9=0"]
for counter in (1,2,6,7,8,10,11):o.append(f"r @$t{counter}=1")
for counter in (3,4,5):o.append(f"r @$t{counter}=0")
o.append('bp0 QcDeviceMFT8380+0x746f18 ".if (@$t0 < 0n8) { r @$t9=qwo(@x26+0x3ef0); .printf \\"E011AF_REQ n=%I64u req=%I64u\\n\\",@$t0,@$t9; r @$t0=@$t0+1 } .else { bd 0 }; g"')
for bid,rva,counter,name,limit in ((1,0x890208,1,"calc",16),(2,0x88a8d0,2,"gain",16),
        (6,0x897d6c,6,"gen",16),(7,0x9c16b0,7,"common",3),(8,0xa09524,8,"select",3),
        (9,0x94e2f0,10,"interp",3),(10,0xb41090,11,"pack",3)):
    cmd=("$$><"+win+"\\"+name+".cmd").replace("\\","\\\\")
    o.append(f'bp{bid} QcDeviceMFT8380+0x{rva:x} ".if (@$t{counter} <= 0n{limit}) {{ {cmd} }} .else {{ bd {bid}; g }}"')
for bid,rva in ((3,0x88a7e0),(4,0x88a814),(5,0x88a840)):
    o.append(f'bp{bid} QcDeviceMFT8380+0x{rva:x} ".if (@$t{bid} < 0n32) {{ .printf \\"E011AF_SNAPSHOT stage={bid} req=%I64u isp=%p tid=%x context=%u\\n\\",@$t9,@x19,@$tid,(@x0 & 0xff); r @$t{bid}=@$t{bid}+1 }} .else {{ bd {bid} }}; g"')
o+=['.printf "E011AF_ARMED_11_BP\\n"',"bl"];write("oracle.cmd",o)
print("E011AF_OBSERVER_GENERATED files=8 breakpoints=11")
