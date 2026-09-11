#!/usr/bin/env python3
from pathlib import Path
import hashlib,importlib.util,json,os,struct,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
DZ=BASE/'dz-current-first-cq-publish-sensor-release';EA=BASE/'ea-current-first-full-aec-demux-loop';EM=BASE/'em-post-r6-template-free-composer'
ARCH=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ea/attempt1-pass-20260911T0348/runtime-output')
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
EN=load(HERE/'live-iq-producer.py','en_verify_prod')
def sha(b):return hashlib.sha256(bytes(b)).hexdigest()
def need(x,m):
 if not x: raise AssertionError(m)
def rd(p):
 try:return p.read_bytes()
 except PermissionError:return subprocess.check_output(['sudo','-n','cat',str(p)])
# Parent change is intentionally narrow; scheduler/feed ABI are byte-identical.
for f in ('gain-feed.c','gain-feed.h','native-db-schedule.c','native-db-schedule.h'):
 need(sha((HERE/f).read_bytes())==sha((DZ/f).read_bytes()),f'{f} drift')
s=(HERE/'e003i-en-six-frame-native-aec.c').read_text(); z=(DZ/'e003i-dz-six-frame-native-aec.c').read_text()
need('if (target <= 6U)' in s and 'if (target <= 3U)' not in s,'gain publish bound')
need('if (target >= 2U && target <= 4U)' in s,'sensor release window changed')
# Normalize the two intended edits and require exact DZ identity.
need(s.replace('if (target <= 6U) {','if (target <= 3U) {').replace('EN_GAIN_FEED_FAIL','DZ_GAIN_FEED_FAIL')==z,'parent source has extra changes')
# Strict helper build.
with tempfile.TemporaryDirectory(prefix='e003i-en-verify-') as td:
 out=Path(td)/'helper';subprocess.run([str(HERE/'build-helper.sh'),str(out)],check=True);need(out.exists(),'helper build')
 # Producer replay with actual accepted EA gain bits.
 work=Path(td)/'producer';p=EN.Producer(work)
 gains=[0x3f802d08,0x3f800544,0x3f801646,0x3f801646,0x3f801646,0x3f801646]
 expect={5:'818b65e439b3df9723ce2447e7f5d39f39a44c24cea35aa410bcef279393e4de',6:'7e6f2503165706b1f0f81069a33aae09244ccc5a1c5bc3ae6a8c3626d766199a',
         7:'681f17d83d289fba57548241bbb7db4219afbfde48495d680de969274720ea2e',8:'79804d678235f53429e4690c0d5e4a905873edde6652f002c878e2fad8634d2e',9:'1bd2e7cd98eb6ebc6c4161a34b3b8c72343d6e69232b11346f65496f79e33fda'}
 rows=[]
 for gen,u in enumerate(gains,1):
  sb=rd(ARCH/f'STATS3A-{gen-1}.bin');tb=rd(ARCH/f'TLBG-{gen-1}.bin');gain=struct.unpack('<f',struct.pack('<I',u))[0]
  row,cap,_=p.process(sb,tb,gain)
  if gen==1:need(cap is None and row['request_target'] is None,'G1 must not submit')
  else:
   req=gen+3;need(row['request_target']==req,'request target');need(sha(cap)==expect[req],f'R{req} capsule regression {sha(cap)}')
   need(row['composer_kind']==('EA_R5_R6_COMPAT' if req<=6 else 'EM_POST_R6'),f'R{req} composer kind')
  rows.append({'generation':gen,'request':row['request_target'],'gain_bits':f'0x{u:08x}','composer_kind':row['composer_kind'],'capsule_sha256':None if cap is None else sha(cap),'total_process_ms':row['total_process_ms'],'compose_ms':row['compose_ms'],'lsc':row['lsc'],'awb_scalar_registers':row['awb_scalar_registers']})
 # Six-record pipe ABI/order.
 rfd,wfd=os.pipe();gf=EN.GainFeed(rfd)
 for gen,u in enumerate(gains,1):
  os.write(wfd,EN.GAIN_RECORD.pack(EN.GAIN_MAGIC,EN.GAIN_VERSION,EN.GAIN_RECORD.size,gen,gen+3,u,0));g,meta=gf.get(gen,1000);need(EN.bits(g)==u and meta['request']==gen+3,f'gain feed G{gen}')
 os.close(wfd);os.close(rfd)
# Producer source must consume all six generations and keep old R5/R6 path separated from EM.
ps=(HERE/'live-iq-producer.py').read_text();need('for gen in (1,2,3,4,5,6):' in ps,'six-gen producer loop');need("if gen in (2,3):" in ps and "elif gen in (4,5,6):" in ps,'composer split')
em=json.loads((EM/'RESULT.json').read_text());need(em['status']=='PASS_OFFLINE_R7_R9_COMPOSITION','EM authority')
out={'schema':'sp11-e003i-en-r5-r9-live-producer-integration-v1','status':'PASS_OFFLINE_R5_R9_INTEGRATION','helper_strict_build':True,
 'parent_delta':'gain-feed publish bound G1..G3 -> G1..G6 only; sensor release schedule unchanged','gain_feed_records':'6/6',
 'r5_r6_regression':'2/2 byte-identical to EA live accepted capsules','r7_r9_regression':'3/3 exact EM deterministic hashes',
 'live_runtime_performed':False,'six_frame_video_loop_unchanged':True,'post_g6_application_observed':False,'continuous_aec_claimed':False,'rows':rows}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2))
