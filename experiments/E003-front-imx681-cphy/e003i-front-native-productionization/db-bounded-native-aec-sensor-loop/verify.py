#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, tempfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
BASE=HERE.parent
AQ=BASE/'aq-windows-aec-arbitration-table'
CH=BASE/'ch-native-aec-t681-preview-arbitration'
CQ=BASE/'cq-aec-output-imx681-control-adapter'
CV=BASE/'cv-native-aec-offline-sensor-control-join'
DA=BASE/'da-native-aec-delayed-sensor-schedule'
CW=BASE/'cw-imx681-atomic-dynamic-control-cluster'
PARENT='c094198'

def need(v,m):
    if not v: raise AssertionError(m)
def load(p): return json.loads(p.read_text())

need(subprocess.run(['git','merge-base','--is-ancestor',PARENT,'HEAD'],cwd=REPO).returncode==0,'corrected range parent missing')
need(subprocess.check_output(['git','rev-parse','--abbrev-ref','HEAD'],cwd=REPO,text=True).strip()=='experiment/e003-front-imx681-cphy','branch')
aq=load(AQ/'RESULT.json'); ch=load(CH/'RESULT.json'); cq=load(CQ/'RESULT.json'); cv=load(CV/'RESULT.json'); da=load(DA/'RESULT.json'); cw=load(CW/'RESULT.json')
need(aq['status']=='PASS' and aq['windows_oracle']['active_preview_range_recap']['max_time_ns']==66666664,'AQ corrected preview range')
need(aq['windows_oracle']['active_preview_range_recap']['max_gain']==92.0 and aq['windows_oracle']['active_preview_range_recap']['policy']==0,'AQ gain/policy')
need(ch['status']=='PASS' and ch['preview_limits']['max_time_ns']==66666664 and ch['preview_limits']['max_gain']==92.0,'CH corrected range')
need(cq['status'].startswith('PASS_') and cq['gain']['actual_t681_postfit_output_max']==92.0,'CQ corrected gain domain')
need(cq['windows']['active_preview_range']['max_time_ns']==66666664,'CQ corrected time domain')
need(cv['status']=='PASS' and cv['sensor_delay']['max_pipeline_frames']==2,'CV sensor delay')
need(da['status']=='PASS_OFFLINE' and da['windows_stats_to_request_frames']==3 and da['cy_write_to_first_effect_generations']==2,'DA timing law')
need(da['write_after_generation_offset']==1 and da['first_effect_generation_offset']==3,'DA offsets')
need(da['cold_bootstrap']=={'frame_length_lines':3562,'vertical_blanking':1402,'exposure_lines':3554,'analogue_gain_code':0,'digital_gain_code':256,'isp_gain':1.0},'DA cold bootstrap')
need(cw['status']=='PASS_OFFLINE','CW parent')

src=(HERE/'e003i-db-six-frame-native-aec.c').read_text()
sched=(HERE/'native-db-schedule.c').read_text()+(HERE/'native-db-schedule.h').read_text()
for x in ['atomic_uint video_completed_generation','DB_VIDEO_GATE_PASS','DB_BOUNDARY_RELEASE_FAIL','DB_AEC_OWNERSHIP_FAIL','e003i_raw_request_to_imx681_controls','e003i_db_schedule_queue','e003i_db_schedule_release','rc = apply_sensor_controls(ctx->sensor_fd, &ev->controls)']:
    need(x in src+sched,x)
need(src.count('rc = apply_sensor_controls(ctx->sensor_fd, &ev->controls)')==1,'one runtime sensor apply site')
need('.count = 4' in src and all(x in src for x in ['V4L2_CID_VBLANK','V4L2_CID_EXPOSURE','V4L2_CID_ANALOGUE_GAIN','V4L2_CID_DIGITAL_GAIN']),'four-control cluster')
thread=src[src.index('static void *pair_audit_thread'):]
need(thread.index('release_control_at_video_boundary(ctx, target)') < thread.index('e003i_raw_request_to_imx681_controls'),'release must precede current-generation AEC compute')
need(src.count('if (completed != after_generation)')>=3,'exact DQBUF window guards')
for x in ['E003I_DB_STATS_TO_REQUEST_DELAY 3U','E003I_DB_WRITE_AFTER_OFFSET 1U','E003I_DB_WRITE_TO_EFFECT_DELAY 2U','E003I_DB_WRITTEN_SOURCE_GENERATIONS 3U']:
    need(x in sched,x)

