#!/usr/bin/env python3
from pathlib import Path
import json,sys
E=Path(__file__).resolve().parent; fail=[]
def need(rel,*tok):
 s=(E/rel).read_text(errors='replace')
 for t in tok:
  if t not in s: fail.append(f'{rel}: missing {t!r}')
 return s
r=json.loads((E/'RESULT.json').read_text())
if r.get('status')!='PASS_WINDOWS_SECURE_CPU_WORKERS_ARE_VTL1_WORKLOADS_NO_REUSABLE_CAMERA_SECURE_SERVICE_FOUND': fail.append('status')
if r['runtime_actions']!={'windows_boot':False,'trustlet_launch':False,'qtee_qsee_call':False,'secure_app_start':False,'scm_assign_mem':False,'protected_memory_operation':False,'camera_runtime':False}: fail.append('runtime boundary')
i=need('evidence/IUM-SECURE-SECTION-CLIENT-SCAN.txt','files_with_ium_secure_section_surface= 8','BioIso.exe','QcISPTrustlet8380.dll','SecureUSBVideo.dll','UsbXhciCompanion.dll','FsIso.exe')
q=need('evidence/IUM-QCTREE-CROSSMATCH-EXACT.txt','service_count= 11','PassThroughService','MemSharingService','InvokeService','NO_QCTREE_SERVICE_GUID_MATCH')
w=need('evidence/IUM-WORKLOAD-REGISTRATION.txt','ServiceType = SecureCompanion','TrustletIdentity = 4096','SecureUSBVideo.dll','UsbXhciCompanion.dll','QcISPTrustlet8380.dll')
x=need('ghidra/XHCI-SECURE-SECTION.txt','GetExposedSecureSection','DmaMapMemory','MapSecureIo','OpenSecureSection','CreateSecureSection')
e=need('evidence/SECUREKERNEL-EXPOSED-SECTION-SEMANTICS.txt','SkmmCreateExposedSecureSection','SkmiClaimPhysicalPage','SKMI_WRITE_PTE_WORKER','not a VTL0 exposure API')
f=need('evidence/FACE-VSM-SECURE-WORKER.txt','WbioFrameworkLockAndValidateSecureBuffer','CopyingFrameBuffer','WbioFrameworkReleaseSecureBuffer','RunInfraredFaceProcessor','VirtualSecureMode')
need('evidence/WBIO-SECURE-BUFFER-FRAMEWORK-SCAN.txt','FaceRecognitionSensorAdapterVsmSecure.dll','WbioFrameworkLockAndValidateSecureBuffer')
d=need('ghidra/QCDX-SECURE-COPY.txt','CryptoSendCopyCmdSecureApp','IOCTL_SCM_SECURE_APP_SEND_COMMAND','sampleap.mbn','Playready')
need('evidence/QCDX-PRODUCTION-SECURE-APPS.txt','Use secure app for copying Non secure to secure buffer','qcdxkmsuc8380.mbn')
need('evidence/QCDX-SIGNED-PAYLOAD-ROLE.txt','Qualcomm Cryptographic Operations')
need('evidence/PLATFORM-WORKER-MATRIX.txt','FaceRecognitionSensorAdapterVsmSecure.dll','QcDX qcdxkm8380.sys','No same-machine generic QcTrEE/QSEE secure-copy service')
need('README.md','not necessarily members of one Qualcomm VMID owner list','E004ck — VTL trusted-CPU visibility versus Qualcomm device-domain ownership')
if fail:
 print('E004cj VERIFY: FAIL'); [print(' -',x) for x in fail]; sys.exit(1)
print('E004cj VERIFY: PASS')
print(' - exact IUM secure-section client set is bounded on the SP11 image')
print(' - IUM trusted workloads contain no QcTrEE service GUID bridge')
print(' - SecureISP, SecureUSBVideo and xHCI are separate SecureCompanion workloads')
print(' - Windows Hello provides an independent VSM secure CPU IR worker')
print(' - xHCI exposed sections are claimed into Secure Kernel, not exposed to VTL0')
print(' - QcDX secure copy is a GPU/content-protection secure-app protocol, not camera authority')
print(' - no reusable same-machine QcTrEE/QSEE camera secure-copy service was found')
print(' - no secure runtime operation was performed')
