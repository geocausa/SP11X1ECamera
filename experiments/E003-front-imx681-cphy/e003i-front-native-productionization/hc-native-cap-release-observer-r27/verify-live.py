#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,math,re,struct
D=Path(__file__).resolve().parent; O=D/'runtime-output'
CAPMAX=6133333088
HA_CAP_ACTIVE=2; HA_UNCHANGED=3; HA_APPLY=4; HA_ALREADY=5

def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def frombits(u): return struct.unpack('<f',struct.pack('<I',u))[0]
run=(O/'RUN.txt').read_text(errors='replace'); dmesg=(D/'DMESG.txt').read_text(errors='replace'); tx=(O/'CONTROL-TRANSACTION.txt').read_text(errors='replace')
need('HELPER_RC=0' in run,'helper rc'); need('STREAMON_OK_ASYNC' in run and 'STREAMOFF_OK' in run,'stream lifecycle'); need('E003I_GM_PRODUCER=PASS' in run,'producer marker')
for bad in ('PINNED_FOR_REBOOT:','DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','HB_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL','EN_GAIN_FEED_FAIL','E003I_GM_PRODUCER=FAIL','GN_DQBUF_MISMATCH'):
    need(bad not in run,bad)
cycle=[0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2]
for i in range(27):
    need(re.search(rf'DQBUF{i}_INDEX={cycle[i]} BYTESUSED=7778304 SEQUENCE={i}\b',run),f'dqbuf{i}')
    need(f'DB_VIDEO_COMPLETION_PUBLISH G={i+1}' in run,f'completion G{i+1}')
    need(re.search(rf'TLBG_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=61472\b',run),f'tlbg{i}')
    need(re.search(rf'STATS3A_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=331840\b',run),f'stats{i}')
for req in range(7,28): need(f'E003I_ES_IQ_CONSUMED R={req} FRAME={req} SLOT={(req-7)&1}' in dmesg,f'kernel IQ R{req}')
need('X1E front PIX completed provider-owned bounded twenty-seven-frame live requeue' in dmesg,'kernel 27-frame completion')
# Native AEC controls and continuous scheduler ownership.
pat=r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+) FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) ISP=0x([0-9a-fA-F]{8}) RELEASED_AT_G=(\d+) RELEASE_SOURCE=(\d+) EFFECT=(\d+)'
acc=[]
for m in re.finditer(pat,run):
    x=list(m.groups()); x[7]=int(x[7],16); acc.append(tuple(int(v) for v in x))
need(len(acc)==27,'27 AEC accepts')
for r in acc:
    g,req,fll,vb,exp,ag,dg,isp,rel,src,effect=r
    need(req==g+3 and vb==fll-2160 and exp<=((fll-4)&~1),f'geometry G{g}')
    need(math.isfinite(frombits(isp)) and frombits(isp)>0,f'ISP G{g}')
    if g==1: need((rel,src,effect)==(0,0,0),'G1 release')
    else: need((rel,src,effect)==(g,g-1,g+2),f'release G{g}')
# Policy logs for G4..G24; G25,G26 are evidence-horizon forced shadows.
allow_rx=r'HB_NATIVE_CAP_RELEASE_ALLOW SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) CONV=(\d+) CAP=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+)'
allows=[tuple(map(int,m.groups())) for m in re.finditer(allow_rx,run)]
need(len(allows)<=1,'at most one cap-release allow')
sh_rx=r'HB_NATIVE_CAP_RELEASE_SHADOW SOURCE=(\d+) AFTER_G=(\d+) DECISION=(\d+) CONV=(\d+) CAP=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+)'
shadows=[tuple(map(int,m.groups())) for m in re.finditer(sh_rx,run)]
hz_rx=r'HC_CAP_RELEASE_HORIZON_SHADOW SOURCE=(\d+) AFTER_G=(\d+) CONV=(\d+) CAP=(\d+) EFFECT_G=(\d+)'
horizon=[tuple(map(int,m.groups())) for m in re.finditer(hz_rx,run)]
need([x[0] for x in horizon]==[25,26],'G25,G26 horizon shadow')
need([(x[0],x[1],x[4]) for x in horizon]==[(25,26,28),(26,27,29)],'horizon mapping')
policy_sources=[x[0] for x in allows]+[x[0] for x in shadows]
need(sorted(policy_sources)==list(range(4,25)),'exact G4..G24 HA decisions')
for x in shadows:
    src,after,decision,conv,cap,fll,exp,ag,dg=x
    need(after==src+1,'shadow boundary')
    need(decision in (HA_CAP_ACTIVE,HA_UNCHANGED,HA_ALREADY),f'shadow decision G{src}')
    if decision==HA_CAP_ACTIVE: need(conv>=CAPMAX or cap!=conv,f'cap-active evidence G{src}')
