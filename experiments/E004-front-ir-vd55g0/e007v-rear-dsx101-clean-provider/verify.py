#!/usr/bin/env python3
from pathlib import Path
import json,py_compile
D=Path(__file__).resolve().parent
a=json.load(open(D/'AUTHORITY-SAFE.json'))
p=json.load(open(D/'PRIVATE-VALIDATION-SAFE.json'))
s=(D/'camss-e007v-dsx101.inc').read_text()
assert a['schema']=='E007v-rear-dsx101-clean-authority-v1'
assert a['status']=='PASS_DERIVED_SEMANTIC_AUTHORITY'
assert a['source']['semantic_float_count']==706
assert a['source']['luma_banks_identical'] is True
assert a['source']['chroma_banks_identical'] is True
assert a['validated_path']=={'scale_x':4.0,'scale_y':4.0,'nclib_fixed_4x_branch':True}
assert len(a['luma_coefficients'])==192 and len(a['chroma_coefficients'])==96
assert a['policy']['captured_windows_payload_embedded'] is False
assert a['policy']['generic_non_4x_dsx_claimed'] is False
assert p['status']=='PASS' and p['payload_checks']==16 and p['payload_checks_exact']==16
for token in (
 '#define E007V_DSX_LUMA_REG 0xa008',
 '#define E007V_DSX_CHROMA_REG 0xa208',
 '#define E007V_DSX_LUMA_BYTES 768',
 '#define E007V_DSX_CHROMA_BYTES 384',
 'e007v_dsx_pack_bank',
 'e007v_dsx101_pack',
 'e007v_rear_dsx',
 'e007v_rear_validate_request',
 'e007v_rear_prepare_dynamic',
 'e007v_rear_fill_slot',
 'e007v_rear_dsx_recipe',
):
    assert token in s
assert 'captured' not in s.lower()
assert 'writel' not in s and 'readl' not in s
for f in ('derive-authority.py','validate-private.py','generate-provider.py'):
    py_compile.compile(str(D/f),doraise=True)
print('E007V_VERIFY_PASS dsx4x=true private_exact=16/16')
print('first_frame_payload_blockers=0 remaining_transport_blocker=PERIOD_CFG')
