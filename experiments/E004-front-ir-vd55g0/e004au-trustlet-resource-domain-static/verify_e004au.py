#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def fail(m): print("E004au VERIFY: FAIL - "+m); sys.exit(1)
r=json.loads((d/"RESULT.json").read_text())
if r.get("status")!="PASS_TRUSTLET_RESOURCE_AND_CP_CAMERA_DOMAIN_STATIC": fail("status")
if r.get("linux_secureisp_runtime_authorized") is not False: fail("runtime authorization")
h=r["secure_hardware"]
for k,v in {
 "callback":"EvtCompanionPrePrepareHardware",
 "mapping_api":"MapSecureIo",
 "resource_selector":"first memory resource",
 "mapping_mode_literal":"0x12",
 "physical_window":"0x0acca000..0x0accdfff",
 "size":"0x4000",
 "kd_direct_readable":False,
}.items():
    if h.get(k)!=v: fail("hardware "+k)
b=r["secure_internal_buffer"]
for k,v in {
 "page_size":"0x1000",
 "domain_va_seed":"0x18000000",
 "domain_va_rollover_threshold":"0x19000000",
 "domain_id":"0x0d",
 "protection_literal":"0x04",
 "api":"AssignMemoryToSocDomain",
}.items():
    if b.get(k)!=v: fail("buffer "+k)
x=r["linux_crosscheck"]
if x.get("vmid_symbol")!="QCOM_SCM_VMID_CP_CAMERA" or x.get("vmid_value")!="0x0d" or not x.get("exact_domain_id_match"): fail("CP_CAMERA match")
if x.get("windows_protection_equals_linux_perm_flags")!="unproven": fail("protection overclaim")
if any(r["runtime"].values()): fail("runtime action occurred")

t=(d/"evidence/TRUSTLET-RESOURCE-DECOMP.txt").read_text(errors="replace")
for s in [
 "EvtCompanionPrePrepareHardware",
 "MapSecureIo(uVar3,*(undefined8 *)(pcVar4 + 4),0x12",
 "AssignMemoryToSocDomain(hFileMappingObject,pvVar7,0,uVar1,0xd,4,0)",
 "CreateSecureSection",
 "FlushSecureSectionBuffers",
]:
    if s not in t: fail("trustlet evidence "+s)
w=(d/"evidence/WINDOWS-SECUREISP-RESOURCE.txt").read_text(errors="replace")
for s in [
 "ACPI\\\\QCOM0CCC\\\\19",
 "0x000000000ACCA000 - 0x000000000ACCDFFF",
 "rejected both normal KD physical reads",
]:
    if s not in w: fail("Windows resource "+s)
l=(d/"evidence/LINUX-CAMERA-DOMAIN.txt").read_text(errors="replace")
if "QCOM_SCM_VMID_CP_CAMERA" not in l or "0xD" not in l: fail("Linux VMID")
v=(d/"evidence/TRUSTLET-DOMAIN-VA.txt").read_text()
for s in ["domain_va_seed=0x18000000","AssignMemoryToSocDomain_domain_id=0x0d","AssignMemoryToSocDomain_protection=0x04","runtime_executed=no"]:
    if s not in v: fail("domain VA "+s)

print("E004au VERIFY: PASS")
print(" - SecureCompanion maps the CameraSecureISP protected hardware resource")
print(" - secure internal buffers are assigned to domain 0x0d")
print(" - Linux defines the same value as QCOM_SCM_VMID_CP_CAMERA")
print(" - Windows protection literal is recorded without Linux-permission overclaim")
print(" - no Linux secure-camera runtime occurred")
