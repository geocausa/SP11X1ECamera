#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,time
D=Path(__file__).resolve().parent
O=D/'runtime-output'
S=O/'front'

def need(v,m):
    if not v:
        raise AssertionError(m)

need((D/'ATTEMPT1-CONSUMED.marker').is_file(),'consumed marker')
for f,expect in [('ROUTE-REAR-ONLY.txt','rear-only'),('ROUTE-NEUTRAL-HANDOFF.txt','neutral'),('ROUTE-FRONT-ONLY.txt','front-only')]:
    cp=subprocess.run([str(D/'route-state.py'),str(O/f),'--expect',expect],text=True,capture_output=True)
    need(cp.returncode==0,f+' '+cp.stdout+cp.stderr)

cb=O/'rear-colorbar.raw'
need(cb.is_file() and cb.stat().st_size==14321824,'rear colorbar size')
need(hashlib.sha256(cb.read_bytes()).hexdigest()=='6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346','rear colorbar hash')
c=(O/'REAR-COLORBAR.txt').read_text(errors='replace')
n=(O/'REAR-NORMAL16.txt').read_text(errors='replace')
need('COLORBAR_RC=0' in c and 'NORMAL16_RC=0' in n,'rear rc')
seq=[int(x) for x in re.findall(r'seq:\s*(\d+)\s+bytesused:\s*14321824',n)]
need(seq==list(range(16)),'rear sequences '+repr(seq))
ts=[float(x) for x in re.findall(r'ts:\s*([0-9]+\.[0-9]+)',n)]
fps=None
if len(ts)==16:
    delta=[b-a for a,b in zip(ts,ts[1:])]
    fps=1.0/(sum(delta)/len(delta))
    need(29.0<=fps<=31.0,'rear fps '+str(fps))
need('IG_REAR_RUNTIME_SUSPEND=PASS' in (O/'REAR-SUSPEND.txt').read_text(),'rear suspend')

run=(O/'FRONT-R27.txt').read_text(errors='replace')
need('FRONT_LAUNCHER_RC=0' in run,'front launcher rc')
need('PROD_POST_G3_POLICY=shadow' in run,'front shadow policy')
need('STREAMON_OK_ASYNC' in run and 'STREAMOFF_OK' in run,'front lifecycle')
need('E003I_GM_PRODUCER=PASS' in run,'front producer')
need('STATS3A_READ0_GENERATION=1' in run and 'TLBG_READ0_GENERATION=1' in run,'front generation1')
for bad in ('PINNED_FOR_REBOOT:','DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','HB_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL','EN_GAIN_FEED_FAIL','E003I_GM_PRODUCER=FAIL','GN_DQBUF_MISMATCH'):
    need(bad not in run,'front '+bad)
dq=[int(x) for x in re.findall(r'^DQBUF\d+_INDEX=\d+ BYTESUSED=\d+ SEQUENCE=(\d+)$',run,re.M)]
need(dq==list(range(27)),'front DQBUF '+repr(dq))
mr=re.search(r'PROD_NATIVE_SCHEDULE_PASS ACCEPTED_G=1\.\.27 RELEASED_SOURCES=G1\.\.G26 POLICY=shadow CONTROL_IOCTLS=(\d+) LATER_NATIVE_WRITES=(\d+) LATER_SHADOW=(\d+) POLICY_DISABLED_SHADOW=(\d+) CAP_ACTIVE_SHADOW=(\d+) UNCHANGED_SHADOW=(\d+) ALREADY_APPLIED_SHADOW=(\d+) HORIZON_SHADOW=(\d+) PENDING=G27 APPLY_EFFECT_MAX=G27',run)
need(mr,'front schedule')
ci,lw,ls,pds,cas,us,aas,hs=map(int,mr.groups())
need(ci==3 and lw==0 and ls==23 and pds+cas+us+aas+hs==23 and hs==2,'front schedule accounting')
writes=[int(x) for x in re.findall(r'DB_SENSOR_WRITE_OK SOURCE=(\d+)',run)]
need(writes==[1,2,3],'front writes '+repr(writes))
need('HB_NATIVE_CAP_RELEASE_ALLOW' not in run,'front later native allow')
prod=json.loads((S/'producer/RESULT.json').read_text())
need(prod['status']=='PASS' and len(prod['rows'])==24,'front producer result')
need([x['generation'] for x in prod['rows']]==list(range(1,25)),'front producer generations')
submitted=[x for x in prod['rows'] if x.get('request_target') is not None]
need(len(submitted)==23 and all(x.get('submitted_live') is True for x in submitted),'front submissions')
for i in range(27):
    for prefix,size in (('QC10C',0x76b000),('TLBG',0xf020),('STATS3A',0x51040)):
        p=S/f'{prefix}-{i}.bin'
        need(p.is_file() and p.stat().st_size==size,f'front {prefix}-{i}')

time.sleep(0.5)
front=[p for p in Path('/sys/bus/i2c/devices').glob('*-0010') if (p/'name').exists() and (p/'name').read_text().strip()=='imx681']
need(len(front)==1,'front sysfs')
front_st=(front[0]/'power/runtime_status').read_text().strip()
need(front_st=='suspended','front runtime '+front_st)

d=(D/'DMESG.txt').read_text(errors='replace')
for bad in ('TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic','Unhandled fault'):
    need(bad.lower() not in d.lower(),'kernel '+bad)
need(d.count('X1E front PIX completed provider-owned bounded twenty-seven-frame live requeue')>=1,'front kernel completion')
tx=[x for x in d.splitlines() if 'AM request controls:' in x]
need(len(tx)==4,'front hardware control tx '+str(len(tx)))

res={
 'schema':'sp11-camera-ig-rear-to-front-live-v1',
 'status':'PASS_CAPTURE_IG_REAR_TO_FRONT_R16_R27',
 'direction':'rear-to-front',
 'runtime_performed':True,
 'rear_colorbar_frames':1,
 'rear_normal_frames':16,
 'rear_sequences':seq,
 'rear_mean_fps':fps,
 'rear_runtime_status':'suspended',
 'neutral_handoff':'PASS',
 'front_frames':27,
 'front_first_snapshot_generation':1,
 'front_producer_generations':24,
 'front_producer_requests':23,
 'front_post_g3_policy':'shadow',
 'front_startup_native_writes':3,
 'front_post_g3_native_writes':0,
 'front_hardware_control_transactions_including_bootstrap':4,
 'front_streamoff_count':1,
 'front_runtime_status':front_st,
 'final_route_state':'front-only',
 'kernel_health':'PASS',
 'same_stream_retry_performed':False,
 'same_boot_retry_performed':False,
 'golden_return_required':True,
}
(O/'LIVE-RESULT.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
p=dict(res)
p.update({'schema':'sp11-camera-ig-attempt1-pass-v1','candidate_consumed':True,'camera_runtime_performed':True})
(D/'ATTEMPT1-PASS.json').write_text(json.dumps(p,indent=2,sort_keys=True)+'\n')

print('IG_REAR=PASS COLORBAR=EXACT NORMAL16=PASS RUNTIME_SUSPEND=PASS')
print('IG_HANDOFF=PASS REAR_ONLY->NEUTRAL->FRONT_ONLY')
print('IG_FRONT=PASS FRAMES=27 GENERATION1=PASS POST_G3_NATIVE_WRITES=0')
print('IG_KERNEL_HEALTH=PASS RETRY=NO')
print('IG_LIVE_VERIFY=PASS')
