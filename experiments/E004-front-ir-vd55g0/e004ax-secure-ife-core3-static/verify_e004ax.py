#!/usr/bin/env python3
from pathlib import Path
import json, sys

d=Path(__file__).resolve().parent
def need(x,m):
    if not x:
        print("E004ax VERIFY: FAIL - "+m)
        sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_SECUREISP_ACTIVE_LOGICAL_CORE3_IS_IFE_LITE","status")
need(r["device_config"]["active_core_count"]==1,"core count")
need(r["device_config"]["active_core_ids"]==[3],"core list")
need(r["e004aw_mapping"]["hal_family"]=="IFE-Lite","HAL family")
need(r["runtime_executed"] is False,"runtime")
need(r["qcomtee_loaded"] is False,"qcomtee")
need(r["protected_aperture_accessed_linux"] is False,"protected aperture")
need(r["linux_secureisp_runtime_authorized"] is False,"Linux authorization")

t=(d/"evidence/TRUSTLET-CORE3-LIFECYCLE.txt").read_text(errors="replace")
for s in (
    "*(undefined4 *)(param_1 + 0x18) = 3",
    "*(undefined4 *)(param_1 + 0x24) = 1",
    "FUN_18000bbf0(param_1,*(uint *)(param_1 + (uVar43 + 6) * 4)",
    "IFE initialization is failed with result 0x%x, for core %d",
    "CSID initialization is failed with result 0x%x, for core %d",
    "uVar5 = *(uint *)(param_1 + 0x18)",
):
    need(s in t,"trustlet core-list evidence missing "+s)

k=(d/"evidence/KMD-IFE3-CLOCK.txt").read_text(errors="replace")
need("ife3 clock request" in k,"KMD IFE3 corroboration")

h=(d/"evidence/CORE3-TO-LITE.txt").read_text(errors="replace")
for s in (
    "if (param_2 < 2)",
    "*(uint *)(lVar32 + 0x6b568) = (uint)(param_2 >= 2)",
    "pcVar23 = FUN_18000d000",
    "HAL_ife_lite_get_hw_version",
):
    need(s in h,"E004aw cross-check missing "+s)

print("E004ax VERIFY: PASS")
print(" - DeviceConfig creates one active logical core: core 3")
print(" - secure IFE and CSID initialization consume the same core list")
print(" - Windows KMD independently references the IFE3 clock request")
print(" - E004aw maps logical core 3 to the IFE-Lite HAL family")
print(" - no Linux secure-camera runtime occurred")
