#!/usr/bin/env python3
from pathlib import Path
import json

D=Path(__file__).resolve().parent
t=json.loads((D/"TUNING-SAFE.json").read_text())
src=(D/"camss-e006s-bc101.inc").read_text()

assert t["schema"]=="E006s-rear-bc101-tuning-safe-v1"
assert t["source"]["sha256"]=="4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"
assert t["source"]["module_name"]=="com.surface.tuned.rfc_ov13858"
assert t["source"]["record_type"]=="bincorr10_ife_v2"
assert t["source"]["symbol_id"]==23
assert t["source"]["data_bytes"]==76
assert t["enable"]["value"]==0
assert t["enable"]["meaning"]=="BC101 tuning/module enable"
assert t["trigger_path"]["region_values"]==[112,112,112,112]
assert t["common_setting"]["max_value"]==128
assert t["raw_windows_command_values_committed"] is False

for token in [
    "e006s_bc101_state",
    "e006s_bc101_clamp",
    "e006s_bc101_lookup",
    "e006s_bc101_recipe",
]:
    assert token in src

assert "value > 0x80" in src
assert "*value = 0;" in src
assert "*value = (u32)b0 | ((u32)b1 << 16);" in src
assert "*value = (u32)b2 | ((u32)b3 << 16);" in src

owner=json.loads((D.parent/"e006l-rear-startup-register-ownership"/"STARTUP-REGISTER-OWNER-MAP.json").read_text())
regs={int(x["register"],16) for x in owner["startup_only"] if x["owner"]=="BC101"}
assert regs=={0x3f60,0x3f64,0x3f68}
assert len(regs)==3

print("E006S_VERIFY_PASS")
print("bc101_regs=3 range=0x3f60..0x3f68")
print("rear_tuning_enable=0 disabled_image=zero_initialized")
print("common_setting=nonzero_min_128 region_values=112x4")
print("raw_windows_command_values=false")
