#!/usr/bin/env python3
from __future__ import annotations
import json,os,re,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; BASE=HERE.parent; REPO=HERE.parents[3]
HW=BASE/'hw-production-boot-bundle-activation-prep'; HQ=BASE/'hq-four-stream-shadow-r27'; FRONT=REPO/'src/front-imx681'; K=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
MEDIA=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-hc/attempt1-pass-no-cap-release-20260912T060723/runtime-output/MEDIA.txt')
def need(v,m):
    if not v: raise AssertionError(m)
def run(cmd,**kw): return subprocess.run(cmd,text=True,capture_output=True,check=True,**kw)
hw=json.loads((HW/'RESULT.json').read_text()); hq=json.loads((HQ/'RESULT.json').read_text())
need(hw['status']=='PASS_ACTIVATION_SMOKE_GOLDEN_RESTORED_RETIRED','HW parent')
need(hw['production_activation_path_proven'] is True and hw['stream_executed'] is False,'HW scope')
need(hq['status']=='PASS_CAPTURE_HQ_FOUR_STREAM_SHADOW_R27_GOLDEN_RESTORED_RETIRED','HQ parent')
need(hq['four_stream_live_robustness_proven'] is True and hq['post_g3_native_write_count_total']==0,'HQ stream authority')
launcher=(FRONT/'bin/front-imx681-launcher.py').read_text(); capture=(FRONT/'userspace/runtime/front-imx681-production-capture.c').read_text(); policy=(FRONT/'userspace/runtime/production-write-policy.c').read_text()
need("default='shadow'" in launcher and "choices=('shadow','cap-release-one-shot')" in launcher,'launcher shadow default')
need("need(not a.output_dir.exists(),'output-dir already exists; choose a fresh session directory')" in launcher,'fresh output collision guard')
need("SP11_FRONT_POST_G3_WRITE_POLICY" in launcher and "post_g3_write_policy" in launcher,'policy env')
need('STREAMOFF_OK' in capture and 'PROD_NATIVE_SCHEDULE_PASS' in capture and 'DB_SENSOR_WRITE_OK' in capture,'capture lifecycle telemetry')
need('SP11_FRONT_POST_G3_SHADOW' in policy and 'SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT' in policy and 'E003I_HA_APPLY_ONE_NATIVE' in policy,'write policy source')
with tempfile.TemporaryDirectory(prefix='e003i-hx-') as td0:
    td=Path(td0); build=td/'build'; env=os.environ.copy(); env['KERNEL_BUILD']=str(K)
    run([str(FRONT/'build-production.sh'),str(build)],env=env)
    stage=td/'stage'; penv=env.copy(); penv['BUILD_DIR']=str(build); run([str(FRONT/'stage-package.sh'),str(stage)],env=penv)
    m=stage/'PACKAGE-MANIFEST.sha256'; import hashlib
    need(hashlib.sha256(m.read_bytes()).hexdigest()=='57aa9cc2ad85131881416d7795603ab777a70e7c5877828986ff279266a5a757','package manifest')
    prefix=stage/'usr/lib/sp11-front-imx681'; out=td/'fresh-session'
    plan=json.loads(run([str(prefix/'bin/front-imx681-launcher.py'),'--topology-file',str(MEDIA),'--build-dir',str(prefix/'build'),'--output-dir',str(out)]).stdout)
    need(plan['post_g3_write_policy']=='shadow' and plan['execute'] is False,'dry plan policy')
    need(plan['output_dir']==str(out) and not out.exists(),'dry plan output')
    need(plan['discovery']['csiphy_entity']=='msm_csiphy2' and plan['discovery']['csid_entity']=='msm_csid1' and plan['discovery']['pix_entity']=='msm_vfe1_pix' and plan['discovery']['video_entity']=='msm_vfe1_video3','route plan')
    need(len(plan['capture_command'])==8+27,'capture argv frame count')
result={
 'schema':'sp11-e003i-hx-production-one-stream-acceptance-policy-v1',
 'status':'PASS_OFFLINE_PRODUCTION_ONE_STREAM_ACCEPTANCE_POLICY',
 'parent':['HW production activation PASS','HQ four-stream shadow PASS'],
 'camera_runtime_performed':False,
 'stream_authorized_by_this_stage':False,
 'future_candidate_stream_count':1,
 'frames':27,
 'frame_bytes':0x76b000,
 'tlbg_bytes':0xf020,
 'stats3a_bytes':0x51040,
 'fresh_snapshot_generation':1,
 'producer_generations':24,
 'producer_requests':23,
 'post_g3_policy':'shadow',
 'startup_native_writes':3,
 'post_g3_native_writes':0,
 'hardware_control_transactions_including_bootstrap':4,
 'streamoff_required':True,
 'kernel_health_required':True,
 'fresh_output_directory_required':True,
 'output_collision_fail_closed':True,
 'same_stream_retry_authorized':False,
 'same_boot_retry_authorized':False,
 'golden_return_required':True,
 'candidate_retirement_required':True,
 'minimum_free_bytes_before_arm':8589934592,
 'production_package_manifest_sha256':'57aa9cc2ad85131881416d7795603ab777a70e7c5877828986ff279266a5a757',
 'hv_dtb_sha256':'34880dc20d349bf966ebf62d6d8bb3f0130f436c88d9e4838585624a869e04c7',
 'qcom_camss_sha256':'7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95',
 'imx681_sha256':'ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6',
 'acceptance':{
   'production_discovery_matches_HW':True,
   '27_qc10c_tlbg_stats3a_files_exact_sizes':True,
   'producer_status_PASS':True,
   'producer_generations_G1_G24':True,
   'submitted_requests_R5_R27_count':23,
   'scheduler_release_G1_G26':True,
   'startup_sensor_writes_G1_G3_only':True,
   'post_G3_shadow_only':True,
   'STREAMOFF_OK':True,
   'kernel_health_PASS':True,
   'one_attempt_no_retry':True,
   'Golden_return_and_retirement':True
 },
 'next_gate':'HY fresh one-shot production stream candidate preparation using HW boot authority and HX policy'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HX_POLICY=PASS STREAMS=1 FRAMES=27 POLICY=shadow POST_G3_NATIVE_WRITES=0')
print('HX_EXPECTED_FILES=27x(QC10C_0x76b000 TLBG_0xf020 STATS3A_0x51040)')
print('HX_PRODUCER=G1..G24 REQUESTS=23 STARTUP_WRITES=3 HW_TX_WITH_BOOTSTRAP=4')
print('HX_RETRY=FORBIDDEN GOLDEN_RETURN=REQUIRED RETIRE=REQUIRED')
print('HX_CAMERA_RUNTIME=NO STREAM_AUTHORIZED=NO')
print('HX_VERIFY=PASS')
