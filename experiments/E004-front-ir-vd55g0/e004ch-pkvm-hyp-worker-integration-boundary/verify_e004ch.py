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
if r.get('status')!='PASS_PKVM_NVHE_WORKER_BUILDS_DIRECT_HYP_BACKEND_BLOCKED_BY_QCSK_EXCLUSIVITY': fail.append('status')
if r['runtime_actions']!={'pkvm_boot':False,'nvhe_worker_runtime':False,'scm_assign_mem':False,'cp_camera_plus_hyp_attempt':False,'qtee_qsee_ffa_gunyah':False,'camera_runtime':False,'windows_boot':False}: fail.append('runtime boundary')
need('evidence/WINDOWS-OVERLAP-REQUIREMENT.txt','retain the assignment handle and trustlet mapping simultaneously','hardware-domain visibility plus trusted-worker visibility on the same protected backing during capture')
q=need('evidence/QCSK-HYP-EXCLUSIVITY.txt','assignment to HYP domain cannot be shared with other domains','cmp\tw1, #0x1','destination-HYP ownership')
need('evidence/SCM-MULTIOWNER-VS-HYP-POLICY.txt','VMID 4: source named HYP','QCOM_SCM_VMID_CP_CAMERA','HYP must be the sole destination owner')
need('evidence/PKVM-HOST-HYP-BOUNDARY.txt','kvm_nvhe.o','HANDLE_FUNC(__pkvm_host_share_hyp)','PKVM_PAGE_SHARED_BORROWED')
n=need('evidence/NVHE-COMPILE-AND-DISASM.txt','__kvm_nvhe_handle___pkvm_camera_worker_copy_mapped','__kvm_nvhe___pkvm_camera_worker_copy_mapped','__pkvm_camera_worker_copy_mapped','memcpy','FORBIDDEN_POLICY_MATCHES=0')
b=need('evidence/BUILD-AND-ZERO-RUNTIME.txt','TEXT_BYTE_IDENTICAL=1','CAMSS_PROTECTED_CAP_HW_WORKER_OVERLAP_PROVEN','0x7f','FORBIDDEN_CONCRETE_BACKEND_MATCHES=0','CALLBACK_INVOCATIONS=0','sp11_entry=7.1.5-sp11-fullio-v19c')
h=need('scaffold/camss-protected-pipeline.h','CAMSS_PROTECTED_CAP_HW_WORKER_OVERLAP_PROVEN','hardware_worker_overlap_proven','time_multiplex_visibility_allowed','0x7f')
need('nvhe-scaffold/camera_worker.c','get_hyp_state(src_page) != PKVM_PAGE_OWNED','get_hyp_state(dst_page) != PKVM_PAGE_OWNED','memcpy(dst, src, len)')
need('README.md','direct pKVM-HYP cannot currently satisfy parity','E004ci — protected guest/partition worker visibility feasibility')
if fail:
 print('E004ch VERIFY: FAIL'); [print(' -',x) for x in fail]; sys.exit(1)
print('E004ch VERIFY: PASS')
print(' - disposable nVHE worker and host-call boundary compile successfully')
print(' - worker only operates on already-HYP-owned pages and establishes no policy')
print(' - Windows requires CP_CAMERA + trusted-worker visibility to overlap')
print(' - same-machine QcSk requires destination HYP to be the sole destination owner')
print(' - direct CP_CAMERA + HYP architecture is therefore not parity-authorized')
print(' - CAMSS provider gate now requires explicit hardware/worker overlap proof (0x7f)')
print(' - production/Golden sources and runtime remain untouched')
