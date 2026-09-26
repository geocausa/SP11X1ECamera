#!/usr/bin/env python3
from pathlib import Path
import json
D=Path(__file__).resolve().parent
S=json.loads((D/'SOURCE-SAFE.json').read_text())
V=json.loads((D/'PRIVATE-VALIDATION-SAFE.json').read_text())
C=(D/'camss-e006y-awbbg17.inc').read_text()
assert S['schema']=='E006y-rear-awbbg17-source-safe-v1'
assert S['module']=='IFEAWBBGStats17Titan680'
assert S['functions']['create_cmd_list']=='0x180b39720'
assert S['functions']['create_sub_cmd_list']=='0x180b398a0'
assert S['functions']['pack_iq_register_setting']=='0x180b39950'
assert S['functions']['hardware_caps']=='0x180b39870'
assert S['functions']['dependence_copy']=='0x1809fdf60'
assert S['functions']['modern_adjust_roi']=='0x1809fe120'
assert S['functions']['validate_dependence_params']=='0x1809fe600'
assert S['functions']['execute']=='0x1809fe780'
assert S['writes']==[
 {'register':'0xb86c','count':5},{'register':'0xb880','count':10},
 {'register':'0xb868','count':1},{'register':'0xb864','count':1},{'register':'0xb860','count':1}]
assert sum(x['count'] for x in S['writes'])==18
assert S['semantic_core']['identical_to_e006w_aecbe17_packer'] is True
assert S['semantic_core']['identical_hardware_function_to_e006x_tintless'] is True
assert S['semantic_core']['black_level_request_byte_offset']=='0x2170'
assert S['raw_windows_command_values_committed'] is False
assert V['schema']=='E006y-rear-awbbg17-private-validation-safe-v1'
assert V['exact_repack_count']==2 and V['exact_repack_total']==2
assert V['startup1_exact_semantic_repack'] and V['startup2_exact_semantic_repack']
assert V['startup3_block_absent'] and V['startup4_block_absent']
assert V['words_per_emitted_startup']==18
assert V['shared_e006w_core_exact']
assert not V['raw_register_values_committed'] and not V['raw_packet_bytes_committed']
for t in ['e006y_awbbg17_lookup','e006w_aecbe17_lookup','reg - 0x800','e006y_awbbg_stats17_recipe']:
    assert t in C
P=D.parent
owner=json.loads((P/'e006l-rear-startup-register-ownership'/'STARTUP-REGISTER-OWNER-MAP.json').read_text())
regs={int(x['register'],16) for x in owner['startup_only'] if x['owner']=='AWB_BG_STATS17'}
assert regs==set(range(0xb860,0xb8a8,4))
recipe=json.loads((P/'e006k-rear-startup-main-symbolic-recipe'/'STARTUP-SYMBOLIC-RECIPE.json').read_text())
want={f'0x{x:04x}' for x in range(0xb860,0xb8a8,4)}
presence={}
for name,v in recipe['variants'].items():
    presence[name]={x['register_offset'] for c in v['commands'] for x in c.get('values',[])}
assert want<=presence['startup1'] and want<=presence['startup2']
assert want.isdisjoint(presence['startup3']) and want.isdisjoint(presence['startup4'])
print('E006Y_VERIFY_PASS')
print('awbbg17_regs=18 startup1_2=present startup3_4=absent')
print('shared_e006w_semantic_core=true black_level=request_0x2170')
print('startup_only_coverage_after_e006y=184/184')
print('raw_windows_command_values=false')
