#!/usr/bin/env python3
from pathlib import Path
import hashlib, importlib.util, json, py_compile, sys

D=Path(__file__).resolve().parent
auth=json.load(open(D/'AUTHORITY-SAFE.json'))
priv=json.load(open(D/'PRIVATE-VALIDATION-SAFE.json'))
inc=(D/'camss-e007t-gamma151.inc').read_text()

s=importlib.util.spec_from_file_location('e007t_derive',D/'derive-authority.py')
m=importlib.util.module_from_spec(s)
sys.modules['e007t_derive']=m
assert s.loader
s.loader.exec_module(m)
assert m.derive()==auth

assert auth['status']=='PASS_DERIVED_SEMANTIC_AUTHORITY'
assert auth['curve']['entries']==257
assert auth['curve']['semantic_bits']==12
assert auth['curve']['channels_identical'] is True
assert auth['curve']['min']==0 and auth['curve']['max']==4095
assert auth['curve']['integral'] is True
assert auth['curve']['monotonic_nondecreasing'] is True
assert auth['policy']['raw_windows_dmi_embedded'] is False

assert priv['status']=='PASS'
assert priv['payload_checks']==9
assert priv['captures']==['startup0','startup1','steady_ac8']
assert priv['selectors']==[1,2,3]
assert priv['packed_payload_sha256']=='5a0237322ad86a63afa00152f43d049ba9db6494753a20fbf35149a51e978f2b'
assert priv['raw_windows_values_emitted'] is False

for token in (
    '#define E007T_GAMMA_DMI_REG 0x5f08',
    '#define E007T_GAMMA_BYTES   1024',
    'static const u16 e007t_gamma_curve[E007T_GAMMA_SAMPLES]',
    'word = (u32)x | (((u32)d & 0xfff) << 12);',
    'selector >= 1 && selector <= 3',
    'e007t_rear_validate_request',
    'e007t_rear_prepare_dynamic',
    'e007t_rear_fill_slot',
    'e007t_rear_gamma_recipe',
):
    assert token in inc

for bad in ('writel(', 'readl(', 'dma_alloc', 'RTCDM_FIFO', '5a0237322ad86a63'):
    assert bad not in inc

py_compile.compile(str(D/'derive-authority.py'),doraise=True)
py_compile.compile(str(D/'gamma151.py'),doraise=True)
py_compile.compile(str(D/'generate-provider.py'),doraise=True)
py_compile.compile(str(D/'validate-private.py'),doraise=True)

print('E007T_VERIFY_PASS authority=257x12 gamma_payloads=9/9')
print('bpcabf_dsx=explicit_upstream runtime_submission=none')
