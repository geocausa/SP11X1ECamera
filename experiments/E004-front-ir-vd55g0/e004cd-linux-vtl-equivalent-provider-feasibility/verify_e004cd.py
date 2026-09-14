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
if r.get('status')!='PASS_LINUX_SURFACE_AND_OWNERSHIP_PRIMITIVES_EXIST_NO_TRUSTED_WORKER_PROVIDER': fail.append('status')
if r['runtime_provider_authorized_now'] is not False: fail.append('provider authorization')
if not r['qcom_assign']['can_replace_owner_set'] or r['qcom_assign']['external_camera_owner_identity_known']: fail.append('assign boundary')
if not r['tee_dma_heap']['surface_matches_no_cpu_map_shape'] or r['tee_dma_heap']['qcomtee_protmem_backend_found']: fail.append('tee backend boundary')
if r['pkvm']['golden_booted_protected'] or r['pkvm']['dma_isolation_status']!='unimplemented': fail.append('pkvm boundary')
if r['runtime_actions']!={'windows_boot':False,'scm_assign_mem':False,'protected_heap_register':False,'qcomtee_probe':False,'ffa_probe':False,'optee_probe':False,'gunyah_operation':False,'pkvm_boot':False,'camera_runtime':False}: fail.append('runtime boundary')
w=need('evidence/WINDOWS-REQUIRED-CONTRACT.txt','PASS_EXTERNAL_FLAG0_SECURE_SECTION_HYPERV_VTL0_NO_ACCESS','"vtl0_access": "none (no R/W/X)"','"cp_camera_external_provider": false')
p=need('evidence/PKVM-NOT-CAMERA-PROVIDER.txt','kvm-arm.mode','DMA isolation using an IOMMU','Status: **Unimplemented.**','Protected KVM')
if 'kvm-arm.mode=protected' in Path('/proc/cmdline').read_text(): fail.append('Golden unexpectedly booted pKVM protected')
q=need('evidence/QCOM-ASSIGN-CAPABILITY.txt','Make a secure call to reassign memory ownership','array having new owners and corresponding permission','*srcvm = next_vm','QCOM_SCM_VMID_HLOS_FREE','QCOM_SCM_VMID_CP_CAMERA')
t=need('evidence/TEE-PROTMEM-BACKEND-CONTRACT.txt','static const struct dma_buf_ops tee_heap_buf_ops','struct tee_protmem_pool_ops','physical memory will','become inaccesible after the lend_protmem() call','--- QCOMTEE provider search ---')
sec=t.split('--- QCOMTEE provider search ---',1)[1].strip()
if sec: fail.append('QCOMTEE protmem provider appeared: '+sec[:160])
g=need('evidence/GUNYAH-NOT-HOST-CONTROLLED.txt','gunyah-hyp@80000000','When running under Gunyah','--- upstream host control implementation in this source tree ---','--- live DT only exposes reserved region ---')
need('evidence/TRUSTED-WORKER-AUTHORITY.txt','PASS_QCSK_CAMERA_PIL_STATE_MACHINE_IS_FIRMWARE_HANDOFF_NOT_FRAME_PROVIDER','PASS_QCTREE_TRANSPORTS_MAP_TO_EXISTING_LINUX_ABIS_NO_CAMERA_PROVIDER_IDENTITY')
s=need('evidence/RUNTIME-SAFETY.txt','7.1.5-sp11-render-parity-v4+','sp11_entry=7.1.5-sp11-fullio-v19c')
need('README.md','which trusted execution identity is allowed to own/map the pages and execute the worker?','E004ce — compile-only protected-provider capability gate')
if fail:
 print('E004cd VERIFY: FAIL'); [print(' -',x) for x in fail]; sys.exit(1)
print('E004cd VERIFY: PASS')
print(' - Qualcomm ASSIGN can mechanically replace HLOS with a different owner set')
print(' - generic TEE protected DMA-BUF supplies the correct no-CPU-map surface')
print(' - no QCOMTEE secure-video-record/protmem backend or trusted camera owner is identified')
print(' - pKVM is not enabled on Golden and its documented DMA isolation is unimplemented')
print(' - Gunyah platform memory exists but Golden exposes no host control implementation/device')
print(' - feasible architecture exists in principle, but no parity-safe runtime provider is authorized')
print(' - Windows one-shot is not needed for this already-resolved behavior question')
print(' - no secure runtime operation occurred')
