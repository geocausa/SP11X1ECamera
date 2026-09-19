#!/usr/bin/env python3
"""In-memory tampering tests: no Windows, KD, camera, PMIC or archive mutation."""
from verify_result import originals,dry_check,parse_trace,capture_check,verify

o=originals()
dry=o["e004gb-flash-enable-kd.log"].decode("ascii")
kd=o["e004gb-observer-kd.log"].decode("ascii")
capture=o["CAPTURE-ORIGINAL-WINDOWS.txt"].decode("ascii")
result=verify()
assert result["identity_consumed"] and result["kd_pre_calls"]==result["kd_post_calls"]==11
assert not result["native_linux_emitter_activation_authorized"]
assert not result["independent_stuck_trigger_or_host_failure_off_verified"]
cases=[
 ("bad_dry_ee46",lambda:dry_check(dry.replace(
      "E004GB_DRY_TARGET reg=ee46","E004GB_DRY_SKIP reg=ee46"))),
 ("missing_dry_ee4e",lambda:dry_check(dry.replace(
      "E004GB_DRY_TARGET reg=ee4e","E004GB_DRY_TARGET reg=ee4f"))),
 ("altered_module_enable",lambda:parse_trace(kd.replace(
      "E004GB_PRE hit=8 reg=ee46 mask=80 read_rc=0",
      "E004GB_PRE hit=8 reg=ee46 mask=40 read_rc=0"))),
 ("altered_channel_disable",lambda:parse_trace(kd.replace(
      "E004GB_POST hit=11 reg=ee4e mask=f write_rc=0",
      "E004GB_POST hit=11 reg=ee4e mask=f write_rc=1"))),
 ("missing_preview_stop",lambda:capture_check(capture.replace(
      "E004GB_STOP_PASS","E004GB_STOP_FAILED"))),
 ("missing_frame",lambda:capture_check(capture.replace(
      "E004GB_FRAME n=12","E004GB_FRAME n=13"))),
]
for name,exercise in cases:
    try:exercise()
    except ValueError as e:
        assert "E004GB_EVIDENCE_FAIL_CLOSED" in str(e),name
    else:raise AssertionError("accepted altered evidence "+name)
print("E004GB_OFFLINE_TESTS=PASS NEGATIVE_CASES=6 NO_HARDWARE_IO=YES")
