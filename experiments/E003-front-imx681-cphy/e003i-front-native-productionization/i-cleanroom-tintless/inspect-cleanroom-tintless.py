#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,sys
here=Path(__file__).resolve().parent
c=json.loads((here/'ACTIVE-PATH.json').read_text())
assert c['schema']=='sp11-e003i-tintless-active-path-v1'
assert all(x in c['cleanroom_substitutions'] for x in ('0xc9e590','0xca1fb0','0xca2310','0xc9ed88','0xc9c868'))
assert all(x not in c['remaining_native_active'] for x in ('0xca1d98','0xca1ed0','0xca1fb0','0xca2310','0xc9ed88','0xc9c868'))
assert c['inactive_on_validated_front_path']['0xca1410']=='stats fusion'
subprocess.run([sys.executable,str(here/'prove-cleanroom-tintless-helper-substitution.py')],check=True)
print('E003I_CLEANROOM_TINTLESS_INSPECT=PASS')
