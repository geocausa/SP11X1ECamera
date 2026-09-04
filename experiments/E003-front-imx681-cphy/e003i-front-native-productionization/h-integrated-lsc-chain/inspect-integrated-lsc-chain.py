#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile,shutil
HERE=Path(__file__).resolve().parent
src=(HERE/'generate-integrated-front-lsc-wire.py').read_text()
for forbidden in ("req{req}_input_mesh.bin","req{req}_output_mesh_pre.bin","atomic-req{req}-lsc-staging.bin","pack_live_staging"):
 if forbidden in src:raise SystemExit('forbidden captured-input reference: '+forbidden)
tmp=Path(tempfile.mkdtemp(prefix='e003i-h-inspect-'))
try:
 subprocess.run([str(HERE/'generate-integrated-front-lsc-wire.py'),'--output-dir',str(tmp/'wire'),'--manifest',str(tmp/'chain.json')],check=True)
 subprocess.run([str(HERE/'prove-integrated-lsc-0076-composition.py')],check=True)
finally:shutil.rmtree(tmp)
print('E003I_INTEGRATED_LSC_CHAIN=PASS')
print('CLEANROOM_PRETINTLESS=true')
print('CAPTURED_PRETINTLESS_INPUT=false')
print('CAPTURED_OUTPUT_PRE_INPUT=false')
print('CAPTURED_LSC_STAGING_INPUT=false')
print('DEVICE_MFT_ROLE=Tintless-only')
print('RUNTIME_AUTHORIZED=false')
