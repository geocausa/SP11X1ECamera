#!/usr/bin/env python3
"""E004hl: exact original SPMI provider/PMIC consumer callback slot mutations."""
from pathlib import Path
import importlib.util
import pefile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hl_verify",HERE/"verify_spmi_callback.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
spmi=m.original("qcspmi8380",m.SPMI_HASH)
pmic=m.original("qcpmic8380",m.PMIC_HASH)
r=m.audit(spmi,pmic)
assert m.prior()
assert r["provider_original_callback_rva"]=="0x1660"
assert r["pmic_consumer_raw_write_indirect_slot_offset"]=="0x30"
assert r["pmic_raw_callback_invoked_on_actual_windows_timer_during_this_stage"] is False
alterations=(
    ("spmi",0x3e4c),("spmi",0x3e54),
    ("spmi",0x3e60),("spmi",0x3e68),
    ("spmi",0x3e74),("spmi",0x3e78),
    ("spmi",0x3e84),("spmi",0x3e88),
    ("spmi",0x3e9c),("spmi",0x3ec4),
    ("spmi",0x3ef4),("spmi",0x3efc),
    ("spmi",0x3f00),("spmi",0x3f10),
    ("spmi",0x3f24),("spmi",0x3f38),
    ("spmi",0x1660),("spmi",0x1688),
    ("spmi",0x168c),("spmi",0x1690),
    ("spmi",0x1698),("spmi",0x177c),
    ("spmi",0x1780),("spmi",0x1784),
    ("spmi",0x1788),
    ("pmic",0x393c),("pmic",0x3948),
    ("pmic",0x395c),("pmic",0x3974),
    ("pmic",0x23f1c),("pmic",0x23f24),
    ("pmic",0x23f2c),("pmic",0x23f3c),
)
for name,rva in alterations:
    pe=spmi if name=="spmi" else pmic
    mutated=bytearray(pe.__data__)
    mutated[pe.get_offset_from_rva(rva)]^=0x40
    wrong=pefile.PE(data=bytes(mutated))
    try:m.audit(wrong,pmic) if name=="spmi" else m.audit(spmi,wrong)
    except AssertionError:pass
    else:raise AssertionError("E004HL_MUTATION_ACCEPTED "+name+" "+hex(rva))
print("E004HL_ORIGINAL_SPMI_CALLBACK_PLUS30_STRUCT_MUTATIONS=PASS COUNT="+str(len(alterations)))
print("E004HL_LIVE_SPMI_WRITER_OR_TIMER_FIRST_ORIGIN=UNOBSERVED NATIVE_IR=OFF")
