#!/usr/bin/env python3
"""E004ic static source/evidence archive; no live cameras, models or IR."""
from pathlib import Path
from hashlib import sha256
import json
import importlib.util

HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location("e004ic_source",HERE/"verify_readiness.py")
assert S and S.loader
v=importlib.util.module_from_spec(S)
S.loader.exec_module(v)
def need(ok,why):
    if not ok:raise AssertionError("E004IC_ARCHIVE_FAIL_CLOSED "+why)
def main():
    r=json.loads((HERE/"evidence/RESULT.json").read_text())
    need(r["experiment"]=="E004ic" and r["status"]==
         "PASS_RGB_FEEDBACK_RELEASE_READINESS_AND_INDEPENDENT_IR_PHYSICAL_TRUST_GATES_OFFLINE"
         and r["baseline_commit"]=="05000d98be58cc888a0ea6de11a199b267d293f6",
         "archive identity drift")
    for rel,actual in r["source_sha256"].items():
        file=v.ROOT/rel
        need(file.is_file() and sha256(file.read_bytes()).hexdigest()==actual,
             "readiness or original evidence digest changed: "+rel)
    need(r["test_sha256"]==sha256((HERE/"test_readiness.py").read_bytes()).hexdigest()
         and r["verifier_sha256"]==sha256((HERE/"verify_readiness.py").read_bytes()).hexdigest(),
         "test/verifier source changed")
    need(r["front_native_changed_post_g3_feedback_closed_from_consumed_one_shot"] is True
         and r["nonprotected_rgb_guarded_nondefault_ready"] is True,
         "closed original RGB proof unexpectedly absent")
    for key in (
      "original_accepted_full_1to1_default_promoted",
      "protected_worker_signed_or_admitted",
      "real_nir_face_auth_user_enrollment_or_pam",
      "independent_physical_emitter_off_proven",
      "native_linux_ir_emitter_authorized",
      "camera_reboot_kd_pmic_spmi_emitter_or_golden_mutation"):
        need(r[key] is False,"unsafe readiness claim "+key)
    print("E004IC_ARCHIVED_RGB_FRONT_GATE_CLOSED_IR_PHYSICAL_AND_TRUST_BLOCKED=PASS")
if __name__=="__main__":main()
