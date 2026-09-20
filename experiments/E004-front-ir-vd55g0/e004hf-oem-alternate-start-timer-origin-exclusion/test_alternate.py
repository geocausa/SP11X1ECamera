#!/usr/bin/env python3
"""E004hf: reject changed OEM alternate-start/timer-encoding instruction bytes."""
from pathlib import Path
import importlib.util,pefile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hf_original",HERE/"verify_alternate.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
flash=m.image("qccamflash8380",m.FLASH_HASH)
pmic=m.image("qcpmic8380",m.PMIC_HASH)
result=m.original_route(flash,pmic)
assert m.prior()
assert result["fixed_helper_directly_requests_idle_0x93"] is False
assert result["earliest_real_oem_or_firmware_0x93_writer_identified"] is False
assert result["original_flash_direct_alternate_start_caller_rvas"]==["0x6638","0x6a20"]
mutations=(
    ("flash",0x492c),("flash",0x4938),("flash",0x4954),
    ("flash",0x6424),("flash",0x6630),("flash",0x6638),
    ("flash",0x69a8),("flash",0x6a0c),("flash",0x6a10),
    ("flash",0x6a14),("flash",0x6a20),("flash",0x4e18),
    ("flash",0x4e2c),("flash",0x4e30),("flash",0x4e78),
    ("flash",0x4e80),("pmic",0x39498),("pmic",0x26de0),
    ("pmic",0x26e40),
)
count=0
for name,rva in mutations:
    source=flash if name=="flash" else pmic
    altered=bytearray(source.__data__)
    altered[source.get_offset_from_rva(rva)]^=0x40
    wrong=pefile.PE(data=bytes(altered))
    try:
        m.original_route(wrong,pmic) if name=="flash" else m.original_route(flash,wrong)
    except AssertionError:count+=1
    else:raise AssertionError("E004HF_UNREJECTED_MUTATION "+name+" "+hex(rva))
assert count==len(mutations)
print("E004HF_ALTERNATE_START_AND_FIXED_TIMER_ORIGINAL_OPCODE_NEGATIVES=PASS COUNT="+str(count))
print("E004HF_MUTATED_OEM_BINARIES_IN_MEMORY_ONLY_NO_CAMERA_PMIC_OR_LED=YES")
