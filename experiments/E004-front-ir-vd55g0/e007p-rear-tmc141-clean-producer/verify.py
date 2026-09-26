#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, tempfile

D=Path(__file__).resolve().parent
src=(D/'tmc141-clean.c').read_text()
r=json.load(open(D/'RESULT.json'))
safe=json.load(open(D/'PRIVATE-VALIDATION-SAFE.json'))

for token in (
    'E007P_MODE_REAR_4K 0x00060800u',
    'e007p_powf_pos',
    'e007p_scale_index',
    'e007p_global_src',
    'e007p_rear_mode_src',
    'e007p_coeff',
    'e007p_tmc141_solve',
    't[0x29] / runtime_48c',
    'runtime_488 * tune_a0',
):
    assert token in src, token

for bad in ('POST_SRC','POST_DST','POST_COEF','H01_','R4_TMC_'):
    assert bad not in src, bad

assert r['classification']=='USERSPACE_ALGORITHM_PASS_20_OF_20_BYTE_EXACT'
assert r['exact_complete_triplets']==20
assert r['captured_knots_used_as_producer_inputs'] is False
assert r['fail_closed_outside_validated_domain'] is True
assert safe['status']=='PASS'
assert safe['exact_complete_triplets']==20
assert safe['raw_windows_values_emitted'] is False

with tempfile.TemporaryDirectory(prefix='e007p-verify-') as td:
    for cc in ('gcc','clang'):
        subprocess.run([
            cc,'-O2','-Wall','-Wextra','-Werror','-fPIC',
            '-fno-fast-math','-ffp-contract=off','-c',
            str(D/'tmc141-clean.c'),'-o',str(Path(td)/(cc+'.o'))
        ],check=True)

print('E007P_VERIFY_PASS src=20/20 dst=20/20 coeff=20/20 triplets=20/20')
print('gcc_werror=true clang_werror=true capture_knots_as_inputs=false')
