#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile

D=Path(__file__).resolve().parent
BASE=D.parent
FY=BASE/'fy-calibrated-awb-selector-replay'
FW=BASE/'fw-windows-r4-r21-combined-awb-lsc-oracle'
FV=BASE/'fv-r19-r21-continuation-authority'
FZ=BASE/'fz-eighteen-generation-gain-feed-publisher'
GA=BASE/'ga-r5-r21-producer-integration'
GB=BASE/'gb-twentyone-frame-r21-transport'

CAM='d09cd0bf6d91ed7c51c981455d9643d1f486cb0374fec23a375376b83e837fb4'
HELP='8cb43bb96c629ce25c08014192898cc30e21abe226d101d06600f25dba829af5'
GAIN='7f91b0ba03ff494e7544d3ac4c793d4cf2522e3761df43ff620a0799d0e9d4ee'
SCHED='fca5d49b12524a9f24bfca673072cf3bbb85d33645045d3a2cb4b155b58c6aae'

def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

fy=json.loads((FY/'RESULT.json').read_text())
need(fy['status']=='PASS_FX_SELECTOR_OBJECT_AND_EG_FA_FH_FW_BIT_EXACT','FY authority')
need(fy['windows_replays']['FW']['bit_exact']=='18/18','FY FW replay')
fw=json.loads((FW/'RESULT.json').read_text())
need(fw['status']=='PASS_WINDOWS_COMBINED_R4_R21_AWB_LSC' and fw['combined_r21_completion'] is True,'FW authority')
fv=json.loads((FV/'RESULT.json').read_text())
need(fv['status']=='PASS_OFFLINE_R19_R21_COMPOSABLE_AUTHORITY_CLOSED' and fv['linux_live_r19_plus_allowed'] is True,'FV authority')
fz=json.loads((FZ/'RESULT.json').read_text())
need(fz['status']=='PASS_OFFLINE_G1_G18_C_PUBLISHER','FZ authority')
need(fz['accepted_generations']==list(range(1,19)) and fz['rejected_generation']==19 and fz['gain_feed_c_sha256']==GAIN,'FZ bound')
ga=json.loads((GA/'RESULT.json').read_text())
need(ga['status']=='PASS_OFFLINE_R5_R21_AUTHORIZED_INTEGRATION','GA authority')
need(ga['requests']==list(range(5,22)) and ga['source_generations']==list(range(2,19)),'GA bounded authority')
gb=json.loads((GB/'RESULT.json').read_text())
need(gb['status']=='PASS_OFFLINE_TWENTYONE_FRAME_TRANSPORT' and gb['frames']==21,'GB authority')
need(gb['patched_camss_sha256']==CAM and gb['patched_helper_sha256']==HELP and
     gb['gain_feed_c_sha256']==GAIN and gb['patched_schedule_header_sha256']==SCHED,'GB hashes')
need(gb['iq_consumption_requests']==list(range(5,22)),'GB IQ coverage')
need(gb['cq_gain_feed_generations']==list(range(1,19)),'GB gain coverage')
need(gb['aec_generations']==list(range(1,22)),'GB AEC coverage')
need(gb['sensor_write_sources']==[1,2,3] and gb['sensor_write_boundaries']==[2,3,4],'GB write bound')

checks={
  'build-camss.sh':['make-twentyone-frame-camss.py',CAM,'W=1'],
  'build-helper.sh':['make-twentyone-frame-helper.py','fz-eighteen-generation-gain-feed-publisher',HELP,GAIN,SCHED,'-Werror'],
  'invoke-once.sh':['ga-r5-r21-producer-integration','e003i-gc-twentyone-frame-native-aec','QC10C-20.bin'],
  'runtime-preflight.sh':['sp11_camera_e003i_gc_twentyone_frame_r5_r21=1','prior_runtime_output'],
  '99zw_sp11_camera_e003i_gc_twentyone_frame_r5_r21':['sp11-camera-e003i-gc-twentyone-frame-r5-r21-one-shot','sp11_camera_e003i_gc_twentyone_frame_r5_r21=1'],
}
for f,toks in checks.items():
    s=(D/f).read_text()
    for t in toks: need(t in s,f'{f}: missing {t}')

with tempfile.TemporaryDirectory(prefix='e003i-gc-') as td:
    td=Path(td);cam=td/'qcom-camss.ko';helper=td/'helper';bootstrap=td/'bootstrap'
    subprocess.run([str(D/'build-camss.sh'),str(cam)],check=True)
    subprocess.run([str(D/'build-helper.sh'),str(helper)],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(bootstrap)],check=True)
    need(sha(D/'build/camss/camss.c')==CAM,'GC CAMSS generated source')
    need(sha(D/'build/helper/e003i-gc-twentyone-frame-native-aec.c')==HELP,'GC helper generated source')
    need(sha(D/'build/helper/gain-feed.c')==GAIN,'GC FZ publisher')
    need(sha(D/'build/helper/native-db-schedule.h')==SCHED,'GC schedule header')
    result={
      'schema':'sp11-e003i-gc-offline-v1',
      'status':'PASS_OFFLINE_READY_FOR_FRESH_ONE_SHOT',
      'live_runtime_performed':False,'continuous_aec_claimed':False,
      'fy_selector':'PASS_WINDOWS_R4_R21','fw_combined_authority':'PASS_R4_R21',
      'fv_content_authority':'PASS_R19_R21_CLOSED',
      'gb_transport':'PASS_21_FRAMES','fz_c_publisher':'PASS_G1_G18_G19_REJECT',
      'ga_producer':'PASS_R5_R21_AUTHORIZED',
      'camss_source_sha256':CAM,'helper_source_sha256':HELP,'gain_feed_c_sha256':GAIN,
      'schedule_header_sha256':SCHED,'camss_module_sha256':sha(cam),
      'helper_binary_sha256':sha(helper),'bootstrap_binary_sha256':sha(bootstrap),
      'dqbuf_mismatch_diagnostic':True,'one_stream_attempt_per_boot':True,
      'physical_sensor_writes_bounded_to_generations':[1,2,3],
      'producer_gain_generations':list(range(1,19)),
      'collector_generations':list(range(1,22)),
    }
    (D/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')

print('GC_GB_TRANSPORT=PASS_21')
print('GC_FZ_C_PUBLISHER=PASS_G1_G18')
print('GC_GA_PRODUCER=PASS_R5_R21')
print('GC_CAMSS_W1=PASS')
print('GC_HELPER_WERROR=PASS')
print('GC_VERIFY=PASS')
