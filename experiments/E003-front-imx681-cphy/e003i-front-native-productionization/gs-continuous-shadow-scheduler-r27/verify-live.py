#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,math,re,struct
D=Path(__file__).resolve().parent; O=D/'runtime-output'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def frombits(u): return struct.unpack('<f',struct.pack('<I',u))[0]
run=(O/'RUN.txt').read_text(errors='replace'); dmesg=(D/'DMESG.txt').read_text(errors='replace'); tx=(O/'CONTROL-TRANSACTION.txt').read_text(errors='replace')
need('HELPER_RC=0' in run,'helper rc'); need('STREAMON_OK_ASYNC' in run and 'STREAMOFF_OK' in run,'stream lifecycle'); need('E003I_GM_PRODUCER=PASS' in run,'GM producer')
need('GS_SHADOW_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 PHYSICAL_WRITES=G1..G3 SHADOW=G4..G26 PENDING=G27 EFFECT_RANGE=G4..G29' in run,'shadow schedule pass')
for bad in ('PINNED_FOR_REBOOT:','DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','GS_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL','EN_GAIN_FEED_FAIL','E003I_GM_PRODUCER=FAIL','GN_DQBUF_MISMATCH'):
    need(bad not in run,bad)
cycle=[0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2]
for i in range(27):
    need(re.search(rf'DQBUF{i}_INDEX={cycle[i]} BYTESUSED=7778304 SEQUENCE={i}\b',run),f'dqbuf{i}')
    need(f'DB_VIDEO_COMPLETION_PUBLISH G={i+1}' in run,f'completion G{i+1}')
    need(re.search(rf'TLBG_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=61472\b',run),f'tlbg{i}')
    need(re.search(rf'STATS3A_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=331840\b',run),f'stats{i}')
for req in range(7,28):
    need(f'E003I_ES_IQ_CONSUMED R={req} FRAME={req} SLOT={(req-7)&1}' in dmesg,f'kernel consume R{req}')
need('X1E front PIX completed provider-owned bounded twenty-seven-frame live requeue' in dmesg,'27-frame kernel completion')
# Native AEC ownership and continuous scheduler release mapping.
accept=[]
pat=r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+) FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) ISP=0x([0-9a-fA-F]{8}) RELEASED_AT_G=(\d+) RELEASE_SOURCE=(\d+) EFFECT=(\d+)'
for m in re.finditer(pat,run): accept.append(tuple(int(x,16) if i==7 else int(x) for i,x in enumerate(m.groups())))
need(len(accept)==27,'27 AEC accepts')
for g,request,fll,vb,exp,again,dgain,isp,released,source,effect in accept:
    need(request==g+3,f'ownership G{g}'); need(fll>=2160 and vb==fll-2160 and 4<=exp<=((fll-4)&~1),f'geometry G{g}'); need(0<=again<=0x3c0 and 0x100<=dgain<=0xf00,f'gains G{g}'); need(math.isfinite(frombits(isp)) and frombits(isp)>0,f'isp G{g}')
    if g==1: need((released,source,effect)==(0,0,0),'G1 no release')
    else: need((released,source,effect)==(g,g-1,g+2),f'continuous release G{g}')
# Exactly three physical writes: same proven sources as GO.
wpat=r'DB_SENSOR_WRITE_OK SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) START_NS=(\d+) END_NS=(\d+) ELAPSED_NS=(\d+) COMPLETED_G=(\d+)'
writes=[tuple(map(int,m.groups())) for m in re.finditer(wpat,run)]
need(len(writes)==3,'exactly three physical writes')
for n,r in enumerate(writes,1):
    source,after,request,effect,fll,exp,again,dgain,start,end,elapsed,completed=r
    need((source,after,request,effect)==(n,n+1,n+3,n+3),f'physical write {n} mapping'); need(completed==after and end>=start and elapsed==end-start,f'physical write {n} timing')
# G4..G26 must be shadow-only releases at exact boundaries.
spat=r'GS_SENSOR_WRITE_SHADOW SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) MONO_NS=(\d+) COMPLETED_G=(\d+)'
shadow=[tuple(map(int,m.groups())) for m in re.finditer(spat,run)]
need(len(shadow)==23,'23 shadow releases')
for expect,r in zip(range(4,27),shadow):
    source,after,request,effect,fll,exp,again,dgain,mono,completed=r
    need(source==expect and after==source+1 and request==source+3 and effect==source+3 and completed==after,f'shadow source G{expect}')
