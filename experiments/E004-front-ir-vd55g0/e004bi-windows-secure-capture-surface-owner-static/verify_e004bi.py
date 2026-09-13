#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bi VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_MFCORE_OWNS_SECURE_SURFACE_AND_REQUESTS_SECURE_ALLOCATOR","status")

sym=(d/"evidence/MFCORE-SYMBOL-IDENTITY.txt").read_text(errors="replace")
for x in (
    "F9995886-3ED3-A0AE-EE79-5948132AE60F",
    "SetCaptureStreamMode@CKsBasePin",
    "IsSecureBufferEnabled@CKsBasePin",
    "SetCurrentCaptureSurfaceType@CKsBasePin",
    "GetPreferredCaptureSurface@CKsBasePin",
    "InitAndCreateAllocator@CKsBasePin",
    "CreateAllocator@CKsBasePin",
    "__imp_MFCreateSecureBufferAllocator",
):
    need(x in sym,"MFCore symbol evidence missing "+x)

prop=(d/"evidence/MFCORE-VRAM-PROPERTY-CONTRACT.txt").read_text(errors="replace")
for x in (
    "mfcore_guid_at_0x18074a438=e3ac3fe780280249b79988d0cd634e0f",
    "GetPreferred_literal_0x1802a6cd8=0200000001000000",
    "GetPreferred_decoded=Id=2 KSPROPERTY_PREFERRED_CAPTURE_SURFACE; Flags=1 GET",
    "SetCurrent_literal_0x18009e0c8=0300000002000000",
    "SetCurrent_decoded=Id=3 KSPROPERTY_CURRENT_CAPTURE_SURFACE; Flags=2 SET",
):
    need(x in prop,"property evidence missing "+x)

chain=(d/"evidence/MFCORE-SECURE-ALLOCATOR-CHAIN.txt").read_text(errors="replace")
for x in (
    "CKsBasePin::SetCaptureStreamMode: secure mode selects 0x10",
    "18009dc98:",
    "18009dca0:",
    "mov\tw1, #0x10",
    "18009dcac:",
    "1802a72cc:",
    "ldr\tw25, [x19, #0x40c]",
    "1802a7440:",
    "ldr\tw1, [x19, #0x40c]",
    "1802a7444:",
    "[x8, #0x140]",
    "1802a464c:",
    "cmp\tw21, #0x10",
    "1802a4724:",
    "1802a4728:",
    "[x8, #0x200]",
    "__imp_MFCreateSecureBufferAllocator",
):
    need(x in chain,"secure allocator chain missing "+x)

ks=(d/"evidence/KSPROXY-ORDINARY-ALLOCATOR-NEGATIVE.txt").read_text(errors="replace")
for x in (
    "IKsD3DPin private IID=4f432174-8284-4d40-9497-aeeae0cf2fd4",
    "DecideTransportSurfaceType",
    "180015f90:",
    "cmp\tw8, #0x1",
    "180015f98:",
    "cmp\tw8, #0x2",
    "180016060: 80070057",
):
    need(x in ks,"KSProxy negative evidence missing "+x)

fs=(d/"evidence/FRAMESERVER-VRAMCAPTURE-BOUNDARY.txt").read_text(errors="replace")
need("DISPLAY_ADAPTER_GUID GET" in fs,"FrameServer boundary")
need("local_90 = 0x100000001" in fs,"FrameServer Id/GET encoding")

need(r["mfcore"]["secure_surface_set_when_enabled"] is True,"secure surface selection")
need(r["mfcore"]["current_surface_stored_and_reused_for_allocator"] is True,"surface propagation")
need(r["mfcore"]["secure_allocator_api_invoked_for_surface_0x10"] is True,"secure allocator call")
need(r["ksproxy"]["secure_surface_0x10_supported_by_decide_transport"] is False,"KSProxy negative")
need(r["frameserver"]["direct_secure_surface_set_proven"] is False,"FrameServer overclaim")
need(r["ownership_conclusion"]["lower_level_secure_section_implementation_resolved"] is False,"lower-level implementation overclaim")
need(r["windows_volume_read_only"] is True,"Windows volume")
need(r["windows_runtime_executed"] is False,"Windows runtime")
need(r["linux_secure_runtime_executed"] is False,"Linux secure runtime")
need(r["linux_memory_reassignment"] is False,"Linux memory assignment")
need(r["protected_mmio_access_linux"] is False,"protected MMIO")
need(r["qcomtee_loaded"] is False,"QCOMTEE")

print("E004bi VERIFY: PASS")
print(" - MFCore SecureMode detection selects current capture surface 0x10")
print(" - exact VramCapture preferred-GET/current-SET property contract is anchored")
print(" - InitAndCreateAllocator reuses the stored 0x10 surface for allocator creation")
print(" - CreateAllocator(0x10) invokes MFCreateSecureBufferAllocator")
print(" - ordinary KSProxy SYSTEM/VRAM negotiation rejects the secure surface")
print(" - FrameServer direct VramCapture reference is only display-adapter GET")
print(" - no Windows dynamic or Linux secure runtime was required")
