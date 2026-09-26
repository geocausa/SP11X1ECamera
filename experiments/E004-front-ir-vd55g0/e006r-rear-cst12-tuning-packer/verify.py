#!/usr/bin/env python3
from pathlib import Path
import json

D=Path(__file__).resolve().parent
t=json.loads((D/"TUNING-SAFE.json").read_text())
p=json.loads((D/"PRIVATE-VALIDATION-SAFE.json").read_text())
src=(D/"camss-e006r-cst12.inc").read_text()

assert t["schema"]=="E006r-rear-cst12-tuning-safe-v1"
assert t["source"]["sha256"]=="4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"
assert t["source"]["module_name"]=="com.surface.tuned.rfc_ov13858"
assert t["source"]["cst12_ife_symbol_id"]==28
assert t["source"]["cst12_ife_data_bytes"]==108
assert t["source"]["reserve_offset"]==24
assert t["source"]["reserve_bytes"]==84
assert t["source"]["revision_reference_kind"]==2
assert t["source"]["revision_symbol_id"]==582
assert t["reserve"]["c_x0"]==[0,0,0]
assert t["reserve"]["c_x1"]==[4095,4095,4095]
assert t["reserve"]["m_q10_roundf"]==[601,117,306,-338,510,-172,-427,-83,510]
assert t["reserve"]["o"]==[0,2048,2048]
assert t["reserve"]["s"]==[0,0,0]
assert t["raw_windows_command_values_committed"] is False

assert p["schema"]=="E006r-cst12-private-validation-v1"
assert p["raw_private_values_committed"] is False
assert len(p["startup"])==2
for x in p["startup"]:
    assert x["enabled"] is True
    assert x["matched_words"]==19 and x["total_words"]==19
    assert x["semantic_state_matches_rear_tuning"] is True

for token in [
    "e006r_cst12_validate",
    "e006r_cst12_pair",
    "e006r_cst12_hi13",
    "e006r_cst12_clamp12",
    "e006r_cst12_word",
    "e006r_cst12_lookup",
    "e006r_cst12_recipe",
]:
    assert token in src
assert "reg == 0x6160" in src
assert "reg >= 0x6168 && reg <= 0x61ac" in src

owner=json.loads((D.parent/"e006l-rear-startup-register-ownership"/"STARTUP-REGISTER-OWNER-MAP.json").read_text())
regs={int(x["register"],16) for x in owner["startup_only"] if x["owner"]=="CST12"}
expected={0x6160}|set(range(0x6168,0x61b0,4))
assert regs==expected,(sorted(regs),sorted(expected))
assert len(regs)==19

print("E006R_VERIFY_PASS")
print("cst12_regs=19 config=1 data=18 gap_0x6164=preserved")
print("rear_tuning=com.surface.tuned.rfc_ov13858.bin sha256=4858ccb2...f635")
print("private_validation=startup0,startup1 semantic 19/19 exact")
print("raw_private_values=false")
