#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json

R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera")
raw=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/private/e006a/E006A-PRIVATE-RECORDS-v2.json")
decoder=R/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py"

spec=importlib.util.spec_from_file_location("dec",decoder)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
j=json.loads(raw.read_text(encoding="utf-8-sig"))

for n in range(4):
    rec=next(x for x in j["records"] if x["n"]==n and x["idx"]==1)
    d=m.decode(bytes.fromhex(rec["hex"]))
    vals={}
    for reg,value,off,kind in d["writes"]:
        vals.setdefault(reg,[]).append(value)

    assert 0xb26c in vals and len(vals[0xb26c])==1
    v=vals[0xb26c][0]
    assert (v & ~0x1fff1fff)==0

    if n==0:
        assert vals.get(0xb258)==[0]
        assert vals.get(0xb25c)==[0]
    else:
        assert 0xb258 not in vals
        assert 0xb25c not in vals

print("E006U_PRIVATE_VALIDATION_PASS")
print("startup1_dmi_pair=present_zero_seed_exact")
print("startup2_4_dmi_pair=absent")
print("region_word=13plus13_only_all_startups")
print("raw_values_emitted=false")
