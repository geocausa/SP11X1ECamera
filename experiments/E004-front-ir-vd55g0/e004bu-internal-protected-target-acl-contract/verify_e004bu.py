#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, sys
E=Path(__file__).resolve().parent
fail=[]
def need(rel,*tokens):
    s=(E/rel).read_text(errors='replace')
    for t in tokens:
        if t not in s: fail.append(f'{rel}: missing {t!r}')
    return s
r=json.loads((E/'RESULT.json').read_text())
if r.get('status')!='PASS_ACL_LIFECYCLE_CONTRACT_COMPILE_ONLY_ZERO_TEXT': fail.append('status')
if not r['build']['text_byte_identical']: fail.append('text diff')
if r['build']['baseline_text_sha256']!=r['build']['scaffold_text_sha256']: fail.append('text hashes')
if r['runtime_actions']!={'module_installed':False,'module_loaded':False,'scm_assign_mem':False,'qcomtee':False,'camera_runtime':False}: fail.append('runtime boundary')
h=need('scaffold/camss-protected-pipeline.h','struct camss_protected_owner_set_contract','camera_hw_visible','trusted_worker_visible','normal_hlos_cpu_visible','concrete_owner_ids_resolved','concrete_permissions_resolved','CAMSS_SECURE_TARGET_BACKING_READY','CAMSS_SECURE_TARGET_ACTIVE_VISIBILITY','CAMSS_SECURE_TARGET_REVOKING_VISIBILITY','prepare_backing','activate_visibility','deactivate_visibility','release_backing')
for bad in ('qcom_scm_assign_mem(', 'QCOM_SCM_VMID_CP_CAMERA', 'QCOM_SCM_VMID_TZ', '0x0d', '0x0D'):
    if bad in h: fail.append('concrete secure authority leaked into contract: '+bad)
b=need('evidence/BUILD-AND-ZERO-RUNTIME.txt','TEXT_BYTE_IDENTICAL=1','baseline_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e','scaffold_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e','FORBIDDEN_IMPLEMENTATION_SYMBOL_MATCHES=0','CALLBACK_INVOCATIONS=0','sp11_entry=7.1.5-sp11-fullio-v19c')
need('evidence/SCAFFOLD-GENERATE.txt','E004bu ACL scaffold generation: PASS','base_video_sha=2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4')
need('README.md','The corrected type boundary now matches the Windows oracle while refusing to guess the Linux owner identity.','E004bv — external protected-sample metadata contract')
if fail:
    print('E004bu VERIFY: FAIL')
    for x in fail: print(' -',x)
    sys.exit(1)
print('E004bu VERIFY: PASS')
print(' - internal target models simultaneous camera-hardware and trusted-worker visibility explicitly')
print(' - activate/deactivate visibility is separate from backing prepare/release')
print(' - no concrete VMID, permission, QTEE UID, SCM implementation, or runtime selector is encoded')
print(' - baseline/scaffold executable .text is byte-identical')
print(' - no protected runtime operation or module load occurred')
