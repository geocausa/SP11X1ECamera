#!/usr/bin/env python3
"""E004ge: OFFLINE proof-of-evidence gate, never an emitter enable tool.

A missing assertion is a blocker. Claims in existing Windows/Linux software
traces do NOT substitute for calibrated physical measurements or autonomous
fault-cutoff proof. Even a complete checklist requires independent expert
review; this script never produces authorization for IR emission.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUTS = {
    "calibrated_optical_radiometry": (
        "Independent calibrated NIR spectral irradiance/radiance measurements "
        "of the exact SP11 emitter, geometry, wavelength, aperture and duty cycle; "
        "qualified eye-safety assessment with traceable calibration and uncertainty."
    ),
    "physical_pulse_and_current": (
        "Independently measured LED current and emitted optical pulse widths, "
        "repetition and maximum-on envelope, including warm-up and transition."
    ),
    "autonomous_host_and_strobe_fault_off": (
        "Physical LED-off measurements on stuck-high sensor strobe, halted host "
        "and PMIC communication failure, without trusting Linux software disarm, "
        "a watchdog service, reboot, or the Windows software trace."
    ),
    "hardware_limit_proven_and_reviewed": (
        "Independent qualified review of hardware current/time cutoff, verified "
        "against the measured LED/optical conditions; not merely a timer register "
        "bit, a nominal current setting or a vendor driver request."
    ),
    "real_sensor_and_emitter_wiring": (
        "Validated SP11 physical LED/channel/strobe routing, including idle-off "
        "and channel/module interactions and relevant electrical load."
    ),
}
SOFTWARE_FACTS = {
    "e004gb_completed": True,
    "e004gc_e004gd_offline_processing_proven": True,
    "windows_helper_writes_only_not_optical_proof": True,
    "e004fx_idle_timer_not_physical_cutoff_proof": True,
    "e004fy_idle_module_off_not_fault_off_proof": True,
    "linux_flash_patches_uninstalled": True,
}
# This stage does not accept user-provided asserted "passes" as proof or
# silently infer a numerical exposure limit from a nominal 700mA Windows
# request. Human review of actual calibrated measurements is essential.
def assess(evidence):
    if not isinstance(evidence, dict) or set(evidence) != set(INPUTS):
        raise ValueError("required evidence keys mismatch")
    if any(type(evidence[k]) is not bool for k in INPUTS):
        raise ValueError("evidence values must be exact booleans")
    missing = [key for key in INPUTS if not evidence[key]]
    return {
        "status": "BLOCKED_PHYSICAL_ACTION" if missing else "REQUIRES_INDEPENDENT_EXPERT_REVIEW",
        "missing_physical_evidence": missing,
        "physical_evidence_count": sum(bool(evidence[k]) for k in INPUTS),
        "all_physical_checklist_claims_present": not missing,
        "emitter_enable_authorized": False,
        "software_trace_can_substitute_for_physical_proof": False,
        "independent_qualified_review_required": True,
    }

def main():
    source = json.loads((HERE / "evidence" / "PHYSICAL-EVIDENCE-STATUS.json").read_text())
    if set(source) != {"experiment", "physical_evidence", "software_facts"}:
        raise ValueError("status source schema mismatch")
    if source["experiment"] != "E004ge" or source["software_facts"] != SOFTWARE_FACTS:
        raise ValueError("source fact drift")
    result = assess(source["physical_evidence"])
    print(json.dumps(result, sort_keys=True))
    # Return nonzero while still blocked. Never expose a passing enable gate.
    if not result["all_physical_checklist_claims_present"]:
        return 2
    return 3 # qualitative checklist alone NEVER grants hardware authorization

if __name__ == "__main__":
    raise SystemExit(main())
