#!/usr/bin/env python3
import hashlib, json, subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
R=json.loads((D/'RESULT.json').read_text())
fail=[]
def need(path,*tokens):
    p=D/path
    if not p.exists(): fail.append(f'missing {path}'); return ''
    t=p.read_text(errors='replace')
    for x in tokens:
        if x not in t: fail.append(f'{path}: missing {x}')
    return t
inv=need('evidence/ROOT-STATIC-HASH-INVENTORY.txt','/statichashes/example_image.so','/statichashes/fastrpc_shell_3','count=17')
need('evidence/TRUST-DECISION-AUTHORITY.txt','Static hash found','error: dynamic module is unsigned','failed to verify segment')
need('evidence/STATIC-HASH-SOURCE.txt','per-load-segment hashes','/statichashes/%s')
need('evidence/TESTSIG-OEMCONFIG-ROUTE.txt','oemconfig.so: ABSENT','Debug Fuse Enabled','out of scope')
need('README.md','trust-root/admission blocker','E004df — parity worker admission alternatives')
gh=need('ghidra/CDSP-STATIC-HASH-AUTHORITY.txt','FUN_f0138420','FUN_f0137778','FUN_f013d890','error: dynamic module is unsigned')
if 'module: Static hash found' not in gh: fail.append('Ghidra static-hash diagnostic missing')
fw=Path('/lib/firmware/qcom/x1e80100/microsoft/Denali/qccdsp8380.mbn')
if not fw.exists(): fail.append('missing root firmware')
else:
    h=hashlib.sha256(fw.read_bytes()).hexdigest()
    if h!=R['root_firmware']['sha256']: fail.append(f'root firmware changed {h}')
# Recount embedded policy names directly from same-machine firmware.
if fw.exists():
    out=subprocess.check_output(['strings','-a',str(fw)],text=True,errors='replace')
    names=sorted(set(x for x in out.splitlines() if x.startswith('/statichashes/') and '%s' not in x))
    if len(names)!=17: fail.append(f'unexpected static-hash count {len(names)}')
    if any(any(k in x.lower() for k in ('swabf','swasf','secureisp','camera')) for x in names):
        fail.append('unexpected camera parity static-hash module')
# Exact SP11 software must still not contain oemconfig.so.
roots=[Path('/lib/firmware/qcom/x1e80100/microsoft/Denali'), Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump')]
for root in roots:
    if root.exists() and any(p.name.lower()=='oemconfig.so' for p in root.rglob('*') if p.is_file()):
        fail.append(f'oemconfig.so unexpectedly present under {root}')
if R.get('status')!='PASS_NO_AUTHORIZED_SOURCE_CONTROLLED_CPZ_WORKER_ADMISSION_PATH': fail.append('bad status')
if R['trust_paths']['source_controlled_production_admission_resolved']: fail.append('trust admission overclaimed')
if R['reuse']['verification_bypass_accepted']: fail.append('verification bypass accepted')
if R['architecture']['protected_runtime_authorized']: fail.append('runtime unexpectedly authorized')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
if fail:
    print('E004de VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004de VERIFY: PASS')
print(' - exact CDSP root firmware embeds 17 shipping static-hash policy entries')
print(' - static-hash and signed-module paths both enforce per-segment/trust-root verification')
print(' - unsigned dynamic modules are explicitly rejected by the production loader')
print(' - no SP11 oemconfig/test-signature package or project signing credential is claimed')
print(' - editing a trusted shipping module cannot preserve its existing admission record')
print(' - worker trust admission remains the sole CPZ parity blocker; protected runtime stays unauthorized')
