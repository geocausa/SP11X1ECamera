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
FK=BASE/'fk-twelve-generation-gain-feed-publisher'
FL=BASE/'fl-r5-r15-producer-integration'
SRC=PROJ/'02-kernel/e003i-front-production-src/drivers/media/platform/qcom/camss'
K=PROJ/'02-kernel/build-runtime-v4-headers-20260826'

CAM9='683255664a320bf63b1c852c56a8c0373014d6723b6d48a69a277bd02d18706f'
CAM11='335e15f48cac9835d9ddfa0f1dc96f559346f167f2e8cce1c384635b872d13aa'
CAM12='deee56e61090bba938f602a7baeae054435762e6312e47d2cac9dbf9a210f15d'
CAM15='592f31d591ff9542f8f67d8228e5f45808afb63088368107ce56422b4d8e34d6'
HELP9='6d4268fb5e6c637de78f62079719eaa3c107efcca48578c125a58a17d74c565d'
HELP11='b5ecb959b95c63eb38c1e7da98e1f37e9c71d9cc4abe4ee6fbc5456e9bd67993'
HELP12='e6f2a792dc070c9d6a726817f30d3a8b1da56b554debccbe2832bd0b18ae47de'
HELP15='f68413ae23cdfbfb84ee39129582e40ecee2fd4b3a37ee242a5bceb4997fb4b4'
SH9='47890d6b37bc6a484310d983a8a303798b56d06eea6f2287dc4df254eaf5eb14'
SH11='6d6cfc6833c035d545d5d626a4af479717227732cf94ef301422e6c74f3dd113'
SH12='1872289bdd280cc067034c4425234b9bfa334e27dce62841ffb540b061f86690'
SH15='b080113d1a07a2600eb8a06b3e5b045422debe0858577d84ab7d61fae03ff54d'
GAIN12='93e284bca519366817324962278d5403c05cdc7fd0454b8a4e8fe683d2b90b2e'
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
def run(c,**kw): return subprocess.run(c,check=True,text=True,**kw)

fk=json.loads((FK/'RESULT.json').read_text())
need(fk['status']=='PASS_OFFLINE_G1_G12_C_PUBLISHER' and fk['gain_feed_c_sha256']==GAIN12,'FK authority')
fl=json.loads((FL/'RESULT.json').read_text())
need(fl['status']=='PASS_OFFLINE_R5_R15_AUTHORIZED_INTEGRATION' and fl['requests']==list(range(5,16)),'FL authority')

