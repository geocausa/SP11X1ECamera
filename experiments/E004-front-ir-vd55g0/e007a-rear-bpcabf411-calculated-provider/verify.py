#!/usr/bin/env python3
from pathlib import Path

here = Path(__file__).resolve().parent
src = (here / "camss-e007a-bpcabf411.inc").read_text()
regs = [0x49b8, 0x49bc, 0x49d0, 0x49d4, 0x49d8, 0x49dc, 0x49e0]
for r in regs:
    assert f"0x{r:04x}" in src
assert src.count("case 0x") == 7
assert "signed10[c] < -512" in src and "signed10[c] > 511" in src
assert "unsigned9[c] > 0x1ff" in src
assert "nibble4[c] > 0xf" in src
assert "nibble_group[c][i] > 0xf" in src
assert "& 0x3ff" in src
assert "<< 16" in src and "<< 28" in src
assert "e007a_pack_bytes" in src
assert "e007a_bpcabf411_provider_recipe" in src
assert "captured Windows register words" in src
for bad in ("curve_delta", "curve_base", "curve_shift", "curve_sample",
            "curve_slope_mantissa", "curve_slope_exp"):
    assert bad not in src
print("E007A_VERIFY_PASS regs=7 calculated_output_boundary=true")
