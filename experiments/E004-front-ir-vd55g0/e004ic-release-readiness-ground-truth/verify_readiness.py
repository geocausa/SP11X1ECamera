#!/usr/bin/env python3
"""E004ic: release-readiness truth reconciliation from pinned archived evidence.

No camera, firmware, login, PMIC, SPMI or emitter access. Historical E004eo
closed the RGB scene gate; independent physical Linux emitter and protected
worker trust gates must not be conflated with ordinary HLOS offline probes.
"""
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
STACK=ROOT/"src/sp11-camera-stack"
BASE=ROOT/"experiments/E004-front-ir-vd55g0"
EN=BASE/"e004en-natural-cap-release-one-shot-runtime/RESULT.json"
EO=BASE/"e004eo-post-feedback-final-readiness-audit/RESULT.json"
FU=BASE/"e004fu-unilluminated-optical-hlos/evidence/RESULT.json"
GE=BASE/"e004ge-physical-illumination-evidence-gate/evidence/PHYSICAL-EVIDENCE-STATUS.json"
IA=BASE/"e004ia-public-model-after-commit/evidence/RESULT.json"
DOC=STACK/"READINESS.md"
STRUCT=STACK/"READINESS.json"
def need(ok,why):
    if not ok:raise AssertionError("E004IC_FAIL_CLOSED "+why)
def assess(ready,description,en,eo,fu,ge,ia):
    non=ready["nonprotected_product"]
    protected=ready["protected_path"]
    old=ready["remaining_proofs"]
    safety=ready["safety_gates"]
    need(ready["promotion_decision"]=="HOLD_FULL_1TO1_DEFAULT"
         and non["status"]=="READY_NONDEFAULT"
         and non["rear_rgb"]==non["front_rgb"]=="PASS"
         and non["default_activation_authorized"] is False,
         "full 1:1 vs guarded RGB readiness conflated")
    need(eo["status"]==
         "PASS_NONPROTECTED_PRODUCT_READY_FRONT_FEEDBACK_CLOSED_FULL_1TO1_HELD_ONLY_ON_SECURE_ADMISSION"
         and en["status"]==
         "PASS_LIVE_ONE_NATURAL_CHANGED_POST_G3_WRITE_GOLDEN_RETURN_RETIRED_UNINSTALLED"
         and en["later_native_writes"]==1 and en["second_later_writes"]==0
         and en["synthetic_control_delta"] is False
         and en["camera_rerun_after_verifier_fix"] is False
         and en["production_native_changed_post_g3_feedback_proven"] is True,
         "original consumed natural front feedback proof drift")
    need(old["front_post_g3_changed_native_feedback"]==
         "PASS_LIVE_ONE_NATURAL_CHANGED_POST_G3_WRITE"
         and old["current_scene_post_g3_state"]=="NATURAL_BELOW_CAP_RELEASE_OBSERVED"
         and ready["resume_conditions"]["post_g3_feedback"]==
         "CLOSED_BY_E004EN_NO_FURTHER_SCENE_GATE",
         "obsolete preview-cap scene blocker resurrected")
    need("### Front post-G3 changed native feedback — CLOSED by E004en" in description
         and "There was no legitimate APPLY_ONE_NATIVE opportunity" not in description
         and "Wait for a naturally changed/brighter scene" not in description
         and "repeat the consumed E004en identity" in description,
         "stale front feedback narrative")
    need(protected["worker_signed"] is False
         and protected["worker_production_admitted"] is False
         and protected["runtime_authorized"] is False
         and old["protected_ir_windows_hello_end_to_end"]==
         "BLOCKED_ON_PRODUCTION_WORKER_ADMISSION"
         and safety["securepd_worker_production_admitted"] is False,
         "external protected SecurePD admission falsely opened")
    need(fu["status"]=="PASS_LIVE_UNILLUMINATED_OPTICAL_HLOS_16FRAMES"
         and fu["frames_captured_and_processed"]==16
         and fu["optical_signal_sufficient_for_face_auth"] is False
         and fu["protected_worker_used"] is False
         and fu["camera_stop_and_golden_return"]=="PASS"
         and safety["live_unilluminated_ir_sensor_frame_processing"]==
         "PASS_16_LOW_SIGNAL_NOT_FACE_AUTH",
         "unilluminated 16-frame capture falsely promoted to face auth")
    required=("calibrated_optical_radiometry","physical_pulse_and_current",
              "autonomous_host_and_strobe_fault_off","hardware_limit_proven_and_reviewed",
              "real_sensor_and_emitter_wiring")
    need(ge["experiment"]=="E004ge"
         and set(ge["physical_evidence"])==set(required)
         and all(ge["physical_evidence"][key] is False for key in required)
         and safety["native_linux_ir_illumination"]==
         "BLOCKED_ON_INDEPENDENT_PHYSICAL_EVIDENCE"
         and safety["independent_current_irradiance_pulse_strobe_host_failure_emitter_cutoff_proven"] is False
         and safety["native_linux_ir_emitter_activated_or_authorized"] is False,
         "physical emitter guard falsely opened")
    need(ia["status"]==
         "PASS_REAL_ARM64_PUBLIC_PHOTO_NATIVE_HLOS_C_TRANSACTION_THEN_YUNET_SFACE_DIAGNOSTIC"
         and ia["real_nir_sensor_capture_darkness_or_optical_safety_tested"] is False
         and ia["real_user_enrolled_or_face_authenticated"] is False
         and safety["offline_public_ordinary_hlos_native_c_then_yunet_sface"]==
         "PASS_DIAGNOSTIC_ONLY_UNINSTALLED"
         and safety["user_face_enrolled_or_authenticated"] is False
         and safety["pam_or_login_integrated"] is False,
         "public offline face model mislabeled as real protected auth")
    need("E004ge still lacks calibrated optical radiometry" in description
         and "Protected Windows Hello parity is separately blocked" in description
         and "not that physical proof" in description,
         "safety/trust distinction missing from human readiness")
    return True

def main():
    sources=(DOC,STRUCT,EN,EO,FU,GE,IA)
    data=[json.loads(p.read_text()) if p.suffix==".json" else p.read_text()
          for p in sources]
    need(assess(data[1],data[0],*data[2:]),"readiness not reconciled")
    out={
      "experiment":"E004ic",
      "status":"PASS_RGB_FEEDBACK_RELEASE_READINESS_AND_INDEPENDENT_IR_PHYSICAL_TRUST_GATES_OFFLINE",
      "date":"2026-09-20",
      "baseline_commit":"05000d98be58cc888a0ea6de11a199b267d293f6",
      "source_sha256":{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest()
                       for p in sources},
      "test_sha256":sha256((HERE/"test_readiness.py").read_bytes()).hexdigest(),
      "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
      "front_native_changed_post_g3_feedback_closed_from_consumed_one_shot":True,
      "nonprotected_rgb_guarded_nondefault_ready":True,
      "original_accepted_full_1to1_default_promoted":False,
      "protected_worker_signed_or_admitted":False,
      "real_nir_face_auth_user_enrollment_or_pam":False,
      "independent_physical_emitter_off_proven":False,
      "native_linux_ir_emitter_authorized":False,
      "camera_reboot_kd_pmic_spmi_emitter_or_golden_mutation":False,
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(out,indent=2)+"\n")
    print("E004IC_E004EN_NATURAL_POST_G3_FEEDBACK_CLOSED_AND_RGB_NONDEFAULT=PASS")
    print("E004IC_PROTECTED_ADMISSION_AND_PHYSICAL_NATIVE_IR_INDEPENDENT_BLOCKERS_RETAINED=PASS")
if __name__=="__main__":main()