# Hardware transaction evidence: one bootstrap + exactly the three real writes, never a shadow source.
txlines=[x for x in tx.splitlines() if 'AM request controls:' in x]
need(len(txlines)==4,'bootstrap + three hardware transactions only')
need('FLL=3562 exposure=3554 again=0x000 dgain=0x0100 ret=0' in txlines[0],'bootstrap transaction')
for r in writes:
    source,after,request,effect,fll,exp,again,dgain,*_=r
    needle=f'FLL={fll} exposure={exp} again=0x{again:03x} dgain=0x{dgain:04x} ret=0'
    need(any(needle in x for x in txlines[1:]),f'hardware tx source {source}')
# Producer and live IQ coverage.
prod=json.loads((O/'producer/RESULT.json').read_text()); need(prod['status']=='PASS' and prod['schema']=='sp11-e003i-gm-r5-r27-producer-v1','producer manifest')
rows=prod['rows']; need([(r['generation'],r['request_target']) for r in rows]==[(1,None)]+[(g,g+3) for g in range(2,25)],'producer mapping'); need(len(rows)==24,'producer rows')
deadline={}; caps={}
for r in rows[1:]:
    req=r['request_target']; need(r.get('submitted_live') is True,f'R{req} submitted'); cap=O/'producer'/f'R{req}-dynamic.bin'; need(cap.is_file() and cap.stat().st_size==41088,f'R{req} capsule'); need(sha(cap)==r['capsule_sha256'],f'R{req} hash')
    pipeline=float(r['gain_wait_ms'])+float(r['total_process_ms'])+float(r.get('submit_ms',0.0)); need(pipeline<33.333333,f'R{req} deadline'); deadline[str(req)]=pipeline; caps[str(req)]=sha(cap)
post=(O/'CONTROLS-POST-AEC.txt').read_text(errors='replace'); last=writes[-1]; _,_,_,_,lfll,lexp,lagain,ldgain,*_=last
for x in (f'vertical_blanking: {lfll-2160}',f'exposure: {lexp}',f'analogue_gain: {lagain}',f'digital_gain: {ldgain}'): need(x in post,'post '+x)
for bad in ('TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic'): need(bad.lower() not in dmesg.lower(),'kernel '+bad)
hashes={'qc10c':[],'tlbg':[],'stats3a':[]}
for i in range(27):
    for key,prefix,size in [('qc10c','QC10C',7778304),('tlbg','TLBG',61472),('stats3a','STATS3A',331840)]:
        p=O/f'{prefix}-{i}.bin'; need(p.is_file() and p.stat().st_size==size,f'{prefix}-{i}'); hashes[key].append(sha(p))
result={'schema':'sp11-e003i-gs-continuous-shadow-live-r27-v1','status':'PASS_CAPTURE_GS_CONTINUOUS_SHADOW_R27','runtime_performed':True,'same_boot_retry_performed':False,'frames':27,'stats_generations':27,'producer_generations':24,'requests':list(range(5,28)),'physical_sensor_writes':3,'physical_write_sources':[1,2,3],'shadow_release_count':23,'shadow_release_sources':list(range(4,27)),'continuous_scheduler_released_sources':list(range(1,27)),'pending_source_at_end':27,'streamoff':True,'kernel_health':'PASS','hardware_control_transactions_including_bootstrap':4,'deadline_ms':deadline,'capsules':caps,'capture_sha256':hashes,'continuous_physical_writes_proven':False,'continuous_scheduler_live_boundary_ownership_proven':True,'golden_return_required':True}
(O/'LIVE-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GS_LIVE_FRAMES=27 CONTINUOUS_RELEASES=26')
print('GS_PHYSICAL_WRITES=3 SHADOW_RELEASES=23')
print('GS_STREAMOFF=PASS KERNEL_HEALTH=PASS')
print('GS_MAX_PIPELINE_MS=%.6f'%max(deadline.values()))
print('GS_CAPTURE_VERIFY=PASS')
