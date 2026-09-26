#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json

R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera")
raw=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/private/e006a/E006A-PRIVATE-RECORDS-v2.json")
dec=R/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py"
spec=importlib.util.spec_from_file_location("dec",dec)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
j=json.loads(raw.read_text(encoding="utf-8-sig"))

regs=tuple(range(0xb660,0xb6a8,4))
def minw(b): return (0-(b<<13))&0xffffffff
def rep(v):
    s={"en":bool(v[0xb660]&1),"q":bool(v[0xb660]&0x200),
       "bl":(v[0xb664]>>14)&0x3ffff,
       "q4":[(v[0xb668]>>9)&0x7f,(v[0xb668]>>17)&0x7f,(v[0xb668]>>25)&0x7f],
       "ho":v[0xb66c]&0x3ffe,"hn":((v[0xb66c]>>16)&0x3f)+1,
       "w":(v[0xb670]&0x1ff)+1,"vo":v[0xb674]&0x3ffe,
       "vn":((v[0xb674]>>16)&0x3f)+1,"h":(v[0xb678]&0x1ff)+1,
       "gr":(v[0xb680]>>14)&0x3ffff,"r":(v[0xb684]>>14)&0x3ffff,
       "gb":(v[0xb688]>>14)&0x3ffff,"b":(v[0xb68c]>>14)&0x3ffff}
    q=s["q4"]; lo=minw(s["bl"])
    return {
      0xb660:(0xffff<<16)|(0x200 if s["q"] else 0)|(1 if s["en"] else 0),
      0xb664:s["bl"]<<14,0xb668:q[0]<<9|q[1]<<17|q[2]<<25,
      0xb66c:(s["hn"]-1)<<16|s["ho"],0xb670:s["w"]-1,
      0xb674:(s["vn"]-1)<<16|s["vo"],0xb678:s["h"]-1,0xb67c:0,
      0xb680:s["gr"]<<14,0xb684:s["r"]<<14,0xb688:s["gb"]<<14,
      0xb68c:s["b"]<<14,0xb690:s["gb"]<<14,
      0xb694:lo,0xb698:lo,0xb69c:lo,0xb6a0:lo,0xb6a4:lo
    }

matched=0
for n in range(4):
    rec=next(x for x in j["records"] if x["n"]==n and x["idx"]==1)
    d=m.decode(bytes.fromhex(rec["hex"]))
    vals={r:v for r,v,off,kind in d["writes"]}
    if n>=2:
        assert all(a not in vals for a in regs)
        continue
    assert all(a in vals for a in regs)
    v={a:vals[a] for a in regs}
    assert rep(v)==v
    matched+=1
assert matched==2
print("E006X_PRIVATE_VALIDATION_PASS")
print("startup_variants_exact_repack=2/2 startup3_4_absent=true")
print("shared_e006w_semantic_core=true raw_register_values_emitted=false")
