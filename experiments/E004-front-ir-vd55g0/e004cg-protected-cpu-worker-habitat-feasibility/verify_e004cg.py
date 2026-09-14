#!/usr/bin/env python3
from pathlib import Path
import json,sys
E=Path(__file__).resolve().parent; fail=[]
def need(rel,*tokens):
 s=(E/rel).read_text(errors='replace')
 for t in tokens:
  if t not in s: fail.append(f'{rel}: missing {t!r}')
 return s
r=json.loads((E/'RESULT.json').read_text())
if r.get('status')!='PASS_NO_ACTIVE_HABITAT_PKVM_NVHE_IS_LEADING_SOURCE_CONTROLLED_CANDIDATE_NOT_SELECTED': fail.append('status')
if r['pkvm']['selected_backend'] or r['pkvm']['qualcomm_hyp_vmid_equivalence_proven']: fail.append('pKVM overclaim')
if r['windows_one_shot_needed']: fail.append('unneeded Windows boot')
if r['runtime_actions']!={'boot_mode_change':False,'pkvm_activation':False,'qtee_qsee_probe':False,'ffa_probe':False,'gunyah_operation':False,'ownership_change':False,'camera_runtime':False}: fail.append('runtime boundary')
need('evidence/WINDOWS-WORKER-MINIMUM.txt','PASS_TRUSTED_FRAME_WORKER_IS_CPU_MEMORY_PROCESSING_AFTER_PROTECTED_MAPPINGS','trusted CPU execution outside ordinary HLOS')
q=need('evidence/QCOMTEE-SERVICE-ONLY.txt','qcomtee_object_get_service','QCOMTEE_CLIENT_ENV_OPEN','QCOMTEE_ROOT_OP_REG_WITH_CREDENTIALS','--- loader/app vocabulary search ---')
s=q.split('--- loader/app vocabulary search ---',1)[1].split('--- known service UID use ---',1)[0].strip()
if s: fail.append('QCOMTEE arbitrary app loader vocabulary appeared: '+s[:180])
z=need('evidence/QSEECOM-PRELOADED-ONLY.txt','assuming the app has already been loaded','qcom.tz.uefisecapp','QSEECOM_TZ_CMD_APP_LOOKUP','QSEECOM_TZ_CMD_APP_SEND','--- no APP_LOAD/APP_START command implemented by this interface ---')
last=z.split('--- no APP_LOAD/APP_START command implemented by this interface ---',1)[1].strip()
if last: fail.append('QSEECOM app load/start path appeared: '+last[:180])
p=need('evidence/PKVM-HYP-HABITAT.txt','kvm-arm.mode','DMA isolation using an IOMMU','Status: **Unimplemented.**','__pkvm_host_donate_hyp','selftest_state.host = PKVM_NOPAGE','selftest_state.hyp = PKVM_PAGE_OWNED')
h=need('evidence/HYP-VMID-IDENTITY-GAP.txt','VMID 4','QCOM_SCM_VMID_CP_CAMERA','HYP_VMID_PUBLIC_LINUX_AUTHORITY_MATCHES=0','must not be equated to pKVM EL2')
f=need('evidence/FFA-GUNYAH-HABITAT-GAP.txt','FFA_MEM_LEND','gunyah-hyp@80000000','When running under Gunyah','--- no local host implementation/config/device ---')
need('evidence/RUNTIME-SAFETY.txt','7.1.5-sp11-render-parity-v4+','sp11_entry=7.1.5-sp11-fullio-v19c')
need('README.md','pKVM nVHE the **leading engineering candidate**','E004ch — pKVM hyp-worker integration boundary')
if fail:
 print('E004cg VERIFY: FAIL'); [print(' -',x) for x in fail]; sys.exit(1)
print('E004cg VERIFY: PASS')
print(' - QCOMTEE and QSEECOM are clients of already-authorized services/apps, not arbitrary worker loaders')
print(' - FF-A has transport but no camera secure-partition authority')
print(' - Gunyah is present in X1 platform architecture but absent from the local Linux host stack')
print(' - pKVM nVHE can own pages outside HLOS and is source-controlled, making it the leading engineering candidate')
print(' - Golden protected mode is off and pKVM DMA isolation is explicitly unimplemented')
print(' - Windows HYP VMID 4 is not equated to Linux pKVM EL2 without authority')
print(' - no habitat is selected or runtime-authorized')
