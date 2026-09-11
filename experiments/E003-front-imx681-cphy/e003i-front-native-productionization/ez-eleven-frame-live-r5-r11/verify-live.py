#!/usr/bin/env python3
from pathlib import Path
import hashlib,importlib.util,json,math,re,struct,sys
D=Path(__file__).resolve().parent;BASE=D.parent;O=D/'runtime-output'
DVFILE=BASE/'dv-live-residual-isp-demux/demux_bls.py';EFILE=BASE/'e-template-free-capsule/build-template-free-0076-capsules.py';FFILE=BASE/'f-native-iq-backends/generate-steady-scalar-state.py'
GTM_SHA='074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa'
def need(v,m):
 if not v:raise AssertionError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def frombits(u):return struct.unpack('<f',struct.pack('<I',u))[0]
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;assert s.loader;s.loader.exec_module(m);return m
DV=load(DVFILE,'er_dv');E=load(EFILE,'er_e');F=load(FFILE,'er_f')
run=(O/'RUN.txt').read_text(errors='replace');dmesg=(D/'DMESG.txt').read_text(errors='replace');tx=(O/'CONTROL-TRANSACTION.txt').read_text(errors='replace')
need('HELPER_RC=0' in run,'helper rc');need('STREAMON_OK_ASYNC' in run and 'STREAMOFF_OK' in run,'stream lifecycle');need('E003I_EX_PRODUCER=PASS' in run,'EX producer pass')
for req,frame,slot in ((7,7,0),(8,8,1),(9,9,0),(10,10,1),(11,11,0)):
 need(f'E003I_ES_IQ_CONSUMED R={req} FRAME={frame} SLOT={slot}' in dmesg,f'kernel consume R{req}')
need('X1E front PIX completed provider-owned bounded eleven-frame live requeue' in dmesg,'eleven-frame kernel completion')
need('DB_AEC_SCHEDULE_PASS ACCEPTED_G=1..11 WRITES=3 RELEASE=G1@G2,G2@G3,G3@G4 EFFECT=G4,G5,G6' in run,'schedule pass');need('PINNED_FOR_REBOOT:' not in run,'helper pinned')
for bad in ('DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','DZ_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL','DZ_GAIN_FEED_FAIL','EN_GAIN_FEED_FAIL','E003I_EN_PRODUCER=FAIL','E003I_EX_PRODUCER=FAIL'):
 need(bad not in run,bad)
cycle=[0,1,2,3,0,1,2,3,0,1,2]
for i in range(11):
 need(re.search(rf'DQBUF{i}_INDEX={cycle[i]} BYTESUSED=7778304 SEQUENCE={i}\b',run),f'dqbuf{i}');need(f'DB_VIDEO_COMPLETION_PUBLISH G={i+1}' in run,f'completion G{i+1}')
 need(re.search(rf'TLBG_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=61472\b',run),f'tlbg{i}');need(re.search(rf'STATS3A_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=331840\b',run),f'stats{i}')
accept=[];pat=r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+) FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) ISP=0x([0-9a-fA-F]{8}) RELEASED_AT_G=(\d+) RELEASE_SOURCE=(\d+) EFFECT=(\d+)'
for m in re.finditer(pat,run):
 g,request,fll,vb,exp,again,dgain,isp,released,source,effect=m.groups();accept.append((int(g),int(request),int(fll),int(vb),int(exp),int(again),int(dgain),int(isp,16),int(released),int(source),int(effect)))
need(len(accept)==11,'eleven AEC accepts')
for idx,r in enumerate(accept,1):
 g,request,fll,vb,exp,again,dgain,isp,released,source,effect=r;need((g,request)==(idx,g+3),f'ownership G{g}');need(fll>=2160 and vb==fll-2160 and 4<=exp<=((fll-4)&~1),f'geometry G{g}');need(0<=again<=0x3c0 and 0x100<=dgain<=0xf00,f'gains G{g}');need(math.isfinite(frombits(isp)) and frombits(isp)>0,f'ISP G{g}')
 if g==1 or g>=5:need((released,source,effect)==(0,0,0),f'no release G{g}')
 else:need((released,source,effect)==(g,g-1,g+2),f'release G{g}')
writes=[];wpat=r'DB_SENSOR_WRITE_OK SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) START_NS=(\d+) END_NS=(\d+) ELAPSED_NS=(\d+) COMPLETED_G=(\d+)'
for m in re.finditer(wpat,run):writes.append(tuple(map(int,m.groups())))
need(len(writes)==3,'three sensor writes')
for n,r in enumerate(writes,1):
 source,after,request,effect,fll,exp,again,dgain,start,end,elapsed,completed=r;need((source,after,request,effect)==(n,n+1,n+3,n+3),f'write schedule {n}');need(end>=start and elapsed==end-start and completed==after,f'write timing {n}');need(re.search(rf'DB_VIDEO_GATE_PASS SOURCE={source} AFTER_G={after} COMPLETED_G={after}\b',run),f'gate {n}');need(f'FLL={fll} exposure={exp} again=0x{again:03x} dgain=0x{dgain:04x} ret=0' in tx,f'hardware tx {n}')
producer=json.loads((O/'producer/RESULT.json').read_text());need(producer['status']=='PASS' and producer['schema']=='sp11-e003i-ex-r5-r11-producer-v1','producer manifest')
rows=producer['rows'];need([(r['generation'],r['request_target']) for r in rows]==[(1,None),(2,5),(3,6),(4,7),(5,8),(6,9),(7,10),(8,11)],'producer mapping')
for r in rows:
 g=r['generation'];bitsv=accept[g-1][7];e=f'0x{bitsv:08x}';need(r['cq_isp_gain_bits']==e==r['gain_feed']['isp_gain_bits'],f'gain bits G{g}');need((r['gain_feed']['generation'],r['gain_feed']['request'])==(g,g+3),f'gain identity G{g}');need(0<=r['gain_wait_ms']<5000,f'gain wait G{g}')

