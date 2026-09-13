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
if r.get('status')!='PASS_MULTI_OWNER_MECHANISM_PROVEN_CAMERA_ACL_AUTHORITY_UNRESOLVED': fail.append('status')
if r['runtime_actions']!={'scm_assign_mem':False,'shm_bridge_create':False,'qtee_smc':False,'qcomtee_enable_or_load':False,'camera_runtime':False}: fail.append('runtime boundary')
w=need('evidence/WINDOWS-SIMULTANEOUS-VISIBILITY.txt','MapViewOfFile','*(LPVOID *)(param_1 + 0x30) = pvVar6','AssignMemoryToSocDomain(hFileMappingObject,pvVar7,0,uVar1,0xd,4,0)','*(undefined8 **)(lVar3 + 0x30)','CloseHandle(*(HANDLE *)(param_1 + 0x10))','UnmapViewOfFile(*(LPCVOID *)(param_1 + 0x30))')
l=need('evidence/LINUX-SCM-MULTI-OWNER-ACL.txt','QCOM_SCM_VMID_CP_CAMERA\t\t0xD','dst_perms[2]','dst_perms[0].vmid = QCOM_SCM_VMID_HLOS','qcom_scm_assign_mem(map->dma_addr','num_vmids + 1')
c=need('evidence/CP-CAMERA-PRECEDENT-GAP.txt','QCOM_SCM_VMID_CP_CAMERA','QCOM_SCM_VMID_CP_CAMERA_PREVIEW')
# Current tree must still contain no CP_CAMERA references outside the ABI header copies.
for line in c.splitlines():
    if 'QCOM_SCM_VMID_CP_CAMERA' in line and 'dt-bindings/firmware/qcom,scm.h' not in line:
        fail.append('new CP_CAMERA implementation precedent appeared: '+line)
q=need('evidence/QTEE-SHMBRIDGE-VISIBILITY.txt','shm->kaddr = alloc_pages_exact','shm->paddr = virt_to_phys(shm->kaddr)','qcom_tzmem_shm_bridge_create','pfn_and_ns_perm = paddr | QCOM_SCM_PERM_RW','QCOM_SCM_VMID_HLOS','*mem_paddr = mem_object->paddr')
e=need('evidence/EXTERNAL-PROTECTED-SAMPLE-PROVIDER-GAP.txt','TEE_DMA_HEAP_SECURE_VIDEO_RECORD','protected,secure-video-record','drivers/tee/optee','--- qcomtee provider integration search ---','default_cma_region','reserved','system')
section=e.split('--- qcomtee provider integration search ---',1)[1].split('--- runtime heaps ---',1)[0].strip()
if section: fail.append('qcomtee now has protected-heap integration; refresh gate')
need('README.md','The mechanism exists; the camera-specific authority does not.','E004bu — internal protected-target ACL contract')
if fail:
    print('E004bt VERIFY: FAIL')
    for x in fail: print(' -',x)
    sys.exit(1)
print('E004bt VERIFY: PASS')
print(' - Windows keeps VTL1 trustlet mapping alive while CP_CAMERA domain assignment is active')
print(' - Linux SCM supports explicit multi-owner destination ACLs')
print(' - no current Linux callsite establishes a CP_CAMERA ACL or trusted co-owner')
print(' - QCOMTEE SHM-bridge memory is ordinary HLOS-addressable tee_shm, not protected-camera backing')
print(' - QCOMTEE does not provide the secure-video-record DMA heap in this tree')
print(' - no secure runtime operation was performed')
