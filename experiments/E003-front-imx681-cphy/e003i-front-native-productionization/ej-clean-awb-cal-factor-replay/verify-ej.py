#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json
HERE=Path(__file__).resolve().parent
EI=HERE.parent/'ei-front-awb-otp-oracle'
s=importlib.util.spec_from_file_location('cf',HERE/'cal_factors.py'); cf=importlib.util.module_from_spec(s); s.loader.exec_module(cf)
def need(x,m):
    if not x: raise AssertionError(m)
ei=json.loads((EI/'RESULT.json').read_text()); need(ei['status']=='PASS_SAME_DEVICE_OTP_AND_FACTOR_TABLE','EI authority')
z=cf.compute((EI/'AWB-OTP-RAW.bin').read_bytes())
exp=[(int(x['rg'],16),int(x['bg'],16)) for x in ei['windows_factor_bits']]
got=[(cf.bits(a),cf.bits(b)) for a,b in z['table']]
need(got==exp,f'factor table mismatch got={got} exp={exp}')
rec=[(cf.bits(a),cf.bits(b)) for a,b in z['reciprocal']]
exp_rec=[(int(x['rg'],16),int(x['bg'],16)) for x in ei['reciprocal_scale_bits']]
need(rec==exp_rec,'reciprocal table mismatch')
need(rec[0]==(0x3f80a277,0x3f83427b),'EG active scale')
out={'schema':'sp11-e003i-ej-clean-awb-cal-factor-replay-v1','status':'PASS_10_OF_10_BIT_EXACT',
     'tuning_sha256':cf.TUNING_SHA256,'sensorcal_payload_sha256':cf.SENSORCAL_SHA256,
     'raw_eeprom_sha256':ei['raw_eeprom_sha256'],
     'tuning_anchors':{'low':{'cct':z['tuning']['low'][0],'rg_bits':f'0x{cf.bits(z["tuning"]["low"][1]):08x}','bg_bits':f'0x{cf.bits(z["tuning"]["low"][2]):08x}'},
                       'high':{'cct':z['tuning']['high'][0],'rg_bits':f'0x{cf.bits(z["tuning"]["high"][1]):08x}','bg_bits':f'0x{cf.bits(z["tuning"]["high"][2]):08x}'}},
     'factor_regions':{'high':{'slots':[0,1,2,3],'bits':[f'0x{cf.bits(x):08x}' for x in z['high_factor']]},
                       'midpoint':{'slots':[4,5,6],'bits':[f'0x{cf.bits(x):08x}' for x in z['mid_factor']]},
                       'low':{'slots':[7,8,9],'bits':[f'0x{cf.bits(x):08x}' for x in z['low_factor']]}},
     'active_reciprocal_scale_bits':{'rg':f'0x{rec[0][0]:08x}','bg':f'0x{rec[0][1]:08x}'},
     'windows_factor_table_bit_exact':'10/10','compute_cal_factors_clean_replay':True,
     'profile_scope':'SP11_front_IMX681_two_anchor_sensorCalV1','generic_other_profiles':False,
     'linux_runtime_eeprom_read_bound':False}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
