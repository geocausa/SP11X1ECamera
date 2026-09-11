#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
D=Path(__file__).resolve().parent; BASE=D.parent
GP=BASE/'gp-go-control-timing-authority'; GQ=BASE/'gq-continuous-control-ring-scheduler'; GR=BASE/'gr-continuous-helper-integration'; GO=BASE/'go-twentyseven-frame-live-r5-r27'
A=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-go/attempt1-pass-twentyseven-frame-20260911T2145')
CAM='117136b2c624de5ef3f4c081cdcf9c363cda9f6db5c752b7ade5f5e11b1b3e95'; HELP='1dc9d1b2e31ca74c983e6bdf48dc66f3780da1ffbfd369e4c455d88d9266d5b1'; SCHED='8179ef6912a705e7296dd93fc147a6183d9d425b8e2c5052e7424de94cbccea1'; GAIN='2ad568beeeaf0ef9a5229b234ff172e6cbb5f2a3848f063eec103995595031c1'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
for p,status in [(GP,'PASS_OFFLINE_GO_CONTROL_TIMING_AUTHORITY'),(GQ,'PASS_OFFLINE_CONTINUOUS_RING_SCHEDULER'),(GR,'PASS_OFFLINE_CONTINUOUS_HELPER_INTEGRATION')]:
    need(json.loads((p/'RESULT.json').read_text())['status']==status,p.name)
go=json.loads((GO/'ATTEMPT1-PASS.json').read_text()); need(go['status']=='PASS_CAPTURE_GO_TWENTYSEVEN_FRAME_R5_R27' and go['golden_return'] and go['candidate_retired'],'GO authority')
subprocess.run(['sha256sum','-c','MANIFEST.sha256'],cwd=A,check=True,stdout=subprocess.DEVNULL)
with tempfile.TemporaryDirectory(prefix='e003i-gs-') as td0:
    td=Path(td0); cam=td/'qcom-camss.ko'; helper=td/'helper'; bootstrap=td/'bootstrap'
    subprocess.run([str(D/'build-camss.sh'),str(cam)],check=True)
    subprocess.run([str(D/'build-helper.sh'),str(helper)],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(bootstrap)],check=True)
    hs=(D/'build/helper/e003i-gs-shadow-native-aec.c').read_text()
    need(sha(D/'build/camss/camss.c')==CAM,'CAMSS source')
    need(sha(D/'build/helper/e003i-gs-shadow-native-aec.c')==HELP,'shadow helper source')
    need(sha(D/'build/helper/continuous-db-schedule.c')==SCHED,'continuous scheduler source')
    need(sha(D/'build/helper/gain-feed.c')==GAIN,'gain feed source')
    for tok in ('GS_SENSOR_WRITE_SHADOW SOURCE=%u AFTER_G=%u','if (ev->source_generation > 3U)','GS_SHADOW_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 PHYSICAL_WRITES=G1..G3 SHADOW=G4..G26 PENDING=G27 EFFECT_RANGE=G4..G29'):
        need(tok in hs,'shadow contract '+tok)
    need(hs.count('apply_sensor_controls(ctx->sensor_fd, &ev->controls)')==1,'single physical writer path')
    result={'schema':'sp11-e003i-gs-shadow-offline-v1','status':'PASS_OFFLINE_READY_FOR_FRESH_SHADOW_ONE_SHOT','go_live_authority':'PASS_R27_CONSUMED','gp_timing':'PASS','gq_ring_scheduler':'PASS','gr_helper_integration':'PASS','camss_source_sha256':CAM,'helper_source_sha256':HELP,'continuous_scheduler_sha256':SCHED,'gain_feed_c_sha256':GAIN,'camss_module_sha256':sha(cam),'helper_binary_sha256':sha(helper),'bootstrap_binary_sha256':sha(bootstrap),'physical_write_sources':[1,2,3],'shadow_release_sources':list(range(4,27)),'one_stream_attempt_per_boot':True,'camera_runtime_performed':False,'continuous_physical_writes_authorized':False}
    (D/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GS_OFFLINE_AUTHORITY=PASS'); print('GS_SHADOW_HELPER_WERROR=PASS'); print('GS_VERIFY=PASS')
