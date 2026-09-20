#!/usr/bin/env python3
"""E004ha: reject wrong ARM64 descriptor addresses and fake callback identities."""
from pathlib import Path
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004ha_static",HERE/"verify_static.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
pe=m.original()
result=m.verify(pe)
assert result["generic_write_callback_slot_rva"]=="0x3a510"
assert result["generic_write_callback_rva"]=="0x32b70"
count=0
mutations=(
    (0x2021c,"bl","#0x14002f918"),
    (0x20304,"bl","#0x14002fdd0"),
    (0x2f9d0,"add","x8, x8, #0x508"),
    (0x2f9d8,"str","x8, [x11, x9]"),
    (0x2fdf8,"cmp","w5, #0x49"),
    (0x2fe60,"add","x8, x8, #0x4f8"),
    (0x2fe68,"str","x8, [x11, x12]"),
    (0x32b90,"uxth","w25, w2"),
    (0x32b94,"uxtb","w20, w1"),
    (0x32c20,"mov","w4, w25"),
    (0x32c24,"mov","w2, w20"),
    (0x32c2c,"bl","#0x140023968"),
)
for rva,mn,wrong in mutations:
    try:
        m.expect(pe,rva,mn,wrong)
    except AssertionError:
        count+=1
    else:
        raise AssertionError("E004HA_NEGATIVE_ACCEPTED "+hex(rva))
assert count==len(mutations)
assert m.prior_check()
print("E004HA_ORIGINAL_CALLBACK_DESCRIPTOR_OPCODE_NEGATIVES=PASS COUNT="+str(count))
print("E004HA_NEGATIVES_ARE_OFFLINE_ONLY=YES")
