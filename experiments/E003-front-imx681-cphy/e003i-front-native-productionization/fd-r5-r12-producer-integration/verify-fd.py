#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,tempfile
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
EZ=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ez/attempt1-pass-eleven-frame-20260911T1429/runtime-output')
EX=BASE/'ex-r5-r11-producer-integration'
FC=BASE/'fc-nine-generation-gain-feed-publisher'/'RESULT.json'
FB=BASE/'fb-dynamic-awb-cal-slot-replay'/'RESULT.json'
EB=BASE/'eb-windows-r4-r12-gtm-state-oracle'/'RESULT.json'
ED=BASE/'ed-windows-r4-r12-tintless-trigger-staging-oracle'/'RESULT.json'
def need(x,m):
 if not x: raise AssertionError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(cmd,**kw):return subprocess.run(cmd,check=True,text=True,**kw)
live=json.loads((EZ/'LIVE-RESULT.json').read_text());need(live['status']=='PASS_CAPTURE_EZ_ELEVEN_FRAME_R5_R11','EZ live authority')
fc=json.loads(FC.read_text());need(fc['status']=='PASS_OFFLINE_G1_G9_C_PUBLISHER','FC authority')
fb=json.loads(FB.read_text());need(fb['status']=='PASS_EG_8_OF_8_FA_9_OF_9_BIT_EXACT','FB authority')
eb=json.loads(EB.read_text());need(eb['status']=='PASS_WINDOWS_ORACLE' and eb['post_r6_gtm_output_law']=='stable','EB R12 GTM authority')
ed=json.loads(ED.read_text());need(ed['status'].startswith('PASS') and ed['clean_lsc_replay']=='9/9 byte-exact LSC0/LSC1/LSC2/GIC','ED R12 LSC authority')
g={}
for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*?ISP=0x([0-9a-fA-F]{8})',(EZ/'RUN.txt').read_text()):
 gen,req,b=m.groups();gen=int(gen);req=int(req)
 if gen<=9:
  need(req==gen+3,f'EZ gain identity G{gen}');g[str(gen)]=f'0x{b.lower()}'
