#!/usr/bin/env python3
from pathlib import Path
import hashlib,importlib.util,json,math,re,struct

D=Path(__file__).resolve().parent
BASE=D.parent
O=D/'runtime-output'
DVFILE=BASE/'dv-live-residual-isp-demux/demux_bls.py'

def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def frombits(u): return struct.unpack('<f',struct.pack('<I',u))[0]
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
DV=load(DVFILE,'ea_dv')

run=(O/'RUN.txt').read_text(errors='replace')
dmesg=(D/'DMESG.txt').read_text(errors='replace')
tx=(O/'CONTROL-TRANSACTION.txt').read_text(errors='replace')
need('HELPER_RC=0' in run,'helper rc')
need('STREAMON_OK_ASYNC' in run and 'STREAMOFF_OK' in run,'stream lifecycle')
need('DB_AEC_SCHEDULE_PASS ACCEPTED_G=1..6 WRITES=3 RELEASE=G1@G2,G2@G3,G3@G4 EFFECT=G4,G5,G6' in run,'schedule pass')
need('PINNED_FOR_REBOOT:' not in run,'helper pinned')
for bad in ('DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','DZ_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL','DZ_GAIN_FEED_FAIL','E003I_DX_PRODUCER=FAIL'):
    need(bad not in run,bad)

for i in range(6):
    need(re.search(rf'DQBUF{i}_INDEX=\d+ BYTESUSED=7778304 SEQUENCE={i}\b',run),f'dqbuf{i}')
    need(f'DB_VIDEO_COMPLETION_PUBLISH G={i+1}' in run,f'completion G{i+1}')
    need(re.search(rf'TLBG_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=61472\b',run),f'tlbg{i}')
    need(re.search(rf'STATS3A_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=331840\b',run),f'stats{i}')

accept=[]
pat=r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+) FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) ISP=0x([0-9a-fA-F]{8}) RELEASED_AT_G=(\d+) RELEASE_SOURCE=(\d+) EFFECT=(\d+)'
for m in re.finditer(pat,run):
    g,request,fll,vb,exp,again,dgain,isp,released,source,effect=m.groups()
    accept.append((int(g),int(request),int(fll),int(vb),int(exp),int(again),int(dgain),int(isp,16),int(released),int(source),int(effect)))
need(len(accept)==6,'six DX AEC accepts')
for idx,r in enumerate(accept,1):
    g,request,fll,vb,exp,again,dgain,isp,released,source,effect=r
    need((g,request)==(idx,g+3),f'ownership G{g}')
    need(fll>=2160 and vb==fll-2160 and 4<=exp<=((fll-4)&~1),f'control geometry G{g}')
    need(0<=again<=0x3c0 and 0x100<=dgain<=0xf00,f'sensor gains G{g}')
    gain=frombits(isp);need(math.isfinite(gain) and gain>0,f'ISP gain G{g}')
    if g==1 or g>=5: need((released,source,effect)==(0,0,0),f'no release G{g}')
    else: need((released,source,effect)==(g,g-1,g+2),f'release G{g}')

writes=[]
wpat=r'DB_SENSOR_WRITE_OK SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) START_NS=(\d+) END_NS=(\d+) ELAPSED_NS=(\d+) COMPLETED_G=(\d+)'
for m in re.finditer(wpat,run): writes.append(tuple(map(int,m.groups())))
need(len(writes)==3,'three sensor writes')
for n,r in enumerate(writes,1):
    source,after,request,effect,fll,exp,again,dgain,start,end,elapsed,completed=r
    need((source,after,request,effect)==(n,n+1,n+3,n+3),f'write schedule {n}')
    need(end>=start and elapsed==end-start and completed==after,f'write timing {n}')
    need(re.search(rf'DB_VIDEO_GATE_PASS SOURCE={source} AFTER_G={after} COMPLETED_G={after}\b',run),f'gate {n}')
    needle=f'FLL={fll} exposure={exp} again=0x{again:03x} dgain=0x{dgain:04x} ret=0'
    need(needle in tx,f'hardware tx {n}')

producer=json.loads((O/'producer/RESULT.json').read_text())
need(producer['status']=='PASS','producer status')
need(producer['schema']=='sp11-e003i-dx-parent-cq-gain-feed-v1','producer schema')
rows=producer['rows'];need([(r['generation'],r['request_target']) for r in rows]==[(1,None),(2,5),(3,6)],'producer mapping')
for r in rows:
    g=r['generation'];parent=accept[g-1]
    expected_bits=f'0x{parent[7]:08x}'
    need(r['cq_isp_gain_bits']==expected_bits,f'producer parent ISP G{g}')
    need(r['gain_feed']['generation']==g and r['gain_feed']['request']==g+3,f'feed identity G{g}')
    need(r['gain_feed']['isp_gain_bits']==expected_bits,f'feed bits G{g}')
    need(r['gain_wait_ms']>=0 and r['gain_wait_ms']<5000,f'feed wait G{g}')

