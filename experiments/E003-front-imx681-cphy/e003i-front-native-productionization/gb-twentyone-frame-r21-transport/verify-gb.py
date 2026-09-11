#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,shutil,subprocess,tempfile,textwrap

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
PROJ=Path('/home/geoca/Documents/SP11-PROJECT')
ES=BASE/'es-nine-frame-r7-r9-transport'
EN=BASE/'en-r5-r9-live-producer-integration'
EY=BASE/'ey-eleven-frame-r10-r11-transport'
FE=BASE/'fe-twelve-frame-r12-transport'
FM=BASE/'fm-fifteen-frame-r15-transport'
FT=BASE/'ft-eighteen-frame-r18-transport'
FZ=BASE/'fz-eighteen-generation-gain-feed-publisher'
GA=BASE/'ga-r5-r21-producer-integration'
SRC=PROJ/'02-kernel/e003i-front-production-src/drivers/media/platform/qcom/camss'
K=PROJ/'02-kernel/build-runtime-v4-headers-20260826'

CAM18='a096493ae74fc3a22945f71f670f8777f0ea375bd3ad667c7451c96116d2ef6c'
CAM21='d09cd0bf6d91ed7c51c981455d9643d1f486cb0374fec23a375376b83e837fb4'
HELP18='24c87150ae6ee447440fe544cb8af1cec27e33d70fc0f70b198b4b7d9f5f23ce'
HELP21='8cb43bb96c629ce25c08014192898cc30e21abe226d101d06600f25dba829af5'
SH18='092c1b1dfaaa09ede3b9b492fc4173915d64f7b6c3d7e7439576314129e3c6cf'
SH21='fca5d49b12524a9f24bfca673072cf3bbb85d33645045d3a2cb4b155b58c6aae'
GAIN18='7f91b0ba03ff494e7544d3ac4c793d4cf2522e3761df43ff620a0799d0e9d4ee'
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
def run(cmd,**kw): return subprocess.run(cmd,check=True,text=True,**kw)

ft=json.loads((FT/'RESULT.json').read_text())
need(ft['status']=='PASS_OFFLINE_EIGHTEEN_FRAME_TRANSPORT' and ft['frames']==18,'FT authority')
fz=json.loads((FZ/'RESULT.json').read_text())
need(fz['status']=='PASS_OFFLINE_G1_G18_C_PUBLISHER' and fz['gain_feed_c_sha256']==GAIN18,'FZ authority')
ga=json.loads((GA/'RESULT.json').read_text())
need(ga['status']=='PASS_OFFLINE_R5_R21_AUTHORIZED_INTEGRATION','GA authority')
need(ga['requests']==list(range(5,22)),'GA request coverage')