need(set(g)=={str(i) for i in range(1,10)},'EZ G1..G9 gain authority')
with tempfile.TemporaryDirectory(prefix='e003i-fd-') as td0:
 td=Path(td0);fo=td/'fd-out';eo=td/'ex-out';fo.mkdir();eo.mkdir()
 gm9=td/'g9.json';gm8=td/'g8.json';fm=td/'fd.json';em=td/'ex.json'
 gm9.write_text(json.dumps({'cq_gain_bits':g})+'\n');gm8.write_text(json.dumps({'cq_gain_bits':{k:v for k,v in g.items() if int(k)<=8}})+'\n')
 cp=run([str(HERE/'live-iq-producer.py'),'--mode','offline','--snapshot-dir',str(EZ),'--gain-manifest',str(gm9),'--output-dir',str(fo),'--manifest',str(fm)],capture_output=True)
 need('E003I_FD_PRODUCER=PASS' in cp.stdout,'FD producer marker')
 run([str(EX/'live-iq-producer.py'),'--mode','offline','--snapshot-dir',str(EZ),'--gain-manifest',str(gm8),'--output-dir',str(eo),'--manifest',str(em)],capture_output=True)
 f=json.loads(fm.read_text());e=json.loads(em.read_text())
 need(f['schema']=='sp11-e003i-fd-r5-r12-producer-v1' and f['status']=='PASS','FD manifest')
 need([(r['generation'],r['request_target']) for r in f['rows']]==[(1,None),(2,5),(3,6),(4,7),(5,8),(6,9),(7,10),(8,11),(9,12)],'G1..G9 mapping')
 expected_slots={5:5,6:5,7:5,8:5,9:5,10:5,11:5,12:5}
 for req in range(5,13):
  cap=fo/f'R{req}-dynamic.bin';need(cap.is_file() and cap.stat().st_size==41088,f'R{req} capsule')
  row=next(r for r in f['rows'] if r['request_target']==req)
  need(sha(cap)==row['capsule_sha256'],f'R{req} self hash')
  need(row['awb_calibration_slot']==expected_slots[req],f'R{req} dynamic calibration slot')
 # R5/R6 remain byte-exact to the already-live EZ capsules.
 for req in (5,6):
  need(sha(fo/f'R{req}-dynamic.bin')==live['capsules'][str(req)]['sha256'],f'R{req} EZ regression')
 # R7..R11 change only AWB-owned register words relative to the old EX replay.
 awb_regs=('0x3d78','0x3d7c','0x3d80','0x3d84','0x456c','0x4570')
 isolation={}
 for req in range(7,12):
  old=(eo/f'R{req}-dynamic.bin').read_bytes();new=(fo/f'R{req}-dynamic.bin').read_bytes()
  oldr=next(r for r in e['rows'] if r['request_target']==req);newr=next(r for r in f['rows'] if r['request_target']==req)
  pairs={(int(oldr['demux_bls']['awb_regs'][k],16),int(newr['demux_bls']['awb_regs'][k],16)) for k in awb_regs if oldr['demux_bls']['awb_regs'][k]!=newr['demux_bls']['awb_regs'][k]}
  words=sorted(set(i&~3 for i,(a,b) in enumerate(zip(old,new)) if a!=b))
  actual=[]
  import struct
  for off in words:
   pair=(struct.unpack_from('<I',old,off)[0],struct.unpack_from('<I',new,off)[0]);actual.append(pair);need(pair in pairs,f'R{req} non-AWB capsule delta @0x{off:x}')
  need(len(actual)==len(pairs),f'R{req} AWB delta cardinality')
  need(oldr['demux_bls']['gtm_sha256']==newr['demux_bls']['gtm_sha256'],'GTM unchanged')
  need(oldr['demux_bls']['reg_3b70']==newr['demux_bls']['reg_3b70'] and oldr['demux_bls']['reg_3b74']==newr['demux_bls']['reg_3b74'],'Demux unchanged')
  for k in ('x22_sha256','pretintless_sha256','tintless_output_sha256','lsc0_sha256','lsc1_sha256','lsc2_sha256','gic_sha256','cct_selector_mode','aec_selector_mode'):
   need(oldr['lsc'][k]==newr['lsc'][k],f'R{req} LSC field {k} changed')
  isolation[str(req)]={'changed_words':len(words),'awb_only':True}
 r12=next(r for r in f['rows'] if r['request_target']==12)
 need(r12['generation']==9 and r12['gain_feed']['request']==12,'R12 identity')
 need(r12['awb_triangle']==19 and r12['awb_calibration_slot']==5,'R12 AWB selector')
 need(r12['demux_bls']['gtm_sha256']=='074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa','R12 GTM')
 need(r12['lsc']['aec_selector_mode']=='lower_aec' and r12['lsc']['cct_selector_mode']=='leaf_0x4bd','R12 LSC selectors')
 out={'schema':'sp11-e003i-fd-r5-r12-producer-integration-v1','status':'PASS_OFFLINE_R5_R12_DYNAMIC_CAL_SLOT_INTEGRATION',
      'source':'EZ attempt1 PASS G1..G9 Linux snapshots + CQ gain observations',
      'requests':list(range(5,13)),'source_generations':list(range(2,10)),
      'r5_r6_live_regression':'2/2 exact EZ live capsule hashes',
      'r7_r11_correction_isolation':isolation,
      'dynamic_calibration_slots':{str(r['request_target']):r['awb_calibration_slot'] for r in f['rows'] if r['request_target']},
      'r12_capsule_sha256':sha(fo/'R12-dynamic.bin'),'r12_total_process_ms':r12['total_process_ms'],
      'r12_awb_triangle':r12['awb_triangle'],'r12_awb_slot':r12['awb_calibration_slot'],
      'r12_awb_regs':r12['demux_bls']['awb_regs'],'r12_lsc':r12['lsc'],'cq_gain_bits_g1_g9':g,
      'windows_component_authority':'EB GTM through R12 + ED LSC through R12 + FB dynamic AWB through R12',
      'whole_capsule_windows_r12_byte_oracle':False,'linux_camera_runtime_performed_by_fd':False,'continuous_aec_claimed':False}
 (HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2,sort_keys=True))
