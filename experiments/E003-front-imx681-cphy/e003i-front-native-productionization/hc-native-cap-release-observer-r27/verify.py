#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
D=Path(__file__).resolve().parent; BASE=D.parent
GZ=BASE/'gz-native-response-threshold-analysis'; HA=BASE/'ha-native-cap-release-one-write-policy'; HB=BASE/'hb-native-cap-release-helper-integration'; GS=BASE/'gs-continuous-shadow-scheduler-r27'
CAM='117136b2c624de5ef3f4c081cdcf9c363cda9f6db5c752b7ade5f5e11b1b3e95'
HELP='578f41d5cc0935aff327f500d38c095ed64f7428d2e245adc1f8196e9b3c99a3'
HBHELP='5582c49f577b5639859b9326eb2affa70046b7c4bcb8328061fac0f998c5d6bd'
SCHED='8179ef6912a705e7296dd93fc147a6183d9d425b8e2c5052e7424de94cbccea1'
POLICY='bee1b9294556e0c35adc9081fef65489b04c1295a2ea7d8c6ead8d0c137b057f'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
need(json.loads((GZ/'RESULT.json').read_text())['status']=='PASS_OFFLINE_RESPONSE_THRESHOLD_CENSORED_BY_PREVIEW_CAP','GZ authority')
need(json.loads((HA/'RESULT.json').read_text())['status']=='PASS_OFFLINE_NATIVE_CAP_RELEASE_ONE_WRITE_POLICY','HA authority')
need(json.loads((HB/'RESULT.json').read_text())['status']=='PASS_OFFLINE_NATIVE_CAP_RELEASE_HELPER_INTEGRATION','HB authority')
need(json.loads((GS/'ATTEMPT1-PASS.json').read_text())['status']=='PASS_CAPTURE_GS_CONTINUOUS_SHADOW_R27','GS live authority')
with tempfile.TemporaryDirectory(prefix='e003i-hc-') as td0:
    td=Path(td0); cam=td/'qcom-camss.ko'; helper=td/'helper'; bootstrap=td/'bootstrap'
    subprocess.run([str(D/'build-camss.sh'),str(cam)],check=True)
    subprocess.run([str(D/'build-helper.sh'),str(helper)],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(bootstrap)],check=True)
    need(sha(D/'build/camss/camss.c')==CAM,'CAMSS source')
    need(sha(D/'build/helper/helper-hb.c')==HBHELP,'HB intermediate source')
    need(sha(D/'build/helper/e003i-hc-caprelease-native-aec.c')==HELP,'HC helper source')
    need(sha(D/'build/helper/continuous-db-schedule.c')==SCHED,'scheduler source')
    need(sha(D/'build/helper/native-cap-release-policy.c')==POLICY,'HA policy source')
    hs=(D/'build/helper/e003i-hc-caprelease-native-aec.c').read_text()
    for tok in (
      'e003i_ha_decide(',
      'HB_NATIVE_CAP_RELEASE_ALLOW SOURCE=%u',
      'HB_NATIVE_CAP_RELEASE_SHADOW SOURCE=%u',
      'HC_CAP_RELEASE_HORIZON_SHADOW SOURCE=%u',
      'if (ev->source_generation > 24U)',
      'ctx->later_native_write_applied = 1U;',
      'audit.later_native_write_count > 1U',
      'HC_NATIVE_CAP_RELEASE_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26',
      'APPLY_EFFECT_MAX=G27'):
        need(tok in hs,'helper contract '+tok)
    need(hs.count('apply_sensor_controls(ctx->sensor_fd, &ev->controls)')==1,'single physical ioctl site')
    need(hs.count('if (completed != after_generation)\n\t\treturn -ETIME;')>=3,'exact boundary checks')
    need('audit.later_shadow_count + audit.later_native_write_count != 23U' in hs,'post-G3 decision accounting')
    result={
      'schema':'sp11-e003i-hc-native-cap-release-observer-offline-v1',
      'status':'PASS_OFFLINE_READY_FOR_FRESH_ONE_SHOT',
      'gz_threshold_analysis':'PASS','ha_policy':'PASS','hb_helper_integration':'PASS','gs_live_scheduler_authority':'PASS',
      'camss_source_sha256':CAM,'hb_intermediate_sha256':HBHELP,'helper_source_sha256':HELP,
      'scheduler_source_sha256':SCHED,'policy_source_sha256':POLICY,
      'camss_module_sha256':sha(cam),'helper_binary_sha256':sha(helper),'bootstrap_binary_sha256':sha(bootstrap),
      'startup_native_sources':[1,2,3],'post_g3_observed_sources':'G4..G26',
      'post_g3_native_write_eligible_sources':'G4..G24','horizon_forced_shadow_sources':[25,26],
      'maximum_post_g3_native_writes':1,'maximum_effect_generation':27,
      'synthetic_control_delta_added':False,'exact_boundary_fail_closed_preserved':True,
      'valid_live_outcomes':['PASS_NO_CAP_RELEASE','PASS_CAP_RELEASE_ONE_NATIVE_WRITE'],
      'one_stream_attempt_per_boot':True,'camera_runtime_performed':False,
      'production_native_changed_post_g3_feedback_proven':False
    }
    (D/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HC_OFFLINE_AUTHORITY=PASS')
print('HC_HELPER_WERROR=PASS')
print('HC_ONE_NATIVE_LATER_WRITE_MAX=PASS')
print('HC_EFFECT_HORIZON_G27=PASS')
print('HC_SYNTHETIC_DELTA=NONE')
print('HC_VERIFY=PASS')