for x in allows:
    src,after,req,effect,conv,cap,fll,exp,ag,dg=x
    need(4<=src<=24 and after==src+1 and req==src+3 and effect==src+3 and effect<=27,'allow horizon/mapping')
    need(conv<CAPMAX and cap==conv,'allow must be uncapped')
    ar=acc[src-1]
    need((fll,exp,ag,dg)==(ar[2],ar[4],ar[5],ar[6]),'allow tuple must equal native AEC tuple')
# Successful sensor-control ioctl path must be G1..G3 plus optional native cap-release source.
wpat=r'DB_SENSOR_WRITE_OK SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) START_NS=(\d+) END_NS=(\d+) ELAPSED_NS=(\d+) COMPLETED_G=(\d+)'
writes=[tuple(map(int,m.groups())) for m in re.finditer(wpat,run)]
allow_sources=[x[0] for x in allows]
need([r[0] for r in writes]==[1,2,3]+allow_sources,'real ioctl sources')
for r in writes:
    src,after,req,effect,fll,exp,ag,dg,start,end,elapsed,completed=r
    need(after==src+1 and req==src+3 and effect==src+3 and completed==after and end-start==elapsed,f'write mapping G{src}')
    ar=acc[src-1]; need((fll,exp,ag,dg)==(ar[2],ar[4],ar[5],ar[6]),f'exact native tuple G{src}')
# One later allow latches all subsequent eligible sources into already-applied shadow.
if allow_sources:
    s=allow_sources[0]
    for x in shadows:
        if x[0]>s: need(x[2]==HA_ALREADY,f'post-allow source G{x[0]} must be latch-shadow')
else:
    need(all(x[2] in (HA_CAP_ACTIVE,HA_UNCHANGED) for x in shadows),'no-write run cannot use already-applied state')
# Final accounting marker.
mr=re.search(r'HC_NATIVE_CAP_RELEASE_SCHEDULE_PASS ACCEPTED_G=1\.\.27 RELEASED_SOURCES=G1\.\.G26 CONTROL_IOCTLS=(\d+) LATER_NATIVE_WRITES=(\d+) LATER_SHADOW=(\d+) CAP_ACTIVE_SHADOW=(\d+) UNCHANGED_SHADOW=(\d+) ALREADY_APPLIED_SHADOW=(\d+) HORIZON_SHADOW=(\d+) PENDING=G27 APPLY_EFFECT_MAX=G27',run)
need(mr,'final schedule marker')
ci,lw,ls,cas,us,aas,hs=map(int,mr.groups())
need(ci==3+len(allows) and lw==len(allows) and ls==23-len(allows) and hs==2,'final primary accounting')
counts={HA_CAP_ACTIVE:0,HA_UNCHANGED:0,HA_ALREADY:0}
for x in shadows: counts[x[2]]+=1
need((cas,us,aas)==(counts[HA_CAP_ACTIVE],counts[HA_UNCHANGED],counts[HA_ALREADY]),'final decision counts')
# Kernel driver transactions: one bootstrap + each real changed ioctl.
txlines=[x for x in tx.splitlines() if 'AM request controls:' in x]
need(len(txlines)==1+len(writes),'hardware transaction count')
need('FLL=3562 exposure=3554 again=0x000 dgain=0x0100 ret=0' in txlines[0],'bootstrap transaction')
for r in writes:
    src,after,req,effect,fll,exp,ag,dg,*_=r
    needle=f'FLL={fll} exposure={exp} again=0x{ag:03x} dgain=0x{dg:04x} ret=0'
    need(any(needle in x for x in txlines[1:]),f'hardware tx G{src}')
