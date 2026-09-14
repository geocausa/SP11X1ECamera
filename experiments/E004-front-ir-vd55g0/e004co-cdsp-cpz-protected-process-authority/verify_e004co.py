#!/usr/bin/env python3
import json
from pathlib import Path
D=Path(__file__).resolve().parent
R=json.loads((D/'RESULT.json').read_text())
fail=[]
def need(path,*tokens):
    p=D/path
    if not p.exists(): fail.append(f'missing {path}'); return
    t=p.read_text(errors='replace')
    for token in tokens:
        if token not in t: fail.append(f'{path}: missing {token}')
need('ghidra/CDSP-CPZ-FASTRPC.txt','HLOS_PHYSPOOL_CPZ','only one CPZ PD allowed to run!!','fastrpc_invoke_mmap_get_cpz_phys')
need('ghidra/CDSP-CPZ-CALLERS.txt','FUN_f000fb94','FUN_f000fc64')
need('ghidra/DEVICEMFT-CDSP-CONTROLS.txt','remote_session_control(2,&local_1a0,8)','Set to unsigned PD failed')
need('evidence/DOWNSTREAM-FASTRPC-CPZ-HOST-CONTRACT.txt','CPZ_USERPD = 6','FASTRPC_INVOKE2_SESS_INFO','untrusted process')
need('evidence/MEM-BUF-LEND-OWNERSHIP-CONTRACT.txt','LEND','HLOS-excluding ownership transition')
need('evidence/CAMERA-TO-CPZ-MECHANICAL-BRIDGE.txt','mem_buf_lend','CPZ_USERPD','no HLOS CPU owner')
need('evidence/GOLDEN-CPZ-GAP.txt','Golden','CPZ_USERPD','FASTRPC_ATTR_SECUREMAP')
need('README.md','E004cp — CPZ provider port contract','implementation feasibility and upstream/downstream authority')
if R.get('status')!='PASS_CPZ_HOST_IMPORT_AUTHORITY_MECHANICALLY_CONNECTED_GOLDEN_PORT_MISSING': fail.append('bad status')
if R['golden']['runtime_ready']: fail.append('Golden incorrectly marked runtime ready')
if R['camera_bridge']['hlos_in_destination_acl']: fail.append('HLOS incorrectly present')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
if fail:
    print('E004co VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004co VERIFY: PASS')
print(' - exact SP11 CDSP firmware has a real CPZ protected-process/memory class')
print(' - Qualcomm downstream FastRPC exposes privileged CPZ_USERPD + secure context-bank selection')
print(' - Qualcomm mem-buf LEND excludes HLOS from the protected camera owner ACL')
print(' - vendor camera CP_CAMERA+CP_CDSP lending mechanically feeds the CPZ secure-import classification')
print(' - Golden mainline FastRPC lacks the CPZ host binding')
print(' - exact Windows DeviceMFT explicitly requests ordinary unsigned CDSP PD, not CPZ')
print(' - no protected or camera runtime action occurred')
