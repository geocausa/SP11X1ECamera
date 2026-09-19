#!/usr/bin/env python3
"""Read-only E004fs evidence reconciliation; never authorizes emitter activation."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import json

ROOT = Path(__file__).resolve().parents[3]
E = ROOT / "experiments" / "E004-front-ir-vd55g0"
FP = E / "e004fp-windows-pmic-register-trace-corrected" / "evidence" / "RESULT.json"
FR = E / "e004fr-windows-sensor-exposure-trace-corrected" / "evidence" / "RESULT.json"
ARCHIVE = FR.parent / "ORIGINAL-WINDOWS-LOGS.zip"
KD_DIGEST = "e51fe8ac39c4dcada637bf914c18c891ab81d27e974bffc0bd330f4201223722"
CAP_DIGEST = "079dd61665adbfe21c5f5316078e9cebb91d5462ddb05e4be79dda5233cebb78"


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError("E004FS_FAIL_CLOSED " + msg)


def assess(fp: dict, fr: dict) -> dict:
    """Interpret only observed register geometry, not actual optical pulse duration."""
    require(fp.get("status") == "PASS_BOUNDED_WINDOWS_PMIC_REGISTER_TRACE",
            "PMIC trace authority missing")
    require(fr.get("status") == "PASS_BOUNDED_WINDOWS_SENSOR_REGISTER_WRITE_OBSERVATION",
            "sensor trace authority missing")
    require(fp.get("timer_register_access_observed") is False,
            "timer state changed; review evidence manually")
    require(fp.get("frames") == 12 and fr.get("windows_capture", {}).get("frames_acquired") == 12,
            "bounded capture count differs")
    require(fr.get("observed_writes") == 114, "sensor write count differs")
    coarse = fr.get("observed_coarse_exposure_lines")
    frames = fr.get("observed_frame_length_lines")
    require(isinstance(coarse, list) and isinstance(frames, list)
            and len(coarse) == len(frames) == 16, "programming group count differs")
    require(all(type(x) is int and 0 < x <= 65535 for x in coarse + frames),
            "invalid sensor register value")
    require(all(0 < c <= f for c, f in zip(coarse, frames)),
            "coarse exposure exceeds paired frame length")
    require(fr.get("observed_gpio_strobe_register_writes") == 0,
            "new GPIO/strobe write evidence needs review")
    # Pure dimensionless line-count ratios; not an optical duty-cycle measurement.
    ratios = [round(100.0 * c / f, 4) for c, f in zip(coarse, frames)]
    return {
        "experiment": "E004fs",
        "status": "OFFLINE_RECONCILIATION_PASS_EMITTER_ACTIVATION_BLOCKED",
        "inputs": {"pmic": "E004fp", "sensor": "E004fr"},
        "windows_programming_groups": len(coarse),
        "windows_acquired_frames": 12,
        "sensor_coarse_exposure_lines": coarse,
        "sensor_frame_length_lines": frames,
        "exposure_to_frame_line_count_percent": ratios,
        "maximum_observed_line_count_ratio_percent": max(ratios),
        "full_frame_line_count_groups": sum(c == f for c, f in zip(coarse, frames)),
        "interpretation": "Register line-count ratios only; NOT IR LED duty cycle, output power, pulse duration or matched capture-frame timing.",
        "separate_windows_observations": True,
        "physical_pulse_duration_verified": False,
        "physical_current_and_irradiance_verified": False,
        "hardware_independent_fail_safe_timeout_verified": False,
        "camera_process_crash_shutdown_verified": False,
        "sensor_clock_during_windows_capture_verified": False,
        "pmic_timer_register_access_in_bounded_E004fp": False,
        "pmic_timer_global_state_known": False,
        "linux_ir_emitter_activation_authorized": False,
        "next_step": "Independently establish physical pulse/current limits and hardware-backed shutdown on failed or stopped streaming before any illuminated test.",
    }


def main() -> None:
    with ZipFile(ARCHIVE) as z:
        require(set(z.namelist()) == {"WINDOWS-KD.log", "WINDOWS-CAPTURE.txt"},
                "raw E004fr evidence archive entries differ")
        require(sha256(z.read("WINDOWS-KD.log")).hexdigest() == KD_DIGEST,
                "archived KD log hash mismatch")
        require(sha256(z.read("WINDOWS-CAPTURE.txt")).hexdigest() == CAP_DIGEST,
                "archived Windows capture log hash mismatch")
    fp, fr = (json.loads(p.read_text()) for p in (FP, FR))
    require(fr.get("kd_log_sha256") == KD_DIGEST and
            fr.get("capture_log_sha256") == CAP_DIGEST,
            "parsed E004fr result no longer matches raw archive")
    result = assess(fp, fr)
    path = Path(__file__).parent / "evidence" / "RESULT.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print("E004FS_OFFLINE=PASS GROUPS=16 FULL_FRAME_LINE_COUNT_GROUPS="
          + str(result["full_frame_line_count_groups"]))
    print("EMITTER_ACTIVATION=BLOCKED NO_HARDWARE_OPERATION")


if __name__ == "__main__":
    main()
