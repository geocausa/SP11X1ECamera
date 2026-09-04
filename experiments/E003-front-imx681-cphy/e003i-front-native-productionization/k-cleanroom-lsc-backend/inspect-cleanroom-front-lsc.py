#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,sys,tempfile,shutil
here=Path(__file__).resolve().parent
c=json.loads((here/'BACKEND-CONTRACT.json').read_text())
assert c['schema']=='sp11-e003i-cleanroom-front-lsc-backend-v1' and c['accepted'] is True
assert c['device_mft_required'] is False and c['unicorn_required'] is False
assert c['validation']['wrapper_carry_exact'] and c['validation']['core_carry_exact'] and c['validation']['output_abi_exact']
s=(here/'generate-cleanroom-front-lsc-wire.py').read_text()
for bad in ('import unicorn','SurfaceEmu','QcDeviceMFT8380.dll','device-mft'):
    assert bad not in s
assert 'captured pre-Tintless mesh' in c['inputs']['not_inputs']
tmp=Path(tempfile.mkdtemp(prefix='e003i-k-'))
try:
    mp=tmp/'manifest.json'
    subprocess.run([sys.executable,str(here/'generate-cleanroom-front-lsc-wire.py'),'--output-dir',str(tmp/'out'),'--manifest',str(mp)],check=True)
    m=json.loads(mp.read_text())
    assert m['accepted'] and m['device_mft_required'] is False and m['unicorn_required'] is False
    assert m['captured_pretintless_mesh_input'] is False and m['captured_output_mesh_pre_input'] is False and m['captured_lsc_staging_input'] is False
    for r in ('4','5','6'):
        assert m['requests'][r]['lsc0_sha256']==c['validation']['wire_sha256'][r]['lsc0']
        assert m['requests'][r]['lsc1_sha256']==c['validation']['wire_sha256'][r]['lsc1']
        assert m['requests'][r]['gic_sha256']==c['validation']['wire_sha256'][r]['gic']
    print('E003I_CLEANROOM_FRONT_LSC_INSPECT=PASS')
finally:
    shutil.rmtree(tmp)
