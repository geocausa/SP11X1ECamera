#!/usr/bin/env python3
from pathlib import Path
import json, sys

d=Path(__file__).resolve().parent
def need(x,m):
    if not x:
        print("E004ay VERIFY: FAIL - "+m)
        sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_SECURE_IFE_LITE_BUS_MATCHES_LINUX_VFE680_LITE_LAYOUT","status")
need(r["linux"]["compatible"]=="qcom,x1e80100-camss","X1E compatible")
need(r["linux"]["vfe_implementation"]=="vfe_ops_680","VFE ops")
need(r["trustlet"]["active_logical_core"]==3,"active core")
need(r["trustlet"]["hal_family"]=="IFE-Lite","HAL family")
need(r["csid_parity"]=="not_claimed","CSID overclaim")
need(r["runtime_executed"] is False,"runtime")
need(r["qcomtee_loaded"] is False,"qcomtee")
need(r["linux_secureisp_runtime_authorized"] is False,"authorization")

linux=(d/"evidence/LINUX-VFE680-LITE.txt").read_text(errors="replace")
for s in (
    "0x218 : 0xc18",
    "0x228 : 0xc28",
    "0x230 : 0xc30",
    "0x264 : 0xc64",
    "0x268 : 0xc68",
    "0x270 : 0xc70",
    "0x400 : 0xe00",
    "0x404 : 0xe04",
    "0x408 : 0xe08",
    "IFE Lite write master IDs",
):
    need(s in linux,"Linux vfe680 evidence missing "+s)

x1e=(d/"evidence/LINUX-X1E-IFE-RESOURCES.txt").read_text(errors="replace")
for s in ("/* IFE0 */","/* IFE1 */","/* IFE_LITE_0 */","/* IFE_LITE_1 */",".is_lite = true",".hw_ops = &vfe_ops_680"):
    need(s in x1e,"X1E resource evidence missing "+s)

trust=(d/"evidence/TRUSTLET-IFE-LITE-BUS.txt").read_text(errors="replace")
for s in (
    "*(longlong *)(param_1 + 0xf8) + 0x18",
    "*(longlong *)(param_1 + 0xf8) + 0x28",
    "*(longlong *)(param_1 + 0xf8) + 0x30",
    "*(longlong *)(param_1 + 0xf8) + 0x200",
    "*(longlong *)(param_1 + 0xf8) + 0x300",
    "violationStatus=0x%x imageSizeVioaltionStatus=0x%x",
):
    need(s in trust,"trustlet bus evidence missing "+s)

p=(d/"evidence/PARITY-MAP.txt").read_text(errors="replace")
for s in ("+0x18","0x218","+0x64","0x264","+0x200 + n*0x100","0x400 + n*0x100"):
    need(s in p,"parity map missing "+s)

print("E004ay VERIFY: PASS")
print(" - X1E Linux already exposes full/full/lite/lite VFE resources")
print(" - X1E lite VFE resources use vfe_ops_680")
print(" - trustlet IFE-Lite bus IRQ/violation/client geometry matches Linux vfe-680")
print(" - secure ownership/transport remains outside this parity claim")
print(" - no Linux secure-camera runtime occurred")
