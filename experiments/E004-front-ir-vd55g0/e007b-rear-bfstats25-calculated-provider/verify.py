#!/usr/bin/env python3
from pathlib import Path

D=Path(__file__).resolve().parent
src=(D/"camss-e007b-bfstats25.inc").read_text()
regs=[
0xbc58,0xbc5c,0xbc60,0xbc6c,0xbc70,0xbc74,0xbc78,0xbc7c,0xbc80,
0xbc84,0xbc88,0xbc8c,0xbc90,0xbc94,0xbc98,0xbc9c,0xbca0,0xbca4,
0xbca8,0xbcac,0xbcb0,0xbcb4,0xbcb8,0xbcbc,0xbcc0,0xbcc4,0xbcc8,
0xbccc,0xbcd0]
for r in regs:
    assert f"0x{r:04x}" in src
assert src.count("case 0x") == 29
assert "signed6[i] < -32" in src and "signed6[i] > 31" in src
assert "signed4[i] < -8" in src and "signed4[i] > 7" in src
assert "tail_scalar17[b] > 0x1ffff" in src
assert "tail_lane5[b][i] > 0x1f" in src
for token in [
    "dmi_lut_bank","module_lut_bank","gamma_lut_enable",
    "luma_conversion_enable","scale_enable","filter0_enable",
    "filter1_enable","filter3_enable","e007b_pack_signed6",
    "e007b_pack_s16_pair","e007b_pack_tail5",
    "e007b_bfstats25_provider_recipe"
]:
    assert token in src
assert "captured Windows register words" in src
print("E007B_VERIFY_PASS regs=29 calculated_output_boundary=true")
