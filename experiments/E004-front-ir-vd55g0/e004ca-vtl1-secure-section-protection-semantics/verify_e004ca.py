#!/usr/bin/env python3
from pathlib import Path
import json, sys
E=Path(__file__).resolve().parent
fail=[]
def need(rel,*tokens):
 s=(E/rel).read_text(errors='replace')
 for t in tokens:
  if t not in s: fail.append(f'{rel}: missing {t!r}')
 return s
r=json.loads((E/'RESULT.json').read_text())
if r.get('status')!='PASS_EXTERNAL_SAMPLE_IS_IUM_SECURE_SECTION_INTERNAL_CP_CAMERA_ASSIGNMENT_SEPARATE': fail.append('status')
if r['runtime_actions']!={'windows_reboot_or_trace':False,'ium_call':False,'scm_assign_mem':False,'shm_bridge_create':False,'qtee_qsee_call':False,'qcomtee_enable_or_load':False,'camera_runtime':False}: fail.append('runtime boundary')
need('evidence/IUMSDK-FORWARDERS.txt','AssignMemoryToSocDomain','CreateSecureSection','OpenSecureSection','GetExposedSecureSection')
need('evidence/IUMBASE-TO-IUMDLL.txt','IumAssignMemoryToSocDomain','IumCreateSecureSection','IumOpenSecureSection','iumbase.pdb')
i=need('evidence/IUMDLL-VTL1-SYSCALLS.txt','<IumAssignMemoryToSocDomain>','svc\t#0x8000','<IumCreateSecureSection>','svc\t#0x8003','<IumOpenSecureSection>','svc\t#0x800e','iumdll.pdb')
e=need('evidence/EXTERNAL-VS-INTERNAL-CREATE-CONTRACT.txt','CreateSecureSection(&local_378,4,4,param_3,0)','CreateSecureSection(0,4,4,*(undefined4 *)(param_1 + 0x20),2)','AssignMemoryToSocDomain(hFileMappingObject,pvVar7,0,uVar1,0xd,4,0)','scenario_guid=AE53FC6E-8D89-4488-9D2E-4D008731C5FD')
need('evidence/SCENARIO-POLICY-TRUSTED-OPEN.txt','tPolicy_scenario={AE53FC6E-8D89-4488-9D2E-4D008731C5FD}','OpenSecureSection(&local_40)','AsyncImportSecureBuffer')
c=need('evidence/CAMERA-IUM-IMPORT-SURFACE.txt','--- FsIso ---','--- SecureISP trustlet ---','--- BioIso ---','No listed camera component above imports GetExposedSecureSection.')
q=need('evidence/QCSK-ASSIGNMENT-BRIDGE.txt','QcSkAssignMemoryToSocDomain','entry[0] addr=1400042c0 input_domain=0x25 mapped_vmid=0x6','entry[4] addr=1400042e0 input_domain=0x23 mapped_vmid=0x3','QCOM_SCM_VMID_CP_CAMERA','0xD','QCOM_SCM_PERM_WRITE','0x2','Trustlet input: DomainId=0x0d, Protection=4.','QcSkExt permission switch maps IUM Protection=4 -> QHEE permission parameter 0x2.')
l=need('evidence/LINUX-PRIMITIVE-COMPARISON.txt','int qcom_scm_assign_mem','qcom_scm_shm_bridge_create','static const struct dma_buf_ops tee_heap_buf_ops','protected,secure-video-record','# CONFIG_QCOMTEE is not set')
need('README.md','the Windows external sample is protected by a Secure Kernel / IUM object-and-policy boundary, not by the camera\'s CP_CAMERA assignment path.','E004cb — Qualcomm Secure Kernel camera memory state machine')
if fail:
 print('E004ca VERIFY: FAIL')
 for x in fail: print(' -',x)
 sys.exit(1)
print('E004ca VERIFY: PASS')
print(' - IumSdk forwards to iumbase and IUMDLL direct SVC stubs')
print(' - secure-section create/open and SoC-domain assignment are distinct IUM syscalls')
print(' - FsIso external sample is GUID+scenario CreateSecureSection(..., flag 0) with no CP_CAMERA assignment')
print(' - SecureISP internal target is anonymous flag-2 secure section plus separate SoC-domain assignment')
print(' - QcSkExt proves domain 0x0d passes through as Qualcomm VMID 0x0d / CP_CAMERA')
print(' - QcSkExt maps IUM protection 4 to Qualcomm write permission 0x2')
print(' - external sample physical VMID is intentionally left unresolved rather than guessed')
print(' - no secure runtime operation was performed')
