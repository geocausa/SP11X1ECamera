#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, tempfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
BASE=HERE.parent
DB=BASE/'db-bounded-native-aec-sensor-loop'
PARENT='60335de'

def need(v,m):
    if not v: raise AssertionError(m)

need(subprocess.run(['git','merge-base','--is-ancestor',PARENT,'HEAD'],cwd=REPO).returncode==0,'DJ parent missing')
src=(DB/'e003i-db-six-frame-native-aec.c').read_text()
ev=(DB/'LIVE-FAILURE-ATTEMPT3.txt').read_text()
need('STATUS=FAIL_CLOSED_NATIVE_AEC_G4_AFTER_THREE_WRITES' in ev,'attempt3 status')
need('SENSOR_WRITES_SUCCEEDED=3' in ev and 'G4_NATIVE_AEC_RC=-142' in ev,'attempt3 boundary')
need('FOURTH_SENSOR_WRITE=not_permitted_not_performed' in ev,'fourth write absence')
need('GOLDEN_RETURN=PASS' in ev and 'DB_MENU=absent' in ev,'golden cleanup')
need('INVOKE_ORCHESTRATION_MISTAKE=finite_180s_execute_command_used_for_pin-capable_helper' in ev,'timeout disclosure')
need('const char *tlbg_prefix;' in src and 'const char *stats3a_prefix;' in src,'prefix ownership')
need(src.count('evidence_rc = persist_failure_pair(ctx, target, tlbg, stats);')==1,'one failure persistence call')
need(src.count('static int persist_failure_pair(')==1,'one persistence helper')
helper=src[src.index('static int persist_failure_pair('):src.index('static int release_control_at_video_boundary')]
need('"%s-FAIL-G%u.bin"' in helper and helper.count('save_file(')==2,'failure filenames/save count')
need('TLBG_BYTES' in helper and 'STATS3A_BYTES' in helper and 'DB_FAIL_PAIR_SAVED' in helper,'failure pair contract')
save=src[src.index('static int save_file('):src.index('static int submit_iq(')]
need('fsync(fd)' in save,'failure persistence must inherit fsync')
thread=src[src.index('static void *pair_audit_thread'):src.index('int main(')]
call=thread.index('evidence_rc = persist_failure_pair(ctx, target, tlbg, stats);')
branch=thread.rfind('if (rc) {',0,call)
latch=thread.index('e003i_db_schedule_fail(&ctx->schedule);',branch,call)
need(latch < call,'schedule fail must precede persistence')
need(thread.index('g3 != target') < thread.index('e003i_raw_request_to_imx681_controls') and thread.index('g3 != gt') < thread.index('e003i_raw_request_to_imx681_controls'),'identity gate before AEC')
need(src.count('rc = apply_sensor_controls(ctx->sensor_fd, &ev->controls)')==1,'one sensor apply site')
main=src[src.index('int main('):]
full_guard=main.index('if (audit.status || audit.completed != FRAME_COUNT)')
normal_save=main.index('snprintf(path, sizeof(path), "%s-%u.bin", tlbg_prefix, i);')
need(full_guard < normal_save,'normal raw save remains full-success-only')
need('E003I_DB_WRITTEN_SOURCE_GENERATIONS' in main,'three-write schedule guard retained')
with tempfile.TemporaryDirectory(prefix='e003i-dk-') as td:
    out=Path(td)/'helper'
    subprocess.run([str(DB/'build-helper.sh'),str(out)],check=True)
    need(out.is_file() and out.stat().st_size>0,'Werror helper build')
    helper_sha=subprocess.check_output(['sha256sum',str(out)],text=True).split()[0]
lines=[
 'DK_PARENT='+PARENT,
 'DK_ATTEMPT3=G1_R4,G2_R5,G3_R6_WRITES_PASS;G4_RC_MINUS142;NO_FOURTH_WRITE',
 'DK_FAIL_ORDER=schedule_fail_before_fsync_pair_save',
 'DK_FAIL_FILES=TLBG-FAIL-GN.bin,STATS3A-FAIL-GN.bin',
 'DK_SUCCESS_TIMING_PATH=no_per_generation_disk_io_added',
 'DK_SENSOR_APPLY_SITES=1',
 'DK_HELPER_WERROR=PASS SHA256='+helper_sha,
 'DK_REMOTE_INVOKE=persistent_job_required_for_pin_capable_helper',
 'DK_VERIFY=PASS',
]
(HERE/'VERIFY-RESULT.txt').write_text('\n'.join(lines)+'\n')
result={
 'schema':'sp11-e003i-dk-native-aec-fail-snapshot-preservation-v1',
 'status':'PASS_OFFLINE',
 'parent_commit':PARENT,
 'attempt3':{'status':'FAIL_CLOSED_G4_AFTER_THREE_WRITES','g4_rc':-142,'sensor_writes':3,'fourth_write':False,'golden_return':'PASS'},
 'failure_persistence':{'schedule_fail_before_save':True,'validated_pair_only':True,'filenames':['TLBG-FAIL-GN.bin','STATS3A-FAIL-GN.bin'],'fsync':True,'success_path_per_generation_disk_io_added':False},
 'runtime_sensor_apply_call_sites':1,
 'remote_orchestration':{'persistent_job_required':True,'finite_execute_timeout_forbidden':True},
 'helper_werror_sha256':helper_sha,
 'runtime_side_effects':'none',
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print('\n'.join(lines))
