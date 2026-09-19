#!/usr/bin/env python3
"""Negative-path tests for actual Linux flash-driver/Windows-trace review."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json

from verify_timeout_readiness import DRIVER, FP, FR, assess

driver = DRIVER.read_text()
fp = json.loads(FP.read_text())
fr = json.loads(FR.read_text())
result = assess(driver, fp, fr)
assert not result["emitter_enable_permitted"]
assert result["linux_timeout_advertised_max_ms"] == 1280
assert result["linux_timeout_seven_bit_programmable_max_ms"] == 1270
assert result["requested_1280ms_clamped_to_1270ms_in_driver"]
assert result["hypothetical_max_exposure_ms_in_linux_mode"] == 17.0494
assert result["ten_ms_timer_would_be_shorter_than_hypothetical_peak"]
assert not result["host_crash_or_stuck_sensor_strobe_independent_shutdown_proven"]
assert not result["linux_timer_channel_write_readback_proven"]

def reject(source, p, s, expected):
    try:
        assess(source,p,s)
    except ValueError as exc:
        assert expected in str(exc), repr(exc)
    else:
        raise AssertionError("accepted changed evidence: " + expected)

reject(driver.replace("timer = clamp_t(u8, timer, 0, FLASH_TIMER_VAL_MASK)",
                      "timer = timer;"), fp, fr, "timer programming behavior")
reject(driver.replace("set_flash_timeout(led, led->flash_timeout_ms)",
                      "/* removed */"), fp, fr, "flash disarm/current/timer/module/arm")
reject(driver.replace("set_flash_strobe(led, SW_STROBE, false)",
                      "set_flash_strobe(led, HW_STROBE, true)"), fp, fr,
       "flash disarm/current/timer/module/arm")
reject(driver.replace("#define FLASH_CURRENT_DEFAULT_UA\t1000000",
                      "#define FLASH_CURRENT_DEFAULT_UA\t700000"), fp, fr,
       "driver semantics changed")
wrong_fp = deepcopy(fp)
wrong_fp["timer_register_access_observed"] = True
reject(driver,wrong_fp,fr,"different timer evidence")
wrong_fr = deepcopy(fr)
wrong_fr["observed_coarse_exposure_lines"][0] = 0
reject(driver,fp,wrong_fr,"observed exposure and frame pairs")
print("E004FS_TIMER_NEGATIVE_TESTS=PASS CASES=6 EMITTER_ENABLE=BLOCKED")
