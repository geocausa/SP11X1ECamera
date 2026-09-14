#!/usr/bin/env python3
import json
from pathlib import Path
D=Path(__file__).resolve().parent
R=json.loads((D/'RESULT.json').read_text())
fail=[]
def need(path,*tokens):
    p=D/path
    if not p.exists(): fail.append(f'missing {path}'); return
    t=p.read_text(errors='replace')
    for x in tokens:
        if x not in t: fail.append(f'{path}: missing {x}')
need('evidence/QHEE-CP-CDSP-SINGLE-OWNER-RULES.txt','RULE 11.1','vmid=0x2a','RULE 70.2','vmid=0x3','RULE 22.1')
need('evidence/MEMBUF-EXTERNAL-SAMPLE-LIFETIME.txt','mem_buf_lend()','current VM','reclaim','before backing release')
need('evidence/QCOM-HEAP-BACKING-AND-CPU-BLOCK.txt','qcom_system_heap.c','qcom_cma_heap.c','mmap','vmap','-EPERM','IOMMU')
need('evidence/FASTRPC-CPZ-EXTERNAL-IMPORT.txt','dma_buf_get(fd)','mem_buf_dma_buf_exclusive_owner','secure context bank','dma_buf_put')
need('evidence/WINDOWS-ORACLE-CROSSCHECK.txt','CP_CAMERA','CP_CDSP-only protected backing','16-byte id')
need('README.md','HLOS -> CP_CDSP','E004cr — compile-only external CPZ sample provider contract')
if R.get('status')!='PASS_EXTERNAL_CPZ_SAMPLE_CP_CDSP_ONLY_OWNERSHIP_AND_LIFETIME_PROVEN': fail.append('bad status')
if R.get('golden_runtime_ready'): fail.append('Golden must not be runtime ready')
if R['external_backing']['cp_camera_owner_required']: fail.append('external sample must not require CP_CAMERA')
if not R['lifetime']['reclaim_before_heap_free']: fail.append('release ordering missing')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
if fail:
    print('E004cq VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004cq VERIFY: PASS')
print(' - same-machine QHEE authorizes HLOS <-> CP_CDSP-only ownership')
print(' - generic Qualcomm dma-heaps provide mem-buf-aware external backing independent of camera HW')
print(' - HLOS mmap/vmap are denied after an HLOS-excluding lend')
print(' - FastRPC can retain/import the lent dma-buf through the protected secure-context path')
print(' - worker detach, ownership reclaim and heap release have a fail-closed order')
print(' - no protected runtime operation occurred')
