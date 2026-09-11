#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile

D=Path(__file__).resolve().parent
BASE=D.parent
DY=BASE/'dy-bounded-full-aec-demux-loop'
DZ=BASE/'dz-current-first-cq-publish-sensor-release'
DX=BASE/'dx-parent-cq-gain-feed'
DV=BASE/'dv-live-residual-isp-demux'
DW=BASE/'dw-iq-producer-live-cq-demux'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

for f in ('native-db-schedule.c','native-db-schedule.h','bootstrap-controls.c'):
    assert sha(D/f)==sha(DY/f),f
for p in (DV/'RESULT.json',DW/'RESULT.json',DX/'RESULT.json',DZ/'RESULT.json'):
    r=json.loads(p.read_text());assert r['status'].startswith('PASS'),p

build=(D/'build-helper.sh').read_text()
assert '$DZ/build-helper.sh' in build
invoke=(D/'invoke-once.sh').read_text()
assert '$DX/live-iq-producer.py' in invoke
assert 'e003i-ea-six-frame-native-aec' in invoke
assert 'ds-live-iq-producer' not in invoke
live=(D/'verify-live.py').read_text()
assert 'DZ_AEC_ACCEPT' in live
assert 'DZ_BOUNDARY_RELEASE_FAIL' in live
grub=(D/'99zk_sp11_camera_e003i_ea_current_first_demux').read_text()
assert 'sp11-camera-e003i-ea-current-first-demux-one-shot' in grub
assert 'sp11_camera_e003i_ea_current_first_demux=1' in grub
assert 'sp11_entry=7.1.5-sp11-camera-e003i-ea-current-first-demux' in grub
assert 'dy-full-aec-demux' not in grub

with tempfile.TemporaryDirectory(prefix='e003i-ea-') as td:
    td=Path(td)
    subprocess.run([str(D/'build-helper.sh'),str(td/'helper')],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(td/'bootstrap')],check=True)

print('EA_DY_SCHEDULER_BOOTSTRAP_BYTE_EXACT=PASS')
print('EA_DV_DW_DX_DZ_RESULTS=PASS')
print('EA_DZ_PARENT_DX_PRODUCER_LINK=PASS')
print('EA_HELPER_WERROR=PASS')
print('EA_BOOTSTRAP_WERROR=PASS')
print('EA_VERIFY=PASS')
