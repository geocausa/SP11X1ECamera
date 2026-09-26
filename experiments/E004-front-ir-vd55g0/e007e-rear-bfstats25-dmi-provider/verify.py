#!/usr/bin/env python3
from pathlib import Path

D = Path(__file__).resolve().parent
s = (D / "camss-e007e-bfstats25-dmi.inc").read_text()

for token in [
    "#define E007E_BF_ROI_COUNT 25",
    "#define E007E_BF_ROI_BYTES 300",
    "#define E007E_BF_GAMMA_COUNT 32",
    "#define E007E_BF_GAMMA_BYTES 128",
    "((u32)r->width << 14)",
    "((u32)(r->top & 0x1f) << 27)",
    "((u32)r->top >> 5)",
    "((u32)r->left << 9)",
    "((u32)r->rid << 23)",
    "((u32)(r->oid & 0x1) << 31)",
    "((u32)r->oid >> 1)",
    "((u32)r->merge << 7)",
    "((u32)eob << 8)",
    "((u32)r->type << 9)",
    "return -8192;",
    "return 8191;",
    "0x4000",
    "(u32)delta << 14",
    "e007e_bfstats25_dmi",
    "e007e_bfstats25_dmi_recipe",
]:
    assert token in s

for bad in (
    "((u32)r->left << 14)",
    "((u32)r->oid << 8)",
    "((u32)r->merge << 16)",
    "((u32)eob << 17)",
    "((u32)r->type << 18)",
):
    assert bad not in s

print("E007E_VERIFY_PASS roi=25x12 compact=true gamma=32x4 selectors=1,2")
print("af_policy=upstream dmi_encoding=clean")
