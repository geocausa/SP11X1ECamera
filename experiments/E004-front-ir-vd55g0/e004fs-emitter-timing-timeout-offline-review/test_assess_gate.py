#!/usr/bin/env python3
"""Negative-path unit tests for offline, fail-closed interpretation only."""
import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import assess_gate as gate
from assess_gate import E, assess

fp = json.loads((E / "e004fp-windows-pmic-register-trace-corrected/evidence/RESULT.json").read_text())
fr = json.loads((E / "e004fr-windows-sensor-exposure-trace-corrected/evidence/RESULT.json").read_text())

good = assess(fp, fr)
assert good["status"] == "OFFLINE_RECONCILIATION_PASS_EMITTER_ACTIVATION_BLOCKED"
assert not good["linux_ir_emitter_activation_authorized"]
assert good["maximum_observed_line_count_ratio_percent"] == 97.75
assert good["full_frame_line_count_groups"] == 0
assert not good["hardware_independent_fail_safe_timeout_verified"]


def rejects(p, s, expected):
    try:
        assess(p, s)
    except ValueError as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError("offline gate accepted invalid evidence: " + expected)


bad = copy.deepcopy(fr)
bad["observed_writes"] -= 1
rejects(fp, bad, "sensor write count")
bad = copy.deepcopy(fr)
bad["observed_frame_length_lines"][9] = 1900
rejects(fp, bad, "coarse exposure exceeds")
bad = copy.deepcopy(fr)
bad["observed_gpio_strobe_register_writes"] = 1
rejects(fp, bad, "GPIO/strobe")
bad = copy.deepcopy(fp)
bad["timer_register_access_observed"] = True
rejects(bad, fr, "timer state changed")
bad = copy.deepcopy(fr)
bad["observed_coarse_exposure_lines"] = bad["observed_coarse_exposure_lines"][:-1]
rejects(fp, bad, "programming group count")
bad = copy.deepcopy(fr)
bad["windows_capture"]["frames_acquired"] = 13
rejects(fp, bad, "bounded capture")
# The archived inputs and parsed-result files are a single evidence contract.
# A modified result must be rejected even if its simple structural checks pass.
with TemporaryDirectory(prefix="sp11-e004fs-check-") as directory:
    out = Path(directory)
    original_fp, original_fr = gate.FP, gate.FR
    original_result = (Path(__file__).parent / "evidence/RESULT.json").read_bytes()
    try:
        for name, original, old, new, error in (
            ("pmic", original_fp, b'"frames": 12', b'"frames": 13',
             "PMIC result differs"),
            ("sensor", original_fr, b'"observed_writes": 114',
             b'"observed_writes": 113', "sensor result differs"),
        ):
            assert old in original.read_bytes(), name + " fixture drift"
            changed = original.read_bytes().replace(old, new, 1)
            destination = out / (name + "-tampered.json")
            destination.write_bytes(changed)
            gate.FP, gate.FR = original_fp, original_fr
            if name == "pmic":
                gate.FP = destination
            else:
                gate.FR = destination
            try:
                gate.main()
            except ValueError as exc:
                assert error in str(exc), str(exc)
            else:
                raise AssertionError("tampered " + name + " result accepted")
            assert (Path(__file__).parent / "evidence/RESULT.json").read_bytes() == original_result
    finally:
        gate.FP, gate.FR = original_fp, original_fr

print("E004FS_GATE_TESTS=PASS VALID_EVIDENCE_BLOCKED=YES INVALID_EVIDENCE_REJECTED=8")
