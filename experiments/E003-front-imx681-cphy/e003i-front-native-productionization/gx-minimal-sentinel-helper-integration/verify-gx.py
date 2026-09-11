#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
HERE=Path(__file__).resolve().parent; BASE=HERE.parent
GS=BASE/'gs-continuous-shadow-scheduler-r27'; GW=BASE/'gw-minimal-changed-post-g3-authority'; GQ=BASE/'gq-continuous-control-ring-scheduler'; GL=BASE/'gl-twentyfour-generation-gain-feed-publisher'
EN=BASE/'en-r5-r9-live-producer-integration'; DT=BASE/'dt-bounded-native-aec-cap-awb-hold-sensor-loop'; DN=BASE/'dn-native-aec-internal-cap'; CU=BASE/'cu-native-aec-raw-stats-request-loop'; CQ=BASE/'cq-aec-output-imx681-control-adapter'; CR=BASE/'cr-native-aec-effective-analyzer-producer'; CT=BASE/'ct-native-aec-bhist-bank4-replay'; CF=BASE/'cf-native-aec-final-exposure-si'; CE=BASE/'ce-native-aec-final-target-producer'; CC=BASE/'cc-native-aec-adrc-darkboost-tail'; BY=BASE/'by-native-aec-method11-point-aggregation'; CG=BASE/'cg-native-aec-qword-convergence-input'; CH=BASE/'ch-native-aec-t681-preview-arbitration'; BK=BASE/'bk-native-aec-history-state'; BJ=BASE/'bj-native-aec-log103-coordinate'; CV=BASE/'cv-native-aec-offline-sensor-control-join'
BASE_SHA='1dc9d1b2e31ca74c983e6bdf48dc66f3780da1ffbfd369e4c455d88d9266d5b1'; GX_SHA='8f28624537aa5c81da09b026ab6189f4efa9863f5d4519abe38a10986d01c350'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
need(json.loads((GW/'RESULT.json').read_text())['status']=='PASS_OFFLINE_MINIMAL_CHANGED_POST_G3_AUTHORITY','GW authority')
need(json.loads((GS/'ATTEMPT1-PASS.json').read_text())['status']=='PASS_CAPTURE_GS_CONTINUOUS_SHADOW_R27','GS live authority')
with tempfile.TemporaryDirectory(prefix='e003i-gx-') as td0:
    td=Path(td0); gsbin=td/'gs'; gx=td/'gx.c'; exe=td/'gx-helper'
    subprocess.run([str(GS/'build-helper.sh'),str(gsbin)],check=True,stdout=subprocess.DEVNULL)
    base=GS/'build/helper/e003i-gs-shadow-native-aec.c'; need(sha(base)==BASE_SHA,'GS helper drift')
    subprocess.run(['python3',str(HERE/'make-gx-helper.py'),str(base),str(gx)],check=True,stdout=subprocess.DEVNULL); need(sha(gx)==GX_SHA,'GX transform hash')
    hs=gx.read_text()
    for tok in ('#include "minimal-dgain-sentinel.h"','e003i_gw_make_sentinel(','GX_SENTINEL_WRITE_ALLOW SOURCE=4','GX_SENTINEL_SUPPRESSED SOURCE=4','GX_SENSOR_WRITE_SHADOW SOURCE=%u','ctx->last_applied_controls = *write_controls;','if (ev->source_generation == 4U)','else if (ev->source_generation > 4U)','GX_SENTINEL_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26'):
        need(tok in hs,'missing '+tok)
    need('if (ev->source_generation > 3U) {' not in hs,'old GS all-later shadow remains')
    need(hs.count('apply_sensor_controls(ctx->sensor_fd, write_controls)')==1,'single physical ioctl site')
    need(hs.count('if (completed != after_generation)\n\t\treturn -ETIME;')>=3,'boundary gates')
    need('audit.bounded_shadow_count != 22U' in hs,'G5..G26 bound')
    need('audit.sentinel_write_count + audit.sentinel_suppressed_count != 1U' in hs,'one sentinel decision')
    inc=[td,EN,DT,DN,CV,CU,CQ,CR,CT,CF,CE,CC,BY,CG,CH,BK,BJ,GQ,GW,GL]
    sources=[gx,GQ/'continuous-db-schedule.c',GW/'minimal-dgain-sentinel.c',GL/'gain-feed.c',CV/'native-raw-control-join.c',CU/'native-raw-aec-loop.c',CU/'native-stats3a.c',CQ/'native-imx681-control.c',CR/'native-effective-analyzers.c',CT/'native-bhist-bank4.c',DN/'native-aec-request-loop.c',DN/'native-internal-cap.c',CF/'native-final-exposure.c',CE/'native-final-target.c',CC/'native-aec-tail.c',BY/'native-target-aggregate.c',CG/'native-convergence.c',CH/'native-t681.c',BK/'native-aec-state.c',BJ/'native-log103.c']
    subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']+[f'-I{x}' for x in inc]+[str(x) for x in sources]+['-pthread','-lm','-o',str(exe)],check=True)
    binary_sha=sha(exe)
result={'schema':'sp11-e003i-gx-minimal-sentinel-helper-integration-v1','status':'PASS_OFFLINE_MINIMAL_SENTINEL_HELPER_INTEGRATION','base_gs_helper_sha256':BASE_SHA,'transformed_helper_sha256':GX_SHA,'compiled_helper_sha256':binary_sha,'compile':'PASS_WERROR','startup_native_physical_sources':[1,2,3],'conditional_sentinel_source':4,'sentinel_change':'digital_gain_code +1 only','native_g4_changed_action':'suppress sentinel and shadow','g5_g26_action':'shadow-only','bounded_shadow_count':22,'pending_at_end':'G27','exact_boundary_fail_closed_preserved':True,'single_physical_ioctl_site':True,'last_applied_tracks_actual_written_tuple':True,'camera_runtime_performed':False,'broader_post_g3_writes_authorized':False,'safe_next_step':'fresh one-shot candidate requiring one G4 sentinel transaction; archive and Golden-return on any result'}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GX_GS_TRANSFORM=PASS')
print('GX_HELPER_WERROR=PASS')
print('GX_SENTINEL_ONLY_G4=PASS')
print('GX_G5_G26_SHADOW=PASS')
print('GX_VERIFY=PASS')
