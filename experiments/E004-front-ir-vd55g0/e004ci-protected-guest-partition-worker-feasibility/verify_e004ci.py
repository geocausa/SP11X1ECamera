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
if r.get('status')!='PASS_NO_PROTECTED_GUEST_OR_FFA_PARTITION_CAMERA_OWNER_BINDING': fail.append('status')
if r['runtime_actions']!={'pkvm_boot':False,'protected_vm':False,'ffa_call_or_probe':False,'qtee_qsee':False,'scm_assign_mem':False,'camera_runtime':False,'windows_boot':False}: fail.append('runtime boundary')
p=need('evidence/PKVM-GUEST-OWNERSHIP.txt','int __pkvm_host_donate_guest','PKVM_ID_GUEST','PKVM_PAGE_OWNED','QUALCOMM_INTEGRATION_MATCHES=0')
f=need('evidence/FFA-PARTITION-TRANSPORT.txt','int __pkvm_host_share_ffa','PKVM_PAGE_SHARED_OWNED','ffa_partition_probe','uuid')
l=need('evidence/PKVM-PLATFORM-LIMITS.txt','DMA isolation using an IOMMU','Status: **Unimplemented.**','Proxying of Trustzone services','sp11_entry=7.1.5-sp11-fullio-v19c')
need('evidence/ORACLE-AND-HYP-BOUNDARY.txt','direct pKVM-HYP cannot currently satisfy parity','hardware/worker overlap proven')
need('README.md','the two ownership systems are currently unbound','E004cj — platform secure-worker authority closure')
if fail:
 print('E004ci VERIFY: FAIL'); [print(' -',x) for x in fail]; sys.exit(1)
print('E004ci VERIFY: PASS')
print(' - pKVM protected guest donation provides host isolation and guest CPU mapping')
print(' - arm64 KVM/pKVM contains no Qualcomm/QHEE guest-owner binding')
print(' - pKVM DMA/IOMMU isolation remains unimplemented in this tree')
print(' - FF-A supplies memory transport only to an existing secure partition')
print(' - no X1E camera secure-partition identity/provider was found')
print(' - neither path satisfies simultaneous CP_CAMERA + trusted-worker visibility')
print(' - no protected runtime operation was performed')
