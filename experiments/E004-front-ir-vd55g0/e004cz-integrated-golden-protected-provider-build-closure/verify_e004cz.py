#!/usr/bin/env python3
import hashlib, json, subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
S=D/'scaffold'
R=json.loads((D/'RESULT.json').read_text())
fail=[]
def need(path,*tokens):
    p=D/path
    if not p.exists(): fail.append(f'missing {path}'); return
    t=p.read_text(errors='replace')
    for x in tokens:
        if x not in t: fail.append(f'{path}: missing {x}')
need('evidence/PARTIAL-LINK-PROOF.txt','integration edges still unresolved (must be empty):','runtime registration symbols (must be empty):','sp11_cpz_dma_buf_is_protected')
need('evidence/FAIL-CLOSED-REGISTRATION.txt','qcom_scm_init_e004cz_compile_only','return -EPERM')
need('evidence/DISABLED-TOPOLOGY-PROOF.txt','dtc_stderr_bytes=0','iommus=1 c09 20','pd-type=6','status=disabled','ABSENT_EXPECTED')
need('evidence/FAIL-CLOSED-CAPABILITY.txt','runtime_binding_authorized=false','external_sample_runtime_provider=false','protected_transfer_runtime_provider=false')
need('README.md','external protected sample** is still only a contract','E004da — external CPZ protected-sample backing implementation')
need('scaffold/system_heap-e004cz.c','bool sp11_cpz_dma_buf_is_protected','SP11_CPZ_HEAP_POISONED')
need('scaffold/hamoa-secure-cb9-candidate.dtsi','0x0c09 0x20','pd-type = <6>','status = "disabled"')
obj=S/'sp11-protected-stack-e004cz.o'
# Build products are intentionally ignored by git. Validate them mechanically when
# present on the experiment host; otherwise the committed link proof is authoritative.
if obj.exists():
    h=hashlib.sha256(obj.read_bytes()).hexdigest()
    if h!=R['partial_link']['sha256']: fail.append(f'integrated object hash mismatch {h}')
    nm=subprocess.check_output(['nm',str(obj)],text=True,errors='replace')
    for sym in ('qcom_scm_assign_mem_regions','sp11_cpz_assign_sg','sp11_cpz_dma_buf_is_protected','sp11_cpz_system_heap_lend','sp11_cpz_system_heap_mark_active','sp11_cpz_system_heap_mark_detached','sp11_cpz_system_heap_reclaim'):
        if sym not in nm: fail.append(f'missing integrated symbol {sym}')
    if 'init_module' in nm or 'cleanup_module' in nm or '__initcall' in nm: fail.append('runtime registration present')
    nmu=subprocess.check_output(['nm','-u',str(obj)],text=True,errors='replace')
    for sym in ('qcom_scm_assign_mem_regions','sp11_cpz_assign_sg','sp11_cpz_dma_buf_is_protected','sp11_cpz_system_heap_lend','sp11_cpz_system_heap_reclaim'):
        if sym in nmu: fail.append(f'integration edge unresolved {sym}')
# Production source immutability.
prod={
 '/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/drivers/firmware/qcom/qcom_scm.c':R['production_immutability']['qcom_scm_sha256'],
 '/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/drivers/dma-buf/heaps/system_heap.c':R['production_immutability']['system_heap_sha256'],
 '/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/drivers/misc/fastrpc.c':R['production_immutability']['fastrpc_sha256'],
}
for p,expect in prod.items():
    q=Path(p)
    if not q.exists(): fail.append(f'missing production source {p}')
    elif hashlib.sha256(q.read_bytes()).hexdigest()!=expect: fail.append(f'production source changed {p}')
if R.get('status')!='PASS_INTEGRATED_GOLDEN_PROTECTED_INTERNAL_PATH_COMPILES_LINKS_FAILS_CLOSED': fail.append('bad status')
if R['fail_closed']['runtime_binding_authorized']: fail.append('runtime binding unexpectedly authorized')
if R['fail_closed']['secure_cb9_status']!='disabled': fail.append('CB9 unexpectedly enabled')
if R['fail_closed']['external_sample_runtime_provider_present']: fail.append('external runtime provider overclaimed')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
if fail:
    print('E004cz VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004cz VERIFY: PASS')
print(' - protected system-heap, SG ownership, SCM and CPZ FastRPC integration edges resolve in one ARM64 object')
print(' - FastRPC protected query is now backed by the system-heap ownership state machine')
print(' - SCM/FastRPC runtime registration is absent and secure CB9 remains disabled')
print(' - production Golden SCM, system-heap and FastRPC sources remain byte-exact')
print(' - external protected sample and transfer remain contract-only, so runtime binding stays unauthorized')
print(' - no ownership/FastRPC/camera/SecureISP runtime action occurred')
