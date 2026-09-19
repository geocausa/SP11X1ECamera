#!/usr/bin/env python3
"""Offline negative tests for E004gn's pinned register/physical-evidence limits."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gn",HERE/"verify_static.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
src=m.SOURCE.read_text()
old=json.loads(m.IDLE.read_text())
m.local_contract(src,old)
negative=0
for before,after in (
    ("REG_FIELD(0x09, 0, 7)","REG_FIELD(0x0a, 0, 7)"),
    ("REG_FIELD_ID(0x3e, 0, 7, 4, 1)","REG_FIELD_ID(0x3d, 0, 7, 4, 1)"),
    ("REG_FIELD(0x46, 7, 7)","REG_FIELD(0x46, 0, 7)"),
    ("REG_FIELD(0x4e, 0, 3)","REG_FIELD(0x4e, 0, 2)"),
    ("shift = chan_id * 2;","shift = chan_id * 3;"),
    ("if (val & BIT(shift))","if (val & BIT(0))"),
    ("fault_sts |= LED_FAULT_TIMEOUT;","fault_sts |= LED_FAULT_OVER_CURRENT;"),
):
    assert before in src
    try:m.local_contract(src.replace(before,after),old)
    except AssertionError:negative+=1
    else:raise AssertionError("changed status/bit semantics accepted "+before)
for change in ({"read_once_identity_consumed":False},
               {"idle_timer_register_bytes":{"ee3e":"00"}},
              ):
    try:m.local_contract(src,old|change)
    except AssertionError:negative+=1
    else:raise AssertionError("changed consumed idle evidence accepted")
assert negative==9
print("E004GN_FAULT_STATUS_TIMER_MAPPING_NEGATIVES=PASS CASES=9")
print("STATUS3_OFFLINE_REGISTER_CANDIDATE_ONLY=YES PHYSICAL_CUTOFF_PROVEN=NO")
