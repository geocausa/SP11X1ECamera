#!/usr/bin/env python3
"""Fail-closed OFFLINE review of real Linux flash-source and Windows trace.
No PMIC writes, emitter action, sensor activation, or runtime permission.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DRIVER = ROOT / "experiments/E004-front-ir-vd55g0/e004fk-native-flash-disable-ordering/build/source/leds-qcom-flash.c"
FP = ROOT / "experiments/E004-front-ir-vd55g0/e004fp-windows-pmic-register-trace-corrected/evidence/RESULT.json"
FR = ROOT / "experiments/E004-front-ir-vd55g0/e004fr-windows-sensor-exposure-trace-corrected/evidence/RESULT.json"
HASHES = {
    DRIVER: "cd1f98411545cdb4b679bb21c4c29076a88866517488d5b618c31485caa04727",
    FP: "b94a5997ecfb27f8f87527b2099763416cae390abf03e90d909b11efd2deac86",
    FR: "a5da6c08a1a1b4269970750e0971f207561310fd47316561b0ef30f2760c0b92",
}

def need(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError("E004FS_TIMEOUT_REVIEW_FAIL_CLOSED: " + msg)

def between(source: str, start: str, end: str) -> str:
    need(source.count(start) == 1 and source.count(end) == 1,
         "driver function anchors missing or ambiguous")
    start_pos = source.index(start)
    end_pos = source.index(end, start_pos)
    return source[start_pos:end_pos]

def assess(driver: str, fp: dict, fr: dict) -> dict:
    need(fp.get("status") == "PASS_BOUNDED_WINDOWS_PMIC_REGISTER_TRACE",
         "Windows PMIC trace status changed")
    need(fr.get("status") == "PASS_BOUNDED_WINDOWS_SENSOR_REGISTER_WRITE_OBSERVATION",
         "Windows sensor trace status changed")
    need(fp.get("timer_register_access_observed") is False,
         "different timer evidence needs review")
    need(fp.get("physical_current_or_optical_power_measured") is False,
         "physical current evidence changed")
    need(fr.get("observed_writes") == 114, "Windows sensor write count changed")
    require_literals = (
        "#define FLASH_TIMER_EN_BIT", "BIT(7)",
        "#define FLASH_TIMER_STEP_MS", "10",
        "#define FLASH_TIMEOUT_MAX_US", "1280000",
        "#define FLASH_CURRENT_DEFAULT_UA", "1000000",
        "REG_FIELD_ID(0x3e, 0, 7, 4, 1)",
        "led->flash_current_ma = brightness->val / UA_PER_MA;",
        "timeout->val = timeout->max = timeout_us;",
    )
    need(all(x in driver for x in require_literals), "driver semantics changed")
    timer = between(driver, "static int set_flash_timeout(", "static int set_flash_strobe(")
    for marker in ("timeout_ms / FLASH_TIMER_STEP_MS",
                   "timer |= FLASH_TIMER_EN_BIT",
                   "timer = clamp_t(u8, timer, 0, FLASH_TIMER_VAL_MASK)",
                   "regmap_fields_write(flash_data->r_fields[REG_CHAN_TIMER], chan_id, timer)",
                   "if (rc)\n\t\t\treturn rc;"):
        need(marker in timer, "hardware timer programming behavior changed: " + marker)
    arm = between(driver, "static int qcom_flash_strobe(", "static int qcom_flash_strobe_set(")
    order = ("set_flash_strobe(led, SW_STROBE, false)",
             "update_allowed_flash_current(led, &led->flash_current_ma, state)",
             "set_flash_current(led, led->flash_current_ma, FLASH_MODE)",
             "set_flash_timeout(led, led->flash_timeout_ms)",
             "set_flash_module_en(led, state)",
             "return set_flash_strobe(led, strobe, state)")
    offsets = [arm.find(marker) for marker in order]
    need(-1 not in offsets and offsets == sorted(offsets),
         "flash disarm/current/timer/module/arm ordering changed")
    need("if (rc)\n\t\treturn rc;" in arm, "early error exit lost")
    coarse = fr["observed_coarse_exposure_lines"]
    frame_lengths = fr["observed_frame_length_lines"]
    need(len(coarse) == len(frame_lengths) == 16
         and all(type(a) is int and 0 < a <= b for a,b in zip(coarse, frame_lengths)),
         "observed exposure and frame pairs invalid")
    # This clock and line length are from the SEPARATE Linux camera mode,
    # deliberately NOT attributed to the Windows session.
    pixel_clock_hz = 137_600_000
    line_length = 1200
    linux_hypothetical_ms = [round(lines * line_length * 1000 / pixel_clock_hz, 4)
                             for lines in coarse]
    # A timer register limits an individual flash event if correctly
    # programmed; it does not itself prove any absolute session on-time bound.
    return {
        "status": "PASS_OFFLINE_CODE_AND_TRACE_REVIEW_ILLUMINATION_STILL_BLOCKED",
        "driver": "E004fk isolated offline patched qcom four-channel flash source",
        "linux_timeout_encoding_step_ms": 10,
        "linux_timeout_advertised_max_ms": 1280,
        "linux_timeout_seven_bit_programmable_max_ms": 1270,
        "requested_1280ms_clamped_to_1270ms_in_driver": True,
        "driver_default_flash_current_ma_before_external_configuration": 1000,
        "windows_requested_flash_current_ma": 700,
        "current_parity_automatic": False,
        "linux_timer_set_before_module_arm_in_patched_source": True,
        "linux_timer_channel_write_readback_proven": False,
        "linux_timer_active_in_installed_runtime": False,
        "windows_timer_write_seen_in_one_bounded_E004fp_capture": False,
        "timer_initial_register_state_known": False,
        "timer_cumulative_session_limit_proven": False,
        "host_crash_or_stuck_sensor_strobe_independent_shutdown_proven": False,
        "requested_windows_exposure_lines": coarse,
        "hypothetical_exposure_ms_if_windows_lines_used_linux_mode": linux_hypothetical_ms,
        "hypothetical_max_exposure_ms_in_linux_mode": max(linux_hypothetical_ms),
        "ten_ms_timer_would_be_shorter_than_hypothetical_peak": max(linux_hypothetical_ms) > 10,
        "windows_clock_or_pulse_duration_inferred": False,
        "safe_hardware_current_and_irradiance_limits_proven": False,
        "emitter_enable_permitted": False,
        "required_next_authority": [
            "Verify channel timer values and readback on actual board while emitter remains disabled",
            "Establish real sensor strobe edges and LED electrical pulse with appropriate optical/electrical instrumentation",
            "Verify current/irradiance limits and an autonomous off path across host crash, hung strobe and streaming stop",
            "Only then design a separately gated candidate with bounded exposure/current and forced Golden return",
        ],
    }

def main() -> None:
    for path, expected in HASHES.items():
        need(path.is_file() and sha256(path.read_bytes()).hexdigest() == expected,
             "pinned source/evidence mismatch: " + str(path))
    result = assess(DRIVER.read_text(), json.loads(FP.read_text()),
                    json.loads(FR.read_text()))
    (HERE / "evidence" / "TIMEOUT-READINESS.json").write_text(json.dumps(result, indent=2)+"\n")
    print("E004FS_DRIVER_TIMER_REVIEW=PASS ARM_ORDER=OFF_CURRENT_TIMER_MODULE_TRIGGER")
    print("HYPOTHETICAL_LINUX_CLOCK_MAX_EXPOSURE_MS=" + str(result["hypothetical_max_exposure_ms_in_linux_mode"]))
    print("ACTUAL_WINDOWS_PULSE_MEASURED=NO AUTONOMOUS_SHUTDOWN_PROVEN=NO EMITTER=BLOCKED")

if __name__ == "__main__":
    main()
