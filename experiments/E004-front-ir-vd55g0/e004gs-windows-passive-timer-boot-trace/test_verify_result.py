#!/usr/bin/env python3
"""E004gs: reject tampered archive/result and invented passive timer observations."""
from pathlib import Path
import importlib.util
import json
import zipfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gs_verify", HERE/"verify_result.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
with zipfile.ZipFile(m.ZIP) as z:
    raw=z.read("ORIGINAL-SP7-KD.log")
result=json.loads(m.RESULT.read_text())
m.validate(raw,result)
mutations=(
    (raw+b"tamper",result,"raw log hash"),
    (raw.replace(b"E004GS_PASSIVE_ALL_KD_BP_CLEARED",b"KD_BP_NOT_CLEARED"),
     result,"breakpoint cleanup"),
    (raw,result|{"windows_new_boot_count":2},"incorrect boot count"),
    (raw,result|{"first_windows_boot_init_timer_requests_excluded":True},
     "unsupported early boot claim"),
    (raw,result|{"linux_native_emitter_activated":True},"emitter misuse"),
    (raw,result|{"passive_idle_timer_breakpoint_hits":
                       {"timer4":1,"timer1":0,"flash_timer_helper":0}},
     "fabricated callback hit"),
)
for log,metadata,why in mutations:
    try: m.validate(log,metadata)
    except AssertionError:pass
    else:raise AssertionError("E004GS mutation accepted: "+why)
print("E004GS_NEGATIVE_EVIDENCE_TESTS=PASS CASES=6")
print("NO_REPEATED_WINDOWS_CAPTURE_OR_KD_IDENTITY=YES")
