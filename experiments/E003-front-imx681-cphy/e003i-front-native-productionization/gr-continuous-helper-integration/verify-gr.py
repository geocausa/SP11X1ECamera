#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
GO=BASE/'go-twentyseven-frame-live-r5-r27'
GQ=BASE/'gq-continuous-control-ring-scheduler'
GP=BASE/'gp-go-control-timing-authority'
EN=BASE/'en-r5-r9-live-producer-integration'; GL=BASE/'gl-twentyfour-generation-gain-feed-publisher'
DT=BASE/'dt-bounded-native-aec-cap-awb-hold-sensor-loop'; DN=BASE/'dn-native-aec-internal-cap'; CU=BASE/'cu-native-aec-raw-stats-request-loop'
CQ=BASE/'cq-aec-output-imx681-control-adapter'; CR=BASE/'cr-native-aec-effective-analyzer-producer'; CT=BASE/'ct-native-aec-bhist-bank4-replay'
CF=BASE/'cf-native-aec-final-exposure-si'; CE=BASE/'ce-native-aec-final-target-producer'; CC=BASE/'cc-native-aec-adrc-darkboost-tail'
BY=BASE/'by-native-aec-method11-point-aggregation'; CG=BASE/'cg-native-aec-qword-convergence-input'; CH=BASE/'ch-native-aec-t681-preview-arbitration'
BK=BASE/'bk-native-aec-history-state'; BJ=BASE/'bj-native-aec-log103-coordinate'; CV=BASE/'cv-native-aec-offline-sensor-control-join'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
gq=json.loads((GQ/'RESULT.json').read_text()); need(gq['status']=='PASS_OFFLINE_CONTINUOUS_RING_SCHEDULER','GQ authority')
gp=json.loads((GP/'RESULT.json').read_text()); need(gp['status']=='PASS_OFFLINE_GO_CONTROL_TIMING_AUTHORITY','GP authority')
source=GO/'build/helper/e003i-go-twentyseven-frame-native-aec.c'
need(sha(source)=='32ecff0848a3f47fe149ead36ccf63eec26a8c78180075129253a65792dedf1e','GO helper source')
with tempfile.TemporaryDirectory(prefix='e003i-gr-') as td0:
    td=Path(td0); helper=td/'e003i-gr-continuous-helper.c'; exe=td/'helper'
    subprocess.run(['python3',str(HERE/'make-gr-helper.py'),str(source),str(helper)],check=True,stdout=subprocess.DEVNULL)
    hs=helper.read_text()
    # Integration delta contract.
    for tok in ('#include "continuous-db-schedule.h"','struct e003i_cont_schedule_state schedule','struct e003i_cont_apply_event apply_event[FRAME_COUNT]','if (target >= 2U) {','e003i_cont_schedule_queue','e003i_cont_schedule_release','GR_CONT_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 PENDING=G27 EFFECT_RANGE=G4..G29'):
        need(tok in hs,'missing integration token '+tok)
    need('target >= 2U && target <= 4U' not in hs,'old release cap remains')
    # Exact-window fail-closed timing semantics must remain present around the real ioctl.
    need(hs.count('if (completed != after_generation)\n\t\treturn -ETIME;')==3,'exact-boundary checks before release, before write, and after write')
    need('start_ns = mono_ns();\n\trc = apply_sensor_controls(ctx->sensor_fd, &ev->controls);\n\tend_ns = mono_ns();' in hs,'real sensor write path changed')
    need('if (completed >= after_generation)\n\t\t\tbreak;' in hs,'boundary wait changed')
    # No producer/transport/AEC bound drift.
    for tok in ('#define FRAME_COUNT 27U','if (target <= 24U) {','TARGETS=1..27','GN_DQBUF_MISMATCH','LIVE_REQUEUE_INDEX'):
        need(tok in hs,'GO integration drift '+tok)
    # Build exactly as a live-capable helper, but do not execute it.
    shutil_files=[(EN/'native-db-schedule.c',None)]
    inc=[td,EN,DT,DN,CV,CU,CQ,CR,CT,CF,CE,CC,BY,CG,CH,BK,BJ]
    sources=[helper,GQ/'continuous-db-schedule.c',GL/'gain-feed.c',CV/'native-raw-control-join.c',CU/'native-raw-aec-loop.c',CU/'native-stats3a.c',CQ/'native-imx681-control.c',CR/'native-effective-analyzers.c',CT/'native-bhist-bank4.c',DN/'native-aec-request-loop.c',DN/'native-internal-cap.c',CF/'native-final-exposure.c',CE/'native-final-target.c',CC/'native-aec-tail.c',BY/'native-target-aggregate.c',CG/'native-convergence.c',CH/'native-t681.c',BK/'native-aec-state.c',BJ/'native-log103.c']
    # Header/source inputs used by helper.
    (td/'continuous-db-schedule.h').write_bytes((GQ/'continuous-db-schedule.h').read_bytes())
    (td/'gain-feed.h').write_bytes((GL/'gain-feed.h').read_bytes())
    cmd=['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']+[f'-I{x}' for x in inc]+[str(x) for x in sources]+['-pthread','-lm','-o',str(exe)]
    subprocess.run(cmd,check=True)
    helper_sha=sha(helper); binary_sha=sha(exe)
# Boundary-miss state machine proof. This mirrors the two equality checks surrounding the real ioctl.
def gate(expected, before, after):
    if before < expected: return 'wait'
    if before != expected: return 'reject-before-write'
    # writer would run only here
    if after != expected: return 'reject-after-write'
    return 'pass'
need(gate(8,7,7)=='wait','early gate')
need(gate(8,9,9)=='reject-before-write','missed boundary')
need(gate(8,8,9)=='reject-after-write','write crossed boundary')
need(gate(8,8,8)=='pass','exact boundary')
result={'schema':'sp11-e003i-gr-continuous-helper-integration-v1','status':'PASS_OFFLINE_CONTINUOUS_HELPER_INTEGRATION','base_go_helper_sha256':sha(source),'transformed_helper_sha256':helper_sha,'compiled_helper_sha256':binary_sha,'compile':'PASS_WERROR','release_targets':'G2..G27','released_sources':'G1..G26','pending_at_bounded_end':'G27','exact_boundary_precheck_preserved':True,'exact_boundary_postwrite_check_preserved':True,'real_sensor_ioctl_path_preserved':True,'boundary_miss_simulation':{'early':'wait','already_advanced':'reject-before-write','advanced_during_write':'reject-after-write','exact':'pass'},'continuous_physical_writes_performed':False,'camera_runtime_performed':False,'live_authorized':False,'safe_next_step':'fresh one-shot shadow scheduler: run continuous release/gate logic live but suppress physical writes after G3'}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GR_HELPER_WERROR=PASS')
print('GR_CONT_RELEASE_RANGE=G2_G27 PASS')
print('GR_EXACT_BOUNDARY_FAIL_CLOSED=PASS')
print('GR_VERIFY=PASS')
