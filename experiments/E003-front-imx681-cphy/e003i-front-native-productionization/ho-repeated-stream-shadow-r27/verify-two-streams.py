#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re
D=Path(__file__).resolve().parent;O=D/'runtime-output'

def need(v,m):
    if not v:raise AssertionError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
streams=[]
for n in (1,2):
    S=O/f'stream{n}';run=(O/f'RUN{n}.txt').read_text(errors='replace')
    need('LAUNCHER_RC=0' in run,f'run{n} rc');need('PROD_POST_G3_POLICY=shadow' in run,f'run{n} policy')
    need('STREAMON_OK_ASYNC' in run and 'STREAMOFF_OK' in run,f'run{n} lifecycle');need('E003I_GM_PRODUCER=PASS' in run,f'run{n} producer')
    for bad in ('PINNED_FOR_REBOOT:','DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','HB_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL','EN_GAIN_FEED_FAIL','E003I_GM_PRODUCER=FAIL','GN_DQBUF_MISMATCH'):
        need(bad not in run,f'run{n} {bad}')
    mr=re.search(r'PROD_NATIVE_SCHEDULE_PASS ACCEPTED_G=1\.\.27 RELEASED_SOURCES=G1\.\.G26 POLICY=shadow CONTROL_IOCTLS=(\d+) LATER_NATIVE_WRITES=(\d+) LATER_SHADOW=(\d+) POLICY_DISABLED_SHADOW=(\d+) CAP_ACTIVE_SHADOW=(\d+) UNCHANGED_SHADOW=(\d+) ALREADY_APPLIED_SHADOW=(\d+) HORIZON_SHADOW=(\d+) PENDING=G27 APPLY_EFFECT_MAX=G27',run)
    need(mr,f'run{n} final schedule');ci,lw,ls,pds,cas,us,aas,hs=map(int,mr.groups());need(ci==3 and lw==0 and ls==23 and pds+cas+us+aas+hs==23 and hs==2,f'run{n} accounting')
    writes=[int(x) for x in re.findall(r'DB_SENSOR_WRITE_OK SOURCE=(\d+)',run)];need(writes==[1,2,3],f'run{n} write sources {writes}')
    need('HB_NATIVE_CAP_RELEASE_ALLOW' not in run,f'run{n} later allow leaked')
    prod=json.loads((S/'producer/RESULT.json').read_text());need(prod['status']=='PASS' and len(prod['rows'])==24,f'run{n} producer manifest')
    submitted=[r for r in prod['rows'] if r.get('request_target') is not None];need(len(submitted)==23 and all(r.get('submitted_live') is True for r in submitted),f'run{n} producer submissions')
    hsums={'qc10c':[],'tlbg':[],'stats3a':[]}
    for i in range(27):
        for key,prefix,size in (('qc10c','QC10C',0x76b000),('tlbg','TLBG',0xf020),('stats3a','STATS3A',0x51040)):
            p=S/f'{prefix}-{i}.bin';need(p.is_file() and p.stat().st_size==size,f'run{n} {prefix}-{i}');hsums[key].append(sha(p))
    streams.append({'stream':n,'control_ioctls':ci,'post_g3_native_writes':lw,'policy_disabled_shadow':pds,'cap_active_shadow':cas,'unchanged_shadow':us,'already_applied_shadow':aas,'horizon_shadow':hs,'producer_requests':23,'hashes':hsums})
dmesg=(D/'DMESG.txt').read_text(errors='replace')
for bad in ('TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic'):
    need(bad.lower() not in dmesg.lower(),'kernel '+bad)
need(dmesg.count('X1E front PIX completed provider-owned bounded twenty-seven-frame live requeue')>=2,'two kernel stream completions')
tx=[x for x in dmesg.splitlines() if 'AM request controls:' in x]
need(len(tx)==8,f'hardware control transaction count {len(tx)}')
result={'schema':'sp11-e003i-ho-repeated-stream-shadow-r27-v1','status':'PASS_CAPTURE_HO_TWO_STREAM_SHADOW_R27','runtime_performed':True,'streams_completed':2,'frames_per_stream':27,'producer_requests_per_stream':23,'post_g3_policy':'shadow','post_g3_native_write_count_total':0,'startup_native_writes_per_stream':3,'hardware_control_transactions_including_bootstrap_total':8,'streamoff_count':2,'kernel_health':'PASS','same_stream_retry_performed':False,'repeated_stream_live_robustness_proven':True,'production_native_changed_post_g3_feedback_proven':False,'streams':streams,'golden_return_required':True}
(O/'LIVE-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HO_STREAM1=PASS HO_STREAM2=PASS')
print('HO_POST_G3_POLICY=shadow POST_G3_NATIVE_WRITES=0')
print('HO_STREAMOFF_COUNT=2 KERNEL_HEALTH=PASS')
print('HO_REPEAT_VERIFY=PASS')
