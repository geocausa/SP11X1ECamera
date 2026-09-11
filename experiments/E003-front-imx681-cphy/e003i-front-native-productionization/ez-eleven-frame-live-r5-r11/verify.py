#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
D=Path(__file__).resolve().parent; BASE=D.parent
EY=BASE/'ey-eleven-frame-r10-r11-transport'; EW=BASE/'ew-eight-generation-gain-feed-publisher'; EX=BASE/'ex-r5-r11-producer-integration'
CAM='335e15f48cac9835d9ddfa0f1dc96f559346f167f2e8cce1c384635b872d13aa'
HELP='b5ecb959b95c63eb38c1e7da98e1f37e9c71d9cc4abe4ee6fbc5456e9bd67993'
GAIN='619970bcc9570bbbbaaee062312788e97d0bcbf3348b0722a53893316d8f79bd'
SCHED='6d6cfc6833c035d545d5d626a4af479717227732cf94ef301422e6c74f3dd113'
def need(x,m):
    if not x: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ey=json.loads((EY/'RESULT.json').read_text()); need(ey['status']=='PASS_OFFLINE_ELEVEN_FRAME_TRANSPORT' and ey['frames']==11,'EY authority'); need(ey['patched_camss_sha256']==CAM and ey['patched_helper_sha256']==HELP and ey['gain_feed_c_sha256']==GAIN,'EY hashes')
ew=json.loads((EW/'RESULT.json').read_text()); need(ew['status']=='PASS_OFFLINE_G1_G8_C_PUBLISHER' and ew['accepted_generations']==list(range(1,9)) and ew['rejected_generation']==9 and ew['gain_feed_c_sha256']==GAIN,'EW authority')
ex=json.loads((EX/'RESULT.json').read_text()); need(ex['status']=='PASS_OFFLINE_R5_R11_INTEGRATION' and ex['requests']==list(range(5,12)) and ex['r5_r9_live_regression']=='5/5 exact EV live capsule hashes','EX authority'); need(ex['r10_capsule_sha256']=='ff9b6265c3ce990bb05a94f300df55082992bcc8aaca293b3f091b522209d64f' and ex['r11_capsule_sha256']=='3bcd19f2082e80ca41fa9a6200ef072c9a49a165b9f91896544dfad20dfe1736','EX R10/R11 hash drift')
checks={
 'build-camss.sh':['make-eleven-frame-camss.py',CAM,'W=1'],
 'build-helper.sh':['make-eleven-frame-helper.py','ew-eight-generation-gain-feed-publisher',HELP,GAIN,SCHED,'-Werror'],
 'invoke-once.sh':['ex-r5-r11-producer-integration','e003i-ez-eleven-frame-native-aec','QC10C-10.bin'],
 'runtime-preflight.sh':['sp11_camera_e003i_ez_eleven_frame_r5_r11=1','prior_runtime_output'],
 '99zs_sp11_camera_e003i_ez_eleven_frame_r5_r11':['sp11-camera-e003i-ez-eleven-frame-r5-r11-one-shot','sp11_camera_e003i_ez_eleven_frame_r5_r11=1'],
}
for f,toks in checks.items():
    s=(D/f).read_text()
    for t in toks: need(t in s,f'{f}: missing {t}')
with tempfile.TemporaryDirectory(prefix='e003i-ez-') as td:
    td=Path(td); cam=td/'qcom-camss.ko'; helper=td/'helper'; bootstrap=td/'bootstrap'
    subprocess.run([str(D/'build-camss.sh'),str(cam)],check=True)
    subprocess.run([str(D/'build-helper.sh'),str(helper)],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(bootstrap)],check=True)
    need(sha(D/'build/camss/camss.c')==CAM,'EZ CAMSS generated source')
    need(sha(D/'build/helper/e003i-ez-eleven-frame-native-aec.c')==HELP,'EZ helper generated source')
    need(sha(D/'build/helper/gain-feed.c')==GAIN,'EZ EW publisher')
    need(sha(D/'build/helper/native-db-schedule.h')==SCHED,'EZ schedule header')
    result={'schema':'sp11-e003i-ez-offline-v1','status':'PASS_OFFLINE_READY_FOR_FRESH_ONE_SHOT','live_runtime_performed':False,'continuous_aec_claimed':False,'ey_transport':'PASS_11_FRAMES','ew_c_publisher':'PASS_G1_G8_G9_REJECT','ex_producer':'PASS_R5_R11','camss_source_sha256':CAM,'helper_source_sha256':HELP,'gain_feed_c_sha256':GAIN,'schedule_header_sha256':SCHED,'camss_module_sha256':sha(cam),'helper_binary_sha256':sha(helper),'bootstrap_binary_sha256':sha(bootstrap),'dqbuf_mismatch_diagnostic':True,'one_stream_attempt_per_boot':True}
    (D/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('EZ_EY_TRANSPORT=PASS_11')
print('EZ_EW_C_PUBLISHER=PASS_G1_G8')
print('EZ_EX_PRODUCER=PASS_R5_R11')
print('EZ_CAMSS_W1=PASS')
print('EZ_HELPER_WERROR=PASS')
print('EZ_VERIFY=PASS')
