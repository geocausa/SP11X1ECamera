#!/usr/bin/env python3
from pathlib import Path
D=Path(__file__).resolve().parent
o=(D/'oracle.cmd').read_text()
e=(D/'entry.cmd').read_text()
h=(D/'holder.ps1').read_text()
assert '0x9241c0' in o.lower() and '0x924258' in o.lower()
assert 'r @$t5=@$t5+1' in o
for bad in ('0x9255f0','0x9241c4','0x92425c','post.cmd','||'):
    assert bad not in o.lower()
assert '0x60800' not in e
assert '@$t0 <' not in e and '@$t0 >' not in e
assert 'H01_HIST.bin' in e and 'H40_HIST.bin' in e
assert 'H01_TUNE.bin' in e and 'H40_RUNTIME.bin' in e
assert 'E007N_WINDOW_COMPLETE' in e
assert e.strip().endswith('gc')
assert e.splitlines().count('gc')==1
assert e.count('_HIST.bin')==40
assert 'E007N' in h and 'E007M' not in h
print('E007N_VERIFY_PASS callsites=2 hit_window=40 unfiltered=true')
print('early_gc=false return_breakpoints=false raw_pixels=false')
