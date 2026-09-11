#!/usr/bin/env python3
from pathlib import Path
import hashlib,importlib.util,json,re,struct,sys

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
MOD=HERE/'dynamic_awb.py'
FXOBJ=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fx/windows-selector-20260911/capture/CSFSTATDIST-OBJECT.bin')
FX_SHA='ef2d954f099ae484ad26955e89c4b0ff76e3cbdbc2bd87b3eb4d412e99a9d61a'
FWLOG=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fw/windows-r4-r21-20260911/capture/E003I-FW-oracle.log')

def need(v,m):
    if not v: raise AssertionError(m)

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m
    assert s.loader;s.loader.exec_module(m);return m

def kv(line):
    return dict(re.findall(r'(\w+)=([0-9A-Fa-f]+)',line))

def fbits(h):
    return struct.unpack('<f',struct.pack('<I',int(h,16)))[0]

FY=load(MOD,'fy_dynamic')
obj=FXOBJ.read_bytes()
need(len(obj)==0x240,'FX object size')
need(hashlib.sha256(obj).hexdigest()==FX_SHA,'FX object SHA')

probe=FY.DynamicCalibratedAWB()
sel=probe.selector
def bitsf(x): return struct.unpack('<I',struct.pack('<f',float(x)))[0]

bmatch=smatch=lmatch=0
boundary_bits=[];search_bits=[];length_bits=[]
for i,b in enumerate(sel.boundaries):
    got=(bitsf(b.m),bitsf(-1.0),bitsf(b.c),bitsf(b.sign))
    exp=struct.unpack_from('<4I',obj,0x10+i*0x10)
    need(got==exp,f'FX boundary {i}')
    bmatch+=1;boundary_bits.append([f'0x{x:08x}' for x in got])
for i,b in enumerate(sel.search):
    got=(bitsf(b.m),bitsf(-1.0),bitsf(b.c),bitsf(b.sign))
    exp=struct.unpack_from('<4I',obj,0x90+i*0x10)
    need(got==exp,f'FX search {i}')
    smatch+=1;search_bits.append([f'0x{x:08x}' for x in got])
for i,b in enumerate(sel.boundaries):
    got=bitsf(b.length);exp=struct.unpack_from('<I',obj,0x110+i*4)[0]
    need(got==exp,f'FX length {i}')
    lmatch+=1;length_bits.append(f'0x{got:08x}')

def replay(name,path,gp,pp,requests):
    lines=path.read_text(errors='replace').replace('\r','').splitlines()
    ga=[kv(x) for x in lines if x.startswith(gp)]
    pub=[kv(x) for x in lines if x.startswith(pp)]
    need(len(ga)==len(pub)==len(requests),f'{name} pair count')
    c=FY.DynamicCalibratedAWB();rows=[]
    for a,p,req in zip(ga,pub,requests):
        need(int(p['req'])==req,f'{name} R{req} pub request')
        if 'req' in a: need(int(a['req'])==req,f'{name} R{req} GA request')
        o=c.run(*[fbits(a[k]) for k in ('rg','bg','lux','cct')],1.0);z=o['gain_adjust']
        need(z['triangle']==int(a['tri']),f'{name} R{req} triangle')
        need(z['vertices']==[int(a[k]) for k in ('v0','v1','v2')],f'{name} R{req} vertices')
        need([FY.bits(x) for x in z['weights']]==[int(a[k],16) for k in ('w0','w1','w2')],f'{name} R{req} weights')
        need([FY.bits(x) for x in z['cct_rgb']]==[int(a[k],16) for k in ('cctr','cctg','cctb')],f'{name} R{req} CCT RGB')
        need([FY.bits(x) for x in z['final_rgb']]==[int(a[k],16) for k in ('ar','ag','ab')],f'{name} R{req} final GA')
        got=[FY.bits(o[k]) for k in ('R','G','B')]
        exp=[int(p[k],16) for k in ('R','G','B')]
        need(got==exp,f'{name} R{req} publisher')
        rows.append({'request':req,'slot':o['calibration_slot'],'region':o['calibration_region'],
                     'ratio_bits':f'0x{FY.bits(o["calibration_ratio"]):08x}','triangle':z['triangle']})
    return rows

sets=[
 ('EG',BASE/'eg-windows-awb-gain-adjust-oracle'/'ORACLE-PAIRS.txt','EG_GA ','EG_PUB ',list(range(4,12))),
 ('FA',BASE/'fa-windows-r12-awb-gain-adjust-oracle'/'ORACLE-PAIRS.txt','FA_GA ','FA_PUB ',list(range(4,13))),
 ('FH',BASE/'fh-recovered-windows-r18-awb-oracle'/'ORACLE-PAIRS.txt','FA_GA ','FA_PUB ',list(range(4,19))),
 ('FW',FWLOG,'FW_GA ','FW_PUB ',list(range(4,22))),
]
rows={}
for name,path,gp,pp,reqs in sets:
    rows[name]=replay(name,path,gp,pp,reqs)

table=FY.stored_calibration_table()
factor_bits=[[f'0x{FY.bits(a):08x}',f'0x{FY.bits(b):08x}'] for a,b in table]
need(factor_bits[:4]==[['0x3f7ebcac','0x3f79a47c']]*4,'high stored factors')
need(factor_bits[4:7]==[['0x3f7f2038','0x3f7a40d6']]*3,'mid stored factors')
need(factor_bits[7:]==[['0x3f7f66ed','0x3f7b3bff']]*3,'low stored factors')

out={
 'schema':'sp11-e003i-fy-calibrated-awb-selector-replay-v1',
 'status':'PASS_FX_SELECTOR_OBJECT_AND_EG_FA_FH_FW_BIT_EXACT',
 'profile':'SP11_front_IMX681_normal_preview',
 'selector_rule':'refPtV1 multiplied by same-device EJ/EK stored ComputeCalFactors before CSFStatDistV1 geometry',
 'stored_factor_bits':factor_bits,
 'fx':{'object_sha256':FX_SHA,'bytes':len(obj),'boundaries_bit_exact':f'{bmatch}/8',
       'search_lines_bit_exact':f'{smatch}/8','lengths_bit_exact':f'{lmatch}/8',
       'boundary_bits':boundary_bits,'search_bits':search_bits,'length_bits':length_bits},
 'windows_replays':{
   name:{'requests':[x['request'] for x in r],'slots':[x['slot'] for x in r],
         'bit_exact':f'{len(r)}/{len(r)}'} for name,r in rows.items()
 },
 'authority':{'EK':'live Linux physical 12-byte OTP read','EJ':'clean 10-slot ComputeCalFactors replay',
              'FX':'first-call configured CSFStatDistV1 object dump'},
 'historical_fb_modified':False,
 'windows_streams_added_by_fy':0,
 'linux_camera_runtime_performed_by_fy':False,
}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('FY_FX_BOUNDARIES=8/8 PASS')
print('FY_FX_SEARCH_LINES=8/8 PASS')
print('FY_FX_LENGTHS=8/8 PASS')
print('FY_EG=8/8 PASS')
print('FY_FA=9/9 PASS')
print('FY_FH=15/15 PASS')
print('FY_FW=18/18 PASS')
print('FY_VERIFY=PASS')
