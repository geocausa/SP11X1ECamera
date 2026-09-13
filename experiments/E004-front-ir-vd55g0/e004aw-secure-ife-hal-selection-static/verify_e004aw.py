#!/usr/bin/env python3
from pathlib import Path
import json, sys

d=Path(__file__).resolve().parent

def need(cond,msg):
    if not cond:
        print("E004aw VERIFY: FAIL - "+msg)
        sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_SECURE_IFE_HAL_SELECTION_IS_CORE_INDEX_NOT_HW_VERSION","status")
need(r["ife_hal_selection"]["full_ife_core_ids"]==[0,1],"full core IDs")
need(r["ife_hal_selection"]["ife_lite_core_ids"]==[2,3],"lite core IDs")
need(r["ife_hal_selection"]["selection_occurs_before_hw_version_sample"] is True,"selection ordering")
need(r["hw_version"]["chooses_full_vs_lite"] is False,"HW version selector claim")
need(r["surface_ir"]["active_logical_ife_core"]=="unproven","Surface core overclaim")
need(r["runtime_executed"] is False,"runtime must be false")
need(r["qcomtee_loaded"] is False,"qcomtee load must be false")
need(r["linux_secureisp_runtime_authorized"] is False,"Linux SecureISP authorization must remain false")

hal=(d/"evidence/IFE-HAL-SELECTION.txt").read_text(errors="replace")
for s in (
    "if (param_2 < 2)",
    "lVar9 = param_4 + 0xc00",
    "uVar33 = param_4 + 0x4000",
    "lVar9 = param_4 + 0x1200",
    "uVar33 = param_4;",
    "*(uint *)(lVar32 + 0x6b568) = (uint)(param_2 >= 2)",
    "pcVar23 = FUN_18000f610",
    "pcVar23 = FUN_18000d000",
    "HAL_ife_get_hw_version = 0x%x",
    "HAL_ife_lite_get_hw_version = 0x%x",
):
    need(s in hal,"IFE HAL evidence missing "+s)

life=(d/"evidence/HW-VERSION-LIFECYCLE.txt").read_text(errors="replace")
for s in (
    "IFE powered on and clocks enabled successfully",
    "*(undefined8 *)(lVar10 + 0x6b570)",
    "*(undefined4 *)(lVar10 + 0x100) = uVar3",
):
    need(s in life,"HW-version lifecycle missing "+s)

csid=(d/"evidence/CSID-HAL-SELECTION.txt").read_text(errors="replace")
for s in (
    "*(uint *)(param_1 + 0xe00) = param_3[0x23] >> 1 & 1",
    "if (*(int *)(param_1 + 0xe00) == 0)",
    "Register_secure_CSID_HAL1",
):
    need(s in csid,"CSID selector evidence missing "+s)

print("E004aw VERIFY: PASS")
print(" - full IFE vs IFE-Lite HAL is selected from logical core ID")
print(" - cores 0/1 use full IFE; cores 2/3 use IFE-Lite")
print(" - HW version is sampled only after the HAL table is installed")
print(" - CSID has an independent DeviceConfig-bit HAL selector")
print(" - active Surface IR core remains intentionally unclaimed")
print(" - no Linux secure-camera runtime occurred")
