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
if r.get('status')!='PASS_COMPILE_ONLY_CPZ_PROVIDER_PORT_CONTRACT_ZERO_TEXT': fail.append('status')
if r.get('runtime_binding_authorized') or r.get('concrete_runtime_backend_selected'): fail.append('backend unexpectedly selected')
if r.get('external_sample_provider_resolved'): fail.append('external sample incorrectly resolved')
if not r['build']['text_byte_identical'] or r['build']['baseline_text_sha256']!=r['build']['scaffold_text_sha256']: fail.append('text identity')
if any(r['runtime_actions'].values()): fail.append('runtime boundary')
h=need('scaffold/camss-protected-cpz-provider.h',
 'CAMSS_CPZ_CAP_CAMERA_CDSP_COOWNED_TARGET','CAMSS_CPZ_CAP_HLOS_EXCLUDED_TARGET',
 'CAMSS_CPZ_CAP_PRIVILEGED_PROCESS_TYPE','CAMSS_CPZ_CAP_SECURE_CONTEXT_IMPORT',
 'CAMSS_CPZ_CAP_EXTERNAL_SAMPLE_IMPORT','CAMSS_CPZ_CAP_RECLAIM_ORDER_RESOLVED',
 'CAMSS_CPZ_CAP_NO_HLOS_FALLBACK','CAMSS_CPZ_PROVIDER_REQUIRED_CAPS',
 'runtime_binding_authorized','external_sample_provider_resolved',
 'ownership_reclaim_before_backing_release','hlos_transfer_fallback_allowed')
for bad in ('qcom_scm_','mem_buf_lend(','mem_buf_reclaim(','fastrpc_','remote_session_control(',
            'QCOM_SCM_VMID','CPZ_USERPD','qcom,vmids','pd-type','dma_heap_buffer_alloc',
            'of_property_','ioctl(','qcomtee','qseecom'):
 if bad.lower() in h.lower(): fail.append('runtime implementation leaked into contract: '+bad)
need('evidence/SCAFFOLD-GENERATE.txt','E004cp CPZ provider scaffold generation: PASS','base_video_sha=2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4')
need('evidence/BUILD-AND-ZERO-RUNTIME.txt',
 'TEXT_BYTE_IDENTICAL=1',
 'baseline_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e',
 'scaffold_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e',
 'FORBIDDEN_RUNTIME_CALL_MATCHES=0','CALLBACK_INVOCATIONS=0','sp11_entry=7.1.5-sp11-fullio-v19c')
need('README.md','All seven form `CAMSS_CPZ_PROVIDER_REQUIRED_CAPS = 0x7f`','E004cq — external protected-sample CPZ visibility authority')
if fail:
 print('E004cp VERIFY: FAIL'); [print(' -',x) for x in fail]; sys.exit(1)
print('E004cp VERIFY: PASS')
print(' - CPZ provider readiness requires all seven ownership/process/import/release capabilities')
print(' - the separate external protected sample remains an explicit unresolved gate')
print(' - no concrete VMID, process-type value, FastRPC, mem-buf or SCM call is encoded')
print(' - baseline/scaffold executable .text is byte-identical')
print(' - no callback invocation, module load or protected runtime operation occurred')
