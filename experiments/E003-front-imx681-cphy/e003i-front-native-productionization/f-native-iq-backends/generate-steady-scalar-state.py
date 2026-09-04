#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,struct
from pathlib import Path

BANK_REGS={
 'PDPC':[0x3d58,0x3d5c],'LSC':[0x4358,0x435c],'GIC':[0x4758,0x475c],
 'BPC_ABF':[0x4958,0x495c],'GTM':[0x5a58,0x5a5c],'GAMMA':[0x5f58,0x5f5c],
 'DSX':[0xa058,0xa05c,0xa258,0xa25c],
}
EXPECTED_MATCHED_R6={
 0x3b70:0x04280428,0x3b74:0x04280428,
 0x3d78:0x00001c80,0x3d7c:0x00001efc,0x3d80:0x000008fc,0x3d84:0x00000843,
 0x456c:0x0f7e0000,0x4570:0x0e400000,
}

def round_half_up(v:float)->int:return int(math.floor(v+0.5))
def q_clamp(v:int,lo:int=0,hi:int=0xffffffff)->int:return max(lo,min(hi,v))

def wb(awbg:float,awbb:float,awbr:float,predictive_gain:float)->dict[int,int]:
 g=q_clamp(round_half_up(awbg*predictive_gain*1024.0),0,0x7fff)
 b=q_clamp(round_half_up(awbb*predictive_gain*1024.0),0,0x7fff)
 r=q_clamp(round_half_up(awbr*predictive_gain*1024.0),0,0x7fff)
 return {0x4568:g<<17,0x456c:b<<17,0x4570:r<<17}

def pdpc(awbg:float,awbb:float,awbr:float)->dict[int,int]:
 if awbg<=0 or awbb<=0 or awbr<=0:raise ValueError('AWB gains must be positive')
 vals=[awbr/awbg,awbb/awbg,awbg/awbr,awbg/awbb]
 q=[q_clamp(round_half_up(x*4096.0),0,0x3ffff) for x in vals]
 return dict(zip((0x3d78,0x3d7c,0x3d80,0x3d84),q))

def demux(dgain:float,black_level:list[int],channel_terms:list[float])->dict[int,int]:
 if len(black_level)!=4 or len(channel_terms)!=4:raise ValueError('Demux requires four BLS/channel terms')
 p2=[dgain*(16383.0/(16383.0-float(bl))) for bl in black_level]
 # Exact Bayer0 order from the Surface common calculation.
 norm=[p2[1]*channel_terms[1],p2[3]*channel_terms[0],p2[2]*channel_terms[2],p2[0]*channel_terms[3]]
 limit=31.999000549316406; mx=max(norm)
 if mx>limit:norm=[x*(limit/mx) for x in norm]
 q=[q_clamp(round_half_up(1024.0*x),0,0x7fff) for x in norm]
 return {0x3b70:((q[0]&0x7fff)<<16)|(q[1]&0x7fff),0x3b74:((q[3]&0x7fff)<<16)|(q[2]&0x7fff)}

def banks(request_id:int)->dict[int,int]:
 regular=(request_id+1)&1; inverse=request_id&1
 out={}
 for m,regs in BANK_REGS.items():
  v=inverse if m in ('GTM','GAMMA') else regular
  for r in regs:out[r]=v
 return out

def produce(state:dict)->dict:
 regs={};regs.update(demux(float(state['dgain']),list(state['black_level_terms']),list(state['channel_terms'])))
 regs.update(pdpc(float(state['awbg']),float(state['awbb']),float(state['awbr'])))
 regs.update(wb(float(state['awbg']),float(state['awbb']),float(state['awbr']),float(state['predictive_gain'])))
 return {'request_id':int(state['request_id']),'calculated_registers':{f'0x{k:04x}':f'0x{v:08x}' for k,v in sorted(regs.items())},
         'bank_registers':{f'0x{k:04x}':v for k,v in sorted(banks(int(state['request_id'])).items())}}

def main():
 here=Path(__file__).resolve().parent;repo=here.parents[3];prod=repo/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
 ap=argparse.ArgumentParser();ap.add_argument('--state',type=Path);ap.add_argument('--out',type=Path,default=Path('/tmp/e003i-scalar-state.json'));a=ap.parse_args()
 if a.state:state=json.loads(a.state.read_text())
 else:
  oracle=json.loads((prod/'surface-titan680-steady-packer-oracle.json').read_text());d=json.loads((prod/'demux-dgain-oracle.json').read_text())
  t=oracle['pdpc311']['request6']['trigger']; dr=d['request6_reproduction']
  state={'request_id':6,'awbg':t['AWBG'],'awbb':t['AWBB'],'awbr':t['AWBR'],'predictive_gain':1.0,
         'dgain':d['windows_frames']['6']['dgain_float'],'black_level_terms':d['chromatix_default']['black_level_terms'],
         'channel_terms':d['chromatix_default']['channel_terms']}
 result=produce(state);got={int(k,16):int(v,16) for k,v in result['calculated_registers'].items()}
 if not a.state:
  for reg,want in EXPECTED_MATCHED_R6.items():
   if got.get(reg)!=want:raise RuntimeError(f'matched R6 scalar mismatch 0x{reg:x}: {got.get(reg)} != {want}')
  # WB green is part of the packed range but not one of the 8 changing fields.
  if wb(state['awbg'],state['awbb'],state['awbr'],state['predictive_gain'])[0x4568]!=0x08000000:raise RuntimeError('WB green baseline drift')
 a.out.write_text(json.dumps({'schema':'sp11-e003i-steady-scalar-state-v1','input':state,'output':result},indent=2,sort_keys=True)+'\n')
 print('STEADY_SCALAR_BACKEND=PASS');print('CALCULATED_FIELDS=8/8');print('BANK_FIELDS=16');print('OUT',a.out)
if __name__=='__main__':main()
