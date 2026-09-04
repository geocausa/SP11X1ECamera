#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,sys
here=Path(__file__).resolve().parent
c=json.loads((here/'ACTIVE-PATH.json').read_text())
assert c['schema']=='sp11-e003i-cleanroom-gtm-v1' and c['accepted'] is True
assert set(c['cleanroom_substitutions'])=={'0x9a4f38','0x9a55c8','0x9aa3a8'}
assert c['clean_generator']['device_mft_required'] is False
assert c['clean_generator']['unicorn_required'] is False
b=(here/'mode2-domain-257-f32le.bin').read_bytes()
assert len(b)==1028 and hashlib.sha256(b).hexdigest()=='b33525b102690e0894d55245a0af56e655f10615fe6b144cbfca2cb9e5836325'
gen=(here/'generate-cleanroom-gtm-wire.py').read_text()
assert 'QcDeviceMFT' not in gen and 'import unicorn' not in gen.lower() and 'SurfaceEmu' not in gen
for name in ('prove-mode2-cubic-map.py','prove-tmc-domain-map.py','prove-final-adaptive-map.py','generate-cleanroom-gtm-wire.py'):
 subprocess.run([sys.executable,str(here/name)],check=True)
print('E003I_CLEANROOM_GTM_INSPECT=PASS')
