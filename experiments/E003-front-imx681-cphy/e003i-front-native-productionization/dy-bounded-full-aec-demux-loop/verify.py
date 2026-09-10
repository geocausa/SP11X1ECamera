#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile

D=Path(__file__).resolve().parent
BASE=D.parent
DT=BASE/'dt-bounded-native-aec-cap-awb-hold-sensor-loop'
DV=BASE/'dv-live-residual-isp-demux'
DW=BASE/'dw-iq-producer-live-cq-demux'
DX=BASE/'dx-parent-cq-gain-feed'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

# DY intentionally inherits only these already-live transport/scheduler pieces.
for f in ('native-db-schedule.c','native-db-schedule.h','bootstrap-controls.c'):
    assert sha(D/f)==sha(DT/f),f

for p in (DV/'RESULT.json',DW/'RESULT.json',DX/'RESULT.json'):
    r=json.loads(p.read_text());assert r['status']=='PASS',p

build=(D/'build-helper.sh').read_text()
assert '$DX/build-helper.sh' in build
invoke=(D/'invoke-once.sh').read_text()
assert '$DX/live-iq-producer.py' in invoke
assert 'ds-live-iq-producer' not in invoke
assert 'e003i-dy-six-frame-native-aec' in invoke
grub=(D/'99zj_sp11_camera_e003i_dy_full_aec_demux').read_text()
assert 'sp11-camera-e003i-dy-full-aec-demux-one-shot' in grub
assert 'sp11_camera_e003i_dy_full_aec_demux=1' in grub
assert 'sp11_entry=7.1.5-sp11-camera-e003i-dy-full-aec-demux' in grub
assert 'dt-cap' not in grub

with tempfile.TemporaryDirectory(prefix='e003i-dy-') as td:
    td=Path(td)
    subprocess.run([str(D/'build-helper.sh'),str(td/'helper')],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(td/'bootstrap')],check=True)

print('DY_DT_SCHEDULER_BOOTSTRAP_BYTE_EXACT=PASS')
print('DY_DV_DW_DX_RESULTS=PASS')
print('DY_DX_HELPER_PRODUCER_LINK=PASS')
print('DY_HELPER_WERROR=PASS')
print('DY_BOOTSTRAP_WERROR=PASS')
print('DY_VERIFY=PASS')
