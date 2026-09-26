#!/usr/bin/env python3
from pathlib import Path
D=Path(__file__).resolve().parent
entry=(D/'entry.cmd').read_text()
post=(D/'post.cmd').read_text()
oracle=(D/'oracle.cmd').read_text()
holder=(D/'holder.ps1').read_text()

assert '0x9241c0' in oracle and '0x924258' in oracle
assert '0x9241c4' in oracle and '0x92425c' in oracle
assert '||' not in oracle
assert 'qwo(@x1+0x1ff8)' not in oracle
assert oracle.count('$$><') == 4
assert entry.strip().endswith('gc')
assert entry.count('\ngc') == 1
assert post.strip().endswith('gc')
assert post.count('\ngc') == 1
assert 'E007O_CAPTURE_COMPLETE H=20' in post
assert 'bc *; .logclose; .detach; q' in post
for i in range(1,21):
    q=f'H{i:02d}'
    for k in ('TUNE','RUNTIME','DESC','PRE_SRC','PRE_DST','PRE_COEF'):
        assert f'{q}_{k}.bin' in entry
    for k in ('POST_SRC','POST_DST','POST_COEF'):
        assert f'{q}_{k}.bin' in post
assert '_HIST.bin' not in entry
assert 'E007O' in holder and 'E007N' not in holder
assert 'Surface Camera Rear' in holder
assert 'VideoRecord' in holder and 'NV12' in holder and '3840' in holder and '2160' in holder
assert 'CopyTo' not in holder and 'SoftwareBitmap' not in holder
assert 'SCRIPT-ENTRY-CONSUMED.marker' in holder
print('E007O_VERIFY_PASS calls=20 prepost=true single_gc_per_handler=true')
print('request_filter=false histogram_recapture=false raw_pixels=false one_shot=true')
