#!/usr/bin/env python3
"""E004gh CPU-level Windows timer regression/negative tests; no hardware access."""
from pathlib import Path
import importlib.util
import json
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("original_timer",HERE/"emulate_timer.py")
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

orig=m.PREV_SHA
m.PREV_SHA="0"*64
try:
    try: m.run_timer(200,True)
    except AssertionError: pass
    else: raise AssertionError("drifted CPU emulator accepted")
finally:
    m.PREV_SHA=orig

for ms,enabled,fail in ((-1,True,0),(1282,True,0),(200,1,0),
                         (200,True,-1),(200,True,6),("200",True,0)):
    try: m.run_timer(ms,enabled,fail)
    except AssertionError: pass
    else: raise AssertionError("invalid timer fixture accepted")

for ms in (0,10,11,19,20,199,200,201,1270,1280):
    requested=ms if ms else 10
    writes,status=m.run_timer(requested,ms!=0)
    want=0 if ms==0 else 0x80+(ms-10)//10
    assert status==0 and len(writes)==5
    assert [int(w["request"],16) for w in writes]==[want,want,0,0,0]
    assert [w["register"] for w in writes]==[
        "0xee3e","0xee41","0xee3f","0xee40","0xee40"]
for i in range(1,6):
    writes,code=m.run_timer(200,True,i)
    assert code!=0 and len(writes)==(2 if i<=2 else 4 if i<=4 else 5)
a=json.loads((HERE/"evidence/RESULT.json").read_text())
assert a["linux_emitter_activation_authorized"] is False
assert a["archived_idle_byte_proves_timer_enforcement"] is False
assert a["type0_windows_camera_stream_called_timer_handler_proven"] is False
print("E004GH_NEGATIVE_SHA_PARAMS_AND_ENCODING=PASS")
print("E004GH_PAIRED_WRITE_FAILURES=PASS FIVE_INJECTED_SOFTWARE_ERRORS")
print("HARDWARE_LED_TIMING=NOT_MEASURED WINDOWS_REBOOT=NO IR_EMITTER=OFF")
