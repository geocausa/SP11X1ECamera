#!/usr/bin/env python3
from pathlib import Path
import json,sys
E=Path(__file__).resolve().parent
fail=[]
def need(rel,*tokens):
 s=(E/rel).read_text(errors='replace')
 for t in tokens:
  if t not in s: fail.append(f'{rel}: missing {t!r}')
 return s
r=json.loads((E/'RESULT.json').read_text())
if r.get('status')!='PASS_HYPX_IS_AUTHENTICATED_BOOT_PLATFORM_HYPERV_SUPPORT_NOT_REUSABLE_CAMERA_WORKER': fail.append('status')
if any(r['runtime_actions'].values()): fail.append('runtime action occurred')
q=need('evidence/QHEE-HYPX-SURFACE.txt','HYP_IMG_AUTHENTICATE','HYP_IMG_LAUNCH','qcom.tz.mssecapp','hyp_secure_launch_enabled','Failed to create AC_VM_HYP VM','Failed to map HypX ELF header','HYPX REGISTRATION SUCCESS')
m=need('evidence/MSSECAPP-HYPERV-AUTHORITY.txt','MSSECAPP_IMAGEAUTH_ID','Printing hyperV stage logs below','HyperVStageEnded','Microsoft Authenticode','Microsoft Code Verification Root')
w=need('evidence/WINDOWS-HYPERV-BOOT-CHAIN.txt','hvaa64.exe','hvloader.dll','BlArchQcSlSupported','BlArchStartedInEL2','BlArchGetEl2Regions','Microsoft Hypervisor V7.0','LockedByVtl1')
s=need('evidence/QCTREE-MSSEC-RUNTIME-SURFACE.txt','MssecServiceInvoke','MssecServicePpi','MssecServiceShutdown','--- HypX launch/auth terms in QcTrEE Mssec decomp ---')
if s.split('--- HypX launch/auth terms in QcTrEE Mssec decomp ---',1)[1].strip(): fail.append('runtime HypX launch surface appeared')
n=need('evidence/NO-INSTALLED-HYPX-PACKAGE.txt','--- INF/manifest text hits ---','--- candidate package filenames ---')
if n.split('--- candidate package filenames ---',1)[1].strip(): fail.append('installed HypX package candidate appeared')
need('README.md','we cannot put the Linux camera worker into HypX as if it were a loadable EL2 plugin.','E004cm — Gunyah/QHEE worker-VM ownership feasibility')
if fail:
 print('E004cl VERIFY: FAIL')
 for x in fail: print(' -',x)
 sys.exit(1)
print('E004cl VERIFY: PASS')
print(' - QHEE HypX is a boot-time, devcfg-gated authenticated ELF launch path')
print(' - qcom.tz.mssecapp authenticates the Hyper-V stage with Microsoft trust roots')
print(' - Windows hvloader is Qualcomm secure-launch/EL2 aware and loads hvaa64.exe')
print(' - runtime QcTrEE MssecService exposes no HypX authenticate/launch operation')
print(' - no separately installable HypX package exists in the Windows image')
print(' - no Windows boot or secure runtime operation occurred')
