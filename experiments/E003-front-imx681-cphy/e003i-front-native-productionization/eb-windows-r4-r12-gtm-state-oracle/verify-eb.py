#!/usr/bin/env python3
from pathlib import Path
import hashlib,re

HERE=Path(__file__).resolve().parent
holder=(HERE/'holder.ps1').read_text()
oracle=(HERE/'oracle.cmd').read_text()
entry=(HERE/'entry.cmd').read_text()
post=(HERE/'post.cmd').read_text()
an=(HERE/'analyze-eb.py').read_text()

assert "Surface Camera Front" in holder
assert "WAIT_START" in holder and "START.GO" in holder
assert "Start-Sleep -Milliseconds 5000" in holder
assert "EB_HOLDER_END" in holder
assert "New-Item $base -ItemType Directory" in holder

assert "QcDeviceMFT8380+0x9aa6e0" in oracle
assert "@lr == QcDeviceMFT8380+0xa28f2c" in oracle
assert "QcDeviceMFT8380+0xa290a8" in oracle
assert "qwo(@x19+0x1ff8)" in oracle
assert r"$$><C:\\Users\\Geoca\\Documents\\E003I-EB\\entry.cmd" in oracle
assert r"$$><C:\\Users\\Geoca\\Documents\\E003I-EB\\post.cmd" in oracle
assert "EB_BREAKPOINTS_ARMED R4_R12" in oracle
assert oracle.count('bp QcDeviceMFT8380+')==2
assert max(map(len,oracle.splitlines())) < 512
assert max(map(len,entry.splitlines())) < 512
assert max(map(len,post.splitlines())) < 512
assert "dwo(@$t1+8) != 5" in entry
assert "dwo(@$t1+0x10) == 0" in entry
assert "EB_CAPTURE_COMPLETE R=12" in post
assert ".detach; q" in post
for r in range(4,13):
    q=f'{r:02d}'
    for n in ('GTM_COMMON','GTM_REGION','GTM_FLAGS','GTM_AUX','TMC_HDR','TMC_MODE','TMC_BLEND','TMC_SRC','TMC_DST','TMC_COEF','TMC_DOMAIN'):
        assert f'R{q}_{n}.bin' in entry,(r,n)
    assert f'R{q}_GTM_OUT.bin' in post,(r,'GTM_OUT')
assert "post_r6_common_law" in an and "bank_values" in an and "post_r6_tmc_state_law" in an

print('EB_HOLDER_GATE=PASS')
print('EB_GTM_ENTRY_FILTER=PASS')
print('EB_R4_R12_BOUNDED_FILES=PASS')
print('EB_AUTO_DETACH_R12=PASS')
print('EB_PROVEN_CDB_SCRIPT_SHAPE=PASS')
print('EB_ANALYZER_STATIC=PASS')
print('EB_VERIFY=PASS')
