#!/usr/bin/env python3
"""E004gu: negative tests for true PMIC table vs CFG/unwind metadata.

All mutated PEs are bytes in RAM. Original DriverStore files never change.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util
import pefile
import struct

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gu",HERE/"verify_static.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
files=sorted(m.ARCH.glob("*/*.sys"))
p=next(f for f in files if f.name==m.NAME)
raw=p.read_bytes()
m.audit_archive(files)
m.audit_pmic_image(raw)
m.audit_literal_sites(files)
m.audit_prior()
negative=0
try:
    m.audit_pmic_image(raw+b"drift")
except AssertionError:
    negative+=1
else:
    raise AssertionError("Original PE hash change accepted")

pe=pefile.PE(data=raw)
old=m.PE_HASHES[m.NAME]
for rva,patch in (
    (0x36d48,struct.pack("<I",0xee3d)),
    (0x36d54,struct.pack("<I",0xee42)),
    (0x39498,struct.pack("<Q",m.BASE+0x26f30)),
    (0x394a0,struct.pack("<Q",m.BASE+0x26d50)),
    (0x364c4,struct.pack("<I",0x26f30)),
    (0x364c8,struct.pack("<I",0x26d50)),
    (0x3faa0,struct.pack("<I",0x26f30)),
    (0x3faa8,struct.pack("<I",0x26d50)),
    (0x26e2c,b"\x1f\x20\x03\xd5"),
    (0x27010,b"\x1f\x20\x03\xd5"),
):
    altered=bytearray(raw)
    offset=pe.get_offset_from_rva(rva)
    assert offset is not None and offset>=0
    altered[offset:offset+len(patch)]=patch
    m.PE_HASHES[m.NAME]=sha256(altered).hexdigest()
    try:
        m.audit_pmic_image(bytes(altered))
    except AssertionError:
        negative+=1
    else:
        raise AssertionError(f"Mutated original PE structural invariant accepted at {rva:#x}")
    finally:
        m.PE_HASHES[m.NAME]=old

class SyntheticArchivedSys:
    """Read-only in-memory injected SYS sequence, never edits DriverStore."""
    name="qcpmicglink8380.sys"
    def read_bytes(self):
        return b"synthetic-no-real-driver"+m.TIMER_BYTES

replacement=[SyntheticArchivedSys() if f.name==SyntheticArchivedSys.name else f
             for f in files]
try:
    m.audit_archive(replacement)
except AssertionError:
    negative+=1
else:
    raise AssertionError("Second candidate firmware-driver table accepted")

expect=12
assert negative==expect,(negative,expect)
print(f"E004GU_PIN_AND_STRUCTURAL_PE_METADATA_NEGATIVES=PASS COUNT={negative}")
print("E004GU_SYNTHETIC_BINARY_MUTATION=MEMORY_ONLY NO_CAMERA_PMIC_OR_IR=YES")
