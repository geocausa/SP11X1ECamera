#!/usr/bin/env python3
"""E004hk: exact original PMIC/SPMI GUID, transport, selector negatives."""
from pathlib import Path
import importlib.util,pefile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hk_verifier",HERE/"verify_bus.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
pmic=m.original("qcpmic8380")
spmi=m.original("qcspmi8380")
r=m.audit(pmic,spmi)
assert m.prior()
assert r["original_timer_0x93_first_writer_identified"] is False
assert r["spmi_provider_interface_bound_at_runtime_in_this_stage"] is False
assert r["lower_indirect_function_is_specific_original_spmi_method_verified"] is False
assert m.model_selector(0,1,0xee3e,1)==0x0001ee3e
bad=((2,1,0xee3e,1),(-1,1,0xee3e,1),(0,14,0xee3e,1),
     (0,1,0x10000,1),(0,1,-1,1),(0,1,0xee3e,0),
     (0,1,0xee3e,257),(0,True,0xee3e,1))
for arguments in bad:
    try:m.model_selector(*arguments)
    except AssertionError:pass
    else:raise AssertionError("E004HK_UNREJECTED_SELECTOR_INPUT "+str(arguments))
corruptions=(
    ("pmic",0x37058),("spmi",0xa1d8),
    ("pmic",0x393c),("pmic",0x3948),
    ("pmic",0x3958),("pmic",0x395c),
    ("pmic",0x3974),("spmi",0x3efc),
    ("spmi",0x3f10),("spmi",0x3f24),
    ("spmi",0x3f38),("pmic",0x23de8),
    ("pmic",0x23df0),("pmic",0x23ec4),
    ("pmic",0x23ec8),("pmic",0x23ed0),
    ("pmic",0x23ed8),("pmic",0x23edc),
    ("pmic",0x23f14),("pmic",0x23f1c),
    ("pmic",0x23f24),("pmic",0x23f3c),
    ("pmic",0x23a04),("pmic",0x32c2c),
)
for name,rva in corruptions:
    original=pmic if name=="pmic" else spmi
    source=bytearray(original.__data__)
    source[original.get_offset_from_rva(rva)]^=0x40
    wrong=pefile.PE(data=bytes(source))
    try:m.audit(wrong,spmi) if name=="pmic" else m.audit(pmic,wrong)
    except AssertionError:pass
    else:raise AssertionError("E004HK_UNREJECTED_ORIGINAL_OPCODE "+name+" "+hex(rva))
print("E004HK_ORIGINAL_PMIC_SPMI_GUID_OPCODE_SELECTOR_NEGATIVES=PASS COUNT="+str(len(bad)+len(corruptions)))
print("E004HK_NORM_BUS0_SID1_SELECTOR_IS_OFFLINE_MODEL_NOT_ACTUAL_LED_WIRING=PASS")
