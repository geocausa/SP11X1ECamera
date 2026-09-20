#!/usr/bin/env python3
"""E004ib: reproducible scratch-root lifecycle hardening verification."""
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import os
import platform
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
STACK=ROOT/"src/sp11-camera-stack"
MANIFEST=ROOT/"experiments/E004-front-ir-vd55g0/e004dw-canonical-full-stack-package/evidence/CAMERA-STACK-MANIFEST.sha256"
LEGACY=ROOT/"experiments/E004-front-ir-vd55g0/e004dx-offline-install-update-remove-lifecycle/RESULT.json"
GUARD=STACK/"offline-root-guard.py"
INSTALL=STACK/"install-staged-root.sh"
UNINSTALL=STACK/"uninstall-root.sh"
TEST=HERE/"test_guard.py"
def need(ok,why):
    if not ok:raise AssertionError("E004IB_FAIL_CLOSED "+why)
def main():
    need(platform.machine()=="aarch64" and os.geteuid()!=0,
         "requires original unprivileged SP11 ARM64 scratch-only environment")
    prior=json.loads(LEGACY.read_text())
    need(prior["status"]==
         "PASS_DISPOSABLE_ROOT_INSTALL_UPDATE_TAMPER_REJECT_UNINSTALL_LIFECYCLE"
         and prior["live_root_modified"] is False,
         "original legacy scratch lifecycle evidence drift")
    lines=MANIFEST.read_text().splitlines()
    need(len(lines)==51 and len(lines)==len(set(lines)) and
         all(re.fullmatch(r"[0-9a-f]{64}  usr/[A-Za-z0-9_.+/-]+",line)
             for line in lines),
         "original accepted real full-stack package member inventory drift")
    need('python3 "$ROOT/offline-root-guard.py" install "$PKG" "$DEST"' in
         INSTALL.read_text() and
         'python3 "$ROOT/offline-root-guard.py" uninstall "$DEST"' in
         UNINSTALL.read_text(),
         "actual maintained offline install/uninstall not wired to guard")
    s=importlib.util.spec_from_file_location("e004ib_test_runner",TEST)
    need(s is not None and s.loader is not None,"test source missing")
    test=importlib.util.module_from_spec(s);s.loader.exec_module(test)
    rejected=test.run()
    need(rejected==24,"scratch guard regression count drift")
    out={
      "experiment":"E004ib",
      "status":"PASS_ARM64_OFFLINE_ROOT_GUARD_AND_MAINTAINED_SANDBOX_UNINSTALL",
      "date":"2026-09-20",
      "baseline_commit":"788b4ae42f6294f8a0d25ee9788048ea4f5f73b9",
      "previous_accepted_full_package_manifest_sha256":sha256(MANIFEST.read_bytes()).hexdigest(),
      "previous_accepted_full_package_manifest_member_count":len(lines),
      "previous_disposable_lifecycle_evidence_sha256":sha256(LEGACY.read_bytes()).hexdigest(),
      "new_offline_root_guard_sha256":sha256(GUARD.read_bytes()).hexdigest(),
      "maintained_offline_installer_sha256":sha256(INSTALL.read_bytes()).hexdigest(),
      "maintained_offline_uninstaller_sha256":sha256(UNINSTALL.read_bytes()).hexdigest(),
      "test_source_sha256":sha256(TEST.read_bytes()).hexdigest(),
      "verifier_source_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
      "scratch_symlink_path_manifest_and_late_uninstall_negatives":rejected,
      "actual_maintained_uninstall_synthetic_user_private_sandbox_tested":True,
      "original_accepted_full_package_installer_live_or_sandbox_rerun":False,
      "nonconcurrent_preflight_is_security_boundary":False,
      "previous_signed_protected_camera_worker_admitted":False,
      "original_live_camera_illumination_or_spmi_pmic_activity":False,
      "protected_golden_kernel_boot_pam_or_login_changed":False,
      "optical_ir_hardware_emitter_cutoff_proven":False,
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(out,indent=2)+"\n")
    print("E004IB_ARM64_SCRATCH_ONLY_PACKAGE_ROOT_PREFLIGHT_AND_SANDBOX_UNINSTALL=PASS")
    print("E004IB_LIVE_ROOT_UNTOUCHED_ORIGINAL_PACKAGE_INSTALL_NOT_REEXECUTED=PASS")
if __name__=="__main__":main()
