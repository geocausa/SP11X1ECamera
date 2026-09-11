#!/usr/bin/env python3
from pathlib import Path
import hashlib,importlib.util,json,math,re,struct,subprocess,sys,tempfile
D=Path(__file__).resolve().parent;B=D.parent;O=D/'runtime-output';P=O/'producer'
ENFILE=B/'en-r5-r9-live-producer-integration/live-iq-producer.py'
GTM_SHA='074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa'
def need(v,m):
    if not v: raise AssertionError(m)
def sha_bytes(b): return hashlib.sha256(bytes(b)).hexdigest()
def sha(p): return sha_bytes(p.read_bytes())
def frombits(u): return struct.unpack('<f',struct.pack('<I',u))[0]
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;assert s.loader;s.loader.exec_module(m);return m
EN=load(ENFILE,'eo_en_replay')
run=(O/'RUN.txt').read_text(errors='replace');dmesg=(D/'DMESG.txt').read_text(errors='replace');tx=(O/'CONTROL-TRANSACTION.txt').read_text(errors='replace')
need('HELPER_RC=0' in run,'helper rc');need('STREAMON_OK_ASYNC' in run and 'STREAMOFF_OK' in run,'stream lifecycle')
need('DB_AEC_SCHEDULE_PASS ACCEPTED_G=1..6 WRITES=3 RELEASE=G1@G2,G2@G3,G3@G4 EFFECT=G4,G5,G6' in run,'schedule pass')
need('PINNED_FOR_REBOOT:' not in run,'helper pinned')
for bad in ('DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','DZ_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL','EN_GAIN_FEED_FAIL','E003I_EN_PRODUCER=FAIL'):
    need(bad not in run,bad)
for i in range(6):
    need(re.search(rf'DQBUF{i}_INDEX=\d+ BYTESUSED=7778304 SEQUENCE={i}\b',run),f'dqbuf{i}')
    need(f'DB_VIDEO_COMPLETION_PUBLISH G={i+1}' in run,f'completion G{i+1}')
    need(re.search(rf'TLBG_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=61472\b',run),f'tlbg{i}')
    need(re.search(rf'STATS3A_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=331840\b',run),f'stats{i}')
# Parent AEC/CQ rows.
accept=[];pat=r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+) FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) ISP=0x([0-9a-fA-F]{8}) RELEASED_AT_G=(\d+) RELEASE_SOURCE=(\d+) EFFECT=(\d+)'
for m in re.finditer(pat,run):
    g,request,fll,vb,exp,again,dgain,isp,released,source,effect=m.groups();accept.append((int(g),int(request),int(fll),int(vb),int(exp),int(again),int(dgain),int(isp,16),int(released),int(source),int(effect)))
need(len(accept)==6,'six AEC accepts')
for idx,r in enumerate(accept,1):
    g,request,fll,vb,exp,again,dgain,isp,released,source,effect=r;need((g,request)==(idx,g+3),f'ownership G{g}')
    need(fll>=2160 and vb==fll-2160 and 4<=exp<=((fll-4)&~1),f'geometry G{g}');need(0<=again<=0x3c0 and 0x100<=dgain<=0xf00,f'gains G{g}')
    gain=frombits(isp);need(math.isfinite(gain) and gain>0,f'ISP G{g}')
    if g==1 or g>=5:need((released,source,effect)==(0,0,0),f'no release G{g}')
    else:need((released,source,effect)==(g,g-1,g+2),f'release G{g}')
# Exact three sensor writes remain unchanged.
writes=[];wpat=r'DB_SENSOR_WRITE_OK SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) START_NS=(\d+) END_NS=(\d+) ELAPSED_NS=(\d+) COMPLETED_G=(\d+)'
for m in re.finditer(wpat,run):writes.append(tuple(map(int,m.groups())))
need(len(writes)==3,'three sensor writes')
for n,r in enumerate(writes,1):
    source,after,request,effect,fll,exp,again,dgain,start,end,elapsed,completed=r
    need((source,after,request,effect)==(n,n+1,n+3,n+3),f'write schedule {n}');need(end>=start and elapsed==end-start and completed==after,f'write timing {n}')
    need(re.search(rf'DB_VIDEO_GATE_PASS SOURCE={source} AFTER_G={after} COMPLETED_G={after}\b',run),f'gate {n}')
    need(f'FLL={fll} exposure={exp} again=0x{again:03x} dgain=0x{dgain:04x} ret=0' in tx,f'hardware tx {n}')
# Producer: six gain records, five submissions.
producer=json.loads((P/'RESULT.json').read_text());need(producer['schema']=='sp11-e003i-en-r5-r9-live-producer-v1','producer schema');need(producer['status']=='PASS','producer status')
rows=producer['rows'];need([(r['generation'],r['request_target']) for r in rows]==[(1,None),(2,5),(3,6),(4,7),(5,8),(6,9)],'producer mapping')
for r in rows:
    g=r['generation'];bitsv=accept[g-1][7];expect=f'0x{bitsv:08x}';need(r['cq_isp_gain_bits']==expect,f'CQ G{g}');need(r['gain_feed']['generation']==g and r['gain_feed']['request']==g+3 and r['gain_feed']['isp_gain_bits']==expect,f'feed G{g}');need(0<=r['gain_wait_ms']<5000,f'gain wait G{g}')
    if g==1:need(r.get('submitted_live') is not True,'G1 submission')
    else:
        req=g+3;need(r.get('submitted_live') is True,f'R{req} not submitted');need(r['composer_kind']==('EA_R5_R6_COMPAT' if req<=6 else 'EM_POST_R6'),f'R{req} composer')
        need(re.search(rf'EN_R{req}_SUBMITTED_FROM_G{g}\b',run),f'R{req} submit log')
