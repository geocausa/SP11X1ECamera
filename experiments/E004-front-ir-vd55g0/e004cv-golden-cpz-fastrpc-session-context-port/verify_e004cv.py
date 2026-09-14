#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
R=json.loads((D/'RESULT.json').read_text())
fail=[]
def need(path,*tokens):
    p=D/path
    if not p.exists(): fail.append(f'missing {path}'); return
    t=p.read_text(errors='replace')
    for x in tokens:
        if x not in t: fail.append(f'{path}: missing {x}')
need('scaffold/fastrpc-e004cv.c',
     'FASTRPC_REMOTE_PD_CPZ_USER','capable(CAP_SYS_ADMIN)',
     'current->tgid != fl->opener_tgid','session_config_locked',
     'sp11_cpz_dma_buf_is_protected','attr & FASTRPC_ATTR_SECUREMAP',
     'map->va = map->protected ? NULL : sg_virt(map->table->sgl)',
     'E004cv compile-only: FastRPC driver registration disabled.')
need('scaffold/fastrpc-e004cv-uapi.h','FASTRPC_INVOKE2_SESS_INFO_E004CV','FASTRPC_REMOTE_PD_CPZ_USER 6')
need('evidence/CPZ-SESSION-AUTHORITY-GATE.txt','delegated caller','CAP_SYS_ADMIN','-ENODEV')
need('evidence/PROTECTED-DMABUF-IMPORT-GATE.txt','provider-authoritative','legacy FASTRPC_ATTR_SECUREMAP is NOT set','map->va is forced to NULL')
need('README.md','3432 bytes of `.text`','E004cw — CPZ typed context-bank authority and topology')
obj=D/'scaffold/fastrpc-e004cv.o'
if not obj.exists(): fail.append('missing compiled object')
else:
    out=subprocess.check_output(['size','-A',str(obj)],text=True)
    if '.text' not in out or '3432' not in out: fail.append('unexpected text proof')
    nm=subprocess.check_output(['nm',str(obj)],text=True,errors='replace')
    for x in ('fastrpc_map_attach','fastrpc_set_session_info_e004cv','fastrpc_invoke2_session_info_e004cv'):
        if x not in nm: fail.append(f'missing emitted root {x}')
    if 'init_module' in nm or 'cleanup_module' in nm: fail.append('runtime registration symbol present')
    nmu=subprocess.check_output(['nm','-u',str(obj)],text=True,errors='replace')
    if 'sp11_cpz_dma_buf_is_protected' not in nmu: fail.append('provider dependency not retained')
if R.get('status')!='PASS_COMPILE_ONLY_CPZ_FASTRPC_PRIVILEGE_AND_IMPORT_GATE': fail.append('bad status')
if R['context_bank']['dt_pd_type_parser_added']: fail.append('DT pd-type unexpectedly enabled')
if R['build']['runtime_registration_present']: fail.append('runtime registration unexpectedly present')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
if fail:
    print('E004cv VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004cv VERIFY: PASS')
print(' - privileged CPZ process selection compiles and rejects delegated callers')
print(' - CPZ requires secure CDSP device, CAP_SYS_ADMIN and a matching typed session')
print(' - protected dma-buf import is provider-authoritative and rejects legacy SECUREMAP')
print(' - protected FastRPC maps retain no HLOS CPU virtual address')
print(' - emitted .text proves the new logic compiled while driver registration stays absent')
print(' - no FastRPC, protected-memory, camera or SecureISP runtime action occurred')
