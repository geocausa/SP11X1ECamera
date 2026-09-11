#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
D=Path(__file__).resolve().parent;B=D.parent
EN=B/'en-r5-r9-live-producer-integration';EM=B/'em-post-r6-template-free-composer';EL=B/'el-calibrated-awb-scalar-join';EJ=B/'ej-clean-awb-cal-factor-replay';EK=B/'ek-linux-front-awb-otp-read-gate'
def need(x,m):
    if not x: raise AssertionError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for p,status in [(EN/'RESULT.json','PASS_OFFLINE_R5_R9_INTEGRATION'),(EM/'RESULT.json','PASS_OFFLINE_R7_R9_COMPOSITION'),(EL/'RESULT.json','PASS_OFFLINE_JOIN'),(EJ/'RESULT.json','PASS_10_OF_10_BIT_EXACT')]:
    o=json.loads(p.read_text());need(o.get('status')==status,f'{p} status')
ek=json.loads((EK/'RESULT.json').read_text());need(ek.get('status')=='PASS_LIVE_LINUX_PHYSICAL_OTP' and ek.get('live_read_proven') is True,'EK live authority')
# Candidate helper sources are intentionally EN-owned.
build=(D/'build-helper.sh').read_text(); need('$EN/build-helper.sh' in build,'build-helper not EN')
invoke=(D/'invoke-once.sh').read_text(); need('$EN/live-iq-producer.py' in invoke,'invoke not EN producer'); need('e003i-eo-six-frame-native-aec' in invoke,'EO helper name')
# Fresh identity only.
grub=(D/'99zm_sp11_camera_e003i_eo_r5_r9').read_text()
for t in ('sp11-camera-e003i-eo-r5-r9-one-shot','sp11_camera_e003i_eo_r5_r9=1','sp11_entry=7.1.5-sp11-camera-e003i-eo-r5-r9','SP11 Camera E003i-EO — bounded R5-R9 IQ one-shot'): need(t in grub,'grub '+t)
for old in ('ea-current-first-demux','dy-full-aec-demux','sp11_camera_e003i_ea_'): need(old not in grub,'old identity '+old)
# EN parent safety shape: only publish bound extended; release remains G2..G4.
s=(EN/'e003i-en-six-frame-native-aec.c').read_text(); need('if (target <= 6U)' in s,'gain feed through G6'); need('if (target >= 2U && target <= 4U)' in s,'release window'); need('FRAME_COUNT 6' in s or '#define FRAME_COUNT 6' in s,'six-frame bound')
# Strict helper/bootstrap builds.
with tempfile.TemporaryDirectory(prefix='e003i-eo-verify-') as td:
    td=Path(td); subprocess.run([str(D/'build-helper.sh'),str(td/'helper')],check=True); subprocess.run([str(D/'build-bootstrap.sh'),str(td/'bootstrap')],check=True)
need((D/'verify-live.py').exists(),'live verifier missing')
print('EO_DEPENDENCY_CHAIN=PASS')
print('EO_FRESH_IDENTITY=PASS')
print('EO_EN_PARENT_SAFETY_SHAPE=PASS')
print('EO_HELPER_WERROR=PASS')
print('EO_BOOTSTRAP_WERROR=PASS')
print('EO_VERIFY=PASS')
