#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, hashlib, tempfile, shutil
here=Path(__file__).resolve().parent
contract=json.loads((here/'STATE-CONTRACT.json').read_text())
if contract['capsule']['capsule_template_is_input']:
    raise SystemExit('capsule template policy drift')
if contract['section_partition']['invariant_count'] != 31 or contract['section_partition']['request_generated_count'] != 5:
    raise SystemExit('section partition drift')
builder=(here/'build-template-free-0076-capsules.py').read_text()
for bad in ('E003H_PIX_ORACLE_CAPSULE','atomic-runtime-capsules','read_bytes() # capsule'):
    if bad in builder: raise SystemExit('full capsule source dependency: '+bad)
expected={4:'1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa',5:'8e447a662a47e47db7dd211d6a109d590531309f944e52b729a4351b5a00da11',6:'c88e7a75f228fac7b69a4a122fd618aa054bdbf98e83ff541be9c20177844583'}
tmp=Path(tempfile.mkdtemp(prefix='e003i-e-'))
try:
    subprocess.run([str(here/'build-template-free-0076-capsules.py'),'--output-dir',str(tmp/'caps'),'--manifest',str(tmp/'manifest.json')],check=True)
    for r,want in expected.items():
        p=tmp/'caps'/f'E003I_TEMPLATE_FREE_R{r}.bin'
        got=hashlib.sha256(p.read_bytes()).hexdigest()
        if p.stat().st_size != 41088 or got != want: raise SystemExit(f'R{r} identity mismatch')
finally:
    shutil.rmtree(tmp)
if contract['safety']['production_runtime_authorized'] or contract['safety']['linux_camera_runtime_executed']:
    raise SystemExit('runtime gate drift')
print('E003I_TEMPLATE_FREE_COMPOSER=PASS')
print('R4_R5_R6_BYTE_EXACT_0076=true')
print('CAPSULE_TEMPLATE_READS=0')
print('RUNTIME_AUTHORIZED=false')
