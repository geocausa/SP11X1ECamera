#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
D=Path(__file__).resolve().parent;BASE=D.parent
EN=BASE/'en-r5-r9-producer-integration';EM=BASE/'em-r7-r9-template-free-composer';EL=BASE/'el-calibrated-awb-scalar-join'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in (EN/'RESULT.json',EM/'RESULT.json',EL/'RESULT.json'):
 o=json.loads(p.read_text());assert str(o['status']).startswith('PASS'),p
assert 'generation > 6U' in (EN/'gain-feed.c').read_text()
parent=(EN/'e003i-en-six-frame-native-aec.c').read_text();assert 'if (target <= 6U)' in parent and 'if (target >= 2U && target <= 4U)' in parent
assert '$EN/build-helper.sh' in (D/'build-helper.sh').read_text()
inv=(D/'invoke-once.sh').read_text();assert '$EN/live-iq-producer.py' in inv and 'e003i-eo-six-frame-native-aec' in inv
gr=(D/'99zn_sp11_camera_e003i_eo_r5_r9').read_text();assert 'sp11-camera-e003i-eo-r5-r9-one-shot' in gr and 'sp11_camera_e003i_eo_r5_r9=1' in gr
with tempfile.TemporaryDirectory(prefix='e003i-eo-') as td:
 td=Path(td);subprocess.run([str(D/'build-helper.sh'),str(td/'helper')],check=True);subprocess.run([str(D/'build-bootstrap.sh'),str(td/'bootstrap')],check=True)
print('EO_EN_OFFLINE_AUTHORITY=PASS');print('EO_HELPER_WERROR=PASS');print('EO_BOOTSTRAP_WERROR=PASS');print('EO_VERIFY=PASS')
