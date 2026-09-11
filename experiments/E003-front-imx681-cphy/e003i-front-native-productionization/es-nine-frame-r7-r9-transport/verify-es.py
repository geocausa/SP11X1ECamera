#!/usr/bin/env python3
from pathlib import Path
import hashlib, subprocess, tempfile, shutil, json, os, textwrap
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
PROJ=Path('/home/geoca/Documents/SP11-PROJECT')
BASE=HERE.parent
SRC=PROJ/'02-kernel/e003i-front-production-src/drivers/media/platform/qcom/camss'
K=PROJ/'02-kernel/build-runtime-v4-headers-20260826'
EN=BASE/'en-r5-r9-live-producer-integration'
BASE_CAMSS_SHA='b9de92306b4d386274968dcab3f1a96ec13359f1eb22c27fda43bb15b0af7abb'
PATCHED_CAMSS_SHA='683255664a320bf63b1c852c56a8c0373014d6723b6d48a69a277bd02d18706f'
BASE_HELPER_SHA='3788ca6a05747961f523942117925d28b4a2edb91f76a06bb001071ffd238b08'
PATCHED_HELPER_SHA='6d4268fb5e6c637de78f62079719eaa3c107efcca48578c125a58a17d74c565d'
BASE_SCHED_H_SHA='50bbb9c59538167241245ea60b57f76e3b7e8979135c88c9ff4a363318ca328f'
PATCHED_SCHED_H_SHA='47890d6b37bc6a484310d983a8a303798b56d06eea6f2287dc4df254eaf5eb14'
BASE_SCHED_C_SHA='313f87c2f7d57b2027410edf6342a1cb0081de9a128bb374e300170ac7a61664'
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
def run(cmd,**kw): return subprocess.run(cmd,check=True,text=True,**kw)
need(sha(SRC/'camss.c')==BASE_CAMSS_SHA,'CAMSS base drift')
need(sha(EN/'e003i-en-six-frame-native-aec.c')==BASE_HELPER_SHA,'EN helper drift')
need(sha(EN/'native-db-schedule.h')==BASE_SCHED_H_SHA,'EN schedule header drift')
need(sha(EN/'native-db-schedule.c')==BASE_SCHED_C_SHA,'EN schedule C drift')
with tempfile.TemporaryDirectory(prefix='e003i-es-') as td0:
    td=Path(td0); cam=td/'camss.c'; helper=td/'e003i-es-nine-frame-native-aec.c'; sh=td/'native-db-schedule.h'
    run(['python3',str(HERE/'make-nine-frame-camss.py'),str(SRC/'camss.c'),str(cam)])
    run(['python3',str(HERE/'make-nine-frame-helper.py'),str(EN/'e003i-en-six-frame-native-aec.c'),str(EN/'native-db-schedule.h'),str(helper),str(sh)])
    need(sha(cam)==PATCHED_CAMSS_SHA,'patched CAMSS drift')
    need(sha(helper)==PATCHED_HELPER_SHA,'patched helper drift')
    need(sha(sh)==PATCHED_SCHED_H_SHA,'patched schedule header drift')
    cs=cam.read_text(); hs=helper.read_text(); hh=sh.read_text()
    # Kernel transport: five deferred requests total, with R7/R8/R9 consumed at their own Epoch0 gates.
    for tok in ['frame_limit > 9','camss_x1e_pix_runner_frames(camss, &req, &result, 9)',
                'frame_number < 7 || frame_number > 9','request_id != frame_number',
                '7, 7, 0, req->video[2]','8, 8, 1, req->video[3]','9, 9, 0, req->video[0]',
                'bounded nine-frame live requeue','E003I_ES_IQ_CONSUMED R=%llu FRAME=%u SLOT=%u']:
        need(tok in cs,'CAMSS contract '+tok)
    need(cs.count('camss_x1e_pix_iq_provider_next_steady(camss, req->live_video,')>=1,'provider helper absent')
    # Userspace transport: 9 DQBUFs, exact 4-buffer cycle, recycle first five completions only.
    for tok in ['#define FRAME_COUNT 9U','{ 0, 1, 2, 3, 0, 1, 2, 3, 0 }','if (i < 5U)',
                'TARGETS=1..9','ACCEPTED_G=1..9','R5..R9','argc != 17']:
        need(tok in hs,'helper contract '+tok)
    need(hs.count('if (target <= 6U) {')==1,'CQ gain publication must remain G1..G6')
    need(hs.count('if (target >= 2U && target <= 4U) {')==1,'sensor release window drift')
    need('#define E003I_DB_FRAME_COUNT 9U' in hh,'schedule count')
    need('#define E003I_DB_WRITTEN_SOURCE_GENERATIONS 3U' in hh,'write count drift')
    # Build CAMSS externally with W=1.
    cb=td/'camss-build'; shutil.copytree(SRC,cb); shutil.copy2(cam,cb/'camss.c')
    run(['make','-C',str(K),f'M={cb}','clean'],stdout=subprocess.DEVNULL)
    run(['make','-C',str(K),f'M={cb}','W=1','-j4'],stdout=subprocess.DEVNULL)
    ko=cb/'qcom-camss.ko'; need(ko.exists(),'CAMSS module absent')
    ver=subprocess.check_output(['modinfo','-F','vermagic',str(ko)],text=True).strip();need(ver==VERMAGIC,'vermagic')
    # Build helper against unchanged EN/AEC dependencies, but copied schedule C sees generated 9-frame header.
    hb=td/'helper-build';hb.mkdir();shutil.copy2(helper,hb/helper.name);shutil.copy2(sh,hb/'native-db-schedule.h')
    for n in ['native-db-schedule.c','gain-feed.c','gain-feed.h']: shutil.copy2(EN/n,hb/n)
    deps={k:BASE/k for k in []}
    names=['dt-bounded-native-aec-cap-awb-hold-sensor-loop','dn-native-aec-internal-cap','cu-native-aec-raw-stats-request-loop',
           'cq-aec-output-imx681-control-adapter','cr-native-aec-effective-analyzer-producer','ct-native-aec-bhist-bank4-replay',
           'cf-native-aec-final-exposure-si','ce-native-aec-final-target-producer','cc-native-aec-adrc-darkboost-tail',
           'by-native-aec-method11-point-aggregation','cg-native-aec-qword-convergence-input','ch-native-aec-t681-preview-arbitration',
           'bk-native-aec-history-state','bj-native-aec-log103-coordinate','cv-native-aec-offline-sensor-control-join']
    mp={n:BASE/n for n in names}
    inc=[hb,EN]+[mp[n] for n in names]
    sources=[hb/helper.name,hb/'gain-feed.c',hb/'native-db-schedule.c',
      mp['cv-native-aec-offline-sensor-control-join']/'native-raw-control-join.c',mp['cu-native-aec-raw-stats-request-loop']/'native-raw-aec-loop.c',mp['cu-native-aec-raw-stats-request-loop']/'native-stats3a.c',
      mp['cq-aec-output-imx681-control-adapter']/'native-imx681-control.c',mp['cr-native-aec-effective-analyzer-producer']/'native-effective-analyzers.c',mp['ct-native-aec-bhist-bank4-replay']/'native-bhist-bank4.c',
      mp['dn-native-aec-internal-cap']/'native-aec-request-loop.c',mp['dn-native-aec-internal-cap']/'native-internal-cap.c',mp['cf-native-aec-final-exposure-si']/'native-final-exposure.c',
      mp['ce-native-aec-final-target-producer']/'native-final-target.c',mp['cc-native-aec-adrc-darkboost-tail']/'native-aec-tail.c',mp['by-native-aec-method11-point-aggregation']/'native-target-aggregate.c',
      mp['cg-native-aec-qword-convergence-input']/'native-convergence.c',mp['ch-native-aec-t681-preview-arbitration']/'native-t681.c',mp['bk-native-aec-history-state']/'native-aec-state.c',mp['bj-native-aec-log103-coordinate']/'native-log103.c']
    exe=hb/'helper'; cmd=['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']+[f'-I{x}' for x in inc]+[str(x) for x in sources]+['-pthread','-lm','-o',str(exe)]
    run(cmd,stdout=subprocess.DEVNULL)
    need(exe.exists(),'helper build absent')
    # Pure scheduler acceptance: G1..G9 queue; only three releases at completed G2/G3/G4.
    test=hb/'sched-test.c';test.write_text(textwrap.dedent(r'''
      #include <assert.h>
      #include <string.h>
      #include "native-db-schedule.h"
      int main(void){
        struct e003i_db_schedule_state s; struct e003i_db_apply_event ev; struct e003i_imx681_controls c;
        memset(&c,0,sizeof(c)); c.isp_gain=1.0f; c.frame_length_lines=3554; c.vertical_blanking=1394; c.line_count_before_even=100; c.exposure_lines=100; c.analogue_gain_code=0; c.digital_gain_code=0x100;
        e003i_db_schedule_init(&s);
        for(unsigned g=1;g<=9;g++){ assert(e003i_db_schedule_queue(&s,g,&c)==0); if(g>=2 && g<=4){ assert(e003i_db_schedule_release(&s,g,&ev)==0); assert(ev.apply && ev.source_generation==g-1); } }
        assert(!s.failed && s.queued_generation==9 && s.released_writes==3); return 0;
      }
    '''))
    st=hb/'sched-test';run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror']+[f'-I{x}' for x in inc]+[str(test),str(hb/'native-db-schedule.c'),'-lm','-o',str(st)],stdout=subprocess.DEVNULL);run([str(st)])
    out={'schema':'sp11-e003i-es-nine-frame-r7-r9-transport-v1','status':'PASS_OFFLINE_NINE_FRAME_TRANSPORT',
         'base_camss_sha256':BASE_CAMSS_SHA,'patched_camss_sha256':PATCHED_CAMSS_SHA,'camss_build':'PASS_W1','vermagic':ver,
         'base_helper_sha256':BASE_HELPER_SHA,'patched_helper_sha256':PATCHED_HELPER_SHA,'helper_build':'PASS_WERROR',
         'base_schedule_header_sha256':BASE_SCHED_H_SHA,'patched_schedule_header_sha256':PATCHED_SCHED_H_SHA,
         'frames':9,'buffer_cycle':[0,1,2,3,0,1,2,3,0],'requeue_after_sequences':[0,1,2,3,4],
         'iq_consumption_requests':[5,6,7,8,9],'new_kernel_consumption_requests':[7,8,9],
         'aec_generations':[1,2,3,4,5,6,7,8,9],'cq_gain_feed_generations':[1,2,3,4,5,6],
         'sensor_write_sources':[1,2,3],'sensor_write_boundaries':[2,3,4],'scheduler_unit_test':'PASS',
         'camera_runtime_performed':False,'same_boot_retry_performed':False}
    (HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
