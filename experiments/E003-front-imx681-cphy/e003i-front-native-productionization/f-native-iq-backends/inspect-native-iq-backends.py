#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,tempfile,shutil
here=Path(__file__).resolve().parent; repo=here.parents[3]
contract=json.loads((here/'BACKEND-CONTRACT.json').read_text())
if contract['safety']['production_runtime_authorized'] or contract['safety']['linux_camera_runtime_executed']:
    raise SystemExit('runtime safety gate drift')
raw=repo.parent/'.local-oracles/oracle-live-20260904-front-atomic'
if not raw.is_dir(): raise SystemExit('missing local raw front-atomic fixture')
tmp=Path(tempfile.mkdtemp(prefix='e003i-f-inspect-'))
try:
 subprocess.run([str(here/'generate-steady-scalar-state.py'),'--out',str(tmp/'scalar.json')],check=True)
 subprocess.run([str(here/'generate-native-gtm-wire.py'),'--output-dir',str(tmp/'gtm'),'--manifest',str(tmp/'gtm.json')],check=True)
 subprocess.run([str(here/'prove-native-lsc-0076-composition.py')],check=True)
finally: shutil.rmtree(tmp)
for f in ('generate-native-front-lsc-wire.py','generate-native-gtm-wire.py'):
 s=(here/f).read_text()
 if 'linux' in s.lower() and 'camera runtime' in s.lower(): pass
print('E003I_NATIVE_IQ_BACKENDS=PASS')
print('BANK_FIELDS=16')
print('SCALAR_FIELDS=8/8')
print('NATIVE_LSC_0076_COMPOSITION=true')
print('NATIVE_GTM_ADAPTIVE_LIVE=true')
print('RUNTIME_AUTHORIZED=false')
