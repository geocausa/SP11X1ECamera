#!/usr/bin/env python3
from pathlib import Path
import hashlib,importlib.util,json,re,struct,sys
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
MOD=HERE/'dynamic_awb.py'
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
FB=load(MOD,'fb_dynamic')
def need(x,m):
 if not x: raise AssertionError(m)
def fb(h):return struct.unpack('<f',struct.pack('<I',int(h,16)))[0]
def kv(s):return dict(re.findall(r'(\w+)=([0-9A-Fa-f]+)',s))
def replay(path,gp,pp,requests,expected_slots):
 lines=[x.strip() for x in path.read_text().splitlines() if x.strip()]
 ga=[kv(x) for x in lines if x.startswith(gp)];pub=[kv(x) for x in lines if x.startswith(pp)]
 need(len(ga)==len(pub)==len(requests),f'{path.name} pair count')
 c=FB.DynamicCalibratedAWB();rows=[]
 for a,p,req,slot in zip(ga,pub,requests,expected_slots):
  need(int(p['req'])==req,f'R{req} publisher request')
  if 'req' in a: need(int(a['req'])==req,f'R{req} GA request')
  rg,bg,lux,cct=[fb(a[k]) for k in ('rg','bg','lux','cct')]
  o=c.run(rg,bg,lux,cct,1.0);z=o['gain_adjust']
  need(o['calibration_slot']==slot,f'R{req} calibration slot got={o["calibration_slot"]} exp={slot}')
  need(z['triangle']==int(a['tri']),f'R{req} triangle')
  need(z['vertices']==[int(a[k]) for k in ('v0','v1','v2')],f'R{req} vertices')
  need([FB.bits(x) for x in z['weights']]==[int(a[k],16) for k in ('w0','w1','w2')],f'R{req} weights')
  need([FB.bits(x) for x in z['cct_rgb']]==[int(a[k],16) for k in ('cctr','cctg','cctb')],f'R{req} CCT multiplier')
  need([FB.bits(x) for x in z['final_rgb']]==[int(a[k],16) for k in ('ar','ag','ab')],f'R{req} final GA')
  got=[FB.bits(o[k]) for k in ('R','G','B')];exp=[int(p[k],16) for k in ('R','G','B')]
  need(got==exp,f'R{req} published RGB got={got} exp={exp}')
  rows.append({'request':req,'slot':o['calibration_slot'],'region':o['calibration_region'],
               'ratio_bits':f'0x{FB.bits(o["calibration_ratio"]):08x}',
               'scale_bits':o['calibration_scale_bits'],'triangle':z['triangle'],
               'published_gain_bits':[f'0x{x:08x}' for x in got]})
 return rows
eg=json.loads((BASE/'eg-windows-awb-gain-adjust-oracle/RESULT.json').read_text())
el=json.loads((BASE/'el-calibrated-awb-scalar-join/RESULT.json').read_text())
ej=json.loads((BASE/'ej-clean-awb-cal-factor-replay/RESULT.json').read_text())
need(eg['status']=='PASS_8_OF_8_BIT_EXACT','EG authority')
need(el['status']=='PASS_OFFLINE_JOIN','EL authority')
need(ej['status']=='PASS_10_OF_10_BIT_EXACT' and ej['linux_runtime_eeprom_read_bound'],'EJ/EK authority')
egrows=replay(BASE/'eg-windows-awb-gain-adjust-oracle/ORACLE-PAIRS.txt','EG_GA ','EG_PUB ',list(range(4,12)),[3]*8)
farows=replay(BASE/'fa-windows-r12-awb-gain-adjust-oracle/ORACLE-PAIRS.txt','FA_GA ','FA_PUB ',list(range(4,13)),[3]+[5]*8)
probe=FB.DynamicCalibratedAWB()
out={'schema':'sp11-e003i-fb-dynamic-awb-cal-slot-replay-v1',
     'status':'PASS_EG_8_OF_8_FA_9_OF_9_BIT_EXACT',
     'profile':'SP11_front_IMX681_normal_preview',
     'windows_selector':'CAWBCtrlV1_to_CSFStatDistV1',
     'refpt_sha256':FB.REFPT_SHA256,'sfdist_sha256':FB.SFDIST_SHA256,
     'f_bound_no_shift_distance':probe.selector.f_distance,
     'eg':{'requests':list(range(4,12)),'slots':[x['slot'] for x in egrows],'bit_exact':'8/8'},
     'fa':{'requests':list(range(4,13)),'slots':[x['slot'] for x in farows],'bit_exact':'9/9'},
     'fa_transition':'R4_slot3_high_to_R5_R12_slot5_midpoint',
     'eg_oracle_sha256':hashlib.sha256((BASE/'eg-windows-awb-gain-adjust-oracle/ORACLE-PAIRS.txt').read_bytes()).hexdigest(),
     'fa_oracle_sha256':hashlib.sha256((BASE/'fa-windows-r12-awb-gain-adjust-oracle/ORACLE-PAIRS.txt').read_bytes()).hexdigest(),
     'historical_el_modified':False,'windows_streams_added':0,'camera_runtime_performed':False,
     'rows':farows}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
