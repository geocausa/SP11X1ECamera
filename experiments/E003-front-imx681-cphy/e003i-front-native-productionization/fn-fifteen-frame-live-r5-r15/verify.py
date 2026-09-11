#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile

D=Path(__file__).resolve().parent
BASE=D.parent
FM=BASE/'fm-fifteen-frame-r15-transport'
FK=BASE/'fk-twelve-generation-gain-feed-publisher'
FL=BASE/'fl-r5-r15-producer-integration'
CAM='592f31d591ff9542f8f67d8228e5f45808afb63088368107ce56422b4d8e34d6'
HELP='f68413ae23cdfbfb84ee39129582e40ecee2fd4b3a37ee242a5bceb4997fb4b4'
GAIN='93e284bca519366817324962278d5403c05cdc7fd0454b8a4e8fe683d2b90b2e'
SCHED='b080113d1a07a2600eb8a06b3e5b045422debe0858577d84ab7d61fae03ff54d'

def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

fm=json.loads((FM/'RESULT.json').read_text())
need(fm['status']=='PASS_OFFLINE_FIFTEEN_FRAME_TRANSPORT' and fm['frames']==15,'FM authority')
need(fm['patched_camss_sha256']==CAM and fm['patched_helper_sha256']==HELP and fm['gain_feed_c_sha256']==GAIN and fm['patched_schedule_header_sha256']==SCHED,'FM hashes')
need(fm['iq_consumption_requests']==list(range(5,16)) and fm['cq_gain_feed_generations']==list(range(1,13)),'FM bounded coverage')
need(fm['sensor_write_sources']==[1,2,3] and fm['sensor_write_boundaries']==[2,3,4],'FM physical write bound')

fk=json.loads((FK/'RESULT.json').read_text())
need(fk['status']=='PASS_OFFLINE_G1_G12_C_PUBLISHER','FK authority')
need(fk['accepted_generations']==list(range(1,13)) and fk['rejected_generation']==13 and fk['gain_feed_c_sha256']==GAIN,'FK bound')

fl=json.loads((FL/'RESULT.json').read_text())
need(fl['status']=='PASS_OFFLINE_R5_R15_AUTHORIZED_INTEGRATION' and fl['requests']==list(range(5,16)),'FL authority')
need(fl['r5_r12_live_regression']=='8/8 exact FF live capsule hashes and key metadata','FL FF regression')
need(fl['r13_r15_authority']=='FJ PASS' and fl['live_capable_code_path_preserved'] is True,'FL R13-R15 authority')

checks={
 'build-camss.sh':['make-fifteen-frame-camss.py',CAM,'W=1'],
 'build-helper.sh':['make-fifteen-frame-helper.py','fk-twelve-generation-gain-feed-publisher',HELP,GAIN,SCHED,'-Werror'],
 'invoke-once.sh':['fl-r5-r15-producer-integration','e003i-fn-fifteen-frame-native-aec','QC10C-14.bin'],
 'runtime-preflight.sh':['sp11_camera_e003i_fn_fifteen_frame_r5_r15=1','prior_runtime_output'],
 '99zu_sp11_camera_e003i_fn_fifteen_frame_r5_r15':['sp11-camera-e003i-fn-fifteen-frame-r5-r15-one-shot','sp11_camera_e003i_fn_fifteen_frame_r5_r15=1'],
}
for f,toks in checks.items():
    s=(D/f).read_text()
    for t in toks: need(t in s,f'{f}: missing {t}')

with tempfile.TemporaryDirectory(prefix='e003i-fn-') as td:
    td=Path(td)
    cam=td/'qcom-camss.ko'; helper=td/'helper'; bootstrap=td/'bootstrap'
    subprocess.run([str(D/'build-camss.sh'),str(cam)],check=True)
    subprocess.run([str(D/'build-helper.sh'),str(helper)],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(bootstrap)],check=True)
    need(sha(D/'build/camss/camss.c')==CAM,'FN CAMSS generated source')
    need(sha(D/'build/helper/e003i-fn-fifteen-frame-native-aec.c')==HELP,'FN helper generated source')
    need(sha(D/'build/helper/gain-feed.c')==GAIN,'FN FK publisher')
    need(sha(D/'build/helper/native-db-schedule.h')==SCHED,'FN schedule header')
    result={
      'schema':'sp11-e003i-fn-offline-v1',
      'status':'PASS_OFFLINE_READY_FOR_FRESH_ONE_SHOT',
      'live_runtime_performed':False,
      'continuous_aec_claimed':False,
      'fm_transport':'PASS_15_FRAMES',
      'fk_c_publisher':'PASS_G1_G12_G13_REJECT',
      'fl_producer':'PASS_R5_R15_AUTHORIZED',
      'camss_source_sha256':CAM,
      'helper_source_sha256':HELP,
      'gain_feed_c_sha256':GAIN,
      'schedule_header_sha256':SCHED,
      'camss_module_sha256':sha(cam),
      'helper_binary_sha256':sha(helper),
      'bootstrap_binary_sha256':sha(bootstrap),
      'dqbuf_mismatch_diagnostic':True,
      'one_stream_attempt_per_boot':True,
      'physical_sensor_writes_bounded_to_generations':[1,2,3],
    }
    (D/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')

print('FN_FM_TRANSPORT=PASS_15')
print('FN_FK_C_PUBLISHER=PASS_G1_G12')
print('FN_FL_PRODUCER=PASS_R5_R15')
print('FN_CAMSS_W1=PASS')
print('FN_HELPER_WERROR=PASS')
print('FN_VERIFY=PASS')
