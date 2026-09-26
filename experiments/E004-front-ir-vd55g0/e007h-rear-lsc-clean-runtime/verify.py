#!/usr/bin/env python3
from pathlib import Path
import json, py_compile

D=Path(__file__).resolve().parent
auth=json.load(open(D/'authority.json'))
proof=json.load(open(D/'RUNTIME-PROOF-SAFE.json'))
runtime=(D/'rear-lsc-runtime.py').read_text()

assert auth['schema']=='sp11-rear-ov13858-lsc-clean-authority-v1'
assert auth['status']=='PASS_DERIVED_CLEAN_RUNTIME_AUTHORITY'
assert set(auth['leaf_b64'])=={'0x29c','0x29e','0x2a0'}
assert len(auth['golden_int'])==884
assert sum(len(x) for x in auth['otp_int_channels'])==884
assert auth['policy']['proprietary_tuning_bytes_embedded'] is False
assert auth['policy']['raw_windows_capture_embedded'] is False
assert auth['policy']['outside_validated_aec_domain_fails_closed'] is True
assert auth['domain']['aec_branch']=='lower_only'

assert proof['schema']=='E007h-rear-lsc-clean-runtime-proof-v1'
assert proof['status']=='PASS'
assert proof['exact_requests']==15 and proof['total_requests']==15
assert proof['all_wire_exact'] is True
assert proof['requests']==list(range(4,19))
assert proof['authority_sha256']=='30f7b36402e8f55c8824d7d97ef560409e15f9f2495a62db56befca2f49c0965'

for token in ('class RearDynamicLsc','def run_parsed','rear LSC AEC domain unproven',
              'native-tintless-core.c','wire_from_output','authority.json'):
    assert token in runtime
for bad in ('sp11-driverdump','oracle-vss-20260902-local','oracle-carved-20260902',
            '/mnt/e007h-win-ro','Users/Geoca/Documents/E007G'):
    assert bad not in runtime

py_compile.compile(str(D/'rear-lsc-runtime.py'),doraise=True)
py_compile.compile(str(D/'derive-authority.py'),doraise=True)
py_compile.compile(str(D/'prove-runtime.py'),doraise=True)
print('E007H_VERIFY_PASS authority_clean=true runtime_capture_independent=true exact=15/15')
print('validated_domain=rear_lower_aec fail_closed_outside=true')
