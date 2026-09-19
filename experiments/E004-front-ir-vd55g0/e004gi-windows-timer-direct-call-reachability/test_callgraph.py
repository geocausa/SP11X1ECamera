#!/usr/bin/env python3
"""Offline negative tests for pinned direct-call and type-0 branch mapping."""
import importlib.util
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gi",HERE/"verify_callgraph.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
code=v.disassemble()
prior=json.loads((v.ROOT/"experiments/E004-front-ir-vd55g0/e004gb-windows-flash-enable-explicit-kd-predicate/evidence/RESULT.json").read_text())
v.verify(code,prior)
negative=0
for addr in (0x4938,0x5b2c,0x5ae8,0x5aec,0x5b44,0x5b48,0x5b7c,0x5c64,0x5ce4):
    bad=dict(code)
    bad[addr]=("nop","")
    try: v.verify(bad,prior)
    except AssertionError: negative+=1
    else: raise AssertionError(f"tampered code at {addr:#x} passed")
for change in ({"identity_consumed":False},{"kd_pre_calls":10},
               {"windows_pmic_module":"wrong.sys"}):
    bad=dict(prior,**change)
    try: v.verify(code,bad)
    except AssertionError: negative+=1
    else: raise AssertionError(f"tampered archived Windows state accepted {change}")
assert negative==12
print(f"E004GI_DIRECT_BRANCH_AND_ARCHIVED_TRACE_NEGATIVES=PASS CASES={negative}")
print("E004GI_NORMAL_TYPE0_DIRECT_TIMER=NONE OTHER_TIMER_PATHS=UNEXCLUDED")
print("PHYSICAL_TIMER_AUTHORITY=UNPROVEN EMITTER=OFF")
