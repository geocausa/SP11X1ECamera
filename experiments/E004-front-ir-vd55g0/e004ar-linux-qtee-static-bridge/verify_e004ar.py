#!/usr/bin/env python3
from pathlib import Path
import json, sys

d=Path(__file__).resolve().parent
def fail(msg):
    print("E004ar VERIFY: FAIL - "+msg)
    sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
if r.get("status")!="PASS_STATIC_QTEE_BRIDGE_PRESENT_NO_SECUREISP_RUNTIME":
    fail("status")
if r.get("linux_secureisp_runtime_authorized") is not False:
    fail("Linux SecureISP runtime boundary")
g=r["golden"]
for k,v in {
    "qcom_scm":"y",
    "qcom_tzmem":"y",
    "qcom_tzmem_mode_shmbridge":"y",
    "qcom_qseecom":"y",
    "tee":"m",
    "qcomtee":"not-set",
}.items():
    if g.get(k)!=v:
        fail("Golden config "+k)
if g.get("tee_device_nodes") or g.get("qcomtee_module_loaded") or g.get("qcomtee_module_installed"):
    fail("runtime QTEE unexpectedly enabled")
if not r["firmware_transport"].get("qcomtee_platform_device_present"):
    fail("qcomtee platform capability device")
b=r["build"]
if not b.get("built_only") or b.get("installed") or b.get("loaded"):
    fail("build-only boundary")
if b.get("sha256")!="3234dc1ffc24e1320356190ec4ba622b6e3a8df7659d26b61f9667d1fac9258d":
    fail("qcomtee module hash")
p=r["linux_primitives"]
for k in ("qtee_object_transport","tzmem_shmbridge","scm_assign_mem","cp_camera_vmid_defined","cp_camera_preview_vmid_defined"):
    if not p.get(k):
        fail("missing primitive "+k)
if p.get("in_tree_camera_secureisp_host"):
    fail("camera-specific SecureISP host must remain unresolved")
if p.get("secure_csi_lane_service_identified"):
    fail("secure CSI lane service must remain unresolved")
if r.get("windows_identity_4096_equals_qtee_service_uid")!="unproven":
    fail("identity namespace overclaim")

runtime=(d/"evidence/RUNTIME-PASSIVE.txt").read_text(errors="replace")
for s in [
    "CONFIG_QCOM_SCM=y",
    "CONFIG_QCOM_TZMEM=y",
    "CONFIG_QCOM_TZMEM_MODE_SHMBRIDGE=y",
    "CONFIG_QCOM_QSEECOM=y",
    "CONFIG_TEE=m",
    "# CONFIG_QCOMTEE is not set",
    "platform:qcomtee",
    "TEE_NODES=none",
    "QCOMTEE_MODULE_INSTALLED=no",
]:
    if s not in runtime:
        fail("runtime evidence missing "+s)

build=(d/"evidence/QCOMTEE-BUILD.txt").read_text(errors="replace")
for s in [
    "CC [M]  async.o",
    "LD [M]  qcomtee.ko",
    "vermagic:       7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64",
    "3234dc1ffc24e1320356190ec4ba622b6e3a8df7659d26b61f9667d1fac9258d",
]:
    if s not in build:
        fail("build evidence missing "+s)

print("E004ar VERIFY: PASS")
print(" - Golden already has SCM, TZMem SHM Bridge and QSEECOM")
print(" - firmware exposes the passive qcomtee platform capability device")
print(" - qcomtee is not enabled/installed/loaded in Golden")
print(" - qcomtee builds cleanly against the exact Golden kernel ABI")
print(" - camera VMIDs and reserved camera/QTEE/TA memory exist")
print(" - camera-specific SecureISP host + secure CSI service remain unresolved")
print(" - no Linux SecureISP runtime occurred")
