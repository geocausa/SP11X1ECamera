#!/usr/bin/env python3
from pathlib import Path
import json, py_compile
D=Path(__file__).resolve().parent
a=json.load(open(D/'AUTHORITY-SAFE.json'))
p=json.load(open(D/'PRIVATE-VALIDATION-SAFE.json'))
s=(D/'camss-e007u-bpcabf411.inc').read_text()
assert a['schema']=='E007u-rear-bpcabf411-clean-authority-v1'
assert a['status']=='PASS_DERIVED_SEMANTIC_AUTHORITY'
assert a['source']['regions_share_lut_fields'] is True
assert a['common_setting']['point_count']==65
assert a['common_setting']['scale']==3.0
assert a['packer']['dmi_register']=='0x4908'
assert a['packer']['selector']==1
assert a['packer']['payload_bytes']==256
assert a['policy']['raw_windows_dmi_embedded'] is False
assert a['policy']['proprietary_tuning_blob_embedded'] is False
assert p['status']=='PASS' and p['payload_checks']==4
assert p['payload_bytes']==256 and p['selector']==1
assert p['packed_payload_sha256']==a['packer']['derived_payload_sha256']
for token in (
 '#define E007U_BPCABF_DMI_REG 0x4908',
 '#define E007U_BPCABF_BYTES 256',
 '#define E007U_BPCABF_POINTS 65',
 'e007u_bpcabf411_pack',
 'e007u_rear_stable_non_gamma',
 'e007u_rear_validate_request',
 'e007u_rear_prepare_dynamic',
 'e007u_rear_fill_slot',
 'e007u_rear_bpcabf_recipe',
):
    assert token in s
assert 'captured' not in s.lower()
assert 'writel' not in s and 'readl' not in s
for f in ('derive-authority.py','bpcabf411.py','validate-private.py','generate-provider.py'):
    py_compile.compile(str(D/f),doraise=True)
print('E007U_VERIFY_PASS semantic_points=65 private_exact=4/4 selector=1')
print('remaining_payload_blocker=DSX101 remaining_transport_blocker=PERIOD_CFG')
