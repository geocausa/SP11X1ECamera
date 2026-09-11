#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
D=Path(__file__).resolve().parent; BASE=D.parent
GS=BASE/'gs-continuous-shadow-scheduler-r27'; GT=BASE/'gt-limited-redundant-write-authority'; GU=BASE/'gu-limited-redundant-write-helper-integration'; GQ=BASE/'gq-continuous-control-ring-scheduler'
CAM='117136b2c624de5ef3f4c081cdcf9c363cda9f6db5c752b7ade5f5e11b1b3e95'; HELP='48fdd41c603ed763ec9044b409e3407d6f90fc8c5a6d08c1f15aae5eed04096b'; SCHED='8179ef6912a705e7296dd93fc147a6183d9d425b8e2c5052e7424de94cbccea1'; POLICY='0612751f1da4559340e5893217f7aca98ad0c265492861ef4888e7bd6a58bd0c'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
gs=json.loads((GS/'ATTEMPT1-PASS.json').read_text()); need(gs['status']=='PASS_CAPTURE_GS_CONTINUOUS_SHADOW_R27' and gs['golden_return'] and gs['candidate_retired'],'GS authority')
need(json.loads((GT/'RESULT.json').read_text())['status']=='PASS_OFFLINE_LIMITED_REDUNDANT_WRITE_AUTHORITY','GT authority')
need(json.loads((GU/'RESULT.json').read_text())['status']=='PASS_OFFLINE_LIMITED_REDUNDANT_WRITE_HELPER_INTEGRATION','GU authority')
need(json.loads((GQ/'RESULT.json').read_text())['status']=='PASS_OFFLINE_CONTINUOUS_RING_SCHEDULER','GQ authority')
with tempfile.TemporaryDirectory(prefix='e003i-gv-') as td0:
    td=Path(td0); cam=td/'qcom-camss.ko'; helper=td/'helper'; bootstrap=td/'bootstrap'
    subprocess.run([str(D/'build-camss.sh'),str(cam)],check=True)
    subprocess.run([str(D/'build-helper.sh'),str(helper)],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(bootstrap)],check=True)
    need(sha(D/'build/camss/camss.c')==CAM,'CAMSS source')
    need(sha(D/'build/helper/e003i-gv-limited-native-aec.c')==HELP,'GV helper source')
    need(sha(D/'build/helper/continuous-db-schedule.c')==SCHED,'scheduler source')
    need(sha(D/'build/helper/redundant-write-policy.c')==POLICY,'policy source')
    hs=(D/'build/helper/e003i-gv-limited-native-aec.c').read_text()
    for tok in ('GU_REDUNDANT_WRITE_ALLOW SOURCE=%u AFTER_G=%u','GU_SENSOR_WRITE_SHADOW_%s SOURCE=%u AFTER_G=%u','GU_LIMITED_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26','if (ev->source_generation <= 3U)','decision == E003I_WRITE_REDUNDANT_ALLOWED'):
        need(tok in hs,'helper contract '+tok)
    need(hs.count('apply_sensor_controls(ctx->sensor_fd, &ev->controls)')==1,'single physical write site')
    result={'schema':'sp11-e003i-gv-limited-redundant-write-offline-v1','status':'PASS_OFFLINE_READY_FOR_FRESH_ONE_SHOT','gs_live_shadow_authority':'PASS','gt_policy':'PASS','gu_helper_integration':'PASS','camss_source_sha256':CAM,'helper_source_sha256':HELP,'scheduler_source_sha256':SCHED,'policy_source_sha256':POLICY,'camss_module_sha256':sha(cam),'helper_binary_sha256':sha(helper),'bootstrap_binary_sha256':sha(bootstrap),'max_physical_write_sources':[1,2,3,4,5,6],'conditional_sources':[4,5,6],'changed_conditional_action':'shadow-only','later_sources':'G7..G26 shadow-only','one_stream_attempt_per_boot':True,'camera_runtime_performed':False,'changed_post_g3_controls_authorized':False}
    (D/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GV_OFFLINE_AUTHORITY=PASS')
print('GV_HELPER_WERROR=PASS')
print('GV_CHANGED_CONTROL_NO_WRITE=PASS')
print('GV_VERIFY=PASS')
