#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,shutil,subprocess,tempfile,textwrap
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
PROJ=Path('/home/geoca/Documents/SP11-PROJECT')
ES=BASE/'es-nine-frame-r7-r9-transport'; EN=BASE/'en-r5-r9-live-producer-integration'
EY=BASE/'ey-eleven-frame-r10-r11-transport'; FE=BASE/'fe-twelve-frame-r12-transport'
FM=BASE/'fm-fifteen-frame-r15-transport'; FT=BASE/'ft-eighteen-frame-r18-transport'
GB=BASE/'gb-twentyone-frame-r21-transport'; GH=BASE/'gh-twentyfour-frame-r24-transport'
GL=BASE/'gl-twentyfour-generation-gain-feed-publisher'; GM=BASE/'gm-r5-r27-producer-integration'
SRC=PROJ/'02-kernel/e003i-front-production-src/drivers/media/platform/qcom/camss'; K=PROJ/'02-kernel/build-runtime-v4-headers-20260826'
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
def run(cmd,**kw): return subprocess.run(cmd,check=True,text=True,**kw)

gh=json.loads((GH/'RESULT.json').read_text()); need(gh['status']=='PASS_OFFLINE_TWENTYFOUR_FRAME_TRANSPORT','GH authority')
gl=json.loads((GL/'RESULT.json').read_text()); need(gl['status']=='PASS_OFFLINE_G1_G24_C_PUBLISHER','GL authority')
gm=json.loads((GM/'RESULT.json').read_text()); need(gm['status']=='PASS_OFFLINE_R5_R27_AUTHORIZED_INTEGRATION','GM authority'); need(gm['requests']==list(range(5,28)),'GM request coverage')

