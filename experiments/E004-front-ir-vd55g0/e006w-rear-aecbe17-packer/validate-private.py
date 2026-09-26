#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json

R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera")
raw=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/private/e006a/E006A-PRIVATE-RECORDS-v2.json")
dec=R/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py"
spec=importlib.util.spec_from_file_location("dec",dec)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
j=json.loads(raw.read_text(encoding="utf-8-sig"))

REGS=tuple(range(0xb060,0xb0a8,4))

def min_word(black):
    return (0 - (black << 13)) & 0xffffffff

def repack(s):
    q=s["q4"]
    return {
      0xb060: (0xffff << 16) | (0x200 if s["quad"] else 0) | (1 if s["enabled"] else 0),
      0xb064: s["black"] << 14,
      0xb068: q[0] << 9 | q[1] << 17 | q[2] << 25,
      0xb06c: (s["h_num"]-1) << 16 | s["h_off"],
      0xb070: s["width"]-1,
      0xb074: (s["v_num"]-1) << 16 | s["v_off"],
      0xb078: s["height"]-1,
      0xb07c: 0,
      0xb080: s["gr"] << 14,
      0xb084: s["r"] << 14,
      0xb088: s["gb"] << 14,
      0xb08c: s["b"] << 14,
      0xb090: s["gb"] << 14,
      0xb094: min_word(s["black"]),
      0xb098: min_word(s["black"]),
      0xb09c: min_word(s["black"]),
      0xb0a0: min_word(s["black"]),
      0xb0a4: min_word(s["black"]),
    }

matched=0
for n in range(4):
    rec=next(x for x in j["records"] if x["n"]==n and x["idx"]==1)
    d=m.decode(bytes.fromhex(rec["hex"]))
    vals={r:v for r,v,off,kind in d["writes"]}
    if n >= 2:
        assert all(r not in vals for r in REGS)
        continue

    assert all(r in vals for r in REGS)
    v={r:vals[r] for r in REGS}
    assert (v[0xb060] & ~0xffff0201)==0
    assert (v[0xb064] & ~0xffffc000)==0
    assert (v[0xb068] & ~0xfefefe00)==0
    assert (v[0xb06c] & ~0x003f3ffe)==0
    assert (v[0xb070] & ~0x000001ff)==0
    assert (v[0xb074] & ~0x003f3ffe)==0
    assert (v[0xb078] & ~0x000001ff)==0
    assert v[0xb07c]==0
    for a in range(0xb080,0xb094,4):
        assert (v[a] & ~0xffffc000)==0
    for a in range(0xb094,0xb0a8,4):
        assert (v[a] & ~0xffffe000)==0

    s={
      "enabled": bool(v[0xb060]&1),
      "quad": bool(v[0xb060]&0x200),
      "black": (v[0xb064]>>14)&0x3ffff,
      "q4":[(v[0xb068]>>9)&0x7f,(v[0xb068]>>17)&0x7f,(v[0xb068]>>25)&0x7f],
      "h_off": v[0xb06c]&0x3ffe,
      "h_num": ((v[0xb06c]>>16)&0x3f)+1,
      "width": (v[0xb070]&0x1ff)+1,
      "v_off": v[0xb074]&0x3ffe,
      "v_num": ((v[0xb074]>>16)&0x3f)+1,
      "height": (v[0xb078]&0x1ff)+1,
      "gr": (v[0xb080]>>14)&0x3ffff,
      "r": (v[0xb084]>>14)&0x3ffff,
      "gb": (v[0xb088]>>14)&0x3ffff,
      "b": (v[0xb08c]>>14)&0x3ffff,
    }
    assert (v[0xb060]>>16)==0xffff
    assert 1 <= s["h_num"] <= 64 and 1 <= s["v_num"] <= 64
    assert 16 <= s["width"] <= 512 and 16 <= s["height"] <= 512
    assert (s["h_off"]&1)==0 and (s["v_off"]&1)==0
    assert v[0xb090] == s["gb"] << 14
    assert repack(s)==v
    matched += 1

assert matched==2
print("E006W_PRIVATE_VALIDATION_PASS")
print("startup_variants_exact_repack=2/2 startup3_4_absent=true")
print("words_per_emitted_startup=18")
print("raw_register_values_emitted=false")
