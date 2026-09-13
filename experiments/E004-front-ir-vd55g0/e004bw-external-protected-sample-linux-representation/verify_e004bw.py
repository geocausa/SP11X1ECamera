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
if r.get('status')!='PASS_EXTERNAL_SAMPLE_REPRESENTATION_COMPILE_ONLY_ZERO_TEXT': fail.append('status')
if not r['build']['text_byte_identical'] or r['build']['baseline_text_sha256']!=r['build']['scaffold_text_sha256']: fail.append('text identity')
if r['runtime_actions']!={'module_installed':False,'module_loaded':False,'linux_secureisp':False,'qtee_qsee':False,'scm_assign_mem':False,'protected_memory_operation':False}: fail.append('runtime boundary')
h=need('scaffold/camss-protected-pipeline.h','struct camss_external_protected_sample','u64 request_id','size_t allocation_extent','size_t captured_extent','size_t serialized_extent','size_t payload_offset','CAMSS_EXTERNAL_SAMPLE_IDENTITY_BOUND','CAMSS_EXTERNAL_SAMPLE_TRUSTED_VISIBLE','CAMSS_EXTERNAL_SAMPLE_PAYLOAD_READY','bind_identity','activate_trusted_visibility','deactivate_trusted_visibility','release_identity','identity_proven','trusted_worker_visible','normal_hlos_cpu_visible')
ext=h.split('struct camss_external_protected_sample {',1)[1].split('};',1)[0]
for bad in ('dma_addr_t','phys_addr_t','ownership_phys','camss_iova'):
    if bad in ext: fail.append('external sample illegally carries internal target field: '+bad)
for bad in ('qcom_scm_', 'QCOM_SCM_VMID', 'qcomtee_', 'qseecom', 'dma_heap', 'tee_shm', 'OpenSecureSection(', 'CreateSecureSection('):
    if bad in h: fail.append('provider/backend leaked into contract: '+bad)
b=need('evidence/BUILD-AND-ZERO-RUNTIME.txt','TEXT_BYTE_IDENTICAL=1','baseline_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e','scaffold_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e','FORBIDDEN_IMPLEMENTATION_SYMBOL_MATCHES=0','CALLBACK_INVOCATIONS=0','sp11_entry=7.1.5-sp11-fullio-v19c')
need('evidence/SCAFFOLD-GENERATE.txt','E004bw external-sample scaffold generation: PASS','base_video_sha=2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4')
need('evidence/WINDOWS-ORACLE-FIELD-MAP.txt','IOConfig +0x128 <- cbBufferSize','IOConfig +0x12c <- cbCaptured','object +0x98 = running serialized external payload offset/length','object +0x9c = old(+0x98) + 8 = frame pixel-data offset','PROCESS_DMFT_SURFACE 0x60 record is NOT the external secure GUID/size contract')
need('README.md','The new fields describe **what must be represented**, not **how Linux obtains it**.','E004bx — external protected-sample provider authority')
if fail:
    print('E004bw VERIFY: FAIL')
    for x in fail: print(' -',x)
    sys.exit(1)
print('E004bw VERIFY: PASS')
print(' - external protected sample preserves opaque identity and request association')
print(' - allocation extent and captured extent are independent fields')
print(' - serialized extent and trusted pixel payload offset are independent fields')
print(' - external sample carries no CAMSS IOVA or physical ownership range')
print(' - no allocator, heap, SCM, QTEE/QSEE or secure-section backend is selected')
print(' - baseline/scaffold executable .text is byte-identical')
print(' - no protected runtime operation or module load occurred')
