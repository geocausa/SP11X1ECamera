#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,struct,sys

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
FBP=BASE/'fy-calibrated-awb-selector-replay'/'dynamic_awb.py'

def need(v,m):
    if not v:
        raise AssertionError(m)

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p)
    m=importlib.util.module_from_spec(s)
    sys.modules[n]=m
    assert s.loader
    s.loader.exec_module(m)
    return m

def fbits(h):
    return struct.unpack('<f',struct.pack('<I',int(h,16)))[0]

def kv(line):
    return dict(re.findall(r'(\w+)=([0-9A-Fa-f]+)',line))

ap=argparse.ArgumentParser()
ap.add_argument('log',type=Path)
ap.add_argument('--end-request',type=int,default=24)
ap.add_argument('--result',type=Path,default=HERE/'AWB-RESULT.json')
a=ap.parse_args()
need(4<=a.end_request<=24,'end request range')

s=a.log.read_text(errors='replace').replace('\r','')
ga_lines=[x.strip() for x in s.splitlines() if x.strip().startswith('GD_GA ')]
pub_lines=[x.strip() for x in s.splitlines() if x.strip().startswith('GD_PUB ')]
count=a.end_request-3
need(len(ga_lines)==len(pub_lines)==count,f'pair count ga={len(ga_lines)} pub={len(pub_lines)} expected={count}')

ga={int(kv(x)['req']):kv(x) for x in ga_lines}
pub={int(kv(x)['req']):kv(x) for x in pub_lines}
need(sorted(ga)==list(range(4,a.end_request+1)),'GA request coverage')
need(sorted(pub)==list(range(4,a.end_request+1)),'PUB request coverage')

FB=load(FBP,'fw_awb_fb')
core=FB.DynamicCalibratedAWB()
rows=[]
for req in range(4,a.end_request+1):
    x=ga[req]; p=pub[req]
    rg,bg,lux,cct=[fbits(x[k]) for k in ('rg','bg','lux','cct')]
    o=core.run(rg,bg,lux,cct,1.0)
    z=o['gain_adjust']
    need(z['triangle']==int(x['tri']),f'R{req} triangle')
    need(z['vertices']==[int(x[k]) for k in ('v0','v1','v2')],f'R{req} vertices')
    need([FB.bits(v) for v in z['weights']]==[int(x[k],16) for k in ('w0','w1','w2')],f'R{req} weights')
    need([FB.bits(v) for v in z['cct_rgb']]==[int(x[k],16) for k in ('cctr','cctg','cctb')],f'R{req} cct rgb')
    need([FB.bits(v) for v in z['final_rgb']]==[int(x[k],16) for k in ('ar','ag','ab')],f'R{req} final GA')
    got=[FB.bits(o[k]) for k in ('R','G','B')]
    exp=[int(p[k],16) for k in ('R','G','B')]
    need(got==exp,f'R{req} published RGB')
    rows.append({
      'request':req,
      'slot':o['calibration_slot'],
      'region':o['calibration_region'],
      'triangle':z['triangle'],
      'published_gain_bits':[f'0x{v:08x}' for v in got],
      'published_cct':int(p['CCT']),
    })

status=f'PASS_WINDOWS_AWB_R4_R{a.end_request}_{count}_OF_{count}_BIT_EXACT'
out={
  'schema':f'sp11-e003i-gd-windows-r4-r{a.end_request}-awb-v1',
  'status':status,
  'requests':list(range(4,a.end_request+1)),
  'bit_exact':f'{count}/{count}',
  'dynamic_slots':[r['slot'] for r in rows],
  'rows':rows,
  'oracle_log_sha256':hashlib.sha256(a.log.read_bytes()).hexdigest(),
  'continuous_aec_claimed':False,
}
a.result.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(f'GD_AWB_REPLAY={count}/{count} PASS')
print('GD_AWB_ANALYZE=PASS')