# Current hardware controls must equal the last successful native write.
last=writes[-1]; post=(O/'CONTROLS-POST-AEC.txt').read_text(errors='replace')
expected=(last[4]-2160,last[5],last[6],last[7])
for x in (f'vertical_blanking: {expected[0]}',f'exposure: {expected[1]}',f'analogue_gain: {expected[2]}',f'digital_gain: {expected[3]}'):
    need(x in post,'post '+x)
# Producer coverage/deadline and immutable capture hashes.
prod=json.loads((O/'producer/RESULT.json').read_text()); need(prod['status']=='PASS' and len(prod['rows'])==24,'producer manifest')
deadline={}; caps={}
for row in prod['rows'][1:]:
    req=row['request_target']; need(row.get('submitted_live') is True,f'R{req} submit'); cap=O/'producer'/f'R{req}-dynamic.bin'; need(cap.is_file() and cap.stat().st_size==41088 and sha(cap)==row['capsule_sha256'],f'R{req} capsule'); p=float(row['gain_wait_ms'])+float(row['total_process_ms'])+float(row.get('submit_ms',0)); need(p<33.333333,f'R{req} deadline'); deadline[str(req)]=p; caps[str(req)]=sha(cap)
for bad in ('TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic'): need(bad.lower() not in dmesg.lower(),'kernel '+bad)
hashes={'qc10c':[],'tlbg':[],'stats3a':[]}
for i in range(27):
    for k,pfx,size in [('qc10c','QC10C',7778304),('tlbg','TLBG',61472),('stats3a','STATS3A',331840)]:
        p=O/f'{pfx}-{i}.bin'; need(p.is_file() and p.stat().st_size==size,f'{pfx}-{i}'); hashes[k].append(sha(p))
if allows:
    status='PASS_CAPTURE_HC_CAP_RELEASE_ONE_NATIVE_WRITE_R27'; outcome='PASS_CAP_RELEASE_ONE_NATIVE_WRITE'; native_feedback=True
else:
    status='PASS_CAPTURE_HC_NO_CAP_RELEASE_R27'; outcome='PASS_NO_CAP_RELEASE'; native_feedback=False
result={
 'schema':'sp11-e003i-hc-native-cap-release-observer-r27-v1','status':status,'outcome':outcome,
 'runtime_performed':True,'same_boot_retry_performed':False,'frames':27,'stats_generations':27,'producer_generations':24,
 'continuous_scheduler_release_sources':list(range(1,27)),'startup_native_sensor_sources':[1,2,3],
 'post_g3_native_write_count':len(allows),'post_g3_native_write_sources':allow_sources,
 'post_g3_native_write_details':allows,'ha_shadow_details':shadows,'horizon_shadow_sources':[25,26],
 'maximum_post_g3_native_writes_enforced':1,'maximum_applied_effect_generation':None if not allows else allows[0][3],
 'sensor_hardware_transactions_including_bootstrap':len(txlines),'streamoff':True,'kernel_health':'PASS',
 'deadline_ms':deadline,'capsules':caps,'capture_sha256':hashes,'synthetic_control_delta_added':False,
 'production_native_changed_post_g3_feedback_proven':native_feedback,'continuous_native_feedback_proven':False,
 'golden_return_required':True
}
(O/'LIVE-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(f'HC_LIVE_FRAMES=27 OUTCOME={outcome} POST_G3_NATIVE_WRITES={len(allows)}')
if allows: print(f'HC_NATIVE_CAP_RELEASE_SOURCE=G{allows[0][0]} EFFECT=G{allows[0][3]} CONV={allows[0][4]} CAP={allows[0][5]}')
else: print('HC_NATIVE_CAP_RELEASE_SOURCE=NONE')
print('HC_HORIZON_SHADOW=G25,G26')
print('HC_STREAMOFF=PASS KERNEL_HEALTH=PASS')
print('HC_MAX_PIPELINE_MS=%.6f'%max(deadline.values()))
print('HC_CAPTURE_VERIFY=PASS')
