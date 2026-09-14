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
if r.get('status')!='PASS_COMPILE_ONLY_PROTECTED_PROVIDER_CAPABILITY_GATE_ZERO_TEXT': fail.append('status')
if r['runtime_binding_authorized'] or r['concrete_backend_selected']: fail.append('backend selected')
if not r['build']['text_byte_identical'] or r['build']['baseline_text_sha256']!=r['build']['scaffold_text_sha256']: fail.append('text identity')
if r['runtime_actions']!={'module_installed':False,'module_loaded':False,'secure_runtime':False,'ownership_change':False,'protected_heap_register':False,'camera_runtime':False}: fail.append('runtime boundary')
h=need('scaffold/camss-protected-pipeline.h','CAMSS_PROTECTED_CAP_HLOS_ACCESS_REVOKED','CAMSS_PROTECTED_CAP_TRUSTED_OWNER_RESOLVED','CAMSS_PROTECTED_CAP_TRUSTED_WORKER_VISIBLE','CAMSS_PROTECTED_CAP_RELEASE_PATH_RESOLVED','CAMSS_PROTECTED_CAP_NO_HLOS_TRANSFER_FALLBACK','CAMSS_PROTECTED_CAP_EXTERNAL_TARGET_DISTINCT','CAMSS_PROTECTED_PROVIDER_REQUIRED_CAPS','runtime_binding_authorized','external_reuses_internal_target','hlos_transfer_fallback_allowed')
for bad in ('qcom_scm_','QCOM_SCM_VMID','qcomtee','qseecom','arm_ffa','gunyah','pkvm','dma_heap','tee_shm','CP_CAMERA','secure-video-record','service_uid'):
 if bad.lower() in h.lower(): fail.append('concrete backend leaked into contract: '+bad)
b=need('evidence/BUILD-AND-ZERO-RUNTIME.txt','TEXT_BYTE_IDENTICAL=1','baseline_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e','scaffold_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e','FORBIDDEN_CONCRETE_BACKEND_MATCHES=0','CALLBACK_INVOCATIONS=0','sp11_entry=7.1.5-sp11-fullio-v19c')
need('evidence/SCAFFOLD-GENERATE.txt','E004ce provider capability scaffold generation: PASS','base_video_sha=2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4')
need('README.md','A future provider must prove all six capabilities','E004cf — trusted-worker execution contract extraction')
if fail:
 print('E004ce VERIFY: FAIL'); [print(' -',x) for x in fail]; sys.exit(1)
print('E004ce VERIFY: PASS')
print(' - provider readiness requires all six security/authority capabilities')
print(' - unsafe internal-target reuse and HLOS transfer fallback are explicit contract state')
print(' - no concrete backend, VMID, service UID, transport or heap is selected')
print(' - baseline/scaffold executable .text is byte-identical')
print(' - no callback invocation, module load or secure runtime operation occurred')
