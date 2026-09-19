#!/usr/bin/env python3
"""Negative-path checks for emulated original ARM64 code (not a physical PMIC)."""
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("e004gg", HERE / "emulate_windows_off.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

original = m.EXPECTED["qcpmic8380.sys"]
m.EXPECTED["qcpmic8380.sys"] = "0" * 64
try:
    try:
        m.run_pmic((0,0,0,0))
    except AssertionError:
        pass
    else:
        raise AssertionError("original Windows binary SHA drift not rejected")
finally:
    m.EXPECTED["qcpmic8380.sys"] = original

for invalid in ((0,0,1,0), (2,0,0,0), (1,1,1,1)):
    try:
        m.run_pmic(invalid)
    except AssertionError:
        pass
    else:
        raise AssertionError("unsupported fixture accepted")
for bad_stage in (-1,3):
    try:
        m.run_pmic((0,0,0,0), bad_stage)
    except AssertionError:
        pass
    else:
        raise AssertionError("unsupported fault stage accepted")

off, status = m.run_pmic((0,0,0,0))
assert status == 0 and [row["register"] for row in off] == ["0xee46", "0xee4e"]
for stage in (1,2):
    requests, status = m.run_pmic((1,0,0,1), stage)
    assert status != 0 and len(requests) == stage
    assert requests[0]["requested"] == "0x80"
    if stage == 2:
        assert requests[1]["requested"] == "0x9"
for val in (-1,2):
    try:
        m.run_flash_off_wrapper(val,0,0,0)
    except AssertionError:
        pass
    else:
        raise AssertionError("invalid flash wrapper argument accepted")
calls, status = m.run_flash_off_wrapper(1,0,1,0)
# The wrapper packs [arg1, arg0, arg2, 0], not [arg0, arg1, arg2, 0].
# Off-only zero payload could not have detected this argument permutation.
assert calls == [{"command":"0x802f0fc8", "payload":[0,1,0,1]}]
assert status == 0
print("E004GG_SHA_DRIFT_AND_INVALID_INPUT=PASS CASES=8")
print("E004GG_ACTUAL_ARM64_ON_FAULT_PATHS=PASS FIRST_AND_SECOND_REQUEST_ERRORS")
print("E004GG_ORIGINAL_OFF_AND_NONZERO_WRAPPER_ARGS=PASS")
print("PHYSICAL_PMIC_FALLOUT_PROVEN=NO IR_EMITTER=OFF")
