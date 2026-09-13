#!/usr/bin/env python3
from pathlib import Path
import json,sys
d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004ba VERIFY: FAIL - "+m); sys.exit(1)
r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_TRUSTLET_SELECTOR_IS_CAM_ISP_CAN_USE_LITE_MODE","status")
need(r["structure_match"]["feature_flag_dword_index"]=="0x23","feature index")
need(r["structure_match"]["feature_flag_byte_offset"]=="0x8c","feature offset")
need(r["selector"]["public_macro"]=="CAM_ISP_CAN_USE_LITE_MODE","macro")
need(r["selector"]["public_bit"]==1,"bit")
need(r["distinct_from_bSfeUsed"] is True,"bSfeUsed distinction")
need(r["live_surface_feature_flag"]=="unproven","live-value overclaim")
need(r["runtime_executed"] is False,"runtime")
need(r["qcomtee_loaded"] is False,"qcomtee")
need(r["linux_secureisp_runtime_authorized"] is False,"authorization")
q=(d/"evidence/QUALCOMM-FEATURE-FLAG.txt").read_text(errors="replace")
for s in (
    "#define CAM_ISP_VC_DT_CFG    4",
    "#define CAM_ISP_CAN_USE_LITE_MODE              BIT(1)",
    "__u32                           feature_flag;",
    "in_port->can_use_lite             = in->feature_flag & CAM_ISP_CAN_USE_LITE_MODE;",
    "csid_caps->is_lite && !can_use_lite",
):
    need(s in q,"public authority missing "+s)
t=(d/"evidence/TRUSTLET-LITE-SELECTOR.txt").read_text(errors="replace")
for s in (
    "*(uint *)(param_1 + 0xe00) = param_3[0x23] >> 1 & 1;",
    'Feature Mask                       = %d',
    "if (*(int *)(param_1 + 0xe00) == 0)",
    "Register_secure_CSID_HAL1",
):
    need(s in t,"trustlet evidence missing "+s)
s=(d/"evidence/SURFACECAMAVS-LITE-STRINGS.txt").read_text(errors="replace")
for x in ("IFE_LITE_MODE","IFE_LITE_SECURE_MODE"):
    need(x in s,"Surface corroboration missing "+x)
print("E004ba VERIFY: PASS")
print(" - DeviceConfig dword 0x23 maps to public cam_isp_in_port_info_v2.feature_flag")
print(" - feature bit 1 is CAM_ISP_CAN_USE_LITE_MODE")
print(" - trustlet copies that bit into the secure CSID HAL selector")
print(" - bSfeUsed remains a distinct state")
print(" - exact live SP11 feature_flag remains intentionally unclaimed")
