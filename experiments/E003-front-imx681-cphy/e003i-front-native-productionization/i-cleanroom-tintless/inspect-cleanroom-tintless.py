#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,sys
here=Path(__file__).resolve().parent
c=json.loads((here/'ACTIVE-PATH.json').read_text())
assert c['schema']=='sp11-e003i-tintless-active-path-v1'
assert all(x in c['cleanroom_substitutions'] for x in ('0xc9e590','0xca1fb0','0xca2310','0xc9ed88','0xc9c868','0xc9a288','0xc98270','0xc989d0','0xc998b8','0xc99130','0xc9a630','0xc9a9b8','0xc9f568','0xca01b0','0xc95fd0'))
assert c['remaining_native_active']=={}
assert c['active_tintless_native_boundary_closed'] is True
assert c['device_mft_active_tintless_execution_required'] is False
assert c['inactive_on_validated_front_path']['0xca1410']=='stats fusion'
k=here/'solver-kernel-quadrant-33x17-f32le.bin'
assert k.stat().st_size==2244
assert hashlib.sha256(k.read_bytes()).hexdigest()=='51d59c5eda5fdb21dd3185562269f747092c95aa64cf52e82f833f25f6a35a30'
subprocess.run([sys.executable,str(here/'prove-cleanroom-tintless-helper-substitution.py')],check=True)
print('E003I_CLEANROOM_TINTLESS_INSPECT=PASS')
