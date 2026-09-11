#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
D=Path(__file__).resolve().parent
BASE=D.parent
GJ=BASE/'gj-windows-r4-r27-combined-awb-lsc-oracle'
GK=BASE/'gk-r25-r27-continuation-authority'
GL=BASE/'gl-twentyfour-generation-gain-feed-publisher'
GM=BASE/'gm-r5-r27-producer-integration'
GN=BASE/'gn-twentyseven-frame-r27-transport'
CAM='117136b2c624de5ef3f4c081cdcf9c363cda9f6db5c752b7ade5f5e11b1b3e95'
HELP='32ecff0848a3f47fe149ead36ccf63eec26a8c78180075129253a65792dedf1e'
GAIN='2ad568beeeaf0ef9a5229b234ff172e6cbb5f2a3848f063eec103995595031c1'
SCHED='b3db42c9a38da0f428277fccbe79b01cc25a5a42d7f4cf26112d1096e0eedfee'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

gj=json.loads((GJ/'RESULT.json').read_text())
need(gj['status']=='PASS_WINDOWS_COMBINED_R4_R27_AWB_LSC','GJ authority')
need(gj['requests']==list(range(4,28)) and gj['windows_stream_count']==1,'GJ bounded one-stream authority')
need(gj['awb_result']['bit_exact']=='24/24','GJ AWB')
need(gj['lsc_result']['clean_lsc_replay']=='24/24 byte-exact LSC0/LSC1/LSC2/GIC','GJ LSC')
need(gj['combined_r27_completion'] is True,'GJ R27 completion')

gk=json.loads((GK/'RESULT.json').read_text())
need(gk['status']=='PASS_OFFLINE_R25_R27_COMPOSABLE_AUTHORITY_CLOSED','GK authority')
need(gk['r5_r24_live_regression']=='20/20 exact GI live capsule hashes','GK regression')
need(gk['r25_r27_deterministic']=='3/3 two-run capsule hashes exact','GK deterministic tail')
need(gk['linux_live_r25_plus_allowed'] is True,'GK live gate')

gl=json.loads((GL/'RESULT.json').read_text())
need(gl['status']=='PASS_OFFLINE_G1_G24_C_PUBLISHER','GL authority')
need(gl['accepted_generations']==list(range(1,25)) and gl['rejected_generation']==25,'GL bound')
need(gl['gain_feed_c_sha256']==GAIN,'GL source hash')

gm=json.loads((GM/'RESULT.json').read_text())
need(gm['status']=='PASS_OFFLINE_R5_R27_AUTHORIZED_INTEGRATION','GM authority')
need(gm['requests']==list(range(5,28)) and gm['source_generations']==list(range(2,25)),'GM bounded authority')
need(gm['r5_r24_live_regression']=='20/20 exact GI live capsule hashes','GM live regression')
need(gm['r25_r27_authority']=='GK CLOSED','GM tail authority')

gn=json.loads((GN/'RESULT.json').read_text())
need(gn['status']=='PASS_OFFLINE_TWENTYSEVEN_FRAME_TRANSPORT' and gn['frames']==27,'GN authority')
need(gn['patched_camss_sha256']==CAM and gn['patched_helper_sha256']==HELP and gn['gain_feed_c_sha256']==GAIN and gn['patched_schedule_header_sha256']==SCHED,'GN hashes')
need(gn['iq_consumption_requests']==list(range(5,28)),'GN IQ coverage')
need(gn['cq_gain_feed_generations']==list(range(1,25)),'GN gain coverage')
need(gn['aec_generations']==list(range(1,28)),'GN AEC coverage')
need(gn['sensor_write_sources']==[1,2,3] and gn['sensor_write_boundaries']==[2,3,4],'GN write bound')

checks={
 'build-camss.sh':['make-twentyseven-frame-camss.py',CAM,'W=1'],
 'build-helper.sh':['make-twentyseven-frame-helper.py','gl-twentyfour-generation-gain-feed-publisher',HELP,GAIN,SCHED,'-Werror'],
 'runtime-preflight.sh':['sp11_camera_e003i_go_twentyseven_frame_r5_r27=1','prior_runtime_output'],
 '99zy_sp11_camera_e003i_go_twentyseven_frame_r5_r27':['sp11-camera-e003i-go-twentyseven-frame-r5-r27-one-shot','sp11_camera_e003i_go_twentyseven_frame_r5_r27=1'],
}
for f,toks in checks.items():
    s=(D/f).read_text()
    for t in toks: need(t in s,f'{f}: missing {t}')

with tempfile.TemporaryDirectory(prefix='e003i-go-') as td:
    td=Path(td); cam=td/'qcom-camss.ko'; helper=td/'helper'; bootstrap=td/'bootstrap'
    subprocess.run([str(D/'build-camss.sh'),str(cam)],check=True)
    subprocess.run([str(D/'build-helper.sh'),str(helper)],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(bootstrap)],check=True)
    need(sha(D/'build/camss/camss.c')==CAM,'GO CAMSS generated source')
    need(sha(D/'build/helper/e003i-go-twentyseven-frame-native-aec.c')==HELP,'GO helper generated source')
    need(sha(D/'build/helper/gain-feed.c')==GAIN,'GO GL publisher')
    need(sha(D/'build/helper/native-db-schedule.h')==SCHED,'GO schedule header')
    result={
      'schema':'sp11-e003i-go-offline-v1',
      'status':'PASS_OFFLINE_READY_FOR_FRESH_ONE_SHOT',
      'live_runtime_performed':False,'continuous_aec_claimed':False,
      'gj_combined_authority':'PASS_R4_R27','gk_content_authority':'PASS_R25_R27_CLOSED',
      'gn_transport':'PASS_27_FRAMES','gl_c_publisher':'PASS_G1_G24_G25_REJECT',
      'gm_producer':'PASS_R5_R27_AUTHORIZED',
      'camss_source_sha256':CAM,'helper_source_sha256':HELP,'gain_feed_c_sha256':GAIN,
      'schedule_header_sha256':SCHED,'camss_module_sha256':sha(cam),
      'helper_binary_sha256':sha(helper),'bootstrap_binary_sha256':sha(bootstrap),
      'dqbuf_mismatch_diagnostic':True,'one_stream_attempt_per_boot':True,
      'physical_sensor_writes_bounded_to_generations':[1,2,3],
      'producer_gain_generations':list(range(1,25)),
      'collector_generations':list(range(1,28)),
      'requests':list(range(5,28)),
    }
    (D/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GO_GJ_GK_R27_AUTHORITY=PASS')
print('GO_GN_TRANSPORT=PASS_27')
print('GO_GL_C_PUBLISHER=PASS_G1_G24')
print('GO_GM_PRODUCER=PASS_R5_R27')
print('GO_CAMSS_W1=PASS')
print('GO_HELPER_WERROR=PASS')
print('GO_VERIFY=PASS')
