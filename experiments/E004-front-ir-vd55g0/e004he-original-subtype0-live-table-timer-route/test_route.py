#!/usr/bin/env python3
"""E004he: reject changed OEM flash/PMIC cross-driver timer and strobe routes."""
from pathlib import Path
import importlib.util
import pefile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004he_verify",HERE/"verify_route.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
flash=m.original("qccamflash8380")
pmic=m.original("qcpmic8380")
result=m.verify(flash,pmic)
assert m.prior()
assert result["normal_subtype_zero_contains_direct_timer_helper_call"] is False
assert result["windows_normal_subtype_zero_actual_0x93_timer_source_identified"] is False
assert result["verified_cross_driver_commands"]["timer"]["ioctl"]=="0x802f0fac"
assert result["verified_cross_driver_commands"]["strobe"]["ioctl"]=="0x802f0fc8"
mutations=(
    ("flash",0x4d50),("flash",0x4e80),("flash",0x4dc8),
    ("flash",0x5ae8),("flash",0x5b2c),("flash",0x5b48),
    ("flash",0x5bd4),("flash",0x5c20),("flash",0x5c50),
    ("flash",0x5c64),("pmic",0x7bf8),("pmic",0x7c10),
    ("pmic",0x6f84),("pmic",0x706c),("pmic",0x73a4),
    ("pmic",0x39470+0x28),("pmic",0x39470+0x90),
    ("pmic",0x28680),("pmic",0x287bc),
)
count=0
for name,rva in mutations:
    target=flash if name=="flash" else pmic
    raw=bytearray(target.__data__)
    raw[target.get_offset_from_rva(rva)]^=0x40
    wrong=pefile.PE(data=bytes(raw))
    try:m.verify(wrong,pmic) if name=="flash" else m.verify(flash,wrong)
    except AssertionError:count+=1
    else:raise AssertionError("E004HE_MUTATION_ACCEPTED "+name+" "+hex(rva))
assert count==len(mutations)
print("E004HE_OEM_ORIGINAL_FLASH_TIMER_STROBE_ROUTE_NEGATIVES=PASS COUNT="+str(count))
print("E004HE_NO_WINDOWS_BOOT_CAMERA_PMIC_LED_OR_EMITTER_ACTIVITY=YES")
