#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json

R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera")
raw=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/private/e006a/E006A-PRIVATE-RECORDS-v2.json")
dec=R/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py"
spec=importlib.util.spec_from_file_location("dec",dec)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
j=json.loads(raw.read_text(encoding="utf-8-sig"))

def shift_bits(w,h):
    area=w*h
    bits=0
    while area:
        bits+=1
        area >>= 1
    return max(bits-4,0)

matched=0
for n in range(4):
    rec=next(x for x in j["records"] if x["n"]==n and x["idx"]==1)
    d=m.decode(bytes.fromhex(rec["hex"]))
    vals={r:v for r,v,off,kind in d["writes"]}
    regs=(0xbe60,0xbe68,0xbe6c,0xbe70)
    if n==3:
        assert all(r not in vals for r in regs)
        continue
    assert all(r in vals for r in regs)
    cfg,off,num,size=(vals[r] for r in regs)
    assert (cfg & ~0x00000f11)==0
    assert (off & ~0x3fff1fff)==0
    assert (num & ~0x03ff000f)==0
    assert (size & ~0x000f1fff)==0

    enabled=bool(cfg & 1)
    color=bool(cfg & 0x10)
    shift=(cfg>>8)&0xf
    h_off=off&0x1fff
    v_off=(off>>16)&0x3fff
    h_num=(num&0xf)+1
    v_num=((num>>16)&0x3ff)+1
    width=(size&0x1fff)+1
    height=((size>>16)&0xf)+1

    assert enabled
    assert 1 <= h_num <= 16 and 1 <= v_num <= 1024
    assert 2 <= width <= 0x2000
    assert 2 <= height <= 16 and (height & 1)==0
    assert (v_off & 1)==0
    assert shift==shift_bits(width,height)

    repack_cfg=1 | (0x10 if color else 0) | (shift_bits(width,height)<<8)
    repack_off=(v_off<<16)|h_off
    repack_num=((v_num-1)<<16)|(h_num-1)
    repack_size=((height-1)<<16)|(width-1)
    assert (repack_cfg,repack_off,repack_num,repack_size)==(cfg,off,num,size)
    matched += 1

print("E006V_PRIVATE_VALIDATION_PASS")
print(f"startup_variants_exact_repack={matched}/3 startup4_absent=true")
print("raw_register_values_emitted=false")
