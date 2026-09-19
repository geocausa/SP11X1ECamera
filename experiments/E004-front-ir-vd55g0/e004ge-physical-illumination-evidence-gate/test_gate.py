#!/usr/bin/env python3
"""E004ge offline fail-closed gate tests; no hardware interactions."""
from pathlib import Path
import importlib.util
import json
import subprocess

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004ge_gate",HERE/"gate.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
base={k:False for k in mod.INPUTS}
blocked=mod.assess(base)
assert blocked["status"]=="BLOCKED_PHYSICAL_ACTION"
assert set(blocked["missing_physical_evidence"])==set(mod.INPUTS)
assert blocked["emitter_enable_authorized"] is False
for key in mod.INPUTS:
    partial=base|{key:True}
    assessed=mod.assess(partial)
    assert assessed["status"]=="BLOCKED_PHYSICAL_ACTION"
    assert key not in assessed["missing_physical_evidence"]
    assert assessed["emitter_enable_authorized"] is False
complete=mod.assess({k:True for k in mod.INPUTS})
assert complete["status"]=="REQUIRES_INDEPENDENT_EXPERT_REVIEW"
assert complete["emitter_enable_authorized"] is False
for invalid in (
    {}, {**base,"windows_kd_success":True},
    {**base,"physical_pulse_and_current":"yes"},
    {**base,"calibrated_optical_radiometry":1},
):
    try:
        mod.assess(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("malformed or software-only evidence accepted")
run=subprocess.run(["python3",str(HERE/"gate.py")],capture_output=True,
                   text=True,timeout=15,check=False)
assert run.returncode==2, (run.returncode,run.stdout,run.stderr)
assert json.loads(run.stdout)["emitter_enable_authorized"] is False
print("E004GE_FAIL_CLOSED_GATE=PASS NO_EMITTER_AUTHORIZATION=PASS")
print("MISSING_PHYSICAL_EVIDENCE=5 INDEPENDENT_REVIEW_REQUIRED=YES")
print("E004GE_NO_CAMERA_PMIC_KD_OR_WINDOWS_RUNTIME=YES")
