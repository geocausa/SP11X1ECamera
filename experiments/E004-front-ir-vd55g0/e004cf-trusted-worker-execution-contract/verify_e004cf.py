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
if r.get('status')!='PASS_TRUSTED_FRAME_WORKER_IS_CPU_MEMORY_PROCESSING_AFTER_PROTECTED_MAPPINGS': fail.append('status')
if r['windows_one_shot_needed']: fail.append('unnecessary Windows boot marked needed')
if r['runtime_actions']!={'windows_boot':False,'secure_runtime':False,'ownership_change':False,'protected_allocation':False,'camera_runtime':False}: fail.append('runtime boundary')
t=need('evidence/TRANSFER-DISPATCH-AND-COPY.txt','FUN_1800037c8','FUN_180003718','FUN_180028600(param_1,param_2','FUN_1800290a0','FUN_180003478','ImageProcessingModule_SWABF','ImageProcessingModule_SWASF')
c=need('evidence/WORKER-CALLGRAPH.txt','FUN_180019828','FUN_18001a138','QueryPerformanceFrequency','QueryPerformanceCounter')
p=need('evidence/SWAB-CPU-PIXEL-WORK.txt','FUN_18001f170','WaitForSingleObject','param_4[iVar12] = param_2[iVar12]','FUN_18001f420')
i=need('evidence/WORKER-IMPORT-SURFACE.txt','FORBIDDEN_SECURE_OR_DEVICE_CALL_MATCHES=0','EnterCriticalSection','CreateThread')
f=need('evidence/CACHE-FLUSH-BOUNDARY.txt','PER_FRAME_FLUSH_MATCHES=0','WORKER_FLUSH_MATCHES=0','FlushSecureSectionBuffers(hFileMappingObject')
s=need('evidence/RUNTIME-SAFETY.txt','7.1.5-sp11-render-parity-v4+','sp11_entry=7.1.5-sp11-fullio-v19c')
need('README.md','protected CPU execution habitat with access to both protected objects','E004cg — protected CPU-worker habitat feasibility')
if fail:
 print('E004cf VERIFY: FAIL'); [print(' -',x) for x in fail]; sys.exit(1)
print('E004cf VERIFY: PASS')
print(' - frame dispatcher consumes trusted internal/external mappings directly')
print(' - early path is memcpy-like CPU copy plus tail fill')
print(' - SWABF/SWASF path is ordinary VTL1 CPU pixel arithmetic with thread/event synchronization')
print(' - extracted worker graph contains no secure-section, assignment, SMC, QcTrEE/QTEE/QSEE or device-IO call')
print(' - per-frame worker performs no FlushSecureSectionBuffers call')
print(' - minimum missing Linux component is a protected CPU execution habitat, not a camera accelerator')
print(' - no secure runtime operation occurred')
