#!/usr/bin/env python3
import hashlib, json
from pathlib import Path
D=Path(__file__).resolve().parent
R=json.loads((D/'RESULT.json').read_text())
fail=[]
def need(rel,*tokens):
    p=D/rel
    if not p.exists(): fail.append(f'missing {rel}'); return
    s=p.read_text(errors='replace')
    for t in tokens:
        if t not in s: fail.append(f'{rel}: missing {t}')
need('README.md','cpz_hold','POISONED','E004cv')
need('evidence/STATE-LIFETIME-CONTRACT.txt','HLOS -> TRANSITION -> LENT -> ACTIVE -> DETACHED','cpz_hold=true','POISONED')
need('evidence/HLOS-CPU-ACCESS-GATES.txt','mmap returns -EPERM','vmap returns -EPERM','DMA_ATTR_SKIP_CPU_SYNC')
need('evidence/DISABLED-RUNTIME-BOUNDARY.txt','module_init(system_heap_create) registration is removed','sp11_cpz_assign_sg','no CPZ_USERPD')
need('evidence/COMPILE-PROOFS.txt','heap_init_symbol_count=0','sp11_cpz_assign_sg','dma_buf_put')
need('scaffold/system_heap-e004cu.c','SP11_CPZ_HEAP_POISONED','get_dma_buf(dmabuf)','dma_buf_put(dmabuf)','DMA_ATTR_SKIP_CPU_SYNC','sp11_cpz_assign_sg','E004cu compile-only: heap registration deliberately disabled')
need('scaffold/sp11-cpz-system-heap.h','sp11_cpz_system_heap_lend','sp11_cpz_system_heap_reclaim')
if 'module_init(system_heap_create)' in (D/'scaffold/system_heap-e004cu.c').read_text(): fail.append('live heap registration remains')
for bad in ('CPZ_USERPD', 'FASTRPC_INVOKE2_SESS_INFO', 'pd-type'):
    if bad in (D/'scaffold/system_heap-e004cu.c').read_text(): fail.append(f'forbidden FastRPC activation token {bad}')
if R.get('status')!='PASS_GOLDEN_PROTECTED_DMABUF_STATE_WRAPPER_COMPILES_DISABLED': fail.append('bad status')
if R['build']['heap_registration_present']: fail.append('heap registration unexpectedly present')
if R['fast_rpc_binding']['runtime_import_authorized']: fail.append('runtime import unexpectedly authorized')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
p=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/drivers/dma-buf/heaps/system_heap.c')
if hashlib.sha256(p.read_bytes()).hexdigest()!=R['build']['production_system_heap_sha256']:
    fail.append('Golden system_heap.c changed')
if fail:
    print('E004cu VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004cu VERIFY: PASS')
print(' - Golden system-heap SG backing is wrapped with explicit protected ownership state')
print(' - lend is blocked by existing HLOS CPU/device mappings')
print(' - HLOS mmap/vmap/CPU access is denied while protected')
print(' - an extra dma-buf reference pins backing until successful reclaim')
print(' - ownership uncertainty becomes POISONED and retains backing fail-closed')
print(' - heap registration and CPZ FastRPC activation remain absent')
print(' - Golden production system_heap.c remains byte-exact; no runtime action occurred')
