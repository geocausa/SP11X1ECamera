#!/usr/bin/env python3
"""E004ib static archive audit; no /tmp package install or device operations."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
STACK=ROOT/"src/sp11-camera-stack"
MANIFEST=ROOT/"experiments/E004-front-ir-vd55g0/e004dw-canonical-full-stack-package/evidence/CAMERA-STACK-MANIFEST.sha256"
LEGACY=ROOT/"experiments/E004-front-ir-vd55g0/e004dx-offline-install-update-remove-lifecycle/RESULT.json"
def need(ok,why):
    if not ok:raise AssertionError("E004IB_ARCHIVE_FAIL_CLOSED "+why)
def main():
    r=json.loads((HERE/"evidence/RESULT.json").read_text())
    need(r["experiment"]=="E004ib" and r["status"]==
         "PASS_ARM64_OFFLINE_ROOT_GUARD_AND_MAINTAINED_SANDBOX_UNINSTALL"
         and r["baseline_commit"]=="788b4ae42f6294f8a0d25ee9788048ea4f5f73b9",
         "experiment identity changed")
    for key,path in (
       ("previous_accepted_full_package_manifest_sha256",MANIFEST),
       ("previous_disposable_lifecycle_evidence_sha256",LEGACY),
       ("new_offline_root_guard_sha256",STACK/"offline-root-guard.py"),
       ("maintained_offline_installer_sha256",STACK/"install-staged-root.sh"),
       ("maintained_offline_uninstaller_sha256",STACK/"uninstall-root.sh"),
       ("test_source_sha256",HERE/"test_guard.py"),
       ("verifier_source_sha256",HERE/"verify_guard.py")):
        need(sha256(path.read_bytes()).hexdigest()==r[key],
             "original or new source/evidence changed: "+key)
    need(r["previous_accepted_full_package_manifest_member_count"]==51
         and r["scratch_symlink_path_manifest_and_late_uninstall_negatives"]==24
         and r["actual_maintained_uninstall_synthetic_user_private_sandbox_tested"] is True,
         "original member inventory/negative suite drift")
    for key in (
        "original_accepted_full_package_installer_live_or_sandbox_rerun",
        "nonconcurrent_preflight_is_security_boundary",
        "previous_signed_protected_camera_worker_admitted",
        "original_live_camera_illumination_or_spmi_pmic_activity",
        "protected_golden_kernel_boot_pam_or_login_changed",
        "optical_ir_hardware_emitter_cutoff_proven"):
        need(r[key] is False,"false hardware/security guarantee: "+key)
    print("E004IB_SOURCE_HASH_MANIFEST_SCRATCH_NEGATIVE_ARCHIVE=PASS")
    print("E004IB_NO_LIVE_ROOT_CAMERA_EMITTER_OR_PROTECTED_TRUST_CLAIM=PASS")
if __name__=="__main__":main()
