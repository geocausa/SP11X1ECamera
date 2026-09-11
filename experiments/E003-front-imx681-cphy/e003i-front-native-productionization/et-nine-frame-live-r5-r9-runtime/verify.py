#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,tempfile
D=Path(__file__).resolve().parent;BASE=D.parent
ES=BASE/'es-nine-frame-r7-r9-transport';EN=BASE/'en-r5-r9-producer-integration';EP=BASE/'ep-gainadj-multiside-r9-replay';CW=BASE/'cw-imx681-atomic-dynamic-control-cluster'
def need(v,m):
 if not v: raise AssertionError(m)
es=json.loads((ES/'RESULT.json').read_text());need(es['status']=='PASS_OFFLINE_NINE_FRAME_TRANSPORT' and es['frames']==9,'ES')
need(es['patched_camss_sha256']=='683255664a320bf63b1c852c56a8c0373014d6723b6d48a69a277bd02d18706f','ES CAMSS SHA')
need(es['patched_helper_sha256']=='6d4268fb5e6c637de78f62079719eaa3c107efcca48578c125a58a17d74c565d','ES helper SHA')
for p in (EN/'RESULT.json',EP/'RESULT.json'):
 o=json.loads(p.read_text());need(str(o['status']).startswith('PASS'),str(p))
ep=json.loads((EP/'RESULT.json').read_text());need(ep['external_archive_full_replay'] is True,'EP replay')
for f,toks in {
 'build-camss.sh':['make-nine-frame-camss.py','W=1','683255664a320bf63b1c852c56a8c0373014d6723b6d48a69a277bd02d18706f'],
 'build-helper.sh':['make-nine-frame-helper.py','-Werror','6d4268fb5e6c637de78f62079719eaa3c107efcca48578c125a58a17d74c565d'],
 'invoke-once.sh':['e003i-et-nine-frame-native-aec','QC10C-8.bin','$EN/live-iq-producer.py'],
 'runtime-preflight.sh':['sp11_camera_e003i_et_nine_frame_r5_r9=1','prior_runtime_output'],
 '99zq_sp11_camera_e003i_et_nine_frame_r5_r9':['sp11-camera-e003i-et-nine-frame-r5-r9-one-shot','sp11_camera_e003i_et_nine_frame_r5_r9=1'],
}.items():
 s=(D/f).read_text()
 for t in toks: need(t in s,f'{f}: {t}')
with tempfile.TemporaryDirectory(prefix='e003i-et-') as td:
 td=Path(td);subprocess.run([str(D/'build-camss.sh'),str(td/'qcom-camss.ko')],check=True);subprocess.run([str(D/'build-helper.sh'),str(td/'helper')],check=True);subprocess.run([str(D/'build-bootstrap.sh'),str(td/'bootstrap')],check=True)
print('ET_ES_TRANSPORT=PASS');print('ET_EP_IQ=PASS');print('ET_CAMSS_W1=PASS');print('ET_HELPER_WERROR=PASS');print('ET_BOOTSTRAP_WERROR=PASS');print('ET_VERIFY=PASS')
