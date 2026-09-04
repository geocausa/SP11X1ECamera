#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile,shutil,json
HERE=Path(__file__).resolve().parent
tmp=Path(tempfile.mkdtemp(prefix='e003i-g-'))
try:
 m=tmp/'manifest.json'; subprocess.run([str(HERE/'prove-cleanroom-front-pretintless.py'),'--output-dir',str(tmp/'out'),'--manifest',str(m)],check=True,stdout=subprocess.DEVNULL)
 j=json.loads(m.read_text())
 if j['status']!='PASS' or j['native_code_dependency'] or j['device_mft_dependency'] or j['captured_pretintless_mesh_input']: raise SystemExit('clean-room contract drift')
 for r in ('4','5','6'):
  if not j['requests'][r]['byte_exact']: raise SystemExit('request parity drift')
 s=(HERE/'cleanroom-front-lsc.py').read_text()+(HERE/'prove-cleanroom-front-pretintless.py').read_text()
 for bad in ('Unicorn','QcDeviceMFT8380.dll','0x9b6048','SurfaceEmu'):
  if bad in s: raise SystemExit('native dependency leaked into clean-room source: '+bad)
 print('E003I_CLEANROOM_PRETINTLESS=PASS')
 print('R4_R5_R6_BYTE_EXACT=true')
 print('DEVICE_MFT_DEPENDENCY=false')
 print('RUNTIME_AUTHORIZED=false')
finally: shutil.rmtree(tmp)
