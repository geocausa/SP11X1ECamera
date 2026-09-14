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
need('scaffold/hamoa-secure-cb9-candidate.dtsi','compute-cb@9','reg = <9>','0x0c09 0x20','pd-type = <6>','status = "disabled"')
need('evidence/OFFLINE-TOPOLOGY-PROOF.txt','canonical_compile_stderr_bytes=0','overlay_compile_stderr_bytes=0','offline_overlay_stderr_bytes=0','iommus=3d c09 20','pd-type=6','ABSENT_EXPECTED')
need('README.md','status = "disabled"','E004cz — integrated Golden protected-provider build closure')
# Decode committed compile harness as a second mechanical check.
dtb=D/'scaffold/compile-harness.dtb'
node='/soc/remoteproc@32300000/glink-edge/fastrpc/compute-cb@9'
if not dtb.exists(): fail.append('missing harness dtb')
else:
    def get(t, prop):
        return subprocess.check_output(['fdtget','-t',t,str(dtb),node,prop], text=True).strip()
    if get('x','reg')!='9': fail.append('bad reg')
    if get('x','iommus').split()[-2:]!=['c09','20']: fail.append('bad iommu tuple')
    if get('u','pd-type')!='6': fail.append('bad pd type')
    if get('s','status')!='disabled': fail.append('candidate not disabled')
if R.get('status')!='PASS_DISABLED_X1E_SECURE_CB9_TOPOLOGY_COMPILES_AND_OFFLINE_MERGES': fail.append('bad status')
if R['candidate']['status']!='disabled': fail.append('result candidate enabled')
if R['offline_merge']['live_node_present_after_test']: fail.append('live CB9 unexpectedly present')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
if fail:
    print('E004cy VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004cy VERIFY: PASS')
print(' - exact recovered X1E CB9 stream tuple compiles in canonical symbolic form')
print(' - downstream CPZ_USERPD type 6 is encoded only in the disabled candidate')
print(' - offline overlay merges cleanly into the exact current SP11 topology')
print(' - live compute-cb@9 remains absent and no context bank was probed')
print(' - no FastRPC/protected-memory/camera/SecureISP runtime action occurred')
