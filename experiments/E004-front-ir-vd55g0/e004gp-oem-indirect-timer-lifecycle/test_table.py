#!/usr/bin/env python3
"""Fail-closed synthetic PE table/instruction mutation tests, never execute PE."""
from pathlib import Path
from hashlib import sha256
import importlib.util
import pefile
import struct

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gp",HERE/"verify_table.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
paths=list(m.ARCH.glob("*/"+m.NAME))
assert len(paths)==1
raw=paths[0].read_bytes()
m.check(raw)
count=0

# Pinned image drift must independently reject any changed original bytes.
try:m.check(raw+b"unauthorized")
except AssertionError:count+=1
else:raise AssertionError("unapproved Windows PE drift accepted")

# In synthetic memory only, repin a modified PE so each *structural* invariant
# is also tested rather than merely rejecting it on the global SHA mismatch.
original_hash=m.EXPECTED_HASH
pe=pefile.PE(data=raw)
for rva,replacement in (
    (0x39470,struct.pack("<Q",m.IMAGE_BASE+0x260b4)),
    (0x39498,struct.pack("<Q",m.IMAGE_BASE+m.TIMER_SINGLE_RVA)),
    (0x394a0,struct.pack("<Q",m.IMAGE_BASE+m.TIMER_BULK_RVA)),
    (0x39500,struct.pack("<Q",m.IMAGE_BASE+0x285c4)),
    (0x210f0,b"\x1f\x20\x03\xd5"),
    (0x210f4,b"\x1f\x20\x03\xd5"),
    (0x210f8,b"\x1f\x20\x03\xd5"),
    (0x210fc,b"\x1f\x20\x03\xd5"),
    (0x21100,b"\x1f\x20\x03\xd5"),
):
    altered=bytearray(raw)
    offset=pe.get_offset_from_rva(rva)
    assert offset is not None and offset>=0
    altered[offset:offset+len(replacement)]=replacement
    m.EXPECTED_HASH=sha256(altered).hexdigest()
    try:m.check(bytes(altered))
    except AssertionError:count+=1
    else:raise AssertionError(f"mutated original PE invariant accepted at {rva:#x}")
m.EXPECTED_HASH=original_hash
assert count==10
print("E004GP_PMIC_TABLE_BINARY_PIN_AND_STRUCTURE_NEGATIVES=PASS CASES=10")
print("E004GP_NO_BINARY_REWRITTEN_OR_EXECUTED=YES NO_HARDWARE_ACCESS=YES")
