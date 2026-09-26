#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
J=REPO/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/j-cleanroom-gtm'
GEN=J/'generate-cleanroom-gtm-wire.py'
RANGES={
 'HDR':(0x0008,0x0c),'MODE':(0x0074,0x04),'BLEND':(0x109c,0x08),
 'SRC':(0x5104,0x1c),'DST':(0x5120,0x1c),'COEF':(0x51b0,0x3c),
 'DOMAIN':(0x6228,0x1000),
}
SIZES={'GTM_COMMON':0x7c,'GTM_REGION':0x404,'GTM_FLAGS':4,'GTM_AUX':2,'GTM_OUT':0x800,
       **{f'TMC_{k}':n for k,(_,n) in RANGES.items()}}

def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(bytes(b)).hexdigest()
def u32(b,o=0):return struct.unpack_from('<I',b,o)[0]
def u16(b,o=0):return struct.unpack_from('<H',b,o)[0]
def f32bits(b,o):return struct.unpack_from('<I',b,o)[0]
def get(cap,r,name):
 p=cap/f'R{r:02d}_{name}.bin'
 if not p.is_file():raise RuntimeError(f'missing {p.name}')
 b=p.read_bytes()
 if len(b)!=SIZES[name]:raise RuntimeError(f'{p.name} size {len(b)} != {SIZES[name]}')
 return b
def classify(seq):
 if len(set(seq))==1:return 'stable'
 a=seq[0::2];b=seq[1::2]
 if len(set(a))==1 and len(set(b))==1 and a[0]!=b[0]:return 'two_cycle'
 return 'evolving'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('capture_dir',type=Path);ap.add_argument('--result',type=Path,default=HERE/'SAFE-ANALYSIS.json');a=ap.parse_args()
 G=load(GEN,'e007j_gtm');domain=G.load_domain(J);rows=[]
 for req in range(4,19):
  common=get(a.capture_dir,req,'GTM_COMMON');region=get(a.capture_dir,req,'GTM_REGION')
  flags=get(a.capture_dir,req,'GTM_FLAGS');aux=get(a.capture_dir,req,'GTM_AUX')
  want=get(a.capture_dir,req,'GTM_OUT');pieces={k:get(a.capture_dir,req,f'TMC_{k}') for k in RANGES}
  tmc=bytearray(0x7228)
  for k,(off,n) in RANGES.items():tmc[off:off+n]=pieces[k]
  branch=(u32(tmc,8),u32(tmc,0xc),u32(tmc,0x10),u32(tmc,0x74),u32(common,0x34),u16(common,0x2a),common[0x70])
  if branch!=(5,0x60800,1,2,0x60800,1,1):raise RuntimeError(f'R{req} GTM branch drift {branch!r}')
  if f32bits(common,0x74)!=0x3f59999a or f32bits(common,0x78)!=0x3f800000:raise RuntimeError(f'R{req} strength/power drift')
  if pieces['BLEND']!=b'\0'*8:raise RuntimeError(f'R{req} nonzero TMC blend: clean backend expansion required')
  got=G.generate(bytes(tmc),domain)
  if got!=want:raise RuntimeError(f'R{req} clean GTM mismatch bytes={sum(x!=y for x,y in zip(got,want))}')
  dynamic=pieces['MODE']+pieces['BLEND']+pieces['SRC']+pieces['DST']+pieces['COEF']+pieces['DOMAIN']
  norm=bytearray(common);bank=norm[0x14];norm[0x14]=0
  rows.append({
   'request':req,'clean_replay':'PASS','bank_byte':bank,
   'gtm_out_sha256':sha(want),'tmc_dynamic_sha256':sha(dynamic),
   'tmc_src_sha256':sha(pieces['SRC']),'tmc_dst_sha256':sha(pieces['DST']),
   'tmc_coef_sha256':sha(pieces['COEF']),'tmc_domain_sha256':sha(pieces['DOMAIN']),
   'common_normalized_sha256':sha(norm),'region_sha256':sha(region),
   'flags_sha256':sha(flags),'aux_sha256':sha(aux),
  })
 post=[x for x in rows if x['request']>=6]
 def law(key):return classify([x[key] for x in post])
 result={
  'schema':'E007j-rear-gtm-tmc-safe-analysis-v1','status':'PASS_WINDOWS_ORACLE',
  'requests':list(range(4,19)),'clean_gtm_replay':'15/15 PASS',
  'post_r6_tmc_state_law':law('tmc_dynamic_sha256'),
  'post_r6_gtm_output_law':law('gtm_out_sha256'),
  'post_r6_region_law':law('region_sha256'),'post_r6_flags_law':law('flags_sha256'),
  'post_r6_aux_law':law('aux_sha256'),'post_r6_common_normalized_law':law('common_normalized_sha256'),
  'post_r6_bank_values':[x['bank_byte'] for x in post],
  'post_r6_distinct_tmc_states':len(set(x['tmc_dynamic_sha256'] for x in post)),
  'post_r6_distinct_gtm_outputs':len(set(x['gtm_out_sha256'] for x in post)),
  'rows':rows,'raw_capture_values_committed':False,'linux_camera_runtime':False,
 }
 a.result.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('E007J_CLEAN_GTM_REPLAY=15/15 PASS')
 print('E007J_POST_R6_TMC_LAW='+result['post_r6_tmc_state_law'])
 print('E007J_POST_R6_GTM_LAW='+result['post_r6_gtm_output_law'])
 print('E007J_DISTINCT_TMC='+str(result['post_r6_distinct_tmc_states']))
 print('E007J_DISTINCT_GTM='+str(result['post_r6_distinct_gtm_outputs']))
 print('E007J_ANALYZE=PASS raw_values_emitted=false')
if __name__=='__main__':main()
