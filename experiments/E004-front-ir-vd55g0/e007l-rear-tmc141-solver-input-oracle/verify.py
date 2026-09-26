#!/usr/bin/env python3
from pathlib import Path

D=Path(__file__).resolve().parent
h=(D/'holder.ps1').read_text()
o=(D/'oracle.cmd').read_text()
e=(D/'entry.cmd').read_text()
p=(D/'post.cmd').read_text()

for token in ('Surface Camera Rear','VideoRecord','NV12','3840','2160',
              'SCRIPT-ENTRY-CONSUMED.marker','WAIT_START','START.GO'):
    assert token in h
assert h.count('StartAsync') == 1
assert 'SoftwareBitmap' not in h

assert 'QcDeviceMFT8380+0x9255f0' in o
assert 'QcDeviceMFT8380+0x9241c4' in o
assert 'QcDeviceMFT8380+0x92425c' in o
assert 'qwo(@x1+0x1ff8)' in o
assert o.count('bp QcDeviceMFT8380+') == 3

assert 'dwo(@x1+8) != 0x60800' in e
for token in ('poi(@x2+0x10)','poi(@x2+0x28)','poi(@x2+0x30)','poi(@x2+0x50)',
              'poi(@x1+0x40)+0x8228','poi(@x1+0x450)'):
    assert token in e

assert 'qwo(@x19+0x1ff8)' in p
assert 'poi(@x19+0x40)+0x5104' in p
assert 'poi(@x19+0x40)+0x5120' in p
assert 'poi(@x19+0x40)+0x51b0' in p

for req in range(4,19):
    q=f'{req:02d}'
    for n in ('TUNE','RUNTIME','DESC','HIST','PRE_SRC','PRE_DST','PRE_COEF',
              'COMMON','CTRL','FACE'):
        assert f'R{q}_{n}.bin' in e,(req,n)
    for n in ('POST_SRC','POST_DST','POST_COEF'):
        assert f'R{q}_{n}.bin' in p,(req,n)

assert 'E007L_CAPTURE_COMPLETE R=18' in p
assert 'bc *; .logclose; .detach; q' in p
for x in (o,e,p):
    assert max(map(len,x.splitlines())) < 512

print('E007L_VERIFY_PASS solver_entry=true returns=2 requests=4..18')
print('capture=processed_hist+bounded_inputs+family2_prepost raw_pixels=false one_shot=true')
