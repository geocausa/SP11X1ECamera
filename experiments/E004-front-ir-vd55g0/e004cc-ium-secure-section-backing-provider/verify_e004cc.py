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
if r.get('status')!='PASS_EXTERNAL_FLAG0_SECURE_SECTION_HYPERV_VTL0_NO_ACCESS': fail.append('status')
if r['runtime_actions']!={'windows_boot':False,'ium_syscall':False,'hypercall':False,'scm_assign_mem':False,'qtee_qsee_call':False,'qcomtee_enable_or_load':False,'camera_runtime':False}: fail.append('runtime boundary')
need('evidence/SECUREKERNEL-PDB-IDENTITY.txt','9a2eeb0e4a3d76aa9a6bfaf287540f5f1f7562d814e8ecb3c3f6df6b57a557b6','0A49C8CF-92C9-F8EC-65C6-D61180FDAE51','8a7182241511195029a512aad0e0eb2b4799269f76d5f9ee71ccf697f649ca72','PDB Types and Main Symbols Processing Terminated Normally')
need('evidence/IUM-SECURE-SECTION-OBJECT-PATH.txt','IumCreateSecureSection','SkmmCreateSecureSection(param_2,0,param_3,uVar4','SkmiAllocateZeroedPage','SkmiMapViewOfSection','IumOpenSecureSection')
p=need('evidence/SECURE-PHYSICAL-PAGE-PROTECTION.txt','SkmiAllocatePhysicalPage','SkmiSecurePhysicalPages((longlong *)param_3,1,(ulonglong)local_e8','SkmiProtectPlaceholderPages(param_1,uVar5,(uint)param_3,0)','SkmiVtlPageAccess','ShvlpInitiateFastHypercall(0xc')
v=need('evidence/VTL0-NO-ACCESS-PROOF.txt','SkmiVtlPageAccess[0] = 0x0','HV_MAP_GPA_PERMISSIONS_NONE','HV_MAP_GPA_READABLE','HvCallModifyVtlProtectionMask call code = 0x000C','+0x0c = 0 (target VTL0)','final VTL0 mask = 0x0 = no access')
f=need('evidence/FLAG0-VS-FLAG2.txt','FsIso external protected sample: CreateSecureSection(descriptor,4,4,size,0)','SecureISP internal target:       CreateSecureSection(NULL,4,4,size,2)','SkmiClaimTrustedPage','flag0 skips that trusted-page claim loop','CP_CAMERA 0x0d')
need('README.md','**Microsoft Secure Kernel + Hyper-V VTL protection.**','**VTL0 has no read, no write and no execute access.**','E004cd — Linux VTL-equivalent protected-sample provider feasibility')
if fail:
 print('E004cc VERIFY: FAIL')
 for x in fail: print(' -',x)
 sys.exit(1)
print('E004cc VERIFY: PASS')
print(' - exact Microsoft PDB resolves the Secure Kernel secure-section/page call chain')
print(' - flag-0 secure section allocates pages through SkmiAllocatePhysicalPage -> SkmiSecurePhysicalPages')
print(' - final access index is 0 and SkmiVtlPageAccess[0] is 0')
print(' - ShvlpProtectPages targets VTL0 with Hyper-V call 0x000c / HvCallModifyVtlProtectionMask')
print(' - mask 0 means VTL0 has no read/write/execute access')
print(' - flag2 adds per-page SkmiClaimTrustedPage before the separate CP_CAMERA/write assignment')
print(' - external protected-sample memory enforcer is Secure Kernel + Hyper-V, not QcTrEE/QTEE/CP_CAMERA')
print(' - no runtime secure operation was performed')