# Same-scene independent replay from the live run's saved evidence.
with tempfile.TemporaryDirectory(prefix='e003i-eo-replay-') as td:
    replay=EN.Producer(Path(td));replay_hash={}
    for g in range(1,7):
        sb=(P/f'STATS3A-G{g}.bin').read_bytes();tb=(P/f'TLBG-G{g}.bin').read_bytes();gain=frombits(accept[g-1][7]);rr,cap,_=replay.process(sb,tb,gain)
        need(rr['generation']==g,f'replay G{g}')
        if g>=2:
            req=g+3;actual=P/f'R{req}-dynamic.bin';need(actual.is_file() and actual.stat().st_size==41088,f'R{req} saved capsule');need(cap==actual.read_bytes(),f'R{req} same-scene replay mismatch');need(sha(actual)==rows[g-1]['capsule_sha256'],f'R{req} manifest hash');replay_hash[str(req)]=sha(actual)
# For new R7-R9, GTM payload must remain the EB post-R6 authority.
def payload(cap:bytes,want_idx:int):
    nsec=struct.unpack_from('<I',cap,20)[0]
    for i in range(nsec):
        typ,idx,off,n=struct.unpack_from('<IIII',cap,64+i*16)
        if typ==5 and idx==want_idx:return cap[off:off+n]
    raise AssertionError(f'payload {want_idx} absent')
for req in (7,8,9):
    b=(P/f'R{req}-dynamic.bin').read_bytes();gtm=payload(b,6);need(len(gtm)==0x800 and sha_bytes(gtm)==GTM_SHA,f'R{req} GTM')
# Capture/control/kernel health.
pre=(O/'CONTROLS-AFTER.txt').read_text(errors='replace')
for x in ('vertical_blanking: 1402','exposure: 3554','analogue_gain: 0','digital_gain: 256'):need(x in pre,'bootstrap '+x)
need('FLL=3562 exposure=3554 again=0x000 dgain=0x0100 ret=0' in tx,'bootstrap tx')
post=(O/'CONTROLS-POST-AEC.txt').read_text(errors='replace');last=writes[-1];_,_,_,_,lfll,lexp,lagain,ldgain,*_=last
for x in (f'vertical_blanking: {lfll-2160}',f'exposure: {lexp}',f'analogue_gain: {lagain}',f'digital_gain: {ldgain}'):need(x in post,'post '+x)
for bad in ('TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic'):need(bad.lower() not in dmesg.lower(),'kernel '+bad)
hashes={'qc10c':[],'tlbg':[],'stats3a':[]}
for i in range(6):
    for key,prefix,size in [('qc10c','QC10C',7778304),('tlbg','TLBG',61472),('stats3a','STATS3A',331840)]:
        p=O/f'{prefix}-{i}.bin';need(p.is_file() and p.stat().st_size==size,f'{prefix}-{i}');hashes[key].append(sha(p))
result={'schema':'sp11-e003i-eo-bounded-r5-r9-live-v1','status':'PASS_CAPTURE_EO_R5_R9_SUBMISSIONS','runtime_performed':True,'same_boot_retry_performed':False,
 'producer_gain_crosscheck':'6/6','iq_submissions':'R5-R9 5/5','postrun_same_scene_replay':'5/5 byte-exact','r7_r9_gtm_stable':True,'gtm_sha256':GTM_SHA,
 'streamoff':True,'kernel_health':'PASS','post_g6_application_observed':False,'continuous_unrestricted_aec_proven':False,'capsule_sha256':replay_hash,
 'generations':[{'generation':r[0],'request_frame':r[1],'frame_length_lines':r[2],'vertical_blanking':r[3],'exposure_lines':r[4],'analogue_gain_code':r[5],'digital_gain_code':r[6],'isp_gain_bits':f'0x{r[7]:08x}','released_at_generation':r[8],'release_source_generation':r[9],'expected_effect_generation':r[10]} for r in accept],
 'capture_sha256':hashes,'golden_return_required':True}
(O/'LIVE-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('EO_LIVE_GENERATIONS=6');print('EO_PARENT_PRODUCER_GAIN_BITS=6/6 PASS');print('EO_IQ_SUBMISSIONS=R5-R9 5/5 PASS');print('EO_SAME_SCENE_REPLAY=5/5 BYTE_EXACT');print('EO_R7_R9_GTM=PASS');print('EO_SENSOR_WRITES=3 STREAMOFF=PASS KERNEL_HEALTH=PASS');print('EO_CAPTURE_VERIFY=PASS')
