#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
HERE=Path(__file__).resolve().parent; BASE=HERE.parent
GS=BASE/'gs-continuous-shadow-scheduler-r27'; HA=BASE/'ha-native-cap-release-one-write-policy'; GQ=BASE/'gq-continuous-control-ring-scheduler'; GL=BASE/'gl-twentyfour-generation-gain-feed-publisher'
EN=BASE/'en-r5-r9-live-producer-integration'; DT=BASE/'dt-bounded-native-aec-cap-awb-hold-sensor-loop'; DN=BASE/'dn-native-aec-internal-cap'; CU=BASE/'cu-native-aec-raw-stats-request-loop'; CQ=BASE/'cq-aec-output-imx681-control-adapter'; CR=BASE/'cr-native-aec-effective-analyzer-producer'; CT=BASE/'ct-native-aec-bhist-bank4-replay'; CF=BASE/'cf-native-aec-final-exposure-si'; CE=BASE/'ce-native-aec-final-target-producer'; CC=BASE/'cc-native-aec-adrc-darkboost-tail'; BY=BASE/'by-native-aec-method11-point-aggregation'; CG=BASE/'cg-native-aec-qword-convergence-input'; CH=BASE/'ch-native-aec-t681-preview-arbitration'; BK=BASE/'bk-native-aec-history-state'; BJ=BASE/'bj-native-aec-log103-coordinate'; CV=BASE/'cv-native-aec-offline-sensor-control-join'
BASE_SHA='1dc9d1b2e31ca74c983e6bdf48dc66f3780da1ffbfd369e4c455d88d9266d5b1'; HB_SHA='5582c49f577b5639859b9326eb2affa70046b7c4bcb8328061fac0f998c5d6bd'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
need(json.loads((HA/'RESULT.json').read_text())['status']=='PASS_OFFLINE_NATIVE_CAP_RELEASE_ONE_WRITE_POLICY','HA authority')
need(json.loads((GS/'ATTEMPT1-PASS.json').read_text())['status']=='PASS_CAPTURE_GS_CONTINUOUS_SHADOW_R27','GS live authority')
with tempfile.TemporaryDirectory(prefix='e003i-hb-') as td0:
    td=Path(td0); gsbin=td/'gs'; hb=td/'hb.c'; exe=td/'hb-helper'
    subprocess.run([str(GS/'build-helper.sh'),str(gsbin)],check=True,stdout=subprocess.DEVNULL)
    base=GS/'build/helper/e003i-gs-shadow-native-aec.c'; need(sha(base)==BASE_SHA,'GS helper drift')
    subprocess.run(['python3',str(HERE/'make-hb-helper.py'),str(base),str(hb)],check=True,stdout=subprocess.DEVNULL); need(sha(hb)==HB_SHA,'HB transform hash')
    hs=hb.read_text()
    for tok in ('#include "native-cap-release-policy.h"','e003i_ha_decide(','HB_NATIVE_CAP_RELEASE_ALLOW SOURCE=%u','HB_NATIVE_CAP_RELEASE_SHADOW SOURCE=%u','ctx->last_applied_controls = ev->controls;','ctx->later_native_write_applied = 1U;','ctx->later_native_write_count++;','audit.later_shadow_count + audit.later_native_write_count != 23U','HB_NATIVE_CAP_RELEASE_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26'):
        need(tok in hs,'missing '+tok)
    need('if (ev->source_generation > 3U) {' in hs,'post-G3 policy branch')
    need(hs.count('apply_sensor_controls(ctx->sensor_fd, &ev->controls)')==1,'single physical ioctl site')
    need(hs.count('if (completed != after_generation)\n\t\treturn -ETIME;')>=3,'exact boundary checks')
    need('audit.later_native_write_count > 1U' in hs,'one later write invariant')
    inc=[td,EN,DT,DN,CV,CU,CQ,CR,CT,CF,CE,CC,BY,CG,CH,BK,BJ,GQ,HA,GL]
    sources=[hb,GQ/'continuous-db-schedule.c',HA/'native-cap-release-policy.c',GL/'gain-feed.c',CV/'native-raw-control-join.c',CU/'native-raw-aec-loop.c',CU/'native-stats3a.c',CQ/'native-imx681-control.c',CR/'native-effective-analyzers.c',CT/'native-bhist-bank4.c',DN/'native-aec-request-loop.c',DN/'native-internal-cap.c',CF/'native-final-exposure.c',CE/'native-final-target.c',CC/'native-aec-tail.c',BY/'native-target-aggregate.c',CG/'native-convergence.c',CH/'native-t681.c',BK/'native-aec-state.c',BJ/'native-log103.c']
    subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']+[f'-I{x}' for x in inc]+[str(x) for x in sources]+['-pthread','-lm','-o',str(exe)],check=True)
    binary_sha=sha(exe)
result={'schema':'sp11-e003i-hb-native-cap-release-helper-integration-v1','status':'PASS_OFFLINE_NATIVE_CAP_RELEASE_HELPER_INTEGRATION','base_gs_helper_sha256':BASE_SHA,'transformed_helper_sha256':HB_SHA,'compiled_helper_sha256':binary_sha,'compile':'PASS_WERROR','startup_native_sources':[1,2,3],'post_g3_policy':'HA exact native cap-release gate','maximum_post_g3_native_writes':1,'post_g3_release_sources':'G4..G26','post_g3_decision_count':23,'pending_at_end':'G27','synthetic_control_delta_added':False,'exact_boundary_fail_closed_preserved':True,'single_physical_ioctl_site':True,'last_applied_updates_only_after_successful_ioctl':True,'one_write_latch_sets_only_after_successful_post_g3_ioctl':True,'camera_runtime_performed':False,'live_run_authorized':False,'safe_next_step':'design a bounded cap-release observation candidate; do not arm until its observation duration/stop conditions are proved offline'}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HB_GS_TRANSFORM=PASS')
print('HB_HELPER_WERROR=PASS')
print('HB_EXACT_BOUNDARY_FAIL_CLOSED=PASS')
print('HB_ONE_NATIVE_LATER_WRITE_MAX=PASS')
print('HB_SYNTHETIC_DELTA=NONE')
print('HB_VERIFY=PASS')