harness=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "native-db-schedule.h"
static struct e003i_imx681_controls good(unsigned n){
    struct e003i_imx681_controls c; memset(&c,0,sizeof(c));
    c.line_count_before_even=3554; c.frame_length_lines=3562; c.vertical_blanking=1402;
    c.exposure_lines=3554; c.analogue_gain_code=n; c.digital_gain_code=256; c.isp_gain=1.0f; return c;
}
static int check_event(const struct e003i_db_apply_event *e,unsigned after){
    unsigned src=after-1; return e->apply && e->source_generation==src && e->write_after_generation==after && e->logical_request_frame==src+3 && e->expected_effect_generation==after+2;
}
static int normal(void){
    struct e003i_db_schedule_state s; struct e003i_db_apply_event e; struct e003i_imx681_controls c; unsigned g;
    e003i_db_schedule_init(&s); c=good(1); if(e003i_db_schedule_queue(&s,1,&c)) return 11;
    for(g=2;g<=6;g++){ if(g<=4 && (e003i_db_schedule_release(&s,g,&e) || !check_event(&e,g))) return 20+g; c=good(g); if(e003i_db_schedule_queue(&s,g,&c)) return 30+g; }
    return (s.failed || s.queued_generation!=6 || s.released_writes!=3) ? 50 : 0;
}
static int failures(void){
    struct e003i_db_schedule_state s; struct e003i_db_apply_event e; struct e003i_imx681_controls c=good(1); int rc;
    e003i_db_schedule_init(&s); rc=e003i_db_schedule_queue(&s,2,&c); if(rc!=-3 || !s.failed || s.released_writes) return 60;
    rc=e003i_db_schedule_queue(&s,1,&c); if(rc!=-2 || s.released_writes) return 61;
    e003i_db_schedule_init(&s); c=good(1); c.vertical_blanking=1401; rc=e003i_db_schedule_queue(&s,1,&c); if(rc!=-4 || !s.failed || s.released_writes) return 62;
    e003i_db_schedule_init(&s); c=good(1); if(e003i_db_schedule_queue(&s,1,&c)) return 63; e003i_db_schedule_fail(&s); c=good(2); rc=e003i_db_schedule_queue(&s,2,&c); if(rc!=-2 || s.released_writes) return 64;
    e003i_db_schedule_init(&s); rc=e003i_db_schedule_release(&s,2,&e); if(rc!=-4 || !s.failed || s.released_writes) return 65;
    e003i_db_schedule_init(&s); c=good(1); if(e003i_db_schedule_queue(&s,1,&c)) return 66; if(e003i_db_schedule_release(&s,2,&e) || s.released_writes!=1) return 67;
    rc=e003i_db_schedule_release(&s,2,&e); if(rc!=-4 || !s.failed || s.released_writes!=1) return 68; c=good(2); rc=e003i_db_schedule_queue(&s,2,&c); if(rc!=-2 || s.released_writes!=1) return 69;
    e003i_db_schedule_init(&s); rc=e003i_db_schedule_release(&s,1,&e); if(rc!=-3 || !s.failed) return 70;
    c=good(0); c.line_count_before_even=7108; c.frame_length_lines=7116; c.vertical_blanking=4956; c.exposure_lines=7108; if(!e003i_db_controls_valid(&c)) return 71;
    return 0;
}
int main(void){ int rc=normal(); if(rc) return rc; rc=failures(); if(rc) return rc; puts("DB_SCHEDULE_NORMAL=queueG1,releaseG1@G2,queueG2,releaseG2@G3,queueG3,releaseG3@G4"); puts("DB_SCHEDULE_EFFECT=G4,G5,G6"); puts("DB_SCHEDULE_FAILURE_LATCH=PASS"); puts("DB_SCHEDULE_TEST=PASS"); return 0; }
'''
bootstrap_src=(HERE/'bootstrap-controls.c').read_text()
for x in ['VIDIOC_S_EXT_CTRLS','.count = 4','V4L2_CID_VBLANK','V4L2_CID_EXPOSURE','V4L2_CID_ANALOGUE_GAIN','V4L2_CID_DIGITAL_GAIN','DB_BOOTSTRAP_EXT_PASS']:
    need(x in bootstrap_src,'bootstrap ext transport '+x)
need('VIDIOC_S_CTRL' not in bootstrap_src,'bootstrap must not use piecemeal S_CTRL')

with tempfile.TemporaryDirectory(prefix='e003i-db-verify-') as td:
    td=Path(td); hp=td/'h.c'; hp.write_text(harness); exe=td/'sched'; helper=td/'helper'; bootstrap=td/'bootstrap'
    subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off','-I',str(HERE),'-I',str(CQ),'-I',str(CH),str(HERE/'native-db-schedule.c'),str(hp),'-lm','-o',str(exe)],check=True)
    out=subprocess.check_output([str(exe)],text=True); need('DB_SCHEDULE_TEST=PASS' in out,'scheduler harness')
    subprocess.run([str(HERE/'build-helper.sh'),str(helper)],check=True); need(helper.is_file() and helper.stat().st_size>0,'integrated helper build')
    subprocess.run([str(HERE/'build-bootstrap.sh'),str(bootstrap)],check=True); need(bootstrap.is_file() and bootstrap.stat().st_size>0,'bootstrap helper build')

prepare=(HERE/'prepare.sh').read_text(); prearm=(HERE/'prearm-check.sh').read_text(); runpre=(HERE/'runtime-preflight.sh').read_text(); invoke=(HERE/'invoke-once.sh').read_text(); entry=(HERE/'99zh_sp11_camera_e003i_db_native_aec').read_text()
need('e003i-db-bootstrap-controls' in prepare and 'BOOTSTRAP-EXT.txt' in prepare,'atomic DA bootstrap invocation')
need('--set-ctrl=' not in prepare,'piecemeal v4l2-ctl bootstrap forbidden')
for stale in ['vertical_blanking=1394,exposure=3500','STEP_EXPOSURE=1000','BASE_AGAIN=64','BASE_DGAIN=272']:
    need(stale not in prepare,'stale bootstrap '+stale)
need('build-helper.sh' in prepare and 'build-helper.sh' in prearm,'canonical helper build')
need('build-bootstrap.sh' in prepare and 'build-bootstrap.sh' in prearm,'canonical bootstrap build')
need('python3 "$D/verify.py"' in prearm and 'python3 "$D/verify.py"' in runpre,'offline verifier in gates')
need('HELPER-CONSUMED.marker' in invoke and 'DB_SUBDEV=' in invoke,'one-shot invocation guard')
need('sp11-camera-e003i-db-native-aec-one-shot' in entry and 'sp11_camera_e003i_db_native_aec=1' in entry and 'modprobe.blacklist=qcom_camss,imx681,ov13858' in entry,'candidate entry')

print('DB_PARENT_RANGE=c094198 maxGain92 maxTime66666664 policy0')
print('DB_BOOTSTRAP=FLL3562_VB1402_EXP3554_AGAIN0_DGAIN256_ISP1')
print('DB_SCHEDULE=releaseG1@G2->G4,releaseG2@G3->G5,releaseG3@G4->G6')
print('DB_DQBUF_COMPLETION_GATE=exact-window release-before-current-AEC PASS')
print('DB_FAILURE_ATOMICITY=permanent-no-further-writes PASS')
print('DB_HELPER_WERROR=PASS')
print('DB_RUNTIME=0 SENSOR_WRITES=0')
print('DB_VERIFY=PASS')
