#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bp VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_WINDOWS_TWO_BUFFER_PIPELINE_INTERNAL_CP_CAMERA_HW_TARGET","status")

internal=(d/"evidence/INTERNAL-CP-CAMERA-HW-TARGET.txt").read_text(errors="replace")
for x in (
    "AssignMemoryToSocDomain(hFileMappingObject,pvVar7,0,uVar1,0xd,4,0)",
    "*(uint *)(param_1 + 0x28) = uVar2;",
    "*(uint *)(param_1 + 0x48) = uVar2 + *(int *)(param_1 + 0x38);",
    "*local_e8 = (ulonglong)*(uint *)(local_f0 + 5);",
    "local_e8[1] = (ulonglong)*(uint *)(local_f0 + 9);",
    "Invalid SMMU address for HW programming",
):
    need(x in internal,"internal hardware-target evidence missing "+x)

external=(d/"evidence/EXTERNAL-VTL1-OPEN-LIFETIME.txt").read_text(errors="replace")
for x in (
    "OpenSecureSection(&local_40)",
    "*(HANDLE *)(param_1 + 0x88) = hFileMappingObject;",
    "*(LPVOID *)(param_1 + 0x90) = pvVar2;",
    "UnmapViewOfFile",
    "CloseHandle",
):
    need(x in external,"external VTL1 evidence missing "+x)

transfer=(d/"evidence/INTERNAL-TO-EXTERNAL-TRANSFER.txt").read_text(errors="replace")
for x in (
    "FUN_1800037c8((undefined8 *)",
    "(*(longlong *)(lVar3 + 0x90) + (ulonglong)*(uint *)(lVar3 + 0x9c))",
    "*(undefined8 **)(lVar3 + 0x30)",
    "undefined4 FUN_180003718(undefined8 *param_1,undefined8 *param_2,int param_3,int param_4)",
    "FUN_180028600(param_1,param_2,(ulonglong)uVar1);",
    "FUN_180003478((longlong)param_1,param_2",
):
    need(x in transfer,"transfer evidence missing "+x)

mem=(d/"evidence/MEMCOPY-DIRECTION.txt").read_text(errors="replace")
for x in (
    "FUN_180028600(undefined8 *param_1,undefined8 *param_2,ulonglong param_3)",
    "param_2",
    "param_1",
):
    need(x in mem,"copy direction evidence missing "+x)

field=(d/"evidence/TWO-BUFFER-FIELD-MAP.txt").read_text(errors="replace")
for x in (
    "+0x28 internal CP_CAMERA SMMU/domain VA base",
    "+0x48 second internal CP_CAMERA SMMU/domain address",
    "+0x90 external trustlet virtual mapping",
    "hMems[0] <- object +0x28",
    "hMems[1] <- object +0x48",
    "destination <- external mapping at +0x90",
    "source      <- internal mapping at +0x30",
):
    need(x in field,"field map missing "+x)

need(r["pipeline"]["external_vtl1_is_direct_hardware_target"] is False,"external target overclaim")
need(r["transfer"]["direction_proven"] is True,"transfer direction")
need(r["parity_correction"]["single_protected_sample_direct_to_vfe_matches_windows"] is False,"single buffer model")
need(r["parity_correction"]["internal_capture_target_and_external_sample_must_be_separate"] is True,"two-buffer split")
need(r["parity_correction"]["cp_camera_applies_to_internal_capture_target_proven"] is True,"CP_CAMERA internal")
need(r["parity_correction"]["cp_camera_for_external_sample_proven"] is False,"external CP_CAMERA overclaim")
need(r["windows_runtime_executed"] is False,"Windows runtime")
need(r["linux_secure_runtime_executed"] is False,"Linux runtime")
need(r["linux_memory_reassignment"] is False,"Linux assignment")
need(r["protected_mmio_access_linux"] is False,"protected MMIO")
need(r["qcomtee_loaded"] is False,"QCOMTEE")

print("E004bp VERIFY: PASS")
print(" - protected IFE hMems are internal CP_CAMERA domain/SMMU addresses")
print(" - external VTL1 sample is opened by GUID and mapped separately")
print(" - worker transfer direction is internal capture target -> external VTL1 sample")
print(" - a single direct-to-VFE protected sample is not Windows parity")
print(" - CP_CAMERA ownership is proven for the internal target, not for the external sample")
print(" - no secure runtime operation occurred")
