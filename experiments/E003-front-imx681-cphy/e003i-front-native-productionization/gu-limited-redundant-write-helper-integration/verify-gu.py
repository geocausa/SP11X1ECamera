#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
GS=BASE/'gs-continuous-shadow-scheduler-r27'
GT=BASE/'gt-limited-redundant-write-authority'
GQ=BASE/'gq-continuous-control-ring-scheduler'
GL=BASE/'gl-twentyfour-generation-gain-feed-publisher'
EN=BASE/'en-r5-r9-live-producer-integration'; DT=BASE/'dt-bounded-native-aec-cap-awb-hold-sensor-loop'; DN=BASE/'dn-native-aec-internal-cap'; CU=BASE/'cu-native-aec-raw-stats-request-loop'
CQ=BASE/'cq-aec-output-imx681-control-adapter'; CR=BASE/'cr-native-aec-effective-analyzer-producer'; CT=BASE/'ct-native-aec-bhist-bank4-replay'; CF=BASE/'cf-native-aec-final-exposure-si'; CE=BASE/'ce-native-aec-final-target-producer'; CC=BASE/'cc-native-aec-adrc-darkboost-tail'; BY=BASE/'by-native-aec-method11-point-aggregation'; CG=BASE/'cg-native-aec-qword-convergence-input'; CH=BASE/'ch-native-aec-t681-preview-arbitration'; BK=BASE/'bk-native-aec-history-state'; BJ=BASE/'bj-native-aec-log103-coordinate'; CV=BASE/'cv-native-aec-offline-sensor-control-join'
BASE_SHA='1dc9d1b2e31ca74c983e6bdf48dc66f3780da1ffbfd369e4c455d88d9266d5b1'
GU_SHA='48fdd41c603ed763ec9044b409e3407d6f90fc8c5a6d08c1f15aae5eed04096b'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p,status in [(GS,'PASS_CAPTURE_GS_CONTINUOUS_SHADOW_R27'),(GT,'PASS_OFFLINE_LIMITED_REDUNDANT_WRITE_AUTHORITY'),(GQ,'PASS_OFFLINE_CONTINUOUS_RING_SCHEDULER')]:
    f=p/('ATTEMPT1-PASS.json' if p==GS else 'RESULT.json')
    need(json.loads(f.read_text())['status']==status,p.name)
subprocess.run(['python3',str(GT/'verify-gt.py')],check=True,stdout=subprocess.DEVNULL)
with tempfile.TemporaryDirectory(prefix='e003i-gu-') as td0:
    td=Path(td0); gs_bin=td/'gs-base'; gu=td/'e003i-gu-limited-redundant-native-aec.c'; exe=td/'gu-helper'
    # Rebuild the exact committed GS helper source; build output is ignored evidence only.
    subprocess.run([str(GS/'build-helper.sh'),str(gs_bin)],check=True,stdout=subprocess.DEVNULL)
    base_src=GS/'build/helper/e003i-gs-shadow-native-aec.c'
    need(sha(base_src)==BASE_SHA,'GS helper source drift')
    subprocess.run(['python3',str(HERE/'make-gu-helper.py'),str(base_src),str(gu)],check=True,stdout=subprocess.DEVNULL)
    need(sha(gu)==GU_SHA,'GU transformed helper hash')
    hs=gu.read_text()
    for tok in (
      '#include "redundant-write-policy.h"',
      'e003i_redundant_write_decide(ev->source_generation,',
      'GU_REDUNDANT_WRITE_ALLOW SOURCE=%u AFTER_G=%u',
      'GU_SENSOR_WRITE_SHADOW_%s SOURCE=%u AFTER_G=%u',
      'if (ev->source_generation <= 3U)',
      'decision == E003I_WRITE_REDUNDANT_ALLOWED',
      'decision == E003I_WRITE_SHADOW_CHANGED',
      'decision == E003I_WRITE_SHADOW_BOUND',
      'ctx->last_applied_controls = ev->controls;',
      'ctx->physical_write_count++;',
      'GU_LIMITED_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26'):
        need(tok in hs,'missing GU contract '+tok)
    need('if (ev->source_generation > 3U) {' not in hs,'old unconditional GS shadow block remains')
    # The one real hardware write site remains inside the original exact-boundary gate.
    need(hs.count('apply_sensor_controls(ctx->sensor_fd, &ev->controls)')==1,'physical ioctl path count')
    need(hs.count('if (completed != after_generation)\n\t\treturn -ETIME;')>=3,'exact boundary checks')
    need('if (target >= 2U) {' in hs,'continuous release range')
    need('if (target <= 24U) {' in hs,'gain publisher bound')
    # Compile live-capable helper with the exact GQ/GT sources.
    inc=[td,EN,DT,DN,CV,CU,CQ,CR,CT,CF,CE,CC,BY,CG,CH,BK,BJ,GQ,GT,GL]
    sources=[gu,GQ/'continuous-db-schedule.c',GT/'redundant-write-policy.c',GL/'gain-feed.c',CV/'native-raw-control-join.c',CU/'native-raw-aec-loop.c',CU/'native-stats3a.c',CQ/'native-imx681-control.c',CR/'native-effective-analyzers.c',CT/'native-bhist-bank4.c',DN/'native-aec-request-loop.c',DN/'native-internal-cap.c',CF/'native-final-exposure.c',CE/'native-final-target.c',CC/'native-aec-tail.c',BY/'native-target-aggregate.c',CG/'native-convergence.c',CH/'native-t681.c',BK/'native-aec-state.c',BJ/'native-log103.c']
    subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']+[f'-I{x}' for x in inc]+[str(x) for x in sources]+['-pthread','-lm','-o',str(exe)],check=True)
    binary_sha=sha(exe)
result={
 'schema':'sp11-e003i-gu-limited-redundant-write-helper-integration-v1',
 'status':'PASS_OFFLINE_LIMITED_REDUNDANT_WRITE_HELPER_INTEGRATION',
 'base_gs_helper_sha256':BASE_SHA,'transformed_helper_sha256':GU_SHA,'compiled_helper_sha256':binary_sha,
 'compile':'PASS_WERROR','continuous_release_sources':'G1..G26','startup_physical_sources':[1,2,3],
 'conditional_redundant_sources':[4,5,6],'changed_g4_g6_action':'shadow-only','g7_g26_action':'shadow-only','pending_at_end':'G27',
 'exact_boundary_fail_closed_preserved':True,'single_physical_ioctl_site':True,'last_applied_updates_only_after_successful_ioctl':True,
 'camera_runtime_performed':False,'changed_post_g3_controls_authorized':False,
 'safe_next_step':'fresh one-shot limited redundant-write candidate: max six physical writes, with G4..G6 real only if exact-equal at runtime'}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GU_GS_TRANSFORM=PASS')
print('GU_HELPER_WERROR=PASS')
print('GU_EXACT_BOUNDARY_FAIL_CLOSED=PASS')
print('GU_POLICY_INTEGRATION=PASS')
print('GU_VERIFY=PASS')
