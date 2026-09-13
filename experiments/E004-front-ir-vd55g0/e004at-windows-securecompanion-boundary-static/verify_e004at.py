#!/usr/bin/env python3
from pathlib import Path
import json, sys

d=Path(__file__).resolve().parent
def fail(m):
    print("E004at VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
if r.get("status")!="PASS_WINDOWS_SECURECOMPANION_IS_NOT_QTEE_UID_EVIDENCE": fail("status")
if r.get("runtime_executed") is not False or r.get("linux_secureisp_runtime_authorized") is not False: fail("runtime boundary")
p=r["package"]
for k,v in {
 "kmd_service":"CameraSecureISP",
 "companion_service":"SecureBioCompanion",
 "companion_binary":"QcISPTrustlet8380.dll",
 "service_type":"SecureCompanion",
 "trustlet_identity":4096,
 "companion_configuration":True,
}.items():
    if p.get(k)!=v: fail("package "+k)
t=r["trustlet"]
for k in ("imports_iumsdk","imports_secure_section","imports_secure_io_mapping","imports_soc_domain_assignment","wdf_um_entry","secure_bio_signer_marker"):
    if not t.get(k): fail("trustlet "+k)
if r["task_transport"].get("api")!="WdfCompanionTargetSendTaskSynchronously": fail("task transport")
if r["task_transport"].get("qtee_object_transport") is not False: fail("task/QTEE separation")
if r["identity_4096"].get("qtee_service_uid_equivalence")!="not_proven": fail("identity overclaim")
if r["identity_4096"].get("safe_linux_assumption")!="do_not_use_as_qtee_uid": fail("unsafe identity assumption")
if not r["lane_transport"].get("separate_from_companion_tasks"): fail("lane/task separation")

inf=(d/"evidence/SECURECOMPANION-INF.txt").read_text(errors="replace")
for x in [
 "KmdfService = CameraSecureISP",
 "UmdfService =  SecureBioCompanion",
 "CompanionConfiguration = CameraSecureISP",
 "ServiceBinary = %13%\\QcISPTrustlet8380.dll",
 "ServiceType = SecureCompanion",
 "TrustletIdentity = 4096",
 "CompanionServices = SecureBioCompanion",
]:
    if x not in inf: fail("INF "+x)

pe=(d/"evidence/TRUSTLET-PE.txt").read_text(errors="replace")
for x in [
 "55ebf254447b9ff8c0a5b20ae81e84f04355f84ce6fa6a09f6205562a5b0b606",
 "Name: IumSdk.dll",
 "Symbol: CreateSecureSection",
 "Symbol: MapSecureIo",
 "Symbol: AssignMemoryToSocDomain",
 "FxDriverEntryUm",
 "EvtCompanionPrePrepareHardware",
 "Microsoft Third Party Secure Bio Signer",
]:
    if x not in pe: fail("PE "+x)

wdf=(d/"evidence/WDF-COMPANION-TASKS.txt").read_text(errors="replace")
for x in [
 "WdfCompanionTargetSendTaskSynchronously",
 "FUN_140004a90(2,0",
 "SendTask - ISPTRUSTLET_START Succeeded",
 "FUN_140004a90(3,0",
]:
    if x not in wdf: fail("WDF task evidence "+x)

print("E004at VERIFY: PASS")
print(" - installed CameraSecureISP explicitly binds a Windows SecureCompanion")
print(" - QcISPTrustlet imports IUM secure-resource APIs")
print(" - camera tasks use WDF companion-target transport")
print(" - secure CSI lane control is a separate QcTrEE/SIP path")
print(" - TrustletIdentity 4096 is not treated as a Linux QTEE UID")
print(" - no Linux secure-camera runtime occurred")
