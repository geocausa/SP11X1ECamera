#!/usr/bin/env python3
from pathlib import Path
import json,re,hashlib,sys

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004be VERIFY: FAIL - "+m)
        sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_COMPILE_ONLY_WINDOWS_EXACT_CAMERA_SCM_WRAPPER","status")
w=r["windows_abi"]
for k,v in {
    "call_type":"standard","convention":"SMC32","owner":"SIP",
    "service":"0x18","command":"0x07","arginfo":"0x00000002",
    "surface_ir_mask":"0x8","reconstructed_header":"0x02001807"
}.items():
    need(w[k]==v,"Windows ABI "+k)

# Reconstruct the exact Windows header independently.
svc=int(w["service"],16); cmd=int(w["command"],16)
owner=2
hdr=(owner<<24)|((svc & 0xff)<<8)|(cmd & 0xff)
need(hdr==0x02001807,"header reconstruction")

p=(d/"0001-qcom-scm-camera-protect-phy-lanes.patch").read_text()
for s in (
    "QCOM_SCM_SVC_CAMERASS",
    "0x18",
    "QCOM_SCM_CAMERASS_PROTECT_PHY_LANES",
    "0x07",
    ".arginfo = QCOM_SCM_ARGS(2)",
    ".args[0] = protect",
    ".args[1] = lane_mask",
    ".owner = ARM_SMCCC_OWNER_SIP",
    "SMC_CONVENTION_ARM_32",
    "&res, false",
    "EXPORT_SYMBOL_GPL(qcom_scm_camera_protect_phy_lanes)",
):
    need(s in p,"patch missing "+s)
need("qcom_scm_call(__scm->dev, &desc" not in p,"generic negotiated wrapper used")

q=(d/"evidence/QUALCOMM-HISTORICAL-CAMERA-SCM.txt").read_text(errors="replace")
for s in (
    "#define SCM_SVC_CAMERASS 0x18",
    "#define SECURE_SYSCALL_ID_2 0x7",
    "desc.arginfo = SCM_ARGS(2, SCM_VAL, SCM_VAL)",
    "desc.args[0] = protect",
    "desc.args[1] = csiphy_dev->csiphy_cpas_cp_reg_mask[offset]",
    "#define SCM_SIP_FNID",
    "0x02000000",
):
    need(s in q,"historical Qualcomm evidence missing "+s)

loc=(d/"evidence/LOCAL-SCM-CONVENTION.txt").read_text(errors="replace")
for s in ("probed_convention = SMC_CONVENTION_ARM_64",
          "qcom_smccc_convention",
          "ARM_SMCCC_SMC_32 : ARM_SMCCC_SMC_64"):
    need(s in loc,"local convention evidence missing "+s)

b=(d/"evidence/PATCH-REPLAY.txt").read_text(errors="replace")
for s in ("patch_dry_run=PASS","patch_apply=PASS","object_build=PASS",
          "T qcom_scm_camera_protect_phy_lanes","U __scm_smc_call",
          "overlay_unmounted=yes"):
    need(s in b,"patch replay missing "+s)

need(r["compile_only"]["runtime_invoked"] is False,"runtime invoked")
need(r["compile_only"]["installed"] is False,"installed")
need(r["compile_only"]["booted"] is False,"booted")
need(r["shared_kernel_source_modified"] is False,"shared source")
need(r["linux_secure_csi_state_changed"] is False,"Linux secure CSI")
need(r["camera_memory_reassigned"] is False,"memory reassignment")
need(r["qcomtee_loaded"] is False,"QCOMTEE")

print("E004be VERIFY: PASS")
print(" - wrapper matches the Windows camera service/operation and two-argument shape")
print(" - wrapper explicitly preserves the Windows-observed SMC32 standard-call convention")
print(" - historical Qualcomm camera source independently corroborates the ABI")
print(" - saved patch replays and qcom_scm.o compiles cleanly")
print(" - shared source stayed unchanged; nothing was installed, booted or invoked")
