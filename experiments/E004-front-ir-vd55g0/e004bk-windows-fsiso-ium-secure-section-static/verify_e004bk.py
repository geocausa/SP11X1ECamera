#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bk VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_FSISO_SERVER_CREATES_SECURE_CAMERA_IUM_SECTION","status")

ids=(d/"evidence/IDENTITY-AND-SYMBOLS.txt").read_text(errors="replace")
for x in (
    "bb8908c6abc4655e96dc8b01eac86dd39839f6df1cd6730f913d182e492ce288",
    "d937099b26149a071af629b1f9b055645c1a58d6cce68a600425a01de01a34c1",
    "93B68425-0001-BB52-0629-3C9D979A1351",
    "RpcCreateSecureSection",
    "RpcCloseSecureSection",
    "RpcEstablishFsIsoConnection",
    "RpcDestroyFsIsoConnection",
    "FSISO_CONNECTION_rundown",
    "SECURE_CAMERA_SCENARIO_GUID",
    "__imp_CreateSecureSection",
    "__imp_OpenSecureSection",
    "__imp_CloseHandle",
):
    need(x in ids,"identity/symbol evidence missing "+x)

fs=(d/"evidence/FSISO-SECURE-SECTION-SERVER.txt").read_text(errors="replace")
for x in (
    "scenario_guid=AE53FC6E-8D89-4488-9D2E-4D008731C5FD",
    "tPolicy_scenario={AE53FC6E-8D89-4488-9D2E-4D008731C5FD}",
    "__imp_CreateSecureSection",
    "__imp_CloseHandle",
    "14000287c: f9400508",
    "140002884: d63f0100",
    "1400026c8: f9404508",
    "1400026cc: d63f0100",
):
    need(x in fs,"FsIso server evidence missing "+x)

need(r["fsiso"]["tpolicy_contains_same_scenario"] is True,"scenario policy")
need(r["fsiso"]["create_import"]=="IumSdk!CreateSecureSection","IUM create")
need(r["fsiso"]["guid_indexed_server_state"] is True,"GUID-indexed state")
need(r["ownership_conclusion"]["lifetime_key"]=="per-buffer GUID","lifetime key")
need(r["ownership_conclusion"]["external_sample_distinct_from_secureisp_internal_cp_camera_buffer"] is True,"external/internal split")
need(r["ownership_conclusion"]["external_sample_distinct_from_secure_lane_ownership"] is True,"sample/lane split")
need(r["windows_volume_read_only"] is True,"Windows volume")
need(r["windows_runtime_executed"] is False,"Windows runtime")
need(r["linux_secure_runtime_executed"] is False,"Linux runtime")
need(r["linux_memory_reassignment"] is False,"Linux reassignment")
need(r["protected_mmio_access_linux"] is False,"protected MMIO")
need(r["qcomtee_loaded"] is False,"QCOMTEE")

print("E004bk VERIFY: PASS")
print(" - FsIso server identity and exact Microsoft PDB match are anchored")
print(" - RpcCreateSecureSection calls IUM CreateSecureSection under the secure-camera scenario")
print(" - the same scenario GUID is independently present in FsIso trusted-process policy")
print(" - RpcCloseSecureSection closes the GUID-indexed secure-section handle")
print(" - external sample, SecureISP internal buffer, and secure-lane lifetimes remain distinct")
print(" - no Windows or Linux secure runtime occurred")
