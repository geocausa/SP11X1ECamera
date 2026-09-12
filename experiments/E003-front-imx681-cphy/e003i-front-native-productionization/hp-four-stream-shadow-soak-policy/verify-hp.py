#!/usr/bin/env python3
from pathlib import Path
import json,os
HERE=Path(__file__).resolve().parent; BASE=HERE.parent
HO=BASE/'ho-repeated-stream-shadow-r27'; HN=BASE/'hn-snapshot-generation-reset-package'
ARCH=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ho/attempt1-pass-two-stream-shadow-20260912T081541')
def need(v,m):
    if not v: raise AssertionError(m)
ho=json.loads((HO/'RESULT.json').read_text()); hn=json.loads((HN/'RESULT.json').read_text())
need(ho['status']=='PASS_CAPTURE_HO_TWO_STREAM_SHADOW_R27_GOLDEN_RESTORED_RETIRED','HO parent')
need(ho['archive_manifest_sha256']=='35975ea08e695d69d8ff69cf530b1236230cb43fb0d9bc739c0538dec2d2c57c','HO manifest')
need(ho['repeated_stream_live_robustness_proven'] is True and ho['post_g3_native_write_count_total']==0,'HO authority')
need(hn['status']=='PASS_OFFLINE_SNAPSHOT_GENERATION_RESET_PACKAGE','HN package')
stream_bytes=[]
for n in (1,2):
    s=ARCH/'runtime-output'/f'stream{n}'; need(s.is_dir(),f'HO stream{n}')
    stream_bytes.append(sum(p.stat().st_size for p in s.rglob('*') if p.is_file()))
max_stream=max(stream_bytes); planned_streams=4; projected=max_stream*planned_streams
free=os.statvfs('/home/geoca/Documents/SP11-PROJECT'); free_bytes=free.f_bavail*free.f_frsize
min_free=8*1024**3; need(free_bytes>=min_free,'free space below 8GiB policy floor')
policy={
 'schema':'sp11-e003i-hp-four-stream-shadow-soak-policy-v1','status':'PASS_OFFLINE_FOUR_STREAM_SHADOW_SOAK_POLICY','parent':'HO two-stream shadow live PASS','camera_runtime_performed':False,
 'stream_count':planned_streams,'frames_per_stream':27,'total_frames':108,'post_g3_policy':'shadow','post_g3_native_writes_authorized':0,
 'expected_startup_native_writes_per_stream':3,'expected_hardware_control_transactions_including_bootstrap_total':16,'expected_streamoff_count':4,
 'producer_generations_per_stream':24,'producer_requests_per_stream':23,
 'fresh_session_contract':{'first_snapshot_generation':1,'last_producer_generation':24,'reset_required_between_streams':True},
 'retry_policy':{'same_stream_retry':False,'same_boot_retry':False,'abort_on_first_failure':True},
 'failure_policy':['capture dmesg and partial runtime evidence','archive immediately','do not launch any later stream','reboot directly to protected Golden','retire candidate after Golden verification'],
 'evidence_budget':{'ho_stream_bytes':stream_bytes,'projected_four_stream_bytes_upper_bound_from_ho_max':projected,'minimum_free_bytes_before_arm':min_free,'current_free_bytes_at_verification':free_bytes},
 'package_authority':{'qcom_camss_sha256':hn['build']['hashes']['qcom-camss.ko'],'manifest_sha256':hn['package']['manifest_sha256']},
 'success_gate':['4 consumed markers','4 launcher rc=0','4 producer PASS','4 x 27 DQBUF exact','4 schedule PASS','4 STREAMOFF_OK','16 kernel sensor control transactions including four bootstraps','zero post-G3 native writes','kernel health PASS','Golden return PASS'],
 'next_gate':'HQ fresh four-stream shadow one-shot candidate preparation/install-unarmed checkpoint'
}
(HERE/'RESULT.json').write_text(json.dumps(policy,indent=2,sort_keys=True)+'\n')
print('HP_SOAK_POLICY=PASS STREAMS=4 FRAMES=108 POLICY=shadow POST_G3_WRITES=0')
print('HP_PROJECTED_EVIDENCE_BYTES='+str(projected)+' FREE_BYTES='+str(free_bytes))
print('HP_CAMERA_RUNTIME=NO')
print('HP_VERIFY=PASS')
