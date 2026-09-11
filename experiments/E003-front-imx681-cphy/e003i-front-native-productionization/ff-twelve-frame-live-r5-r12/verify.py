#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
D=Path(__file__).resolve().parent; BASE=D.parent
FE=BASE/'fe-twelve-frame-r12-transport'
FC=BASE/'fc-nine-generation-gain-feed-publisher'
FD=BASE/'fd-r5-r12-producer-integration'
CAM='deee56e61090bba938f602a7baeae054435762e6312e47d2cac9dbf9a210f15d'
HELP='e6f2a792dc070c9d6a726817f30d3a8b1da56b554debccbe2832bd0b18ae47de'
GAIN='5c44634bf3082b480fbf6e904e6449164756709069f90bbe719c1c6df432ae67'
SCHED='1872289bdd280cc067034c4425234b9bfa334e27dce62841ffb540b061f86690'
R12='ee3dabc5519c8c4851cabc321ef2925824b13a6471c0a7e3bd72223544ecd373'
def need(x,m):
    if not x: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
fe=json.loads((FE/'RESULT.json').read_text())
need(fe['status']=='PASS_OFFLINE_TWELVE_FRAME_TRANSPORT' and fe['frames']==12,'FE authority')
need(fe['patched_camss_sha256']==CAM and fe['patched_helper_sha256']==HELP and fe['gain_feed_c_sha256']==GAIN,'FE hashes')
fc=json.loads((FC/'RESULT.json').read_text())
need(fc['status']=='PASS_OFFLINE_G1_G9_C_PUBLISHER' and fc['accepted_generations']==list(range(1,10)) and fc['rejected_generation']==10 and fc['gain_feed_c_sha256']==GAIN,'FC authority')
fd=json.loads((FD/'RESULT.json').read_text())
need(fd['status']=='PASS_OFFLINE_R5_R12_DYNAMIC_CAL_SLOT_INTEGRATION' and fd['requests']==list(range(5,13)),'FD authority')
need(fd['r5_r6_live_regression']=='2/2 exact EZ live capsule hashes','FD live regression authority')
need(fd['r12_capsule_sha256']==R12 and fd['r12_awb_slot']==5 and fd['r12_awb_triangle']==19,'FD R12 authority')
checks={
 'build-camss.sh':['make-twelve-frame-camss.py',CAM,'W=1'],
 'build-helper.sh':['make-twelve-frame-helper.py','fc-nine-generation-gain-feed-publisher',HELP,GAIN,SCHED,'-Werror'],
 'invoke-once.sh':['fd-r5-r12-producer-integration','e003i-ff-twelve-frame-native-aec','QC10C-11.bin'],
 'runtime-preflight.sh':['sp11_camera_e003i_ff_twelve_frame_r5_r12=1','prior_runtime_output'],
 '99zt_sp11_camera_e003i_ff_twelve_frame_r5_r12':['sp11-camera-e003i-ff-twelve-frame-r5-r12-one-shot','sp11_camera_e003i_ff_twelve_frame_r5_r12=1'],
}
for f,toks in checks.items():
    s=(D/f).read_text()
    for t in toks: need(t in s,f'{f}: missing {t}')
with tempfile.TemporaryDirectory(prefix='e003i-ff-') as td:
    td=Path(td);cam=td/'qcom-camss.ko';helper=td/'helper';bootstrap=td/'bootstrap'
    subprocess.run([str(D/'build-camss.sh'),str(cam)],check=True)
    subprocess.run([str(D/'build-helper.sh'),str(helper)],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(bootstrap)],check=True)
    need(sha(D/'build/camss/camss.c')==CAM,'FF CAMSS generated source')
    need(sha(D/'build/helper/e003i-ff-twelve-frame-native-aec.c')==HELP,'FF helper generated source')
    need(sha(D/'build/helper/gain-feed.c')==GAIN,'FF FC publisher')
    need(sha(D/'build/helper/native-db-schedule.h')==SCHED,'FF schedule header')
    result={
      'schema':'sp11-e003i-ff-offline-v1',
      'status':'PASS_OFFLINE_READY_FOR_FRESH_ONE_SHOT',
      'live_runtime_performed':False,
      'continuous_aec_claimed':False,
      'fe_transport':'PASS_12_FRAMES',
      'fc_c_publisher':'PASS_G1_G9_G10_REJECT',
      'fd_producer':'PASS_R5_R12_DYNAMIC_CAL_SLOT',
      'r12_offline_capsule_sha256':R12,
      'camss_source_sha256':CAM,
      'helper_source_sha256':HELP,
      'gain_feed_c_sha256':GAIN,
      'schedule_header_sha256':SCHED,
      'camss_module_sha256':sha(cam),
      'helper_binary_sha256':sha(helper),
      'bootstrap_binary_sha256':sha(bootstrap),
      'dqbuf_mismatch_diagnostic':True,
      'one_stream_attempt_per_boot':True,
    }
    (D/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('FF_FE_TRANSPORT=PASS_12')
print('FF_FC_C_PUBLISHER=PASS_G1_G9')
print('FF_FD_PRODUCER=PASS_R5_R12')
print('FF_CAMSS_W1=PASS')
print('FF_HELPER_WERROR=PASS')
print('FF_VERIFY=PASS')
