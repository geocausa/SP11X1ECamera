#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
D=Path(__file__).resolve().parent;BASE=D.parent
EN=BASE/'en-r5-r9-producer-integration';EM=BASE/'em-r7-r9-template-free-composer';EL=BASE/'el-calibrated-awb-scalar-join';EP=BASE/'ep-gainadj-multiside-r9-replay'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in (EN/'RESULT.json',EM/'RESULT.json',EL/'RESULT.json',EP/'RESULT.json'):
 o=json.loads(p.read_text());assert str(o['status']).startswith('PASS'),p
assert 'generation > 6U' in (EN/'gain-feed.c').read_text()
parent=(EN/'e003i-en-six-frame-native-aec.c').read_text();assert 'if (target <= 6U)' in parent and 'if (target >= 2U && target <= 4U)' in parent
ep=json.loads((EP/'RESULT.json').read_text());assert ep['status']=='PASS_EO_R9_SELECTOR_CLOSURE' and ep['external_archive_full_replay'] is True and ep['corrected_r9_capsule_sha256']=='209961646647ec9a2747a553c10139f1cd303dc3a5b6cf302deca6636f173191'
assert '$EN/build-helper.sh' in (D/'build-helper.sh').read_text()
inv=(D/'invoke-once.sh').read_text();assert '$EN/live-iq-producer.py' in inv and 'e003i-eq-six-frame-native-aec' in inv
gr=(D/'99zo_sp11_camera_e003i_eq_r5_r9').read_text();assert 'sp11-camera-e003i-eq-r5-r9-one-shot' in gr and 'sp11_camera_e003i_eq_r5_r9=1' in gr
with tempfile.TemporaryDirectory(prefix='e003i-eq-') as td:
 td=Path(td);subprocess.run([str(D/'build-helper.sh'),str(td/'helper')],check=True);subprocess.run([str(D/'build-bootstrap.sh'),str(td/'bootstrap')],check=True)
print('EQ_EN_OFFLINE_AUTHORITY=PASS');print('EQ_HELPER_WERROR=PASS');print('EQ_BOOTSTRAP_WERROR=PASS');print('EQ_VERIFY=PASS')
