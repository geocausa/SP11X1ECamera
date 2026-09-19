#!/usr/bin/env python3
"""Negative CPU control-flow tests for additional Windows flash ON/OFF routes."""
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gk",HERE/"emulate_teardown.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
old=m.PRIOR_SHA
m.PRIOR_SHA="0"*64
try:
    try:m.run_aux(m.OFF_AUX)
    except AssertionError:pass
    else:raise AssertionError("previous emulator source hash drift accepted")
finally:m.PRIOR_SHA=old
for bad in (0,0x4d58,0x6de8,0x6e60):
    try:m.run_aux(bad)
    except AssertionError:pass
    else:raise AssertionError("unsupported auxiliary entry accepted")
for bad in (0,1,"false"):
    try:m.run_aux(m.OFF_AUX,bad)
    except AssertionError:pass
    else:raise AssertionError("nonboolean transport fixture accepted")
on,off=m.check(m.previous())
assert on[0]["payload"]==[1,0,0,1] and off[0]["payload"]==[0,0,0,0]
print("E004GK_ORIGINAL_WINDOWS_AUX_PATH_NEGATIVES=PASS CASES=8")
print("E004GK_ORIGINAL_OFF_WRAPPER_PAYLOAD=PASS ERRORS_PROPAGATE=PASS")
print("PMIC_BUS_MOCKED=YES AUTONOMOUS_LED_CUTOFF=UNPROVEN")
