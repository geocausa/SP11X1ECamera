#!/usr/bin/env python3
"""Negative tests for original ARM64 lifecycle instruction emulation, offline."""
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gl",HERE/"emulate_flash_lifecycle.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
negatives=0
original=m.PRIOR_SHA
m.PRIOR_SHA="0"*64
try:
    for probe in (lambda:m.start(),lambda:m.stop()):
        try:probe()
        except AssertionError:negatives+=1
        else:raise AssertionError("changed original-emulator SHA was accepted")
finally:m.PRIOR_SHA=original

for first,why in (
    (lambda:m.start(1),"non-boolean previous-active flag"),
    (lambda:m.start(False,"prior_off"),"impossible previous-off fixture"),
    (lambda:m.start(False,"hard_fault"),"unknown fault phase"),
    (lambda:m.start(False,1),"nonstring fault phase"),
    (lambda:m.stop(0),"non-boolean stop error"),
    (lambda:m.stop("true"),"string stop error"),
):
    try:first()
    except AssertionError:negatives+=1
    else:raise AssertionError("invalid scenario accepted "+why)

assert m.start(True,"prior_off")=={
    "calls":["prior_off","current","timer","strobe_on"],
    "returned_success":True,"software_active_flag":1,
}
assert m.start(False,"strobe_on")=={
    "calls":["current","timer","strobe_on"],
    "returned_success":False,"software_active_flag":0,
}
assert m.stop(True)=={
    "calls":["strobe_off"],
    "returned_success":False,"software_active_flag":1,
}
a=json.loads((HERE/"evidence/RESULT.json").read_text())
assert a["native_emitter_enable_authorized"] is False
assert a["physical_led_state_after_error_measured"] is False
assert a["emulation_script_sha256"]==sha256((HERE/"emulate_flash_lifecycle.py").read_bytes()).hexdigest()
assert a["negative_test_sha256"]==sha256(Path(__file__).read_bytes()).hexdigest()
assert negatives==8
print("E004GL_ORIGINAL_WINDOWS_LIFECYCLE_CPU_FAULT_NEGATIVES=PASS CASES=8")
print("E004GL_REARM_AFTER_MOCKED_OFF_FAILURE_AND_STOP_ERROR_STATE=PASS")
print("E004GL_IR_EMITTER=OFF PHYSICAL_FAULT_OFF=UNPROVEN WINDOWS_BOOT=NO")
