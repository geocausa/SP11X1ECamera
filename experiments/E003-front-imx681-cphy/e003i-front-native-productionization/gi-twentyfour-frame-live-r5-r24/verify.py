#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile

D=Path(__file__).resolve().parent
BASE=D.parent
FY=BASE/'fy-calibrated-awb-selector-replay'
GD=BASE/'gd-windows-r4-r24-combined-awb-lsc-oracle'
GE=BASE/'ge-r22-r24-continuation-authority'
GF=BASE/'gf-twentyone-generation-gain-feed-publisher'
GG=BASE/'gg-r5-r24-producer-integration'
GH=BASE/'gh-twentyfour-frame-r24-transport'

CAM='b47e9ca26d4591b55d5208eaf40edcef1794d4d6d7fb2e3c33e72edf5f527386'
HELP='df20afacd4f839250b0338de22600b8d89a09b6320f4c685fdfcfa76e7fa6b79'
GAIN='9a4ad8ae24f9672d897d4d6be58394f998df517c9103c8149b59fc0612c57593'
SCHED='71a88a4ebacb453a84e9eeaebd6f21354b73b3363f18a47d719336a3500c993b'

def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

fy=json.loads((FY/'RESULT.json').read_text())
need(fy['status']=='PASS_FX_SELECTOR_OBJECT_AND_EG_FA_FH_FW_BIT_EXACT','FY authority')
need(fy['status']=='PASS_FX_SELECTOR_OBJECT_AND_EG_FA_FH_FW_BIT_EXACT','FY closed selector model')
gd=json.loads((GD/'RESULT.json').read_text())
need(gd['status']=='PASS_WINDOWS_COMBINED_R4_R24_AWB_LSC' and gd['combined_r24_completion'] is True,'GD authority')
ge=json.loads((GE/'RESULT.json').read_text())
need(ge['status']=='PASS_OFFLINE_R22_R24_COMPOSABLE_AUTHORITY_CLOSED' and ge['linux_live_r22_plus_allowed'] is True,'GE authority')
gf=json.loads((GF/'RESULT.json').read_text())
need(gf['status']=='PASS_OFFLINE_G1_G21_C_PUBLISHER','GF authority')
need(gf['accepted_generations']==list(range(1,22)) and gf['rejected_generation']==22 and gf['gain_feed_c_sha256']==GAIN,'GF bound')
gg=json.loads((GG/'RESULT.json').read_text())
need(gg['status']=='PASS_OFFLINE_R5_R24_AUTHORIZED_INTEGRATION','GG authority')
need(gg['requests']==list(range(5,25)) and gg['source_generations']==list(range(2,22)),'GG bounded authority')
gh=json.loads((GH/'RESULT.json').read_text())
need(gh['status']=='PASS_OFFLINE_TWENTYFOUR_FRAME_TRANSPORT' and gh['frames']==24,'GH authority')
need(gh['patched_camss_sha256']==CAM and gh['patched_helper_sha256']==HELP and
     gh['gain_feed_c_sha256']==GAIN and gh['patched_schedule_header_sha256']==SCHED,'GH hashes')
need(gh['iq_consumption_requests']==list(range(5,25)),'GH IQ coverage')
need(gh['cq_gain_feed_generations']==list(range(1,22)),'GH gain coverage')
need(gh['aec_generations']==list(range(1,25)),'GH AEC coverage')
need(gh['sensor_write_sources']==[1,2,3] and gh['sensor_write_boundaries']==[2,3,4],'GH write bound')

checks={
  'build-camss.sh':['make-twentyfour-frame-camss.py',CAM,'W=1'],
  'build-helper.sh':['make-twentyfour-frame-helper.py','gf-twentyone-generation-gain-feed-publisher',HELP,GAIN,SCHED,'-Werror'],
  'invoke-once.sh':['gg-r5-r24-producer-integration','e003i-gi-twentyfour-frame-native-aec','QC10C-23.bin'],
  'runtime-preflight.sh':['sp11_camera_e003i_gi_twentyfour_frame_r5_r24=1','prior_runtime_output'],
  '99zx_sp11_camera_e003i_gi_twentyfour_frame_r5_r24':['sp11-camera-e003i-gi-twentyfour-frame-r5-r24-one-shot','sp11_camera_e003i_gi_twentyfour_frame_r5_r24=1'],
}
for f,toks in checks.items():
    s=(D/f).read_text()
    for t in toks: need(t in s,f'{f}: missing {t}')

with tempfile.TemporaryDirectory(prefix='e003i-gi-') as td:
    td=Path(td);cam=td/'qcom-camss.ko';helper=td/'helper';bootstrap=td/'bootstrap'
    subprocess.run([str(D/'build-camss.sh'),str(cam)],check=True)
    subprocess.run([str(D/'build-helper.sh'),str(helper)],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(bootstrap)],check=True)
    need(sha(D/'build/camss/camss.c')==CAM,'GI CAMSS generated source')
    need(sha(D/'build/helper/e003i-gi-twentyfour-frame-native-aec.c')==HELP,'GI helper generated source')
    need(sha(D/'build/helper/gain-feed.c')==GAIN,'GI GF publisher')
    need(sha(D/'build/helper/native-db-schedule.h')==SCHED,'GI schedule header')
    result={
      'schema':'sp11-e003i-gi-offline-v1',
      'status':'PASS_OFFLINE_READY_FOR_FRESH_ONE_SHOT',
      'live_runtime_performed':False,'continuous_aec_claimed':False,
      'fy_selector':'PASS_WINDOWS_SELECTOR_MODEL','gd_combined_authority':'PASS_R4_R24',
      'ge_content_authority':'PASS_R22_R24_CLOSED',
      'gh_transport':'PASS_24_FRAMES','gf_c_publisher':'PASS_G1_G21_G22_REJECT',
      'gg_producer':'PASS_R5_R24_AUTHORIZED',
      'camss_source_sha256':CAM,'helper_source_sha256':HELP,'gain_feed_c_sha256':GAIN,
      'schedule_header_sha256':SCHED,'camss_module_sha256':sha(cam),
      'helper_binary_sha256':sha(helper),'bootstrap_binary_sha256':sha(bootstrap),
      'dqbuf_mismatch_diagnostic':True,'one_stream_attempt_per_boot':True,
      'physical_sensor_writes_bounded_to_generations':[1,2,3],
      'producer_gain_generations':list(range(1,22)),
      'collector_generations':list(range(1,25)),
    }
    (D/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')

print('GI_GH_TRANSPORT=PASS_24')
print('GI_GF_C_PUBLISHER=PASS_G1_G21')
print('GI_GG_PRODUCER=PASS_R5_R24')
print('GI_CAMSS_W1=PASS')
print('GI_HELPER_WERROR=PASS')
print('GI_VERIFY=PASS')
