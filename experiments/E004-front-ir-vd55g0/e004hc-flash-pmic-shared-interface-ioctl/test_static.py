#!/usr/bin/env python3
"""E004hc: reject synthetic instruction and original GUID/IOCTL mismatches."""
from pathlib import Path
import importlib.util
import pefile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hc_verify",HERE/"verify_static.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
flash=m.original("qccamflash8380")
pmic=m.original("qcpmic8380")
result=m.audit(flash,pmic)
assert result["shared_original_ioctl_code"]=="0x802f0fc8"
assert result["flash_ioctl_handler_is_generic_0x32b70_callback_proven"] is False
assert m.previous()
failures=0
for which,rva in (
    ("flash",0x49fc),("flash",0x4a00),
    ("flash",0x4a18),("flash",0x4b2c),
    ("flash",0x4b70),("flash",0x4a4c),("flash",0x4b20),("flash",0x4da4),
    ("flash",0x4da8),("flash",0xd858),
    ("flash",0x4dc8),("pmic",0x2578),
    ("pmic",0x36fb8),("pmic",0x71e0),
    ("pmic",0x71e8),("pmic",0x7c10),
    ("pmic",0x7378),("pmic",0x73a4),
    ("pmic",0x73d4),
):
    target=flash if which=="flash" else pmic
    original=bytes(target.__data__)
    candidate=bytearray(original)
    offset=target.get_offset_from_rva(rva)
    candidate[offset]^=0x40
    altered=pefile.PE(data=bytes(candidate))
    try:
        m.audit(altered,pmic) if which=="flash" else m.audit(flash,altered)
    except AssertionError:
        failures+=1
    else:
        raise AssertionError("E004HC_ORIGINAL_MUTATION_ACCEPTED "+which+" "+hex(rva))
assert failures==19
print("E004HC_ORIGINAL_OEM_GUID_IOCTL_OPCODE_NEGATIVE_TESTS=PASS COUNT="+str(failures))
print("E004HC_ORIGINAL_PE_MUTATION_ONLY_IN_MEMORY_NO_KD_CAMERA_LED=YES")
