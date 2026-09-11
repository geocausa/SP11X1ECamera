#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
J=BASE/'j-cleanroom-gtm'
GEN=J/'generate-cleanroom-gtm-wire.py'

RANGES={
 'HDR':(0x0008,0x0c),
 'MODE':(0x0074,0x04),
 'BLEND':(0x109c,0x08),
 'SRC':(0x5104,0x1c),
 'DST':(0x5120,0x1c),
 'COEF':(0x51b0,0x3c),
 'DOMAIN':(0x6228,0x1000),
}
SIZES={'GTM_COMMON':0x7c,'GTM_REGION':0x404,'GTM_FLAGS':4,'GTM_AUX':2,'GTM_OUT':0x800,
       **{f'TMC_{k}':n for k,(_,n) in RANGES.items()}}

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(b): return hashlib.sha256(bytes(b)).hexdigest()
def u32(b,o=0): return struct.unpack_from('<I',b,o)[0]
def u16(b,o=0): return struct.unpack_from('<H',b,o)[0]
def f32bits(b,o): return struct.unpack_from('<I',b,o)[0]
def get(cap:Path,r:int,name:str):
    p=cap/f'R{r:02d}_{name}.bin'
    if not p.is_file(): raise RuntimeError(f'missing {p.name}')
    b=p.read_bytes()
    if len(b)!=SIZES[name]: raise RuntimeError(f'{p.name} size {len(b)} != {SIZES[name]}')
    return b

def classify(seq):
    if len(set(seq))==1:return 'stable'
    a=seq[0::2];b=seq[1::2]
    if len(set(a))==1 and len(set(b))==1 and a[0]!=b[0]:return 'two_cycle'
    return 'evolving'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('capture_dir',type=Path)
    ap.add_argument('--result',type=Path,default=HERE/'RESULT.json')
    a=ap.parse_args()
    G=load(GEN,'eb_gtm')
    domain=G.load_domain(J)
    rows=[]
    for r in range(4,13):
        common=get(a.capture_dir,r,'GTM_COMMON')
        region=get(a.capture_dir,r,'GTM_REGION')
        flags=get(a.capture_dir,r,'GTM_FLAGS')
        aux=get(a.capture_dir,r,'GTM_AUX')
        want=get(a.capture_dir,r,'GTM_OUT')
        pieces={k:get(a.capture_dir,r,f'TMC_{k}') for k in RANGES}
        tmc=bytearray(0x7228)
        for k,(off,n) in RANGES.items():tmc[off:off+n]=pieces[k]

        branch=(u32(tmc,0x08),u32(tmc,0x0c),u32(tmc,0x10),u32(tmc,0x74),
                u32(common,0x34),u16(common,0x2a),common[0x70])
        if branch!=(5,0x60800,1,2,0x60800,1,1):
            raise RuntimeError(f'R{r} GTM branch drift {branch!r}')
        if f32bits(common,0x74)!=0x3f59999a or f32bits(common,0x78)!=0x3f800000:
            raise RuntimeError(f'R{r} common strength/power drift')
        if pieces['BLEND']!=b'\0'*8:
            raise RuntimeError(f'R{r} nonzero TMC blend unsupported by current clean replay')
        got=G.generate(bytes(tmc),domain)
        if got!=want:
            diffs=sum(x!=y for x,y in zip(got,want))
            raise RuntimeError(f'R{r} clean GTM mismatch bytes={diffs}')

        dynamic=pieces['MODE']+pieces['BLEND']+pieces['SRC']+pieces['DST']+pieces['COEF']+pieces['DOMAIN']
        rows.append({
          'request':r,
          'gtm_out_sha256':sha(want),
          'tmc_dynamic_sha256':sha(dynamic),
          'tmc_src_sha256':sha(pieces['SRC']),
          'tmc_dst_sha256':sha(pieces['DST']),
          'tmc_coef_sha256':sha(pieces['COEF']),
          'tmc_domain_sha256':sha(pieces['DOMAIN']),
          'common_sha256':sha(common),
          'region_sha256':sha(region),
          'flags_sha256':sha(flags),
          'aux_sha256':sha(aux),
          'clean_replay':'PASS'
        })
    post=[x for x in rows if x['request']>=6]
    dynamic_seq=[x['tmc_dynamic_sha256'] for x in post]
    output_seq=[x['gtm_out_sha256'] for x in post]
    state_law=classify(dynamic_seq)
    output_law=classify(output_seq)
    result={
      'schema':'sp11-e003i-eb-windows-r4-r12-gtm-state-oracle-v1',
      'status':'PASS_WINDOWS_ORACLE',
      'requests':[4,5,6,7,8,9,10,11,12],
      'raw_capture_committed':False,
      'clean_gtm_replay':'9/9 PASS',
      'post_r6_tmc_state_law':state_law,
      'post_r6_gtm_output_law':output_law,
      'post_r6_distinct_tmc_states':len(set(dynamic_seq)),
      'post_r6_distinct_gtm_outputs':len(set(output_seq)),
      'rows':rows,
      'next_gate':('R6 carry-forward may be considered only after checking all other IQ scalars/LSC state'
                   if state_law=='stable' and output_law=='stable' else
                   'derive request7+ TMC recurrence/producer inputs; do not freeze R6'),
      'linux_camera_runtime':False,
      'continuous_aec_claimed':False
    }
    a.result.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('EB_CLEAN_GTM_REPLAY=9/9 PASS')
    print('EB_POST_R6_TMC_LAW='+state_law)
    print('EB_POST_R6_GTM_LAW='+output_law)
    print('EB_DISTINCT_TMC='+str(result['post_r6_distinct_tmc_states']))
    print('EB_DISTINCT_GTM='+str(result['post_r6_distinct_gtm_outputs']))
    print('EB_ANALYZE=PASS')

if __name__=='__main__':main()
