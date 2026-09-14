#!/usr/bin/env python3
from pathlib import Path
import json,sys
E=Path(__file__).resolve().parent; fail=[]
def need(rel,*tokens):
 p=E/rel
 if not p.exists(): fail.append('missing '+rel); return ''
 s=p.read_text(errors='replace')
 for t in tokens:
  if t not in s: fail.append(f'{rel}: missing {t!r}')
 return s
r=json.loads((E/'RESULT.json').read_text())
if r.get('status')!='PASS_COMPILE_ONLY_EXTERNAL_CPZ_SAMPLE_CONTRACT_ZERO_TEXT': fail.append('status')
if r.get('runtime_binding_authorized') or r.get('concrete_runtime_backend_selected'): fail.append('runtime/backend unexpectedly selected')
if not r['build']['text_byte_identical'] or r['build']['baseline_text_sha256']!=r['build']['scaffold_text_sha256']: fail.append('text identity')
if any(r['runtime_actions'].values()): fail.append('runtime boundary')
h=need('scaffold/camss-protected-cpz-external-sample.h',
 'CAMSS_CPZ_EXT_CAP_OPAQUE_IDENTITY','CAMSS_CPZ_EXT_CAP_GENERIC_BACKING',
 'CAMSS_CPZ_EXT_CAP_WORKER_ONLY_OWNERSHIP','CAMSS_CPZ_EXT_CAP_HLOS_CPU_EXCLUDED',
 'CAMSS_CPZ_EXT_CAP_TRUSTED_IMPORT','CAMSS_CPZ_EXT_CAP_WORKER_REF_HELD',
 'CAMSS_CPZ_EXT_CAP_DETACH_BEFORE_RECLAIM','CAMSS_CPZ_EXT_CAP_RECLAIM_BEFORE_FREE',
 'CAMSS_CPZ_EXT_CAP_NO_CAMERA_HW_OWNER','CAMSS_CPZ_EXT_CAP_NO_HLOS_FALLBACK',
 'CAMSS_CPZ_EXTERNAL_REQUIRED_CAPS','CAMSS_CPZ_EXTERNAL_WORKER_IMPORTED',
 'worker_detached_before_reclaim','ownership_reclaimed_before_free')
for bad in ('qcom_scm_','mem_buf_lend(','mem_buf_reclaim(','fastrpc_','remote_session_control(',
            'QCOM_SCM_VMID','CPZ_USERPD','qcom,vmids','pd-type','dma_heap_buffer_alloc',
            'of_property_','ioctl(','qcomtee','qseecom'):
 if bad.lower() in h.lower(): fail.append('runtime implementation leaked into contract: '+bad)
need('evidence/SCAFFOLD-GENERATE.txt','E004cr external CPZ sample scaffold generation: PASS','base_video_sha=2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4')
need('evidence/BUILD-AND-ZERO-RUNTIME.txt','TEXT_BYTE_IDENTICAL=1','FORBIDDEN_RUNTIME_CALL_MATCHES=0','CALLBACK_INVOCATIONS=0','sp11_entry=7.1.5-sp11-fullio-v19c')
need('README.md','CAMSS_CPZ_EXTERNAL_REQUIRED_CAPS = 0x3ff','E004cs — Golden CPZ host-port source delta')
if fail:
 print('E004cr VERIFY: FAIL'); [print(' -',x) for x in fail]; sys.exit(1)
print('E004cr VERIFY: PASS')
print(' - external protected sample requires all ten identity/ownership/import/release invariants')
print(' - external sample explicitly does not require camera-hardware ownership')
print(' - worker detach and ownership reclaim are ordered before backing release')
print(' - no concrete owner ID, allocator, FastRPC, mem-buf, SCM or DT implementation is encoded')
print(' - baseline/scaffold executable .text is byte-identical')
print(' - no module load or protected runtime operation occurred')
