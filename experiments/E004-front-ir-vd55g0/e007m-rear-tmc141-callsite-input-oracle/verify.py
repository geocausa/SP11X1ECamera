#!/usr/bin/env python3
from pathlib import Path
D=Path(__file__).resolve().parent
o=(D/'oracle.cmd').read_text()
e=(D/'entry.cmd').read_text()
h=(D/'holder.ps1').read_text()
assert '0x9241c0' in o.lower() and '0x924258' in o.lower()
for bad in ('0x9255f0','0x9241c4','0x92425c','post.cmd','||'):
    assert bad not in o.lower()
assert 'dwo(@x1+8) != 0x60800' in e
assert '(@$t0*4)+@$t1' in e
assert 'R04_S1_HIST.bin' in e and 'R18_S2_HIST.bin' in e
assert 'R04_S1_PRE_SRC.bin' in e and 'R18_S2_PRE_DST.bin' in e
assert 'E007M_CAPTURE_COMPLETE' in e
assert 'E007M' in h and 'E007L' not in h
assert e.count('_HIST.bin')==30
assert e.count('_TUNE.bin')==30
print('E007M_VERIFY_PASS callsites=2 site_tagged=true input_only=true requests=4..18')
print('return_breakpoints=false raw_pixels=false one_shot=true')
