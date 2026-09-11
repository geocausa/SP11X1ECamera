#!/usr/bin/env python3
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,struct,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent; BASE=HERE.parent
ELP=BASE/'el-calibrated-awb-scalar-join'/'awb_scalar.py'; EN=BASE/'en-r5-r9-producer-integration'; EO=BASE/'eo-bounded-live-r5-r9-runtime'
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;assert s.loader;s.loader.exec_module(m);return m
EL=load(ELP,'ep_el')
def need(v,m):
 if not v: raise AssertionError(m)
def fb(h):return struct.unpack('<f',struct.pack('<I',int(h,16)))[0]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((HERE/'EO-ATTEMPT1-REPLAY.json').read_text())
f=json.loads((EO/'ATTEMPT1-FAILURE.json').read_text())
need(f['status']=='CONSUMED_FAIL_CLOSED_R9_SELECTOR' and f['identity_retired'] and f['golden_return'],'EO consumed authority')
# Exact old failure boundary, independent of runtime files.
core=EL.CalibratedAWB(); core.current_triangle=10
g=core.run(fb('3f2146a9'),fb('3ee089b0'),fb('43b4acde'),fb('4584f583'),1.0)
need(g['gain_adjust']['triangle']==16,'G6 must traverse 10->8->16')
need([int(x,16) for x in g['gain_adjust']['final_bits']]==[0x3f8147ae,0x3f7fffff,0x3f7ae148],'G6 GA RGB')
need([EL.bits(g[k]) for k in ('R','G','B')]==[0x3fcd361f,0x3f800000,0x400f0441],'G6 published gains')
need(g['registers']=={0x3d78:0x19a7,0x3d7c:0x23c1,0x3d80:0x09fb,0x3d84:0x0729,0x4568:0x08000000,0x456c:0x11e00000,0x4570:0x0cd40000},'G6 scalar words')
# Compact replay record itself must show R5-R8 exact live preservation and corrected R9.
rows={r['request_target']:r for r in a['rows'] if r['request_target'] is not None}
for req,h in a['live_submitted_sha256'].items(): need(rows[int(req)]['capsule_sha256']==h,f'R{req} live replay regression')
need(rows[9]['capsule_sha256']==a['corrected_r9_sha256'],'R9 corrected replay hash')
need(rows[9]['awb_triangle']==16,'R9 replay triangle')
# When the external EO archive is present, rerun the real EN producer over all six live snapshots.
arc=Path(a['archive']); full=False
if arc.is_dir():
 sums=arc/'SHA256SUMS.txt';need(sums.is_file() and sha(sums)==a['archive_sha256s_sha256'],'EO archive checksum manifest')
 src=arc/'runtime-output'
 for i in range(6):
  need(sha(src/f'STATS3A-{i}.bin')==a['stats3a_sha256'][i],f'archive STATS3A G{i+1}')
  need(sha(src/f'TLBG-{i}.bin')==a['tlbg_sha256'][i],f'archive TLBG G{i+1}')
 with tempfile.TemporaryDirectory(prefix='ep-eo-replay-') as td:
  td=Path(td); snap=td/'snap';snap.mkdir();out=td/'out';out.mkdir();man=td/'manifest.json';gm=td/'gain.json'
  for i in range(6):
   shutil.copy2(src/f'STATS3A-{i}.bin',snap/f'STATS3A-{i}.bin');shutil.copy2(src/f'TLBG-{i}.bin',snap/f'TLBG-{i}.bin')
  gm.write_text(json.dumps({'schema':'ep-eo-live-gains-v1','cq_gain_bits':a['cq_gain_bits']})+'\n')
  cp=subprocess.run([sys.executable,str(EN/'live-iq-producer.py'),'--mode','offline','--snapshot-dir',str(snap),'--gain-manifest',str(gm),'--output-dir',str(out),'--manifest',str(man)],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  need(cp.returncode==0 and 'E003I_EN_PRODUCER=PASS' in cp.stdout,'real EN replay failed: '+cp.stdout[-1200:])
  m=json.loads(man.read_text());rr={r['request_target']:r for r in m['rows'] if r['request_target'] is not None}
  for req,h in a['live_submitted_sha256'].items():need(rr[int(req)]['capsule_sha256']==h,f'archive R{req} byte regression')
  need(rr[9]['capsule_sha256']==a['corrected_r9_sha256'] and rr[9]['awb_triangle']==16,'archive corrected R9')
  full=True
out={'schema':'sp11-e003i-ep-gainadj-multiside-r9-replay-v1','status':'PASS_EO_R9_SELECTOR_CLOSURE','eo_g6_path':'10->8->16','eo_g6_triangle':16,'eo_g6_ga_bits':['0x3f8147ae','0x3f7fffff','0x3f7ae148'],'eo_g6_published_gain_bits':['0x3fcd361f','0x3f800000','0x400f0441'],'r5_r8_live_byte_regression':'4/4','corrected_r9_capsule_sha256':a['corrected_r9_sha256'],'external_archive_full_replay':full,'true_two_vertex_fallback_proven':False,'linux_camera_runtime_performed_by_ep':False}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
