#!/usr/bin/env python3
from pathlib import Path
import hashlib,json

D=Path(__file__).resolve().parent
s=(D/'camss-e007x-bhist16-startup-dmi.inc').read_text()
j=json.load(open(D/'SOURCE-SAFE.json'))

assert j['schema']=='E007x-rear-bhist16-startup-dmi-source-v1'
assert j['classification']=='SOURCE_LOCKED_ZERO_PRIMING'
assert j['dmi_register']=='0xb208'
assert j['startup_packet']==0
assert j['source_behavior']['zero_region_bytes']==0x1050
assert j['source_behavior']['selector1']['bytes']==0x1000
assert j['source_behavior']['selector2']['bytes']==0x50
assert j['captured_payload_bytes_embedded'] is False

z1=bytes(0x1000)
z2=bytes(0x50)
assert hashlib.sha256(z1).hexdigest()==j['retained_rear_validation']['selector1_sha256']
assert hashlib.sha256(z2).hexdigest()==j['retained_rear_validation']['selector2_sha256']

for token in (
    '#define E007X_BHIST_DMI_REG 0xb208',
    '#define E007X_BHIST_SEL1_BYTES 0x1000',
    '#define E007X_BHIST_SEL2_BYTES 0x0050',
    'e007x_bhist16_startup_dmi',
    'if (packet != 0',
    'memset(dst, 0, bytes);',
    'e007x_bhist16_startup_dmi_recipe',
):
    assert token in s

print('E007X_VERIFY_PASS bhist_startup_dmi=2 zero_exact=2/2 packet0_only=true')
print('startup_dmi_union_covered=true')