with tempfile.TemporaryDirectory(prefix='e003i-gn-') as td0:
    td=Path(td0)
    cam9,cam11,cam12,cam15,cam18,cam21,cam24,cam27a,cam27b=[td/f'cam{x}' for x in ('9.c','11.c','12.c','15.c','18.c','21.c','24.c','27a.c','27b.c')]
    run(['python3',str(ES/'make-nine-frame-camss.py'),str(SRC/'camss.c'),str(cam9)],stdout=subprocess.DEVNULL)
    run(['python3',str(EY/'make-eleven-frame-camss.py'),str(cam9),str(cam11)],stdout=subprocess.DEVNULL)
    run(['python3',str(FE/'make-twelve-frame-camss.py'),str(cam11),str(cam12)],stdout=subprocess.DEVNULL)
    run(['python3',str(FM/'make-fifteen-frame-camss.py'),str(cam12),str(cam15)],stdout=subprocess.DEVNULL)
    run(['python3',str(FT/'make-eighteen-frame-camss.py'),str(cam15),str(cam18)],stdout=subprocess.DEVNULL)
    run(['python3',str(GB/'make-twentyone-frame-camss.py'),str(cam18),str(cam21)],stdout=subprocess.DEVNULL)
    run(['python3',str(GH/'make-twentyfour-frame-camss.py'),str(cam21),str(cam24)],stdout=subprocess.DEVNULL)
    need(sha(cam24)==gh['patched_camss_sha256'],'GH24 CAMSS drift')
    run(['python3',str(HERE/'make-twentyseven-frame-camss.py'),str(cam24),str(cam27a)],stdout=subprocess.DEVNULL)
    run(['python3',str(HERE/'make-twentyseven-frame-camss.py'),str(cam24),str(cam27b)],stdout=subprocess.DEVNULL)
    need(sha(cam27a)==sha(cam27b),'GN CAMSS transform nondeterministic'); cam27sha=sha(cam27a)

    h9,h11,h12,h15,h18,h21,h24,h27a,h27b=[td/f'h{x}' for x in ('9.c','11.c','12.c','15.c','18.c','21.c','24.c','27a.c','27b.c')]
    sh9,sh11,sh12,sh15,sh18,sh21,sh24,sh27a,sh27b=[td/f'sh{x}' for x in ('9.h','11.h','12.h','15.h','18.h','21.h','24.h','27a.h','27b.h')]
    run(['python3',str(ES/'make-nine-frame-helper.py'),str(EN/'e003i-en-six-frame-native-aec.c'),str(EN/'native-db-schedule.h'),str(h9),str(sh9)],stdout=subprocess.DEVNULL)
    run(['python3',str(EY/'make-eleven-frame-helper.py'),str(h9),str(sh9),str(h11),str(sh11)],stdout=subprocess.DEVNULL)
    run(['python3',str(FE/'make-twelve-frame-helper.py'),str(h11),str(sh11),str(h12),str(sh12)],stdout=subprocess.DEVNULL)
    run(['python3',str(FM/'make-fifteen-frame-helper.py'),str(h12),str(sh12),str(h15),str(sh15)],stdout=subprocess.DEVNULL)
    run(['python3',str(FT/'make-eighteen-frame-helper.py'),str(h15),str(sh15),str(h18),str(sh18)],stdout=subprocess.DEVNULL)
    run(['python3',str(GB/'make-twentyone-frame-helper.py'),str(h18),str(sh18),str(h21),str(sh21)],stdout=subprocess.DEVNULL)
    run(['python3',str(GH/'make-twentyfour-frame-helper.py'),str(h21),str(sh21),str(h24),str(sh24)],stdout=subprocess.DEVNULL)
    need(sha(h24)==gh['patched_helper_sha256'] and sha(sh24)==gh['patched_schedule_header_sha256'],'GH24 helper drift')
    run(['python3',str(HERE/'make-twentyseven-frame-helper.py'),str(h24),str(sh24),str(h27a),str(sh27a)],stdout=subprocess.DEVNULL)
    run(['python3',str(HERE/'make-twentyseven-frame-helper.py'),str(h24),str(sh24),str(h27b),str(sh27b)],stdout=subprocess.DEVNULL)
    need(sha(h27a)==sha(h27b) and sha(sh27a)==sha(sh27b),'GN helper transform nondeterministic'); help27sha=sha(h27a); sh27sha=sha(sh27a)

    cs=cam27a.read_text(); hs=h27a.read_text(); hh=sh27a.read_text()
    for tok in ('frame_limit > 27','frame_number < 7 || frame_number > 27',
      'csid, vfe, 25, 25, 0, req->video[0], materialized_r25','csid, vfe, 26, 26, 1, req->video[1], materialized_r26','csid, vfe, 27, 27, 0, req->video[2], materialized_r27',
      'result.video_done_twentyfifth != video0','result.video_done_twentysixth != video1','result.video_done_twentyseventh != video2',
      'result.video_requeued_twentyfirst != video0','result.video_requeued_twentysecond != video1','result.video_requeued_twentythird != video2','result.live_completed != 27',
      'bounded twenty-seven-frame live requeue','result->slot0_reused_twelfth = true','result->slot1_reused_twelfth = true','result->slot0_reused_thirteenth = true'):
        need(tok in cs,'CAMSS contract '+tok)
    cycle='{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2 }'
    for tok in ('#define FRAME_COUNT 27U',cycle,'if (i < 23U)','TARGETS=1..27','ACCEPTED_G=1..27','if (target <= 24U)','R5..R27','argc != 35','GN_DQBUF_MISMATCH'):
        need(tok in hs,'helper contract '+tok)
    need(hs.count('if (target >= 2U && target <= 4U) {')==1,'sensor release window')
    need('#define E003I_DB_FRAME_COUNT 27U' in hh,'schedule count'); need('#define E003I_DB_WRITTEN_SOURCE_GENERATIONS 3U' in hh,'sensor write source bound')

    cb=td/'camss-build'; shutil.copytree(SRC,cb); shutil.copy2(cam27a,cb/'camss.c')
    run(['make','-C',str(K),f'M={cb}','clean'],stdout=subprocess.DEVNULL)
    run(['make','-C',str(K),f'M={cb}','W=1','-j4'],stdout=subprocess.DEVNULL)
    ko=cb/'qcom-camss.ko'; need(ko.exists(),'CAMSS module'); ver=subprocess.check_output(['modinfo','-F','vermagic',str(ko)],text=True).strip(); need(ver==VERMAGIC,'vermagic')

    hb=td/'helper-build'; hb.mkdir(); shutil.copy2(h27a,hb/'e003i-gn-twentyseven-frame-native-aec.c'); shutil.copy2(sh27a,hb/'native-db-schedule.h'); shutil.copy2(EN/'native-db-schedule.c',hb/'native-db-schedule.c'); shutil.copy2(GL/'gain-feed.c',hb/'gain-feed.c'); shutil.copy2(GL/'gain-feed.h',hb/'gain-feed.h')
    names=['dt-bounded-native-aec-cap-awb-hold-sensor-loop','dn-native-aec-internal-cap','cu-native-aec-raw-stats-request-loop','cq-aec-output-imx681-control-adapter','cr-native-aec-effective-analyzer-producer','ct-native-aec-bhist-bank4-replay','cf-native-aec-final-exposure-si','ce-native-aec-final-target-producer','cc-native-aec-adrc-darkboost-tail','by-native-aec-method11-point-aggregation','cg-native-aec-qword-convergence-input','ch-native-aec-t681-preview-arbitration','bk-native-aec-history-state','bj-native-aec-log103-coordinate','cv-native-aec-offline-sensor-control-join']
    mp={n:BASE/n for n in names}; inc=[hb,EN]+[mp[n] for n in names]
    sources=[hb/'e003i-gn-twentyseven-frame-native-aec.c',hb/'gain-feed.c',hb/'native-db-schedule.c',mp['cv-native-aec-offline-sensor-control-join']/'native-raw-control-join.c',mp['cu-native-aec-raw-stats-request-loop']/'native-raw-aec-loop.c',mp['cu-native-aec-raw-stats-request-loop']/'native-stats3a.c',mp['cq-aec-output-imx681-control-adapter']/'native-imx681-control.c',mp['cr-native-aec-effective-analyzer-producer']/'native-effective-analyzers.c',mp['ct-native-aec-bhist-bank4-replay']/'native-bhist-bank4.c',mp['dn-native-aec-internal-cap']/'native-aec-request-loop.c',mp['dn-native-aec-internal-cap']/'native-internal-cap.c',mp['cf-native-aec-final-exposure-si']/'native-final-exposure.c',mp['ce-native-aec-final-target-producer']/'native-final-target.c',mp['cc-native-aec-adrc-darkboost-tail']/'native-aec-tail.c',mp['by-native-aec-method11-point-aggregation']/'native-target-aggregate.c',mp['cg-native-aec-qword-convergence-input']/'native-convergence.c',mp['ch-native-aec-t681-preview-arbitration']/'native-t681.c',mp['bk-native-aec-history-state']/'native-aec-state.c',mp['bj-native-aec-log103-coordinate']/'native-log103.c']
    exe=hb/'helper'; run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']+[f'-I{x}' for x in inc]+[str(x) for x in sources]+['-pthread','-lm','-o',str(exe)],stdout=subprocess.DEVNULL); need(exe.exists(),'helper Werror build')

    sched=hb/'sched.c'; sched.write_text(textwrap.dedent('''
    #include <assert.h>
    #include <string.h>
    #include "native-db-schedule.h"
    int main(void){ struct e003i_db_schedule_state s; struct e003i_db_apply_event ev; struct e003i_imx681_controls c; memset(&c,0,sizeof(c)); c.isp_gain=1.0f; c.frame_length_lines=3554; c.vertical_blanking=1394; c.line_count_before_even=100; c.exposure_lines=100; c.digital_gain_code=0x100; e003i_db_schedule_init(&s); for(unsigned g=1;g<=27;g++){ assert(e003i_db_schedule_queue(&s,g,&c)==0); if(g>=2&&g<=4){ assert(e003i_db_schedule_release(&s,g,&ev)==0); assert(ev.apply&&ev.source_generation==g-1); }} assert(!s.failed); assert(s.queued_generation==27); assert(s.released_writes==3); return 0; }
    ''')); st=hb/'sched'; run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror']+[f'-I{x}' for x in inc]+[str(sched),str(hb/'native-db-schedule.c'),'-lm','-o',str(st)],stdout=subprocess.DEVNULL); run([str(st)])

    out={'schema':'sp11-e003i-gn-twentyseven-frame-r27-transport-v1','status':'PASS_OFFLINE_TWENTYSEVEN_FRAME_TRANSPORT','base_transport':'GH twenty-four-frame','patched_camss_sha256':cam27sha,'camss_build':'PASS_W1','vermagic':ver,'patched_helper_sha256':help27sha,'helper_build':'PASS_WERROR','helper_binary_sha256':sha(exe),'patched_schedule_header_sha256':sh27sha,'frames':27,'buffer_cycle':[0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2],'requeue_after_sequences':list(range(23)),'iq_consumption_requests':list(range(5,28)),'new_kernel_consumption_requests':[25,26,27],'aec_generations':list(range(1,28)),'cq_gain_feed_generations':list(range(1,25)),'gain_feed_c_sha256':gl['gain_feed_c_sha256'],'producer_authority':'GM PASS R5-R27 authorized integration','sensor_write_sources':[1,2,3],'sensor_write_boundaries':[2,3,4],'scheduler_unit_test':'PASS_G1_G27_WRITES3','camera_runtime_performed':False,'same_boot_retry_performed':False,'continuous_aec_claimed':False}
    (HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('GN_CAMSS_W1=PASS'); print('GN_HELPER_WERROR=PASS'); print('GN_SCHEDULER_G1_G27_WRITES3=PASS'); print('GN_VERIFY=PASS')
