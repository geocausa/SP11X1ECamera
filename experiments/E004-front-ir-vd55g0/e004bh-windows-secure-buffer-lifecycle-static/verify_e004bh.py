#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bh VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_WINDOWS_VTL1_GUID_SECURE_BUFFER_DISTINCT_FROM_LANE_LIFETIME","status")

sdk=r["windows_sdk"]
need(sdk["secure_capture_surface"]=="0x0010","secure surface")
need(sdk["secure_capture_surface_meaning"]=="secure buffer in VTL1","VTL1 meaning")
need(sdk["secure_transfer_flag"]=="0x00040000","secure transfer flag")
need(sdk["buffered_transfer_flag"]=="0x00000400","buffered flag")
need(sdk["surfacecam_combined_mask"]=="0x00040400","combined mask")
need(sdk["biometric_import_identity"]=="GUID SecureBufferIdentifier","bio GUID")

s=(d/"evidence/WINDOWS-SDK-SECURE-BUFFER.txt").read_text(errors="replace")
for x in (
    "KS_CAPTURE_ALLOC_SECURE_BUFFER          = 0x0010",
    "secure buffer in VTL1",
    "GUID guidBufferIdentifier",
    "DWORD cbBufferSize",
    "DWORD cbCaptured",
    "KSSTREAM_HEADER_OPTIONSF_SECUREBUFFERTRANSFER 0x00040000",
    "GUID SecureBufferIdentifier",
    "LockAndValidateSecureBuffer",
    "ReleaseSecureBuffer",
):
    need(x in s,"SDK evidence missing "+x)

surf=(d/"evidence/SURFACECAM-SECURE-KS-BRIDGE.txt").read_text(errors="replace")
for x in (
    "14008d378 u32=0x00040400",
    "pSecureBufferInfo is NULL",
    "puVar7 = *(undefined8 **)(lVar8 + 0x28)",
    "*(undefined8 *)(param_3 + 0x6c) = puVar7[1]",
    "*(undefined8 *)(param_3 + 100) = uVar6",
    'pcVar1 = "SECURE_BUFFER"',
    "*(uint *)(param_1 + 0x88) = uVar2",
    "Get external buffer for requestId",
):
    need(x in surf,"SurfaceCam evidence missing "+x)

t=(d/"evidence/TRUSTLET-BUFFER-LIFECYCLE.txt").read_text(errors="replace")
for x in (
    "FUN_180005868",
    "FUN_1800060e0",
    "FUN_180006ce0",
    "FUN_180003c90",
    "FUN_180005968",
    "OpenSecureSection(&local_40)",
    "CreateSecureSection(0,4,4",
    "AssignMemoryToSocDomain(hFileMappingObject,pvVar7,0,uVar1,0xd,4,0)",
    "CloseHandle(*(HANDLE *)(param_1 + 0x10))",
):
    need(x in t,"trustlet evidence missing "+x)

dyn=(d/"evidence/WINDOWS-DYNAMIC-BUFFER-ORDER.txt").read_text(errors="replace")
for x in (
    "1637:E004AQ_KHIT SecureISP_TaskSend x0=0000000000000007",
    "1638:E004AQ_KHIT SecureISP_OpDispatcher",
    "1641:E004AQ_KHIT SecureISP_TaskSend x0=0000000000000002",
    "1544:E004AQ_KHIT SecureISP_TaskSend x0=0000000000000003",
    "1547:E004AQ_KHIT SecureISP_ConfigSecureCamera",
    "1550:E004AQ_KHIT SecureISP_TaskSend x0=0000000000000001",
    "the trace does not directly expose individual trustlet CreateSecureSection/AssignMemoryToSocDomain calls",
):
    need(x in dyn,"dynamic evidence missing "+x)

bio=(d/"evidence/BIOISO-SECURE-IMPORT.txt").read_text(errors="replace")
for x in (
    "2d1e2bb0072a935ac73702dae735961ee208e989287e50c1d3fc888825264a65",
    "SensorAdapterAsyncImportSecureBuffer",
    "OpenSecureSection",
    'local_188 = "AsyncImportSecureBuffer"',
):
    need(x in bio,"BioIso evidence missing "+x)

usb=(d/"evidence/SECUREUSBVIDEO-PLATFORM-CORROBORATION.txt").read_text(errors="replace")
for x in (
    "surface_mipi_ir_creator_proven=no",
    "378f2830f5867f31ec5c63b95fe7e35f78d48bc139989db79590c5ac7d5d7521",
    "UuidCreate(&local_374)",
    "CreateSecureSection(&local_378,4,4",
    "OpenSecureSection(&local_120)",
):
    need(x in usb,"SecureUSBVideo evidence missing "+x)

need(r["surfacecam"]["descriptor_layout_matches_windows_sdk"] is True,"descriptor layout")
need(r["trustlet"]["external_buffer"]["created_by_trustlet"] is False,"external creator claim")
need(r["windows_dynamic"]["individual_secure_section_calls_observed_directly"] is False,"dynamic overclaim")
need(r["platform_corroboration"]["surface_mipi_ir_allocator_proven"] is False,"UVC overclaim")
need(r["parity_consequence"]["lane_ownership_and_secure_sample_lifetime_are_distinct"] is True,"lifetime distinction")
need(r["parity_consequence"]["external_secure_sample_and_cp_camera_internal_buffer_are_distinct"] is True,"object distinction")
need(r["windows_volume_read_only"] is True,"Windows volume")
need(r["linux_secure_runtime_executed"] is False,"Linux runtime")
need(r["linux_memory_reassignment"] is False,"Linux memory assignment")
need(r["protected_mmio_access_linux"] is False,"protected MMIO")
need(r["qcomtee_loaded"] is False,"QCOMTEE")

print("E004bh VERIFY: PASS")
print(" - Windows defines the external camera sample as a VTL1 GUID-addressed SECURE_BUFFER_INFO object")
print(" - SurfaceCam consumes the exact SDK descriptor and secure-transfer flag")
print(" - SecureISP separately creates a CP_CAMERA-owned internal buffer and opens the external secure section")
print(" - secure sample lifetime is distinct from the lane-protection bracket")
print(" - BioIso imports/opens secure samples by identity")
print(" - SecureUSBVideo corroborates the Windows platform mechanism but is not claimed as Surface MIPI allocator")
print(" - no Linux secure runtime or memory reassignment occurred")
