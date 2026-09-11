#!/usr/bin/env python3
from pathlib import Path
import hashlib,re

HERE=Path(__file__).resolve().parent
holder=(HERE/'holder.ps1').read_text()
oracle=(HERE/'oracle.cmd').read_text()
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
assert "dwo(@$t1+8) != 5" in oracle
assert "dwo(@$t1+0x10) == 0" in oracle
assert "EB_CAPTURE_COMPLETE R=12" in oracle
assert ".detach; q" in oracle
for r in range(4,13):
    q=f'{r:02d}'
    for n in ('GTM_COMMON','GTM_REGION','GTM_FLAGS','GTM_AUX','TMC_HDR','TMC_MODE','TMC_BLEND','TMC_SRC','TMC_DST','TMC_COEF','TMC_DOMAIN','GTM_OUT'):
        assert f'R{q}_{n}.bin' in oracle,(r,n)
assert oracle.count('{')==oracle.count('}')
assert oracle.count('bp QcDeviceMFT8380+')==2
assert "clean_gtm_replay" in an and "post_r6_tmc_state_law" in an

print('EB_HOLDER_GATE=PASS')
print('EB_GTM_ENTRY_FILTER=PASS')
print('EB_R4_R12_BOUNDED_FILES=PASS')
print('EB_AUTO_DETACH_R12=PASS')
print('EB_ANALYZER_STATIC=PASS')
print('EB_VERIFY=PASS')
