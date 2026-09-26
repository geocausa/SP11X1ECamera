#!/usr/bin/env python3
from pathlib import Path
import hashlib

D=Path(__file__).resolve().parent
files={x.name:x.read_text() for x in D.iterdir() if x.is_file() and x.suffix in ('.ps1','.cmd','.py')}
h=files['holder.ps1'];o=files['oracle.cmd'];e=files['entry.cmd'];p=files['post.cmd'];a=files['analyze-capture.py']

for token in [
    "Surface Camera Rear","VideoRecord","NV12","3840","2160",
    "SCRIPT-ENTRY-CONSUMED.marker","FileMode]::CreateNew","WAIT_START","START.GO",
]:
    assert token in h
assert h.count('StartAsync')==1
assert h.count('StopAsync')>=1
assert 'TryAcquireLatestFrame' in h
assert 'SoftwareBitmap' not in h

assert 'QcDeviceMFT8380+0x88e1e8' in o
assert 'QcDeviceMFT8380+0xa03b34' in o
assert 'qwo(@x1+0x1ff8)' in o
assert 'poi(@x0+0xa0)' in o
assert '@x1+0x2080' in o
assert 'E007G_BREAKPOINTS_ARMED R4_R18 REAR4K' in o
assert o.count('bp QcDeviceMFT8380+')==2

for token in ['dwo(@$t1+4) != 0x300','(dwo(@$t1)&2) == 0','@$t1+0x12beb','@$t4+0xff']:
    assert token in e
for r in range(4,19):
    q=f'{r:02d}'
    assert f'R{q}_TINTLESS_STATS.bin' in e
    assert f'R{q}_TRIGGER.bin' in e
    assert f'R{q}_LSC_STAGING.bin' in p
assert 'E007G_CAPTURE_COMPLETE R=18' in p
assert 'bc *; .logclose; .detach; q' in p

assert 'REAR_TUNING_SHA' in a and 'REAR_SLOT_SHA' in a
assert 'prove-lsc-live-staging-pack.py' in a
assert 'raw_capture_values_committed' in a
assert 'clean_replay_status' in a

for text in (o,e,p):
    assert max(map(len,text.splitlines()))<512

print('E007G_VERIFY_PASS rear4k_holder=true lsc_hooks=2 requests=4..18')
print('one_shot_entry=true raw_pixels=false runtime_not_yet_performed=true')
