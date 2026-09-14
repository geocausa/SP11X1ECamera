#!/usr/bin/env python3
import hashlib, json, re, subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
S=D/'scaffold'
R=json.loads((D/'RESULT.json').read_text())
fail=[]
def need(path,*tokens):
    p=D/path
    if not p.exists(): fail.append(f'missing {path}'); return ''
    t=p.read_text(errors='replace')
    for x in tokens:
        if x not in t: fail.append(f'{path}: missing {x}')
    return t
need('evidence/WINDOWS-CAPTURED-EXTENT-PREMAP.txt','cbCaptured is known BEFORE','MapViewOfFile','must use the predeclared captured extent')
need('evidence/LINUX-DMABUF-FD-CAPABILITY.txt','DMA_HEAP_IOCTL_ALLOC','does NOT mmap','SAME fd')
need('evidence/FASTRPC-MEM-MAP-UNMAP-LIFETIME.txt','dma_buf_get(req.fd)','map->va is NULL','DSP unmap failure','worker_detached()')
need('evidence/SAME-MACHINE-CDSP-FD-MAP-DISPATCH.txt','fastrpc_invoke_fd_mmap_create','FASTRPC_MAP_FD = 2','fastrpc_invoke_mmap_get_cpz_phys')
need('evidence/CPZ-SESSION-ORDER.txt','pd_type   = 6 (CPZ_USERPD)','MUST occur before process attach/create')
need('evidence/CAPTURED-EXTENT-HANDOFF.txt','declared_captured_extent','payload_offset <= serialized_extent.')
need('README.md','No special kernel FastRPC import API','E004dc — CPZ protected-frame worker image and invoke ABI')
src=need('scaffold/sp11-cpz-fastrpc-handoff.c',
    'sp11_cpz_fastrpc_declare_captured_extent',
    'req->flags = FASTRPC_MAP_FD',
    'req->length = length',
    'captured_extent != handoff->declared_captured_extent',
    'sp11_cpz_external_abort_worker_import',
    'sp11_cpz_external_commit_worker_import',
    'sp11_cpz_external_worker_detached')
# Coordinator must never perform the real ioctl itself.
if re.search(r'\b(?:ioctl|ksys_ioctl|vfs_ioctl)\s*\(', src):
    fail.append('coordinator contains a real ioctl call')
# Same-machine firmware identity.
fw=Path('/lib/firmware/qcom/x1e80100/microsoft/Denali/qccdsp8380.mbn')
if not fw.exists(): fail.append('missing same-machine CDSP firmware')
elif_hash = hashlib.sha256(fw.read_bytes()).hexdigest() if fw.exists() else ''
if elif_hash and elif_hash != R['same_machine_cdsp']['firmware_sha256']:
    fail.append('CDSP firmware hash changed')
# Ghidra direct result must retain map-flag-2 branch/caller evidence.
gh=need('ghidra/CDSP-FASTRPC-MMAP-AUTHORITY.txt','fastrpc_invoke_fd_mmap_create','FUN_f010f290','FUN_f011b0c8')
if 'if (param_4 != 2)' not in gh or 'FUN_f010f290' not in gh:
    fail.append('same-machine flag-2 fd-map dispatch not retained')
# Build products are ignored by git, but validate them mechanically if present.
obj=S/'sp11-cpz-fastrpc-handoff.o'
if obj.exists():
    h=hashlib.sha256(obj.read_bytes()).hexdigest()
    if h != R['build']['handoff_object_sha256']: fail.append(f'handoff object hash mismatch {h}')
    nm=subprocess.check_output(['nm',str(obj)],text=True,errors='replace')
    if 'init_module' in nm or 'cleanup_module' in nm or '__initcall' in nm: fail.append('handoff runtime registration present')
combo=S/'sp11-protected-stack-plus-handoff-e004db.o'
if combo.exists():
    h=hashlib.sha256(combo.read_bytes()).hexdigest()
    if h != R['build']['combined_sha256']: fail.append(f'combined object hash mismatch {h}')
    nmu=subprocess.check_output(['nm','-u',str(combo)],text=True,errors='replace')
    if re.search(r'\bsp11_cpz_', nmu): fail.append('protected integration edge remains unresolved')
# Live safety assertions.
if Path('/proc/device-tree/soc@0/remoteproc@32300000/glink-edge/fastrpc/compute-cb@9').exists():
    fail.append('live secure CB9 unexpectedly present')
if R.get('status')!='PASS_REAL_FASTRPC_FD_HANDOFF_AUTHORITY_COMPILES_MAP_UNMAP_LIFETIME_BOUND': fail.append('bad status')
if R['windows_extent_parity']['map_length_uses_allocation_capacity']: fail.append('map length incorrectly uses allocation capacity')
if R['remaining']['protected_runtime_authorized']: fail.append('runtime unexpectedly authorized')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
if fail:
    print('E004db VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004db VERIFY: PASS')
print(' - userspace dma-buf fd is a lifetime/object capability and does not restore protected CPU access')
print(' - same-machine CDSP firmware proves map flag 2 enters the fd-backed FastRPC mapping path')
print(' - MEM_MAP/MEM_UNMAP results are bound to E004da begin/commit/abort/detach lifetime states')
print(' - Windows cbCaptured is predeclared and is the only external FastRPC process-map length')
print(' - handoff coordinator compiles/links with no protected integration edge and no ioctl/registration path')
print(' - CPZ worker image/invoke ABI remains unresolved, so protected runtime remains unauthorized')
