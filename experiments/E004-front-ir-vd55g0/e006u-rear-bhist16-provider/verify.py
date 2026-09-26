#!/usr/bin/env python3
from pathlib import Path
import json

D=Path(__file__).resolve().parent
S=json.loads((D/"SOURCE-SAFE.json").read_text())
V=json.loads((D/"PRIVATE-VALIDATION-SAFE.json").read_text())
C=(D/"camss-e006u-bhist16.inc").read_text()

assert S["schema"]=="E006u-rear-bhist16-source-safe-v1"
assert S["module"]=="IFEBHistStats16Titan680"
assert S["registers"]["startup1_dmi_side"]==["0xb258","0xb25c"]
assert S["registers"]["region_count"]=="0xb26c"
assert S["register_image"]["bytes"]==80
assert S["register_image"]["constructor_zero_initialized"] is True
assert S["titan680_pack"]["b26c_h_mask"]=="0x00001fff"
assert S["titan680_pack"]["b26c_v_mask"]=="0x1fff0000"
assert S["raw_windows_command_values_committed"] is False

assert V["schema"]=="E006u-rear-bhist16-private-validation-safe-v1"
assert V["startup_variants"]["startup1"]["b258_b25c_present"] is True
assert V["startup_variants"]["startup1"]["zero_seed_words_matched"]==2
for n in ("startup2","startup3","startup4"):
    assert V["startup_variants"][n]["b258_b25c_present"] is False
assert all(x["region_word_modeled"] for x in V["startup_variants"].values())
assert V["region_word_unmodeled_bits_zero_all_startups"] is True
assert V["raw_register_values_committed"] is False
assert V["raw_packet_bytes_committed"] is False

for token in [
    "struct e006u_bhist16_state","e006u_bhist16_region_word",
    "e006u_bhist16_lookup","e006u_bhist16_recipe",
    "half_w > 2 ? half_w - 1 : 1",
    "half_h > 0 ? half_h - 1 : 0",
    "(h_num & 0x1fff) | ((v_num & 0x1fff) << 16)",
    "case 0xb258:","case 0xb25c:","case 0xb26c:"
]:
    assert token in C

P=D.parent
owner=json.loads((P/"e006l-rear-startup-register-ownership"/"STARTUP-REGISTER-OWNER-MAP.json").read_text())
startup_only={int(x["register"],16) for x in owner["startup_only"] if x["owner"]=="BHIST_STATS16"}
startup_diff={int(x["register"],16) for x in owner["startup_differs_from_steady"] if x["owner"]=="BHIST_STATS16"}
assert startup_only=={0xb258,0xb25c}
assert startup_diff=={0xb26c}

recipe=json.loads((P/"e006k-rear-startup-main-symbolic-recipe"/"STARTUP-SYMBOLIC-RECIPE.json").read_text())
presence={}
for name,v in recipe["variants"].items():
    regs=set()
    for cmd in v["commands"]:
        regs.update(x["register_offset"] for x in cmd.get("values",[]))
    presence[name]=regs
assert {"0xb258","0xb25c","0xb26c"} <= presence["startup1"]
for name in ("startup2","startup3","startup4"):
    assert "0xb26c" in presence[name]
    assert "0xb258" not in presence[name] and "0xb25c" not in presence[name]

def word(w,h):
    hw=w>>1
    hh=h>>1
    hn=hw-1 if hw>2 else 1
    vn=hh-1 if hh>0 else 0
    return (hn&0x1fff)|((vn&0x1fff)<<16)

assert word(2,2)==1
assert word(6,2)==2
assert word(4064,2286)==((2031&0x1fff)|((1142&0x1fff)<<16))

print("E006U_VERIFY_PASS")
print("bhist_regs=3 startup1_dmi_side=2 region_count=1")
print("region_formula=modern_BHistStats16 source-locked")
print("raw_windows_command_values=false")
