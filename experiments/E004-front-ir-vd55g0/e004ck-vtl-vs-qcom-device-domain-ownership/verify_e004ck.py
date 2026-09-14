#!/usr/bin/env python3
from pathlib import Path
import json,sys
E=Path(__file__).resolve().parent
fail=[]
def need(rel,*toks):
 s=(E/rel).read_text(errors='replace')
 for t in toks:
  if t not in s: fail.append(f'{rel}: missing {t!r}')
 return s
r=json.loads((E/'RESULT.json').read_text())
if r.get('status')!='PASS_VTL1_CPU_MAPPING_ORTHOGONAL_TO_CP_CAMERA_PKVM_HAS_NO_PARITY_SAFE_QCOM_OWNERSHIP_COMBINATION': fail.append('status')
if r['runtime_actions']!={'windows_boot':False,'pkvm_boot':False,'hyp_assign':False,'scm_assign_mem':False,'cp_camera_operation':False,'qtee_qsee':False,'camera_runtime':False}: fail.append('runtime boundary')
need('evidence/WINDOWS-ORTHOGONAL-VISIBILITY.txt','hardware-domain visibility plus trusted-worker visibility','SkmiVtlPageAccess[0] = 0x0','QCOM_SCM_VMID_CP_CAMERA','Trustlet input: DomainId=0x0d, Protection=4.')
need('evidence/QCSK-HYP-DOMAIN-EXCLUSIVITY.txt','Assignment to AC_VM_HYP successful','assignment to HYP domain cannot be shared with other domains','requires count == 1')
need('evidence/QHEE-HYP-AND-CAMERA-BOUNDARY.txt','qhee_hyp_assign.c','hyp_assign/hyp_assign.c','hyp_manager_map_memory_hlos_to_el2','hyp_manager_map_memory_el2_to_hlos','Failed to create AC_VM_HYP VM','pil_camera_mem_assign','VTTBR_EL2_get_VMID(&vttbr) == QHEE_VMID_HLOS')
need('evidence/PKVM-CANDIDATE-MATRIX.txt','[A] CP_CAMERA only + pKVM stage-2 mapping','[B] CP_CAMERA + Qualcomm AC_VM_HYP','[C] HLOS + CP_CAMERA, pKVM blocks host CPU at stage-2','RESULT=POLICY_REJECTED','RESULT=SECURITY_NOT_EQUIVALENT')
need('README.md','pKVM is not a selectable protected-camera backend on the current SP11 stack.','E004cl — Qualcomm HypX / protected-hypervisor extension authority')
if fail:
 print('E004ck VERIFY: FAIL')
 for x in fail: print(' -',x)
 sys.exit(1)
print('E004ck VERIFY: PASS')
print(' - Windows VTL1 CPU mapping is orthogonal to CP_CAMERA Qualcomm ownership')
print(' - Qualcomm AC_VM_HYP is an explicit exclusive destination class')
print(' - same-machine QHEE mediates HLOS<->EL2/HYP mappings and camera policy')
print(' - CP_CAMERA-only gives pKVM no proven access authority')
print(' - CP_CAMERA+HYP is policy-rejected')
print(' - retaining HLOS is not Windows-equivalent without DMA isolation')
print(' - current pKVM backend remains unselected and no runtime was attempted')
