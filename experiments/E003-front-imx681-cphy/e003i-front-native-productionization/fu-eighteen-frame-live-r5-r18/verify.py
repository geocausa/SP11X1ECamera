#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile

D=Path(__file__).resolve().parent
BASE=D.parent
FT=BASE/'ft-eighteen-frame-r18-transport'
FR=BASE/'fr-fifteen-generation-gain-feed-publisher'
FS=BASE/'fs-r5-r18-producer-integration'

CAM='a096493ae74fc3a22945f71f670f8777f0ea375bd3ad667c7451c96116d2ef6c'
HELP='24c87150ae6ee447440fe544cb8af1cec27e33d70fc0f70b198b4b7d9f5f23ce'
GAIN='c8b03597649ec5e1a6e5b62110eb61ab7cd6a29073a3ecdcf9194f439b410627'
SCHED='092c1b1dfaaa09ede3b9b492fc4173915d64f7b6c3d7e7439576314129e3c6cf'

def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

ft=json.loads((FT/'RESULT.json').read_text())
need(ft['status']=='PASS_OFFLINE_EIGHTEEN_FRAME_TRANSPORT' and ft['frames']==18,'FT authority')
need(ft['patched_camss_sha256']==CAM and ft['patched_helper_sha256']==HELP and
     ft['gain_feed_c_sha256']==GAIN and ft['patched_schedule_header_sha256']==SCHED,'FT hashes')
need(ft['iq_consumption_requests']==list(range(5,19)),'FT IQ coverage')
need(ft['cq_gain_feed_generations']==list(range(1,16)),'FT gain coverage')
need(ft['aec_generations']==list(range(1,19)),'FT AEC coverage')
need(ft['sensor_write_sources']==[1,2,3] and ft['sensor_write_boundaries']==[2,3,4],'FT write bound')

fr=json.loads((FR/'RESULT.json').read_text())
need(fr['status']=='PASS_OFFLINE_G1_G15_C_PUBLISHER','FR authority')
need(fr['accepted_generations']==list(range(1,16)) and fr['rejected_generation']==16 and
     fr['gain_feed_c_sha256']==GAIN,'FR bound')

fs=json.loads((FS/'RESULT.json').read_text())
need(fs['status']=='PASS_OFFLINE_R5_R18_AUTHORIZED_INTEGRATION','FS authority')
need(fs['requests']==list(range(5,19)) and fs['r16_r18_authority']=='FQ PASS','FS bounded authority')
need(fs['r5_r15_live_regression']=='11/11 exact FN live capsule hashes and key metadata','FS FN regression')

checks={
  'build-camss.sh':['make-eighteen-frame-camss.py',CAM,'W=1'],
  'build-helper.sh':['make-eighteen-frame-helper.py','fr-fifteen-generation-gain-feed-publisher',HELP,GAIN,SCHED,'-Werror'],
  'invoke-once.sh':['fs-r5-r18-producer-integration','e003i-fu-eighteen-frame-native-aec','QC10C-17.bin'],
  'runtime-preflight.sh':['sp11_camera_e003i_fu_eighteen_frame_r5_r18=1','prior_runtime_output'],
  '99zv_sp11_camera_e003i_fu_eighteen_frame_r5_r18':['sp11-camera-e003i-fu-eighteen-frame-r5-r18-one-shot','sp11_camera_e003i_fu_eighteen_frame_r5_r18=1'],
}
for f,toks in checks.items():
    s=(D/f).read_text()
    for t in toks:
        need(t in s,f'{f}: missing {t}')

with tempfile.TemporaryDirectory(prefix='e003i-fu-') as td:
    td=Path(td)
    cam=td/'qcom-camss.ko'
    helper=td/'helper'
    bootstrap=td/'bootstrap'
    subprocess.run([str(D/'build-camss.sh'),str(cam)],check=True)
    subprocess.run([str(D/'build-helper.sh'),str(helper)],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(bootstrap)],check=True)

    need(sha(D/'build/camss/camss.c')==CAM,'FU CAMSS generated source')
    need(sha(D/'build/helper/e003i-fu-eighteen-frame-native-aec.c')==HELP,'FU helper generated source')
    need(sha(D/'build/helper/gain-feed.c')==GAIN,'FU FR publisher')
    need(sha(D/'build/helper/native-db-schedule.h')==SCHED,'FU schedule header')

    result={
      'schema':'sp11-e003i-fu-offline-v1',
      'status':'PASS_OFFLINE_READY_FOR_FRESH_ONE_SHOT',
      'live_runtime_performed':False,
      'continuous_aec_claimed':False,
      'ft_transport':'PASS_18_FRAMES',
      'fr_c_publisher':'PASS_G1_G15_G16_REJECT',
      'fs_producer':'PASS_R5_R18_AUTHORIZED',
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

print('FU_FT_TRANSPORT=PASS_18')
print('FU_FR_C_PUBLISHER=PASS_G1_G15')
print('FU_FS_PRODUCER=PASS_R5_R18')
print('FU_CAMSS_W1=PASS')
print('FU_HELPER_WERROR=PASS')
print('FU_VERIFY=PASS')
