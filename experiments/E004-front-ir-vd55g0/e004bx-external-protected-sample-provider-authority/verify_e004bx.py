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
if r.get('status')!='PASS_NO_CURRENT_X1E_EXTERNAL_PROTECTED_SAMPLE_PROVIDER_AUTHORITY': fail.append('status')
if r['runtime_actions']!={'module_loaded':False,'optee_probe':False,'qcomtee_enable_or_load':False,'qtee_qsee_call':False,'scm_assign_mem':False,'protected_heap_created':False,'camera_runtime':False}: fail.append('runtime boundary')
m=need('evidence/GOLDEN-PROVIDER-MATRIX.txt','CONFIG_TEE_DMABUF_HEAPS=y','CONFIG_OPTEE=m','# CONFIG_QCOMTEE is not set','default_cma_region','reserved','system','TEE_DMA_HEAP_SECURE_VIDEO_RECORD','drivers/tee/optee/smc_abi.c','drivers/tee/optee/ffa_abi.c')
# secure-video-record must still have no provider callsite: only enum/name map references in matrix.
for line in m.splitlines():
    if 'TEE_DMA_HEAP_SECURE_VIDEO_RECORD' in line and not ('tee_heap.c' in line or 'tee_core.h' in line):
        fail.append('new secure-video-record provider appeared: '+line)
t=need('evidence/TEE-PROTECTED-DMABUF-SEMANTICS.txt','DMA_ATTR_SKIP_CPU_SYNC','static const struct dma_buf_ops tee_heap_buf_ops','case TEE_DMA_HEAP_SECURE_VIDEO_RECORD','return "protected,secure-video-record";')
ops=t.split('static const struct dma_buf_ops tee_heap_buf_ops = {',1)[1].split('};',1)[0]
for bad in ('.mmap', '.vmap', '.begin_cpu_access', '.end_cpu_access'):
    if bad in ops: fail.append('protected TEE heap gained ordinary CPU op '+bad)
o=need('evidence/OPTEE-PROVIDER-MISMATCH.txt','enum tee_dma_heap_id heap_id = TEE_DMA_HEAP_SECURE_VIDEO_PLAY','enum tee_dma_heap_id id = TEE_DMA_HEAP_SECURE_VIDEO_PLAY','tee_device_register_dma_heap(optee->teedev','--- X1E DT OP-TEE compatible search ---')
# X1E-specific search section must stay empty after its marker.
if o.split('--- X1E DT OP-TEE compatible search ---',1)[1].strip(): fail.append('X1E OP-TEE DT node now present')
q=need('evidence/QCOMTEE-PROVIDER-GAP.txt','# CONFIG_QCOMTEE is not set' if False else 'config QCOMTEE','shm->kaddr = alloc_pages_exact','shm->paddr = virt_to_phys(shm->kaddr)','qcom_tzmem_shm_bridge_create','qtee@d80e0000','ta@d8600000')
# qcomtee protected-heap search section must stay empty.
sec=q.split('--- qcomtee has no protected-heap registration ---',1)[1].split('--- qcomtee ordinary shared memory keeps HLOS kaddr ---',1)[0].strip()
if sec: fail.append('QCOMTEE protected heap implementation appeared: '+sec[:200])
c=need('evidence/CMA-RESERVED-HEAP-REJECTION.txt','.begin_cpu_access = cma_heap_dma_buf_begin_cpu_access','.end_cpu_access = cma_heap_dma_buf_end_cpu_access','.mmap = cma_heap_mmap','.vmap = cma_heap_vmap','reserved','default_cma_region')
x=need('evidence/X1E-FIXED-CARVEOUTS.txt','camera_mem: camera@8e100000','qtee_mem: qtee@d80e0000','ta_mem: ta@d8600000','no-map','--- no Linux driver source references to X1E camera carveout label/address ---')
if x.split('--- no Linux driver source references to X1E camera carveout label/address ---',1)[1].strip(): fail.append('camera carveout gained Linux driver consumer; refresh gate')
l=need('evidence/LOCAL-REUSE-SWEEP.txt','--- qcomtee protected heap/provider terms across local kernel trees (expected empty) ---','--- secure-video-record C references across local kernel trees ---')
if l.split('--- qcomtee protected heap/provider terms across local kernel trees (expected empty) ---',1)[1].split('--- secure-video-record C references across local kernel trees ---',1)[0].strip(): fail.append('local QCOMTEE provider patch found; refresh gate')
need('README.md','A heap name is not a security boundary.','E004by — QcTrEE MemShare/SMCInvoke service authority')
if fail:
    print('E004bx VERIFY: FAIL')
    for x in fail: print(' -',x)
    sys.exit(1)
print('E004bx VERIFY: PASS')
print(' - generic TEE protected DMA-BUF has CPU-inaccessible buffer semantics')
print(' - secure-video-record exists only as an enum/name; no provider registers it')
print(' - OP-TEE provider code registers secure-video-play only and is inactive on X1E')
print(' - QTEE carveouts exist, but QCOMTEE has no protected DMA-heap provider and is disabled')
print(' - live reserved/default CMA heaps are CPU-mappable and are not protected samples')
print(' - fixed camera/QTEE carveouts provide no per-sample provider contract')
print(' - no secure runtime operation was performed')
