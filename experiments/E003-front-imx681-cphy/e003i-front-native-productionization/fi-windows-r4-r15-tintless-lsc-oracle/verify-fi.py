#!/usr/bin/env python3
from pathlib import Path
H=Path(__file__).resolve().parent
h=(H/'holder.ps1').read_text()
o=(H/'oracle.cmd').read_text()
e=(H/'entry.cmd').read_text()
p=(H/'post.cmd').read_text()

assert 'Surface Camera Front' in h
assert 'WAIT_START' in h
assert 'E003I-FI' in h
assert h.count('START_BEGIN')==1
assert h.count('StartAsync')==1
assert h.count('StopAsync')==1

assert 'QcDeviceMFT8380+0x88e1e8' in o
assert 'QcDeviceMFT8380+0xa03b34' in o
assert 'qwo(@x1+0x1ff8)' in o
assert 'poi(@x0+0xa0)' in o
assert '@x1+0x2080' in o
assert 'FI_BREAKPOINTS_ARMED R4_R15 DECIMAL_FIXED' in o
assert o.count('bp QcDeviceMFT8380+')==2

assert 'dwo(@$t1+4) != 0x300' in e
assert '(dwo(@$t1)&2) == 0' in e
assert '@$t0 < 0n4' in e
assert '@$t0 > 0n15' in e
assert '@$t0 < 0n4' in p
assert '@$t0 > 0n15' in p
assert '@$t1+0x12beb' in e
assert '@$t4+0xff' in e
assert '@x19+0xac' in p
assert '@x19+0x194b' in p
assert 'FI_CAPTURE_COMPLETE R=15' in p
assert '.detach; q' in p

for r in range(4,16):
    q=f'{r:02d}'
    assert f'R{q}_TINTLESS_STATS.bin' in e
    assert f'R{q}_TRIGGER.bin' in e
    assert f'R{q}_LSC_STAGING.bin' in p

assert max(map(len,o.splitlines()))<512
assert max(map(len,e.splitlines()))<512
assert max(map(len,p.splitlines()))<512

print('FI_HOLDER_GATE=PASS')
print('FI_REQUEST_LABELLED_ENTRY=PASS')
print('FI_STATS_LAYOUT_FAIL_CLOSED=PASS')
print('FI_R4_R15_INPUT_OUTPUT_SCOPE=PASS')
print('FI_AUTO_DETACH_R15=PASS')
print('FI_VERIFY=PASS')