def sections(b):
 n=struct.unpack_from('<I',b,20)[0];out={}
 for i in range(n):
  typ,idx,off,size=struct.unpack_from('<IIII',b,64+i*16);out[(typ,idx)]=b[off:off+size]
 return out
caps={};deadline={}
for g,req in ((2,5),(3,6),(4,7),(5,8),(6,9),(7,10),(8,11)):
 r=rows[g-1];need(r.get('submitted_live') is True,f'R{req} submitted');need(re.search(rf'EN_R{req}_SUBMITTED_FROM_G{g}\b',run),f'R{req} submit log')
 cap=O/'producer'/f'R{req}-dynamic.bin';need(cap.is_file() and cap.stat().st_size==41088,f'R{req} capsule');need(sha(cap)==r['capsule_sha256'],f'R{req} self hash')
 b=cap.read_bytes();sec=sections(b);module=sec.get((4,0));need(module is not None and len(module)==0x120,f'R{req} module')
 dm=DV.calculate(frombits(accept[g-1][7]));got70,got74=struct.unpack_from('<II',module,4);need((got70,got74)==(dm['reg_3b70'],dm['reg_3b74']),f'R{req} Demux module')
 meta=r['demux_bls'];need(meta['isp_gain_bits']==f'0x{accept[g-1][7]:08x}' and meta['reg_3b70']==f"0x{dm['reg_3b70']:08x}" and meta['reg_3b74']==f"0x{dm['reg_3b74']:08x}",f'R{req} Demux meta')
 if g>=4:
  regs=F.banks(req);regs.update({0x3b70:dm['reg_3b70'],0x3b74:dm['reg_3b74']});regs.update({int(k,16):int(v,16) for k,v in meta['awb_regs'].items()})
  need(meta['awb_triangle']==r['awb_triangle'],'AWB triangle meta')
  for reg,val in regs.items():
   mi,si=E.REG_SLOT[reg];got=struct.unpack_from('<I',module,mi*32+4+si*4)[0];need(got==val,f'R{req} module reg 0x{reg:x}')
  for idx,key in ((1,'lsc0_sha256'),(2,'lsc1_sha256'),(3,'lsc2_sha256'),(4,'gic_sha256')):need(hashlib.sha256(sec[(5,idx)]).hexdigest()==r['lsc'][key],f'R{req} {key}')
  need(hashlib.sha256(sec[(5,6)]).hexdigest()==GTM_SHA==meta['gtm_sha256'],f'R{req} GTM')
 pipeline=float(r['gain_wait_ms'])+float(r['total_process_ms'])+float(r.get('submit_ms',0.0));need(pipeline<33.333333,f'R{req} deadline {pipeline:.3f}ms');deadline[str(req)]=pipeline
 caps[str(req)]={'sha256':sha(cap),'isp_gain_bits':f'0x{accept[g-1][7]:08x}','reg_3b70':f"0x{dm['reg_3b70']:08x}",'reg_3b74':f"0x{dm['reg_3b74']:08x}",'pipeline_ms':pipeline}
pre=(O/'CONTROLS-AFTER.txt').read_text(errors='replace')
for x in ('vertical_blanking: 1402','exposure: 3554','analogue_gain: 0','digital_gain: 256'):need(x in pre,'bootstrap '+x)
need('FLL=3562 exposure=3554 again=0x000 dgain=0x0100 ret=0' in tx,'bootstrap hardware tx')
post=(O/'CONTROLS-POST-AEC.txt').read_text(errors='replace');last=writes[-1];_,_,_,_,lfll,lexp,lagain,ldgain,*_=last
for x in (f'vertical_blanking: {lfll-2160}',f'exposure: {lexp}',f'analogue_gain: {lagain}',f'digital_gain: {ldgain}'):need(x in post,'post '+x)
for bad in ('TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic'):need(bad.lower() not in dmesg.lower(),'kernel '+bad)
hashes={'qc10c':[],'tlbg':[],'stats3a':[]}
for i in range(11):
 for key,prefix,size in [('qc10c','QC10C',7778304),('tlbg','TLBG',61472),('stats3a','STATS3A',331840)]:
  p=O/f'{prefix}-{i}.bin';need(p.is_file() and p.stat().st_size==size,f'{prefix}-{i}');hashes[key].append(sha(p))
result={'schema':'sp11-e003i-ez-eleven-frame-live-r5-r11-v1','status':'PASS_CAPTURE_EZ_ELEVEN_FRAME_R5_R11','runtime_performed':True,'same_boot_retry_performed':False,'frames':11,'stats_generations':11,'requests':[5,6,7,8,9,10,11],'capsules':caps,'deadline_ms':deadline,'writes':[{'source_generation':r[0],'write_after_generation':r[1],'request_frame':r[2],'expected_effect_generation':r[3],'elapsed_ns':r[10]} for r in writes],'streamoff':True,'kernel_health':'PASS','golden_return_required':True,'capture_sha256':hashes,'continuous_unrestricted_aec_proven':False}
(O/'LIVE-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('EZ_LIVE_GENERATIONS=11');print('EZ_IQ_SUBMISSIONS=R5,R6,R7,R8,R9,R10,R11 PASS');print('EZ_SENSOR_WRITES=3 STREAMOFF=PASS KERNEL_HEALTH=PASS');print('EZ_MAX_PIPELINE_MS=%.6f'%max(deadline.values()));print('EZ_CAPTURE_VERIFY=PASS')
