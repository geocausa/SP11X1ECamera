#!/usr/bin/env python3
from pathlib import Path
import json

D=Path(__file__).resolve().parent
S=json.loads((D/"SOURCE-SAFE.json").read_text())
V=json.loads((D/"PRIVATE-VALIDATION-SAFE.json").read_text())
C=(D/"camss-e006w-aecbe17.inc").read_text()

assert S["schema"]=="E006w-rear-aecbe17-source-safe-v1"
assert S["module"]=="IFEAECBEStats17Titan680"
assert S["functions"]["create_cmd_list"]=="0x180b3f660"
assert S["functions"]["create_sub_cmd_list"]=="0x180b3f7b0"
assert S["functions"]["pack_iq_register_setting"]=="0x180b3f860"
assert S["functions"]["modern_adjust_roi"]=="0x180a06288"
assert S["functions"]["validate_dependence_params"]=="0x180a067d8"
assert S["writes"]==[
  {"register":"0xb06c","count":5},
  {"register":"0xb080","count":10},
  {"register":"0xb068","count":1},
  {"register":"0xb064","count":1},
  {"register":"0xb060","count":1},
]
assert sum(x["count"] for x in S["writes"])==18
assert S["black_level_source"]["request_byte_offset"]=="0x2170"
assert S["fields"]["0xb060"]["quad_sync_enable"].startswith("bit9")
assert S["raw_windows_command_values_committed"] is False

assert V["schema"]=="E006w-rear-aecbe17-private-validation-safe-v1"
assert V["exact_repack_count"]==2 and V["exact_repack_total"]==2
assert V["startup1_exact_semantic_repack"] is True
assert V["startup2_exact_semantic_repack"] is True
assert V["startup3_block_absent"] is True
assert V["startup4_block_absent"] is True
assert V["words_per_emitted_startup"]==18
assert V["raw_register_values_committed"] is False
assert V["raw_packet_bytes_committed"] is False

for token in [
 "struct e006w_aecbe17_state","e006w_aecbe17_validate",
 "e006w_aecbe17_min_word","e006w_aecbe17_lookup",
 "e006w_aecbe_stats17_recipe","E006W_AECBE17_SAMPLE_PATTERN",
 "case 0xb060:","case 0xb064:","case 0xb068:","case 0xb06c:",
 "case 0xb070:","case 0xb074:","case 0xb078:","case 0xb07c:",
 "case 0xb080:","case 0xb084:","case 0xb088:","case 0xb08c:",
 "case 0xb090:","case 0xb094:","case 0xb0a4:"
]:
    assert token in C

P=D.parent
owner=json.loads((P/"e006l-rear-startup-register-ownership"/"STARTUP-REGISTER-OWNER-MAP.json").read_text())
regs={int(x["register"],16) for x in owner["startup_only"] if x["owner"]=="AEC_BE_STATS17"}
assert regs==set(range(0xb060,0xb0a8,4))

recipe=json.loads((P/"e006k-rear-startup-main-symbolic-recipe"/"STARTUP-SYMBOLIC-RECIPE.json").read_text())
want={f"0x{x:04x}" for x in range(0xb060,0xb0a8,4)}
presence={}
for name,v in recipe["variants"].items():
    rs={x["register_offset"] for c in v["commands"] for x in c.get("values",[])}
    presence[name]=rs
assert want <= presence["startup1"]
assert want <= presence["startup2"]
assert want.isdisjoint(presence["startup3"])
assert want.isdisjoint(presence["startup4"])

# Synthetic formula checks only; no private capture values.
def min_word(black):
    return (0 - (black << 13)) & 0xffffffff
assert min_word(0)==0
assert min_word(1)==0xffffe000
assert min_word(0x3ffff)==0x80002000
assert ((0x12 << 9) | (0x34 << 17) | (0x56 << 25)) & ~0xfefefe00 == 0

print("E006W_VERIFY_PASS")
print("aecbe17_regs=18 startup1_2=present startup3_4=absent")
print("black_level=request_0x2170 quad_sync=cfg_bit9 sample_pattern=0xffff")
print("raw_windows_command_values=false")
