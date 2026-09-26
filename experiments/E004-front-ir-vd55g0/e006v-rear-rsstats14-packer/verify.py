#!/usr/bin/env python3
from pathlib import Path
import json

D=Path(__file__).resolve().parent
S=json.loads((D/"SOURCE-SAFE.json").read_text())
V=json.loads((D/"PRIVATE-VALIDATION-SAFE.json").read_text())
C=(D/"camss-e006v-rsstats14.inc").read_text()

assert S["schema"]=="E006v-rear-rsstats14-source-safe-v1"
assert S["module"]=="IFERSStats14Titan680"
assert S["functions"]["create_cmd_list"]=="0x180b44840"
assert S["functions"]["pack_iq_register_setting"]=="0x180b44930"
assert S["functions"]["modern_adjust_roi"]=="0x180a0e538"
assert S["writes"]==[{"register":"0xbe60","count":1},{"register":"0xbe68","count":3}]
a=S["modern_adjust_roi"]
assert a["h_num_range"]==[1,16]
assert a["v_num_range"]==[1,1024]
assert a["region_width_range"]==[2,8192]
assert a["region_height_range"]==[2,16]
assert a["region_height_even"] is True and a["v_offset_even"] is True
assert a["shift_rule"]=="max(bit_length(region_width * region_height) - 4, 0)"
assert S["raw_windows_command_values_committed"] is False

assert V["schema"]=="E006v-rear-rsstats14-private-validation-safe-v1"
assert V["exact_repack_count"]==3 and V["exact_repack_total"]==3
assert V["startup1_exact_semantic_repack"] is True
assert V["startup2_exact_semantic_repack"] is True
assert V["startup3_exact_semantic_repack"] is True
assert V["startup4_rs_block_absent"] is True
assert V["reserved_bits_zero_in_validated_blocks"] is True
assert V["raw_register_values_committed"] is False
assert V["raw_packet_bytes_committed"] is False

for token in [
    "struct e006v_rs14_state","e006v_rs14_shift_bits",
    "e006v_rs14_validate","e006v_rs14_lookup","e006v_rs_stats14_recipe",
    "s->region_width < 2 || s->region_width > 0x2000",
    "s->region_height < 2 || s->region_height > 16",
    "(s->region_height & 1)","(s->v_offset & 1)",
    "case 0xbe60:","case 0xbe68:","case 0xbe6c:","case 0xbe70:"
]:
    assert token in C

def shift(w,h):
    area=w*h
    bits=0
    while area:
        bits+=1
        area >>= 1
    return max(bits-4,0)

assert shift(2,2)==0
assert shift(4,4)==1
assert shift(8,2)==1
assert shift(8192,16)==14

P=D.parent
owner=json.loads((P/"e006l-rear-startup-register-ownership"/"STARTUP-REGISTER-OWNER-MAP.json").read_text())
regs={int(x["register"],16) for x in owner["startup_only"] if x["owner"]=="RS_STATS14"}
assert regs=={0xbe60,0xbe68,0xbe6c,0xbe70}

recipe=json.loads((P/"e006k-rear-startup-main-symbolic-recipe"/"STARTUP-SYMBOLIC-RECIPE.json").read_text())
want={"0xbe60","0xbe68","0xbe6c","0xbe70"}
presence={}
for name,v in recipe["variants"].items():
    regs=set()
    for cmd in v["commands"]:
        regs.update(x["register_offset"] for x in cmd.get("values",[]))
    presence[name]=regs
for name in ("startup1","startup2","startup3"):
    assert want <= presence[name]
assert want.isdisjoint(presence["startup4"])

print("E006V_VERIFY_PASS")
print("rsstats14_regs=4 startup1_3=present startup4=absent")
print("shift_rule=modern_AdjustROI_bit_length_minus_4")
print("upstream_AFD_state=semantic_input_not_frozen")
print("raw_windows_command_values=false")
