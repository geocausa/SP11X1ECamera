#!/usr/bin/env python3
"""E004gv: original evidence and uncertainty-preservation mutation checks."""
from pathlib import Path
import importlib.util
import json
import zipfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gv", HERE/"verify_result.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
meta=json.loads(m.RESULT.read_text())
with zipfile.ZipFile(m.ZIP) as z: raw=z.read("ORIGINAL-SP7-EARLY-KD.log")
m.validate(raw,meta)
negative=0
cases=(
    (raw+b"tamper",meta,"original-KD-sha-drift"),
    (raw.replace(b"E004GV_ALL_KD_BREAKPOINTS_CLEARED",b"E004GV_NOT_CLEARED"),
     meta,"missing-cleanup"),
    (raw,meta|{"first_pmic_register_writer_observed":True},"fabricated-first-writer"),
    (raw,meta|{"absence_of_timer_writes_during_early_boot_proven":True},
     "unjustified-absence"),
    (raw,meta|{"one_shot_watcher_could_have_been_consumed_by_nonmatching_call":False},
     "removed-hook-uncertainty"),
    (raw,meta|{"native_ir_emitter_activated":True},"fabricated-emitter"),
    (raw,meta|{"golden_return_boot_id":"wrong-boot"},"wrong-rollback-boot"),
    (raw,meta|{"new_windows_boots_consumed":2},"reused-identity"),
)
for data,modified,why in cases:
    try:m.validate(data,modified)
    except AssertionError:negative+=1
    else:raise AssertionError("E004gv verifier accepted "+why)
assert negative==len(cases)
print("E004GV_ORIGINAL_KD_AND_UNKNOWN_FIRST_WRITER_NEGATIVE_TESTS=PASS COUNT=8")
print("E004GV_PHYSICAL_EMITTER_AND_PMIC_TEST=NOT_EXECUTED")