capsule_checks={}
for g,req in ((2,5),(3,6)):
    r=rows[g-1];need(r.get('submitted_live') is True,f'R{req} submitted')
    dm=DV.calculate(frombits(accept[g-1][7]))
    meta=r['demux_bls'];need(meta is not None,f'R{req} demux meta')
    e70=f"0x{dm['reg_3b70']:08x}";e74=f"0x{dm['reg_3b74']:08x}"
    need(meta['isp_gain_bits']==f'0x{accept[g-1][7]:08x}',f'R{req} demux gain')
    need((meta['reg_3b70'],meta['reg_3b74'])==(e70,e74),f'R{req} demux math')
    cap=O/'producer'/f'R{req}-dynamic.bin';need(cap.is_file() and cap.stat().st_size==41088,f'R{req} cap')
    b=cap.read_bytes();need(sha(cap)==r['capsule_sha256'],f'R{req} hash')
    nsec=struct.unpack_from('<I',b,20)[0];module=None
    for i in range(nsec):
        typ,idx,off,size=struct.unpack_from('<IIII',b,64+i*16)
        if typ==4 and idx==0: module=b[off:off+size]
    need(module is not None and len(module)==0x120,f'R{req} module')
    got70,got74=struct.unpack_from('<II',module,4)
    need((got70,got74)==(dm['reg_3b70'],dm['reg_3b74']),f'R{req} capsule Demux')
    capsule_checks[str(req)]={'sha256':sha(cap),'isp_gain_bits':f'0x{accept[g-1][7]:08x}','reg_3b70':e70,'reg_3b74':e74}

pre=(O/'CONTROLS-AFTER.txt').read_text(errors='replace')
for x in ('vertical_blanking: 1402','exposure: 3554','analogue_gain: 0','digital_gain: 256'): need(x in pre,'bootstrap '+x)
need('FLL=3562 exposure=3554 again=0x000 dgain=0x0100 ret=0' in tx,'bootstrap hardware tx')
post=(O/'CONTROLS-POST-AEC.txt').read_text(errors='replace')
last=writes[-1];_,_,_,_,lfll,lexp,lagain,ldgain,*_=last
for x in (f'vertical_blanking: {lfll-2160}',f'exposure: {lexp}',f'analogue_gain: {lagain}',f'digital_gain: {ldgain}'): need(x in post,'post '+x)
for bad in ('TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic'):
    need(bad.lower() not in dmesg.lower(),'kernel '+bad)

hashes={'qc10c':[],'tlbg':[],'stats3a':[]}
for i in range(6):
    for key,prefix,size in [('qc10c','QC10C',7778304),('tlbg','TLBG',61472),('stats3a','STATS3A',331840)]:
        p=O/f'{prefix}-{i}.bin';need(p.is_file() and p.stat().st_size==size,f'{prefix}-{i}');hashes[key].append(sha(p))

result={
 'schema':'sp11-e003i-ea-bounded-full-aec-demux-live-v1','status':'PASS_CAPTURE_EA_FULL_AEC_DEMUX',
 'runtime_performed':True,'same_boot_retry_performed':False,
 'generations':[{'generation':r[0],'request_frame':r[1],'frame_length_lines':r[2],'vertical_blanking':r[3],
                 'exposure_lines':r[4],'analogue_gain_code':r[5],'digital_gain_code':r[6],
                 'isp_gain_bits':f'0x{r[7]:08x}','released_at_generation':r[8],
                 'release_source_generation':r[9],'expected_effect_generation':r[10]} for r in accept],
 'writes':[{'source_generation':r[0],'write_after_generation':r[1],'request_frame':r[2],
            'expected_effect_generation':r[3],'frame_length_lines':r[4],'exposure_lines':r[5],
            'analogue_gain_code':r[6],'digital_gain_code':r[7],'elapsed_ns':r[10]} for r in writes],
 'iq_demux':capsule_checks,'gain_feed_crosscheck':'PASS','dv_recompute':'PASS',
 'streamoff':True,'kernel_health':'PASS','golden_return_required':True,'capture_sha256':hashes,
 'scope':'bounded six-frame native sensor AEC plus CQ residual ISP gain applied to Titan680 Demux/BLS R5/R6',
 'continuous_unrestricted_aec_proven':False
}
(O/'LIVE-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('EA_LIVE_GENERATIONS=6')
print('EA_PARENT_PRODUCER_GAIN_BITS=3/3 PASS')
print('EA_DV_DEMUX_CAPSULES=R5/R6 PASS')
print('EA_SENSOR_WRITES=3 STREAMOFF=PASS KERNEL_HEALTH=PASS')
print('EA_CAPTURE_VERIFY=PASS')