with tempfile.TemporaryDirectory(prefix='e003i-gb-') as td0:
    td=Path(td0)
    cam9,cam11,cam12,cam15,cam18,cam21=[td/f'cam{x}.c' for x in (9,11,12,15,18,21)]
    run(['python3',str(ES/'make-nine-frame-camss.py'),str(SRC/'camss.c'),str(cam9)],stdout=subprocess.DEVNULL)
    run(['python3',str(EY/'make-eleven-frame-camss.py'),str(cam9),str(cam11)],stdout=subprocess.DEVNULL)
    run(['python3',str(FE/'make-twelve-frame-camss.py'),str(cam11),str(cam12)],stdout=subprocess.DEVNULL)
    run(['python3',str(FM/'make-fifteen-frame-camss.py'),str(cam12),str(cam15)],stdout=subprocess.DEVNULL)
    run(['python3',str(FT/'make-eighteen-frame-camss.py'),str(cam15),str(cam18)],stdout=subprocess.DEVNULL)
    need(sha(cam18)==CAM18,'FT18 CAMSS drift')
    run(['python3',str(HERE/'make-twentyone-frame-camss.py'),str(cam18),str(cam21)],stdout=subprocess.DEVNULL)
    need(sha(cam21)==CAM21,'GB21 CAMSS drift')

    h9,h11,h12,h15,h18,h21=[td/f'h{x}.c' for x in (9,11,12,15,18,21)]
    sh9,sh11,sh12,sh15,sh18,sh21=[td/f'sh{x}.h' for x in (9,11,12,15,18,21)]
    run(['python3',str(ES/'make-nine-frame-helper.py'),str(EN/'e003i-en-six-frame-native-aec.c'),str(EN/'native-db-schedule.h'),str(h9),str(sh9)],stdout=subprocess.DEVNULL)
    run(['python3',str(EY/'make-eleven-frame-helper.py'),str(h9),str(sh9),str(h11),str(sh11)],stdout=subprocess.DEVNULL)
    run(['python3',str(FE/'make-twelve-frame-helper.py'),str(h11),str(sh11),str(h12),str(sh12)],stdout=subprocess.DEVNULL)
    run(['python3',str(FM/'make-fifteen-frame-helper.py'),str(h12),str(sh12),str(h15),str(sh15)],stdout=subprocess.DEVNULL)
    run(['python3',str(FT/'make-eighteen-frame-helper.py'),str(h15),str(sh15),str(h18),str(sh18)],stdout=subprocess.DEVNULL)
    need(sha(h18)==HELP18 and sha(sh18)==SH18,'FT18 helper drift')
    run(['python3',str(HERE/'make-twentyone-frame-helper.py'),str(h18),str(sh18),str(h21),str(sh21)],stdout=subprocess.DEVNULL)
    need(sha(h21)==HELP21 and sha(sh21)==SH21,'GB21 helper drift')

    cs=cam21.read_text(); hs=h21.read_text(); hh=sh21.read_text()
    for tok in (
      'frame_limit > 21','frame_number < 7 || frame_number > 21',
      'csid, vfe, 19, 19, 0, req->video[2], materialized_r19',
      'csid, vfe, 20, 20, 1, req->video[3], materialized_r20',
      'csid, vfe, 21, 21, 0, req->video[0], materialized_r21',
      'result.video_done_nineteenth != video2','result.video_done_twentieth != video3',
      'result.video_done_twentyfirst != video0','result.video_requeued_fifteenth != video2',
      'result.video_requeued_sixteenth != video3','result.video_requeued_seventeenth != video0',
      'result.live_completed != 21','bounded twenty-one-frame live requeue',
      'result->slot0_reused_ninth = true','result->slot1_reused_ninth = true',
      'result->slot0_reused_tenth = true'):
        need(tok in cs,'CAMSS contract '+tok)
    cycle='{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0 }'
    for tok in ('#define FRAME_COUNT 21U',cycle,'if (i < 17U)','TARGETS=1..21',
                'ACCEPTED_G=1..21','if (target <= 18U)','R5..R21','argc != 29','GB_DQBUF_MISMATCH'):
        need(tok in hs,'helper contract '+tok)
    need(hs.count('if (target >= 2U && target <= 4U) {')==1,'sensor release window')
    need('#define E003I_DB_FRAME_COUNT 21U' in hh,'schedule count')
    need('#define E003I_DB_WRITTEN_SOURCE_GENERATIONS 3U' in hh,'sensor write source bound')

    cb=td/'camss-build'; shutil.copytree(SRC,cb); shutil.copy2(cam21,cb/'camss.c')
    run(['make','-C',str(K),f'M={cb}','clean'],stdout=subprocess.DEVNULL)
    run(['make','-C',str(K),f'M={cb}','W=1','-j4'],stdout=subprocess.DEVNULL)
    ko=cb/'qcom-camss.ko'; need(ko.exists(),'CAMSS module')
    ver=subprocess.check_output(['modinfo','-F','vermagic',str(ko)],text=True).strip()
    need(ver==VERMAGIC,'vermagic')

    hb=td/'helper-build';hb.mkdir()
    shutil.copy2(h21,hb/'e003i-gb-twentyone-frame-native-aec.c')
    shutil.copy2(sh21,hb/'native-db-schedule.h')
    shutil.copy2(EN/'native-db-schedule.c',hb/'native-db-schedule.c')
    shutil.copy2(FZ/'gain-feed.c',hb/'gain-feed.c');shutil.copy2(FZ/'gain-feed.h',hb/'gain-feed.h')
    need(sha(hb/'gain-feed.c')==GAIN18,'FZ publisher copy')

    names=['dt-bounded-native-aec-cap-awb-hold-sensor-loop','dn-native-aec-internal-cap',
      'cu-native-aec-raw-stats-request-loop','cq-aec-output-imx681-control-adapter',
      'cr-native-aec-effective-analyzer-producer','ct-native-aec-bhist-bank4-replay',
      'cf-native-aec-final-exposure-si','ce-native-aec-final-target-producer',
      'cc-native-aec-adrc-darkboost-tail','by-native-aec-method11-point-aggregation',
      'cg-native-aec-qword-convergence-input','ch-native-aec-t681-preview-arbitration',
      'bk-native-aec-history-state','bj-native-aec-log103-coordinate',
      'cv-native-aec-offline-sensor-control-join']
    mp={n:BASE/n for n in names}; inc=[hb,EN]+[mp[n] for n in names]
    sources=[
      hb/'e003i-gb-twentyone-frame-native-aec.c',hb/'gain-feed.c',hb/'native-db-schedule.c',
      mp['cv-native-aec-offline-sensor-control-join']/'native-raw-control-join.c',
      mp['cu-native-aec-raw-stats-request-loop']/'native-raw-aec-loop.c',
      mp['cu-native-aec-raw-stats-request-loop']/'native-stats3a.c',
      mp['cq-aec-output-imx681-control-adapter']/'native-imx681-control.c',
      mp['cr-native-aec-effective-analyzer-producer']/'native-effective-analyzers.c',
      mp['ct-native-aec-bhist-bank4-replay']/'native-bhist-bank4.c',
      mp['dn-native-aec-internal-cap']/'native-aec-request-loop.c',
      mp['dn-native-aec-internal-cap']/'native-internal-cap.c',
      mp['cf-native-aec-final-exposure-si']/'native-final-exposure.c',
      mp['ce-native-aec-final-target-producer']/'native-final-target.c',
      mp['cc-native-aec-adrc-darkboost-tail']/'native-aec-tail.c',
      mp['by-native-aec-method11-point-aggregation']/'native-target-aggregate.c',
      mp['cg-native-aec-qword-convergence-input']/'native-convergence.c',
      mp['ch-native-aec-t681-preview-arbitration']/'native-t681.c',
      mp['bk-native-aec-history-state']/'native-aec-state.c',
      mp['bj-native-aec-log103-coordinate']/'native-log103.c']
    exe=hb/'helper'
    run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']+
        [f'-I{x}' for x in inc]+[str(x) for x in sources]+['-pthread','-lm','-o',str(exe)],stdout=subprocess.DEVNULL)
    need(exe.exists(),'helper Werror build')

    sched=hb/'sched.c'
    sched.write_text(textwrap.dedent('''    #include <assert.h>
    #include <string.h>
    #include "native-db-schedule.h"
    int main(void){
      struct e003i_db_schedule_state s; struct e003i_db_apply_event ev; struct e003i_imx681_controls c;
      memset(&c,0,sizeof(c)); c.isp_gain=1.0f; c.frame_length_lines=3554; c.vertical_blanking=1394;
      c.line_count_before_even=100; c.exposure_lines=100; c.digital_gain_code=0x100;
      e003i_db_schedule_init(&s);
      for(unsigned g=1;g<=21;g++){
        assert(e003i_db_schedule_queue(&s,g,&c)==0);
        if(g>=2&&g<=4){ assert(e003i_db_schedule_release(&s,g,&ev)==0); assert(ev.apply&&ev.source_generation==g-1); }
      }
      assert(!s.failed); assert(s.queued_generation==21); assert(s.released_writes==3); return 0;
    }
    '''))
    st=hb/'sched'
    run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror']+[f'-I{x}' for x in inc]+
        [str(sched),str(hb/'native-db-schedule.c'),'-lm','-o',str(st)],stdout=subprocess.DEVNULL)
    run([str(st)])

    out={
      'schema':'sp11-e003i-gb-twentyone-frame-r21-transport-v1',
      'status':'PASS_OFFLINE_TWENTYONE_FRAME_TRANSPORT',
      'base_transport':'FT eighteen-frame',
      'patched_camss_sha256':CAM21,'camss_build':'PASS_W1','vermagic':ver,
      'patched_helper_sha256':HELP21,'helper_build':'PASS_WERROR','helper_binary_sha256':sha(exe),
      'patched_schedule_header_sha256':SH21,'frames':21,
      'buffer_cycle':[0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0],
      'requeue_after_sequences':list(range(17)),
      'iq_consumption_requests':list(range(5,22)),'new_kernel_consumption_requests':[19,20,21],
      'aec_generations':list(range(1,22)),'cq_gain_feed_generations':list(range(1,19)),
      'gain_feed_c_sha256':GAIN18,'producer_authority':'GA PASS R5-R21 authorized integration',
      'sensor_write_sources':[1,2,3],'sensor_write_boundaries':[2,3,4],
      'scheduler_unit_test':'PASS_G1_G21_WRITES3','camera_runtime_performed':False,
      'same_boot_retry_performed':False,'continuous_aec_claimed':False}
    (HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('GB_CAMSS_W1=PASS')
print('GB_HELPER_WERROR=PASS')
print('GB_SCHEDULER_G1_G21_WRITES3=PASS')
print('GB_VERIFY=PASS')
