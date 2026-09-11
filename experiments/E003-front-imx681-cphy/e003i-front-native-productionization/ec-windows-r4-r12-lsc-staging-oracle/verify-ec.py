#!/usr/bin/env python3
from pathlib import Path
HERE=Path(__file__).resolve().parent
h=(HERE/'holder.ps1').read_text();o=(HERE/'oracle.cmd').read_text();c=(HERE/'capture.cmd').read_text();a=(HERE/'analyze-ec.py').read_text()
assert 'Surface Camera Front' in h and 'WAIT_START' in h and "$base='C:\\Users\\Geoca\\Documents\\E003I-EC'" in h and '$base-START.GO' in h
assert 'QcDeviceMFT8380+0xa03b34' in o
assert 'qwo(@x20+0x1ff8)' in o
assert r'$$><C:\\Users\\Geoca\\Documents\\E003I-EC\\capture.cmd' in o
assert 'EC_BREAKPOINT_ARMED R4_R12' in o
assert o.count('bp QcDeviceMFT8380+')==1
assert max(map(len,o.splitlines()))<512 and max(map(len,c.splitlines()))<512
assert '@x19+0xac' in c and '@x19+0x194b' in c
assert 'EC_CAPTURE_COMPLETE R=12' in c and '.detach; q' in c
for r in range(4,13):assert f'R{r:02d}_LSC_STAGING.bin' in c
assert "pack_live_staging" in a and "gic_alias_sha256" in a
print('EC_HOLDER_GATE=PASS')
print('EC_EXACT_POSTCALC_HOOK=PASS')
print('EC_R4_R12_STAGING_SCOPE=PASS')
print('EC_AUTO_DETACH_R12=PASS')
print('EC_ANALYZER_STATIC=PASS')
print('EC_VERIFY=PASS')
