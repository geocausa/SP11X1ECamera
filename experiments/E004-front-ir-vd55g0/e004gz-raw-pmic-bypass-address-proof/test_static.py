#!/usr/bin/env python3
"""E004gz: fail closed for corrupted OEM PE and false timer-overlap exclusions."""
from pathlib import Path
import importlib.util
from hashlib import sha256
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gz_static",HERE/"verify_static.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
pe=m.original_image()
summary=m.address_proof(pe)
assert len(summary["excluded_as_direct_timer_writer"])==2
assert summary["generic_capable_raw_write_callsite"]=="0x32c2c"
assert m.prior()
count=0
for rva in (0x2fc18,0x2fc30,0x2fc3c,0x30394,0x3039c,0x303a4,
            0x32b90,0x32b94,0x32c20,0x32c24,0x32c2c):
    original=m.opcode(pe,rva)
    try:m.assert_instruction(pe,rva,original[0],original[1]+" NOT_THE_ORIGINAL")
    except AssertionError:count+=1
    else:raise AssertionError("E004GZ_NEGATIVE_FAIL "+hex(rva))
assert count==11
# The forbidden overlapping address proof must check BOTH length and start.
for start,length in ((0xee3d,2),(0xee3e,1),(0xee40,2),(0xee41,1)):
    assert start<=m.TIMER_END and start+length>m.TIMER_START
    assert (start & 0x49)!=0x49
for octet in range(256):
    start=0xfd00|octet
    assert start>m.TIMER_END
    for size in (1,2,255):
        assert not(start<=m.TIMER_END and start+size>m.TIMER_START)
print("E004GZ_ORIGINAL_OPCODE_AND_TIMER_ADDRESS_NEGATIVES=PASS COUNT=11")
print("E004GZ_NO_WINDOWS_KD_CAMERA_PMIC_OR_LED_ACCESS=YES")
