#!/usr/bin/env python3
from pathlib import Path
import json, sys

d=Path(__file__).resolve().parent
def need(v,msg):
    if not v:
        print("E004az VERIFY: FAIL - "+msg)
        sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_TRUSTLET_CSID_LITE_MATCHES_LINUX_CSID680","status")
need(r["linux"]["compatible"]=="qcom,x1e80100-camss","compatible")
need(r["linux"]["csid_implementation"]=="csid_ops_680","csid ops")
need(r["trustlet"]["table"]=="CSID_Lite","table")
need(r["trustlet"]["active_surface_selector_proven"] is False,"Surface selector overclaim")
need(r["trustlet"]["selector_semantics"]=="unresolved","selector semantics overclaim")
need(r["runtime_executed"] is False,"runtime")
need(r["qcomtee_loaded"] is False,"qcomtee")
need(r["linux_secureisp_runtime_authorized"] is False,"Linux authorization")

linux=(d/"evidence/LINUX-CSID680.txt").read_text(errors="replace")
for s in (
    "#define CSID_TOP_IRQ_STATUS",
    "0x7c",
    "#define CSID_TOP_IRQ_CLEAR",
    "0x84",
    "#define CSID_BUF_DONE_IRQ_STATUS",
    "0x8c",
    "#define CSID_CSI2_RX_IRQ_STATUS",
    "0x9c",
    "#define CSID_CSI2_RX_CFG0",
    "0x200",
    "#define CSID_RDI_CFG0(rdi)",
    "0x500 + 0x100",
    "#define CSID_RDI_CTRL(rdi)",
    "0x504 + 0x100",
    "#define CSID_RDI_EPOCH_IRQ_CFG(rdi)",
    "0x52c + 0x100",
):
    need(s in linux,"Linux CSID680 evidence missing "+s)

x1e=(d/"evidence/LINUX-X1E-CSID-RESOURCES.txt").read_text(errors="replace")
for s in ("/* CSID_LITE0 */","/* CSID_LITE1 */",".is_lite = true",".hw_ops = &csid_ops_680"):
    need(s in x1e,"X1E resource evidence missing "+s)

trust=(d/"evidence/TRUSTLET-CSID-LITE.txt").read_text(errors="replace")
for s in (
    'CSID_Lite%d is not in Active state',
    "*(longlong *)(param_1 + 8) + 0x200",
    "*(longlong *)(param_1 + 8) + 0x204",
    "*(longlong *)(param_1 + 8) + 0x504",
    "*(longlong *)(param_1 + 8) + 0x7c",
    "*(longlong *)(param_1 + 8) + 0x9c",
    "*(longlong *)(param_1 + 8) + 0x8c",
    "*(longlong *)(param_1 + 8) + 0x84",
    "*(longlong *)(param_1 + 8) + 0xa4",
    "*(longlong *)(param_1 + 8) + 0x94",
):
    need(s in trust,"trustlet CSID-Lite evidence missing "+s)

irq=(d/"ghidra/TRUSTLET-CSID-IRQ-HELPERS.txt").read_text(errors="replace")
for s in ("+ 0xec","+ 0xfc","+ 0x10c","+ 0x11c"):
    need(s in irq,"RDI IRQ helper missing "+s)

pm=(d/"evidence/PARITY-MAP.txt").read_text(errors="replace")
for s in ("0x500 + n*0x100","CSID_RDI_CFG0","0x540 + n*0x100","0x564 + n*0x100"):
    need(s in pm,"parity map missing "+s)

print("E004az VERIFY: PASS")
print(" - trustlet CSID-Lite IRQ/RX/RDI layout matches Linux csid-680")
print(" - X1E Linux exposes CSID_LITE0/1 using csid_ops_680")
print(" - exact Surface selector choice remains intentionally unclaimed")
print(" - no Linux secure-camera runtime occurred")
