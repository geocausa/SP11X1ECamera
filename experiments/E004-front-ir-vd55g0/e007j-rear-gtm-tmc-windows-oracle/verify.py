#!/usr/bin/env python3
from pathlib import Path
D=Path(__file__).resolve().parent
h=(D/'holder.ps1').read_text();o=(D/'oracle.cmd').read_text()
e=(D/'entry.cmd').read_text();p=(D/'post.cmd').read_text();a=(D/'analyze-capture.py').read_text()
for token in ('Surface Camera Rear','VideoRecord','NV12','3840','2160','SCRIPT-ENTRY-CONSUMED.marker','WAIT_START','START.GO'):
    assert token in h
assert h.count('StartAsync')==1 and 'SoftwareBitmap' not in h
assert 'QcDeviceMFT8380+0x9aa6e0' in o and '@lr == QcDeviceMFT8380+0xa28f2c' in o
assert 'QcDeviceMFT8380+0xa290a8' in o and 'E007J_BREAKPOINTS_ARMED R4_R18 REAR4K_GTM' in o
assert o.count('bp QcDeviceMFT8380+')==2
for token in ('dwo(@$t1+8) != 5','dwo(@$t1+0x10) == 0'):
    assert token in e
for req in range(4,19):
    q=f'{req:02d}'
    for n in ('GTM_COMMON','GTM_REGION','GTM_FLAGS','GTM_AUX','TMC_HDR','TMC_MODE','TMC_BLEND','TMC_SRC','TMC_DST','TMC_COEF','TMC_DOMAIN'):
        assert f'R{q}_{n}.bin' in e,(req,n)
    assert f'R{q}_GTM_OUT.bin' in p
assert 'E007J_CAPTURE_COMPLETE R=18' in p and 'bc *; .logclose; .detach; q' in p
for x in (o,e,p):
    assert max(map(len,x.splitlines()))<512
for token in ('range(4,19)','clean_gtm_replay','post_r6_tmc_state_law','raw_capture_values_committed'):
    assert token in a
print('E007J_VERIFY_PASS rear4k_holder=true gtm_hooks=2 requests=4..18')
print('capture=sparse_tmc+gtm_inputs+0x800_output raw_pixels=false one_shot=true')
