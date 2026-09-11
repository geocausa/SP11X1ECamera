#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
D=Path(__file__).resolve().parent; BASE=D.parent
GW=BASE/'gw-minimal-changed-post-g3-authority'; GX=BASE/'gx-minimal-sentinel-helper-integration'; GS=BASE/'gs-continuous-shadow-scheduler-r27'
CAM='117136b2c624de5ef3f4c081cdcf9c363cda9f6db5c752b7ade5f5e11b1b3e95'; HELP='8f28624537aa5c81da09b026ab6189f4efa9863f5d4519abe38a10986d01c350'; SCHED='8179ef6912a705e7296dd93fc147a6183d9d425b8e2c5052e7424de94cbccea1'; SENT='bb2c80f296bc8997f86dd2bac3f2660d507473a9fb3137eb1e14458079c31115'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
need(json.loads((GW/'RESULT.json').read_text())['status']=='PASS_OFFLINE_MINIMAL_CHANGED_POST_G3_AUTHORITY','GW authority')
need(json.loads((GX/'RESULT.json').read_text())['status']=='PASS_OFFLINE_MINIMAL_SENTINEL_HELPER_INTEGRATION','GX authority')
need(json.loads((GS/'ATTEMPT1-PASS.json').read_text())['status']=='PASS_CAPTURE_GS_CONTINUOUS_SHADOW_R27','GS authority')
with tempfile.TemporaryDirectory(prefix='e003i-gy-') as td0:
    td=Path(td0); cam=td/'qcom-camss.ko'; helper=td/'helper'; bootstrap=td/'bootstrap'
    subprocess.run([str(D/'build-camss.sh'),str(cam)],check=True)
    subprocess.run([str(D/'build-helper.sh'),str(helper)],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(bootstrap)],check=True)
    need(sha(D/'build/camss/camss.c')==CAM,'CAMSS source')
    need(sha(D/'build/helper/e003i-gy-sentinel-native-aec.c')==HELP,'GY helper source')
    need(sha(D/'build/helper/continuous-db-schedule.c')==SCHED,'scheduler source')
    need(sha(D/'build/helper/minimal-dgain-sentinel.c')==SENT,'sentinel source')
    hs=(D/'build/helper/e003i-gy-sentinel-native-aec.c').read_text()
    for tok in ('GX_SENTINEL_WRITE_ALLOW SOURCE=4','GX_SENTINEL_SUPPRESSED SOURCE=4','GX_SENSOR_WRITE_SHADOW SOURCE=%u','GX_SENTINEL_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26','e003i_gw_make_sentinel('): need(tok in hs,'helper contract '+tok)
    need(hs.count('apply_sensor_controls(ctx->sensor_fd, write_controls)')==1,'single physical ioctl site')
    result={'schema':'sp11-e003i-gy-minimal-changed-sentinel-offline-v1','status':'PASS_OFFLINE_READY_FOR_FRESH_ONE_SHOT','gw_authority':'PASS','gx_helper_integration':'PASS','camss_source_sha256':CAM,'helper_source_sha256':HELP,'scheduler_source_sha256':SCHED,'sentinel_source_sha256':SENT,'camss_module_sha256':sha(cam),'helper_binary_sha256':sha(helper),'bootstrap_binary_sha256':sha(bootstrap),'startup_native_sources':[1,2,3],'conditional_sentinel_source':4,'sentinel_digital_gain_delta_code':1,'sentinel_relative_gain_delta_percent':0.06798096532971698,'g5_g26':'shadow-only','one_stream_attempt_per_boot':True,'camera_runtime_performed':False,'production_changed_controller_feedback_authorized':False}
    (D/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GY_OFFLINE_AUTHORITY=PASS')
print('GY_HELPER_WERROR=PASS')
print('GY_SENTINEL_ONLY_G4=PASS')
print('GY_VERIFY=PASS')
