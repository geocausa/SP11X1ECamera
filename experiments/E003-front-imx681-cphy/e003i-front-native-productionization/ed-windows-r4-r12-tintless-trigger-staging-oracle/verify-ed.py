#!/usr/bin/env python3
from pathlib import Path
H=Path(__file__).resolve().parent
h=(H/'holder.ps1').read_text();o=(H/'oracle.cmd').read_text();e=(H/'entry.cmd').read_text();p=(H/'post.cmd').read_text()
assert 'Surface Camera Front' in h and 'WAIT_START' in h and "$base='C:\\Users\\Geoca\\Documents\\E003I-ED'" in h
assert 'QcDeviceMFT8380+0x88e1e8' in o and 'QcDeviceMFT8380+0xa03b34' in o
assert 'qwo(@x1+0x1ff8)' in o and 'poi(@x0+0xa0)' in o and '@x1+0x2080' in o
assert 'ED_BREAKPOINTS_ARMED R4_R12' in o and o.count('bp QcDeviceMFT8380+')==2
assert 'dwo(@$t1+4) != 0x300' in e and '(dwo(@$t1)&2) == 0' in e
assert '@$t0 < 0n4' in e and '@$t0 > 0n12' in e and '@$t0 == 0n12' in e
assert '@$t0 < 0n4' in p and '@$t0 > 0n12' in p and '@$t0 == 0n12' in p
assert '@$t1+0x12beb' in e and '@$t4+0xff' in e
assert '@x19+0xac' in p and '@x19+0x194b' in p
assert 'ED_CAPTURE_COMPLETE R=12' in p and '.detach; q' in p
for r in range(4,13):
 q=f'{r:02d}'
 assert f'R{q}_TINTLESS_STATS.bin' in e
 assert f'R{q}_TRIGGER.bin' in e
 assert f'R{q}_LSC_STAGING.bin' in p
assert max(map(len,o.splitlines()))<512 and max(map(len,e.splitlines()))<512 and max(map(len,p.splitlines()))<512
print('ED_HOLDER_GATE=PASS')
print('ED_REQUEST_LABELLED_ENTRY=PASS')
print('ED_STATS_LAYOUT_FAIL_CLOSED=PASS')
print('ED_R4_R12_INPUT_OUTPUT_SCOPE=PASS')
print('ED_AUTO_DETACH_R12=PASS')
print('ED_VERIFY=PASS')
