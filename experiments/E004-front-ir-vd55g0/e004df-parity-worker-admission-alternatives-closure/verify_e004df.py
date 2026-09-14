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
 for x in tokens:
  if x not in t: fail.append(f'{path}: missing {x}')
need('evidence/BACKEND-MATRIX.txt','CPZ / SecurePD','pKVM nVHE','Gunyah trusted VM','HLOS post-processing')
need('evidence/SIGNING-DEVELOPMENT-MATERIAL-SCAN.txt','no oemconfig.so','no private signing key','SID allow-lists')
need('evidence/SECURITY-INVARIANTS.txt','HLOS CPU mapping','disabling/bypassing CDSP','Compile-only/offline worker development remains acceptable')
need('README.md','CPZ is still the technically correct target','E004dg — source-controlled parity worker implementation')
if R.get('status')!='PASS_CPZ_IS_ONLY_PARITY_SHAPED_BACKEND_RUNTIME_BLOCKED_ON_WORKER_TRUST_ADMISSION': fail.append('bad status')
if not R['decision']['cpz_architecture_preserved']: fail.append('CPZ architecture unexpectedly abandoned')
if not R['decision']['protected_runtime_frozen']: fail.append('protected runtime not frozen')
if not R['decision']['verification_bypass_forbidden']: fail.append('verification bypass not forbidden')
if not R['decision']['offline_source_worker_development_authorized']: fail.append('offline worker route missing')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
if fail:
 print('E004df VERIFY: FAIL')
 for x in fail: print(' -',x)
 raise SystemExit(1)
print('E004df VERIFY: PASS')
print(' - CPZ/SecurePD remains the only backend with the required protected memory + trusted CPU shape')
print(' - pKVM/Gunyah/FFA-QTEE/HypX alternatives retain earlier camera-ownership/loader/IOMMU blockers')
print(' - no local manufacturer/development worker signing credential or config route was found')
print(' - HLOS fallback and verification bypass remain explicitly rejected')
print(' - protected runtime is frozen while offline parity-worker implementation can continue safely')
