#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bj VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_MFPLAT_SECURE_BUFFER_OWNER_IS_FSISO_RPC","status")
need(r["mfplat"]["sha256"]=="4384d4ca9e1ed8ae3033eb0812460081c89f71a9dd2550438c9ec0e1e24d05e6","mfplat hash")
need(r["mfplat"]["pdb_sha256"]=="9a85634d558d94546acd05a557b4c7b30abb2f3c1df1b6faf09a9c414e0de206","pdb hash")
need(r["mfplat"]["implementation_factory"]=="CameraTrustletConnectionImpl::CreateInstance","factory")
need(r["fsiso"]["transport"]=="ncalrpc","transport")
need(r["fsiso"]["endpoint_format"]=="FsIso_%u_%I64u","endpoint")
need(r["fsiso"]["process"]=="FsIso.exe","process")
need(r["fsiso"]["connect_order"]==["GenerateEndpointName","LaunchProcess","EstablishRpcConnection"],"connect order")
need(r["secure_media_buffer"]["guid_generated_with"]=="CoCreateGuid","GUID generation")
need(r["secure_media_buffer"]["destructor_calls_allocator_destroy_with_guid"] is True,"destructor lifetime")
need(r["camera_secureisp_internal_cp_camera_buffer_is_separate"] is True,"buffer distinction")
need(r["windows_volume_read_only"] is True,"Windows volume")
need(r["linux_secure_runtime_executed"] is False,"Linux runtime")
need(r["linux_memory_reassignment"] is False,"Linux memory")
need(r["protected_mmio_access_linux"] is False,"Linux MMIO")
need(r["qcomtee_loaded"] is False,"QCOMTEE")

p=(d/"evidence/MFPLAT-PDB-AUTHORITY.txt").read_text(errors="replace")
for s in (
 "PDBGUID: {378BD674-3DCB-DA18-5F23-A355C5740851}",
 "MFCreateSecureBufferAllocator",
 "CreateSecureBuffer@CameraTrustletConnectionImpl",
 "DestroySecureBuffer@CameraTrustletConnectionImpl",
 "CreateSecureSection@CameraTrustlet",
 "CloseSecureSection@CameraTrustlet",
 "CreateInstance@SecureMediaBuffer",
 "GetIdentifier@SecureMediaBuffer",
):
    need(s in p,"PDB authority missing "+s)

a=(d/"evidence/ALLOCATOR-DELEGATION.txt").read_text(errors="replace")
for s in (
 "1800e2c70",
 "1802232c0",
 "0x18023b6e0 = CameraTrustlet::CreateSecureSection",
 "180223498",
 "0x18023b3a0 = CameraTrustlet::CloseSecureSection",
):
    need(s in a,"allocator delegation missing "+s)

f=(d/"evidence/CAMERATRUSTLET-FSISO-RPC.txt").read_text(errors="replace")
for s in (
 "ncalrpc",
 "FsIso_%u_%I64u",
 "%s\\FsIso.exe %s",
 "\\FsIso.exe",
 "Symbol: BCryptGenRandom",
 "Symbol: CreateProcessW",
 "Symbol: RpcStringBindingComposeW",
 "Symbol: NdrClientCall3",
 "0x180079b08 = BCryptGenRandom",
 "0x1802402f8 = GetCurrentProcessId",
 "0x180240a00 = CreateProcessW",
):
    need(s in f,"FsIso evidence missing "+s)

g=(d/"evidence/SECUREMEDIABUFFER-GUID-LIFETIME.txt").read_text(errors="replace")
for x in (
 "0x180078918 = CoCreateGuid",
 "0x180236338 = SecureMediaBuffer constructor",
 "add	x8, x22, #0x118",
 "str	q7, [x8]",
 "ldr	x0, [x19, #0x128]",
 "ldp	x1, x2, [x19, #0x118]",
 "ldr	x8, [x8, #0x20]",
 "GetIdentifier copies stored GUID to caller",
 "str	q7, [x26]",
):
    need(x in g,"GUID lifetime evidence missing "+x)

print("E004bj VERIFY: PASS")
print(" - MFCreateSecureBufferAllocator is backed by CameraTrustletConnectionImpl")
print(" - create/destroy delegate to CameraTrustlet secure-section RPC methods")
print(" - CameraTrustlet launches FsIso.exe and connects over ncalrpc")
print(" - SecureMediaBuffer owns the GUID and destroys the remote section with the same GUID")
print(" - Linux secure-camera runtime remained untouched")
