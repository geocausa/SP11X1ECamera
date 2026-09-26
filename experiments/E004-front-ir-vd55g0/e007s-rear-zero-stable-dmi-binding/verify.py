#!/usr/bin/env python3
from pathlib import Path
import hashlib, json

D=Path(__file__).resolve().parent
REPO=D.parents[2]
src=(D/'camss-e007s-zero-stable.inc').read_text()
meta=json.load(open(REPO/'experiments/E004-front-ir-vd55g0/e006b-windows-rear-dmi-source-payloads/PARTIAL-RESULT.json'))

def sha(b): return hashlib.sha256(b).hexdigest()

startup0=next(x for x in meta['captured']['captures'] if x['label']=='startup0')
by={(x['dmi_register_offset'],x['selector']):x for x in startup0['payloads']}
pdpc=by[('0x3d08',1)]
lsc3=by[('0x4308',3)]

assert pdpc['all_zero'] is True and pdpc['payload_bytes']==512
assert lsc3['all_zero'] is True and lsc3['payload_bytes']==884
assert sha(bytes(512)) == pdpc['payload_sha256']
assert sha(bytes(884)) == lsc3['payload_sha256']

for token in (
    '#define E007S_PDPC_DMI_REG 0x3d08',
    '#define E007S_LSC_DMI_REG  0x4308',
    '#define E007S_PDPC_BYTES   512',
    'memset(dst, 0, bytes);',
    'return -EOPNOTSUPP;',
    's->dmi.remaining = &e007s_rear_e007q_remaining_ops;',
    'e007s_rear_zero_stable_recipe',
):
    assert token in src, token

print('E007S_VERIFY_PASS pdpc_zero_hash=true lsc3_zero_hash=true')
print('complete_request_fail_closed_until_nonzero_provider=true')
