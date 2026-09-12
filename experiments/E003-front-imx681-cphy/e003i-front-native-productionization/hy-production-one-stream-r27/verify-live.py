#!/usr/bin/env python3
from pathlib import Path
import json,re
D=Path(__file__).resolve().parent;O=D/'runtime-output';S=O/'stream1'
def need(v,m):
    if not v: raise AssertionError(m)
run=(O/'RUN1.txt').read_text(errors='replace')
need((D/'ATTEMPT1-CONSUMED.marker').is_file(),'consumed marker')
need('LAUNCHER_RC=0' in run,'launcher rc')
need('PROD_POST_G3_POLICY=shadow' in run,'shadow policy')
need('STREAMON_OK_ASYNC' in run and 'STREAMOFF_OK' in run,'stream lifecycle')
need('E003I_GM_PRODUCER=PASS' in run,'producer')
need('STATS3A_READ0_GENERATION=1' in run and 'TLBG_READ0_GENERATION=1' in run,'fresh generation1')
for bad in ('PINNED_FOR_REBOOT:','DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','HB_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL','EN_GAIN_FEED_FAIL','E003I_GM_PRODUCER=FAIL','GN_DQBUF_MISMATCH'):
    need(bad not in run,bad)
dq=[int(x) for x in re.findall(r'^DQBUF\d+_INDEX=\d+ BYTESUSED=\d+ SEQUENCE=(\d+)$',run,re.M)]
need(dq==list(range(27)),'DQBUF sequences '+repr(dq))
mr=re.search(r'PROD_NATIVE_SCHEDULE_PASS ACCEPTED_G=1\.\.27 RELEASED_SOURCES=G1\.\.G26 POLICY=shadow CONTROL_IOCTLS=(\d+) LATER_NATIVE_WRITES=(\d+) LATER_SHADOW=(\d+) POLICY_DISABLED_SHADOW=(\d+) CAP_ACTIVE_SHADOW=(\d+) UNCHANGED_SHADOW=(\d+) ALREADY_APPLIED_SHADOW=(\d+) HORIZON_SHADOW=(\d+) PENDING=G27 APPLY_EFFECT_MAX=G27',run)
need(mr,'final schedule');ci,lw,ls,pds,cas,us,aas,hs=map(int,mr.groups());need(ci==3 and lw==0 and ls==23 and pds+cas+us+aas+hs==23 and hs==2,'schedule accounting')
writes=[int(x) for x in re.findall(r'DB_SENSOR_WRITE_OK SOURCE=(\d+)',run)];need(writes==[1,2,3],'write sources '+repr(writes));need('HB_NATIVE_CAP_RELEASE_ALLOW' not in run,'later native allow')
prod=json.loads((S/'producer/RESULT.json').read_text());need(prod['status']=='PASS' and len(prod['rows'])==24,'producer result');need([r['generation'] for r in prod['rows']]==list(range(1,25)),'producer generations')
submitted=[r for r in prod['rows'] if r.get('request_target') is not None];need(len(submitted)==23 and all(r.get('submitted_live') is True for r in submitted),'producer submissions')
for i in range(27):
    for prefix,size in (('QC10C',0x76b000),('TLBG',0xf020),('STATS3A',0x51040)):
        p=S/f'{prefix}-{i}.bin';need(p.is_file() and p.stat().st_size==size,f'{prefix}-{i}')
dmesg=(D/'DMESG.txt').read_text(errors='replace')
for bad in ('TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic'):
    need(bad.lower() not in dmesg.lower(),'kernel '+bad)
need(dmesg.count('X1E front PIX completed provider-owned bounded twenty-seven-frame live requeue')>=1,'kernel stream completion')
tx=[x for x in dmesg.splitlines() if 'AM request controls:' in x];need(len(tx)==4,'hardware control transaction count '+str(len(tx)))
result={'schema':'sp11-e003i-hy-production-one-stream-r27-v1','status':'PASS_CAPTURE_HY_PRODUCTION_ONE_STREAM_R27','runtime_performed':True,'streams_completed':1,'frames':27,'producer_generations':24,'producer_requests':23,'first_snapshot_generation':1,'post_g3_policy':'shadow','startup_native_writes':3,'post_g3_native_writes':0,'hardware_control_transactions_including_bootstrap':4,'streamoff_count':1,'kernel_health':'PASS','same_stream_retry_performed':False,'same_boot_retry_performed':False,'golden_return_required':True}
(O/'LIVE-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HY_STREAM=PASS FRAMES=27 FIRST_GENERATION=1')
print('HY_PRODUCER=PASS GENERATIONS=24 REQUESTS=23')
print('HY_POST_G3_POLICY=shadow STARTUP_WRITES=3 POST_G3_NATIVE_WRITES=0')
print('HY_KERNEL_HEALTH=PASS CONTROL_TX=4 STREAMOFF=1')
print('HY_LIVE_VERIFY=PASS')
