#!/usr/bin/env python3
from pathlib import Path
import json
D=Path(__file__).resolve().parent
S=json.loads((D/"SOURCE-SAFE.json").read_text())
V=json.loads((D/"PRIVATE-VALIDATION-SAFE.json").read_text())
C=(D/"camss-e006x-tintlessbg17.inc").read_text()
assert S["schema"]=="E006x-rear-tintlessbg17-source-safe-v1"
assert S["functions"]["create_cmd_list"]=="0x180b45e60"
assert S["functions"]["pack_iq_register_setting"]=="0x180b39950"
assert S["functions"]["hardware_caps"]=="0x180b39870"
assert S["functions"]["check_dependence_change"]=="0x180a10e58"
assert S["writes"]==[
 {"register":"0xb66c","count":5},{"register":"0xb680","count":10},
 {"register":"0xb668","count":1},{"register":"0xb664","count":1},{"register":"0xb660","count":1}]
assert sum(x["count"] for x in S["writes"])==18
assert S["semantic_core"]["identical_to_e006w_aecbe17_packer"] is True
assert S["semantic_core"]["black_level_request_byte_offset"]=="0x2170"
assert V["exact_repack_count"]==2 and V["shared_e006w_core_exact"] is True
assert V["startup3_block_absent"] and V["startup4_block_absent"]
assert not V["raw_register_values_committed"] and not V["raw_packet_bytes_committed"]
for t in ["e006x_tintless_bg17_lookup","e006w_aecbe17_lookup","reg - 0x600","e006x_tintless_bg_stats17_recipe"]:
    assert t in C
P=D.parent
owner=json.loads((P/"e006l-rear-startup-register-ownership"/"STARTUP-REGISTER-OWNER-MAP.json").read_text())
regs={int(x["register"],16) for x in owner["startup_only"] if x["owner"]=="TINTLESS_BG_STATS17"}
assert regs==set(range(0xb660,0xb6a8,4))
recipe=json.loads((P/"e006k-rear-startup-main-symbolic-recipe"/"STARTUP-SYMBOLIC-RECIPE.json").read_text())
want={f"0x{x:04x}" for x in range(0xb660,0xb6a8,4)}
presence={}
for name,v in recipe["variants"].items():
    presence[name]={x["register_offset"] for c in v["commands"] for x in c.get("values",[])}
assert want<=presence["startup1"] and want<=presence["startup2"]
assert want.isdisjoint(presence["startup3"]) and want.isdisjoint(presence["startup4"])
print("E006X_VERIFY_PASS")
print("tintlessbg17_regs=18 startup1_2=present startup3_4=absent")
print("shared_e006w_semantic_core=true black_level=request_0x2170")
print("raw_windows_command_values=false")