with tempfile.TemporaryDirectory(prefix='e003i-fm-') as td0:
    td=Path(td0)
    cam9=td/'cam9.c';cam11=td/'cam11.c';cam12=td/'cam12.c';cam15=td/'cam15.c'
    h9=td/'h9.c';sh9=td/'sh9.h';h11=td/'h11.c';sh11=td/'sh11.h'
    h12=td/'h12.c';sh12=td/'sh12.h';h15=td/'h15.c';sh15=td/'sh15.h'

    run(['python3',str(ES/'make-nine-frame-camss.py'),str(SRC/'camss.c'),str(cam9)],stdout=subprocess.DEVNULL)
    need(sha(cam9)==CAM9,'ES9 CAMSS drift')
    run(['python3',str(EY/'make-eleven-frame-camss.py'),str(cam9),str(cam11)],stdout=subprocess.DEVNULL)
    need(sha(cam11)==CAM11,'EY11 CAMSS drift')
    run(['python3',str(FE/'make-twelve-frame-camss.py'),str(cam11),str(cam12)],stdout=subprocess.DEVNULL)
    need(sha(cam12)==CAM12,'FE12 CAMSS drift')
    run(['python3',str(HERE/'make-fifteen-frame-camss.py'),str(cam12),str(cam15)],stdout=subprocess.DEVNULL)
    need(sha(cam15)==CAM15,'FM15 CAMSS drift')

    run(['python3',str(ES/'make-nine-frame-helper.py'),str(EN/'e003i-en-six-frame-native-aec.c'),str(EN/'native-db-schedule.h'),str(h9),str(sh9)],stdout=subprocess.DEVNULL)
    need(sha(h9)==HELP9 and sha(sh9)==SH9,'ES9 helper drift')
    run(['python3',str(EY/'make-eleven-frame-helper.py'),str(h9),str(sh9),str(h11),str(sh11)],stdout=subprocess.DEVNULL)
    need(sha(h11)==HELP11 and sha(sh11)==SH11,'EY11 helper drift')
    run(['python3',str(FE/'make-twelve-frame-helper.py'),str(h11),str(sh11),str(h12),str(sh12)],stdout=subprocess.DEVNULL)
    need(sha(h12)==HELP12 and sha(sh12)==SH12,'FE12 helper drift')
    run(['python3',str(HERE/'make-fifteen-frame-helper.py'),str(h12),str(sh12),str(h15),str(sh15)],stdout=subprocess.DEVNULL)
    need(sha(h15)==HELP15 and sha(sh15)==SH15,'FM15 helper drift')

    cs=cam15.read_text();hs=h15.read_text();hh=sh15.read_text()
    for tok in (
        'frame_limit > 15',
        'frame_number < 7 || frame_number > 15',
        'csid, vfe, 13, 13, 0, req->video[0], materialized_r13',
        'csid, vfe, 14, 14, 1, req->video[1], materialized_r14',
        'csid, vfe, 15, 15, 0, req->video[2], materialized_r15',
        'camss_x1e_pix_runner_frames(camss, &req, &result, 15)',
        'result.video_done_thirteenth != video0',
        'result.video_done_fourteenth != video1',
        'result.video_done_fifteenth != video2',
        'result.video_requeued_ninth != video0',
        'result.video_requeued_tenth != video1',
        'result.video_requeued_eleventh != video2',
        'result.live_completed != 15',
        'bounded fifteen-frame live requeue',
    ):
        need(tok in cs,'CAMSS contract '+tok)
    for tok in (
        '#define FRAME_COUNT 15U',
        '{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2 }',
        'if (i < 11U)',
        'TARGETS=1..15',
        'ACCEPTED_G=1..15',
        'if (target <= 12U)',
        'R5..R15',
        'argc != 23',
        'FM_DQBUF_MISMATCH',
    ):
        need(tok in hs,'helper contract '+tok)
    need(hs.count('if (target >= 2U && target <= 4U) {')==1,'sensor release window drift')
    need('#define E003I_DB_FRAME_COUNT 15U' in hh,'schedule frame count')
    need('#define E003I_DB_WRITTEN_SOURCE_GENERATIONS 3U' in hh,'written source generations drift')

    cb=td/'camss-build';shutil.copytree(SRC,cb);shutil.copy2(cam15,cb/'camss.c')
    run(['make','-C',str(K),f'M={cb}','clean'],stdout=subprocess.DEVNULL)
    run(['make','-C',str(K),f'M={cb}','W=1','-j4'],stdout=subprocess.DEVNULL)
    ko=cb/'qcom-camss.ko';need(ko.exists(),'CAMSS module')
    ver=subprocess.check_output(['modinfo','-F','vermagic',str(ko)],text=True).strip()
    need(ver==VERMAGIC,'vermagic')

    hb=td/'helper-build';hb.mkdir()
    shutil.copy2(h15,hb/'e003i-fm-fifteen-frame-native-aec.c')
    shutil.copy2(sh15,hb/'native-db-schedule.h')
    shutil.copy2(EN/'native-db-schedule.c',hb/'native-db-schedule.c')
    shutil.copy2(FK/'gain-feed.c',hb/'gain-feed.c')
    shutil.copy2(FK/'gain-feed.h',hb/'gain-feed.h')
    need(sha(hb/'gain-feed.c')==GAIN12,'FK publisher copy')

    names=[
        'dt-bounded-native-aec-cap-awb-hold-sensor-loop',
        'dn-native-aec-internal-cap',
        'cu-native-aec-raw-stats-request-loop',
        'cq-aec-output-imx681-control-adapter',
        'cr-native-aec-effective-analyzer-producer',
        'ct-native-aec-bhist-bank4-replay',
        'cf-native-aec-final-exposure-si',
        'ce-native-aec-final-target-producer',
        'cc-native-aec-adrc-darkboost-tail',
        'by-native-aec-method11-point-aggregation',
        'cg-native-aec-qword-convergence-input',
        'ch-native-aec-t681-preview-arbitration',
        'bk-native-aec-history-state',
        'bj-native-aec-log103-coordinate',
        'cv-native-aec-offline-sensor-control-join',
    ]
    mp={n:BASE/n for n in names}
    inc=[hb,EN]+[mp[n] for n in names]
    sources=[
        hb/'e003i-fm-fifteen-frame-native-aec.c',
        hb/'gain-feed.c',
        hb/'native-db-schedule.c',
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
        mp['bj-native-aec-log103-coordinate']/'native-log103.c',
    ]
    exe=hb/'helper'
    run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']+
        [f'-I{x}' for x in inc]+[str(x) for x in sources]+['-pthread','-lm','-o',str(exe)],stdout=subprocess.DEVNULL)
    need(exe.exists(),'helper Werror build')

    test=hb/'sched.c'
    test.write_text(textwrap.dedent('''\
    #include <assert.h>
    #include <string.h>
    #include "native-db-schedule.h"
    int main(void){
      struct e003i_db_schedule_state s; struct e003i_db_apply_event ev; struct e003i_imx681_controls c;
      memset(&c,0,sizeof(c)); c.isp_gain=1.0f; c.frame_length_lines=3554; c.vertical_blanking=1394;
      c.line_count_before_even=100; c.exposure_lines=100; c.digital_gain_code=0x100;
      e003i_db_schedule_init(&s);
      for(unsigned g=1;g<=15;g++){
        assert(e003i_db_schedule_queue(&s,g,&c)==0);
        if(g>=2&&g<=4){assert(e003i_db_schedule_release(&s,g,&ev)==0);assert(ev.apply&&ev.source_generation==g-1);}
      }
      assert(!s.failed && s.queued_generation==15 && s.released_writes==3); return 0;
    }
    '''))
    st=hb/'sched'
    run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror']+[f'-I{x}' for x in inc]+
        [str(test),str(hb/'native-db-schedule.c'),'-lm','-o',str(st)],stdout=subprocess.DEVNULL)
    run([str(st)])

    out={
        'schema':'sp11-e003i-fm-fifteen-frame-r15-transport-v1',
        'status':'PASS_OFFLINE_FIFTEEN_FRAME_TRANSPORT',
        'base_transport':'FE twelve-frame',
        'patched_camss_sha256':CAM15,
        'camss_build':'PASS_W1',
        'vermagic':ver,
        'patched_helper_sha256':HELP15,
        'helper_build':'PASS_WERROR',
        'patched_schedule_header_sha256':SH15,
        'frames':15,
        'buffer_cycle':[0,1,2,3,0,1,2,3,0,1,2,3,0,1,2],
        'requeue_after_sequences':list(range(11)),
        'iq_consumption_requests':list(range(5,16)),
        'new_kernel_consumption_requests':[13,14,15],
        'aec_generations':list(range(1,16)),
        'cq_gain_feed_generations':list(range(1,13)),
        'gain_feed_c_sha256':GAIN12,
        'producer_authority':'FL PASS R5-R15 authorized integration',
        'sensor_write_sources':[1,2,3],
        'sensor_write_boundaries':[2,3,4],
        'scheduler_unit_test':'PASS',
        'camera_runtime_performed':False,
        'same_boot_retry_performed':False,
        'continuous_aec_claimed':False,
    }
    (HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
