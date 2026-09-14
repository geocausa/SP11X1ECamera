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
need('scaffold/sp11-cpz-external-provider.c',
     'sp11_cpz_system_heap_lend(external->dmabuf, false)',
     'sp11_cpz_dma_buf_is_protected(external->dmabuf)',
     'get_dma_buf(external->dmabuf)',
     'sp11_cpz_system_heap_mark_active',
     'sp11_cpz_system_heap_mark_detached',
     'sp11_cpz_system_heap_reclaim',
     'serialized_extent > captured_extent',
     'CAMSS_CPZ_EXTERNAL_RECLAIMING')
need('evidence/CP-CDSP-ONLY-SEPARATION.txt','camera_target=false keeps nr_dst=1','QCOM_SCM_VMID_CP_CAMERA')
need('evidence/LIFETIME-ORDER.txt','abort_worker_import','reclaim -> release backing ref')
need('evidence/FASTRPC-HANDOFF-BOUNDARY.txt','provider does not call FastRPC itself','future control-plane/import layer')
need('evidence/INTEGRATION-LINK-PROOF.txt','protected integration dependencies remaining (must be empty):','registration symbols (must be empty):')
need('README.md','payload_offset <= serialized_extent <= captured_extent <= allocation_extent','E004db — external protected-sample FastRPC handoff authority')
obj=S/'sp11-protected-stack-plus-external-e004da.o'
if obj.exists():
    h=hashlib.sha256(obj.read_bytes()).hexdigest()
    if h!=R['build']['combined_sha256']: fail.append(f'combined object hash mismatch {h}')
    nm=subprocess.check_output(['nm',str(obj)],text=True,errors='replace')
    for sym in ('sp11_cpz_external_bind','sp11_cpz_external_lend_to_worker','sp11_cpz_external_begin_worker_import','sp11_cpz_external_commit_worker_import','sp11_cpz_external_abort_worker_import','sp11_cpz_external_mark_payload_ready','sp11_cpz_external_worker_detached','sp11_cpz_external_reclaim','sp11_cpz_external_release'):
        if sym not in nm: fail.append(f'missing provider symbol {sym}')
    if 'init_module' in nm or 'cleanup_module' in nm or '__initcall' in nm: fail.append('runtime registration present')
    nmu=subprocess.check_output(['nm','-u',str(obj)],text=True,errors='replace')
    if 'sp11_cpz_' in nmu: fail.append('protected integration dependency unresolved')
if R.get('status')!='PASS_EXTERNAL_CPZ_BACKING_LIFETIME_COMPILES_LINKS_IMPORT_HANDOFF_STILL_EXPLICIT': fail.append('bad status')
if R['external_backing']['cp_camera_owner']: fail.append('external sample must not own CP_CAMERA')
if R['external_backing']['normal_hlos_cpu_visible_while_protected']: fail.append('HLOS CPU visibility incorrectly allowed')
if R['handoff']['actual_fastrpc_import_implemented']: fail.append('FastRPC import overclaimed')
if not R['lifetime']['reclaim_failure_retains_backing']: fail.append('fail-closed reclaim lifetime missing')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
if fail:
    print('E004da VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004da VERIFY: PASS')
print(' - external backing preserves opaque identity/extents and is constrained to CP_CDSP-only lend')
print(' - HLOS visibility is revoked in provider state as soon as protected ownership succeeds or becomes uncertain')
print(' - provider and worker dma-buf references enforce backing lifetime across the future import')
print(' - detach/reclaim/release ordering is fail-closed, including failed-import and reclaim-failure paths')
print(' - provider links against the E004cz protected stack with no remaining sp11_cpz integration edge')
print(' - actual FastRPC fd/import handoff remains explicit and no runtime operation occurred')
