#!/usr/bin/env python3
"""Negative static disassembly pinning and four offline Windows OFF fault paths."""
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gf",HERE/"verify_shutdown.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
pmic=m.section("qcpmic8380.sys",0x140028620,0x140028808)
flash=m.section("qccamflash8380.sys",0x140005c88,0x140005d00)
checks=[
    (flash,0x5cd0,"bl"),(flash,0x5ce4,"bl"),
    (pmic,0x28680,"0xee46"),(pmic,0x28698,"bl"),
    (pmic,0x2869c,"cbnz\tw0, 0x140028804"),(pmic,0x287bc,"0xee4e"),
    (pmic,0x287c4,"bl"),(pmic,0x287c8,"cbnz\tw0, 0x140028804"),
]
for ins,off,substr in checks:
    m.check(ins,off,substr)
    altered=dict(ins)
    altered[0x140000000+off]="nop"
    try:
        m.check(altered,off,substr)
    except AssertionError:
        pass
    else:
        raise AssertionError(f"static code tampering undetected at {off:#x}")
for module_ok in (False,True):
    for channel_ok in (False,True):
        module,channels,calls,status=m.run_fault_model(module_ok,channel_ok,True,9)
        assert module is (not module_ok)
        assert channels==(0 if module_ok and channel_ok else 9)
        assert ("request_channels_off" in calls) is module_ok
        assert (status=="request_succeeded") is (module_ok and channel_ok)
print("E004GF_STATIC_INSTRUCTION_NEGATIVE_TESTS=PASS CASES="+str(len(checks)))
print("E004GF_OFFLINE_FAULT_MODEL=PASS CASES=4 MODEL_NOT_LIVE_WINDOWS")
print("E004GF_MODULE_FIRST_FAILURE_SKIPS_CHANNEL_DISARM=YES")
