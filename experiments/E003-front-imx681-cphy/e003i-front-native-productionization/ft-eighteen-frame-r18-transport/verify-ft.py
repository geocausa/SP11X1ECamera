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
FR=BASE/'fr-fifteen-generation-gain-feed-publisher'
FS=BASE/'fs-r5-r18-producer-integration'

SRC=PROJ/'02-kernel/e003i-front-production-src/drivers/media/platform/qcom/camss'
K=PROJ/'02-kernel/build-runtime-v4-headers-20260826'

CAM9='683255664a320bf63b1c852c56a8c0373014d6723b6d48a69a277bd02d18706f'
CAM11='335e15f48cac9835d9ddfa0f1dc96f559346f167f2e8cce1c384635b872d13aa'
CAM12='deee56e61090bba938f602a7baeae054435762e6312e47d2cac9dbf9a210f15d'
CAM15='592f31d591ff9542f8f67d8228e5f45808afb63088368107ce56422b4d8e34d6'
CAM18='a096493ae74fc3a22945f71f670f8777f0ea375bd3ad667c7451c96116d2ef6c'

HELP9='6d4268fb5e6c637de78f62079719eaa3c107efcca48578c125a58a17d74c565d'
HELP11='b5ecb959b95c63eb38c1e7da98e1f37e9c71d9cc4abe4ee6fbc5456e9bd67993'
HELP12='e6f2a792dc070c9d6a726817f30d3a8b1da56b554debccbe2832bd0b18ae47de'
HELP15='f68413ae23cdfbfb84ee39129582e40ecee2fd4b3a37ee242a5bceb4997fb4b4'
HELP18='24c87150ae6ee447440fe544cb8af1cec27e33d70fc0f70b198b4b7d9f5f23ce'

SH9='47890d6b37bc6a484310d983a8a303798b56d06eea6f2287dc4df254eaf5eb14'
SH11='6d6cfc6833c035d545d5d626a4af479717227732cf94ef301422e6c74f3dd113'
SH12='1872289bdd280cc067034c4425234b9bfa334e27dce62841ffb540b061f86690'
SH15='b080113d1a07a2600eb8a06b3e5b045422debe0858577d84ab7d61fae03ff54d'
SH18='092c1b1dfaaa09ede3b9b492fc4173915d64f7b6c3d7e7439576314129e3c6cf'

GAIN15='c8b03597649ec5e1a6e5b62110eb61ab7cd6a29073a3ecdcf9194f439b410627'
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def need(v,m):
    if not v:
        raise AssertionError(m)

def run(cmd,**kw):
    return subprocess.run(cmd,check=True,text=True,**kw)

fr=json.loads((FR/'RESULT.json').read_text())
need(fr['status']=='PASS_OFFLINE_G1_G15_C_PUBLISHER','FR authority')
need(fr['accepted_generations']==list(range(1,16)) and fr['rejected_generation']==16,'FR coverage')
need(fr['gain_feed_c_sha256']==GAIN15,'FR gain publisher hash')

fs=json.loads((FS/'RESULT.json').read_text())
need(fs['status']=='PASS_OFFLINE_R5_R18_AUTHORIZED_INTEGRATION','FS authority')
need(fs['requests']==list(range(5,19)),'FS request coverage')
need(fs['r5_r15_live_regression']=='11/11 exact FN live capsule hashes and key metadata','FS FN regression')
need(fs['r16_r18_authority']=='FQ PASS','FS R16-R18 authority')

with tempfile.TemporaryDirectory(prefix='e003i-ft-') as td0:
    td=Path(td0)

    cam9=td/'cam9.c'
    cam11=td/'cam11.c'
    cam12=td/'cam12.c'
    cam15=td/'cam15.c'
    cam18=td/'cam18.c'

    h9=td/'h9.c'; sh9=td/'sh9.h'
    h11=td/'h11.c'; sh11=td/'sh11.h'
    h12=td/'h12.c'; sh12=td/'sh12.h'
    h15=td/'h15.c'; sh15=td/'sh15.h'
    h18=td/'h18.c'; sh18=td/'sh18.h'

    run(['python3',str(ES/'make-nine-frame-camss.py'),str(SRC/'camss.c'),str(cam9)],stdout=subprocess.DEVNULL)
    need(sha(cam9)==CAM9,'ES9 CAMSS drift')

    run(['python3',str(EY/'make-eleven-frame-camss.py'),str(cam9),str(cam11)],stdout=subprocess.DEVNULL)
    need(sha(cam11)==CAM11,'EY11 CAMSS drift')

    run(['python3',str(FE/'make-twelve-frame-camss.py'),str(cam11),str(cam12)],stdout=subprocess.DEVNULL)
    need(sha(cam12)==CAM12,'FE12 CAMSS drift')

    run(['python3',str(FM/'make-fifteen-frame-camss.py'),str(cam12),str(cam15)],stdout=subprocess.DEVNULL)
    need(sha(cam15)==CAM15,'FM15 CAMSS drift')

    run(['python3',str(HERE/'make-eighteen-frame-camss.py'),str(cam15),str(cam18)],stdout=subprocess.DEVNULL)
    need(sha(cam18)==CAM18,'FT18 CAMSS drift')

    run(['python3',str(ES/'make-nine-frame-helper.py'),
         str(EN/'e003i-en-six-frame-native-aec.c'),
         str(EN/'native-db-schedule.h'),
         str(h9),str(sh9)],stdout=subprocess.DEVNULL)
    need(sha(h9)==HELP9 and sha(sh9)==SH9,'ES9 helper drift')

    run(['python3',str(EY/'make-eleven-frame-helper.py'),
         str(h9),str(sh9),str(h11),str(sh11)],stdout=subprocess.DEVNULL)
    need(sha(h11)==HELP11 and sha(sh11)==SH11,'EY11 helper drift')

    run(['python3',str(FE/'make-twelve-frame-helper.py'),
         str(h11),str(sh11),str(h12),str(sh12)],stdout=subprocess.DEVNULL)
    need(sha(h12)==HELP12 and sha(sh12)==SH12,'FE12 helper drift')

    run(['python3',str(FM/'make-fifteen-frame-helper.py'),
         str(h12),str(sh12),str(h15),str(sh15)],stdout=subprocess.DEVNULL)
    need(sha(h15)==HELP15 and sha(sh15)==SH15,'FM15 helper drift')

    run(['python3',str(HERE/'make-eighteen-frame-helper.py'),
         str(h15),str(sh15),str(h18),str(sh18)],stdout=subprocess.DEVNULL)
    need(sha(h18)==HELP18 and sha(sh18)==SH18,'FT18 helper drift')

    cs=cam18.read_text()
    hs=h18.read_text()
    hh=sh18.read_text()

    for tok in (
        'frame_limit > 18',
        'frame_number < 7 || frame_number > 18',
        'csid, vfe, 16, 16, 1, req->video[3], materialized_r16',
        'csid, vfe, 17, 17, 0, req->video[0], materialized_r17',
        'csid, vfe, 18, 18, 1, req->video[1], materialized_r18',
        'camss_x1e_pix_runner_frames(camss, &req, &result, 18)',
        'result.video_done_sixteenth != video3',
        'result.video_done_seventeenth != video0',
        'result.video_done_eighteenth != video1',
        'result.video_requeued_twelfth != video3',
        'result.video_requeued_thirteenth != video0',
        'result.video_requeued_fourteenth != video1',
        'result.live_completed != 18',
        'bounded eighteen-frame live requeue',
        'result->slot1_reused_seventh = true',
        'result->slot0_reused_eighth = true',
        'result->slot1_reused_eighth = true',
    ):
        need(tok in cs,'CAMSS contract '+tok)

    expected_cycle='{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1 }'
    for tok in (
        '#define FRAME_COUNT 18U',
        expected_cycle,
        'if (i < 14U)',
        'TARGETS=1..18',
        'ACCEPTED_G=1..18',
        'if (target <= 15U)',
        'R5..R18',
        'argc != 26',
        'FT_DQBUF_MISMATCH',
    ):
        need(tok in hs,'helper contract '+tok)

    need(hs.count('if (target >= 2U && target <= 4U) {')==1,'sensor release window drift')
    need('#define E003I_DB_FRAME_COUNT 18U' in hh,'schedule frame count')
    need('#define E003I_DB_WRITTEN_SOURCE_GENERATIONS 3U' in hh,'written source generations drift')

    cb=td/'camss-build'
    shutil.copytree(SRC,cb)
    shutil.copy2(cam18,cb/'camss.c')
    run(['make','-C',str(K),f'M={cb}','clean'],stdout=subprocess.DEVNULL)
    run(['make','-C',str(K),f'M={cb}','W=1','-j4'],stdout=subprocess.DEVNULL)
    ko=cb/'qcom-camss.ko'
    need(ko.exists(),'CAMSS module')
    ver=subprocess.check_output(['modinfo','-F','vermagic',str(ko)],text=True).strip()
    need(ver==VERMAGIC,'vermagic')

    hb=td/'helper-build'
    hb.mkdir()
    shutil.copy2(h18,hb/'e003i-ft-eighteen-frame-native-aec.c')
    shutil.copy2(sh18,hb/'native-db-schedule.h')
    shutil.copy2(EN/'native-db-schedule.c',hb/'native-db-schedule.c')
    shutil.copy2(FR/'gain-feed.c',hb/'gain-feed.c')
    shutil.copy2(FR/'gain-feed.h',hb/'gain-feed.h')
    need(sha(hb/'gain-feed.c')==GAIN15,'FR publisher copy')

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
        hb/'e003i-ft-eighteen-frame-native-aec.c',
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
    run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror',
         '-fno-fast-math','-ffp-contract=off']+
        [f'-I{x}' for x in inc]+[str(x) for x in sources]+
        ['-pthread','-lm','-o',str(exe)],stdout=subprocess.DEVNULL)
    need(exe.exists(),'helper Werror build')

    sched=hb/'sched.c'
    sched.write_text(textwrap.dedent('''\
    #include <assert.h>
    #include <string.h>
    #include "native-db-schedule.h"
    int main(void){
      struct e003i_db_schedule_state s;
      struct e003i_db_apply_event ev;
      struct e003i_imx681_controls c;
      memset(&c,0,sizeof(c));
      c.isp_gain=1.0f;
      c.frame_length_lines=3554;
      c.vertical_blanking=1394;
      c.line_count_before_even=100;
      c.exposure_lines=100;
      c.digital_gain_code=0x100;
      e003i_db_schedule_init(&s);
      for(unsigned g=1;g<=18;g++){
        assert(e003i_db_schedule_queue(&s,g,&c)==0);
        if(g>=2&&g<=4){
          assert(e003i_db_schedule_release(&s,g,&ev)==0);
          assert(ev.apply && ev.source_generation==g-1);
        }
      }
      assert(!s.failed);
      assert(s.queued_generation==18);
      assert(s.released_writes==3);
      return 0;
    }
    '''))
    st=hb/'sched'
    run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror']+
        [f'-I{x}' for x in inc]+
        [str(sched),str(hb/'native-db-schedule.c'),'-lm','-o',str(st)],
        stdout=subprocess.DEVNULL)
    run([str(st)])

    out={
        'schema':'sp11-e003i-ft-eighteen-frame-r18-transport-v1',
        'status':'PASS_OFFLINE_EIGHTEEN_FRAME_TRANSPORT',
        'base_transport':'FM fifteen-frame',
        'patched_camss_sha256':CAM18,
        'camss_build':'PASS_W1',
        'vermagic':ver,
        'patched_helper_sha256':HELP18,
        'helper_build':'PASS_WERROR',
        'helper_binary_sha256':sha(exe),
        'patched_schedule_header_sha256':SH18,
        'frames':18,
        'buffer_cycle':[0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1],
        'requeue_after_sequences':list(range(14)),
        'iq_consumption_requests':list(range(5,19)),
        'new_kernel_consumption_requests':[16,17,18],
        'aec_generations':list(range(1,19)),
        'cq_gain_feed_generations':list(range(1,16)),
        'gain_feed_c_sha256':GAIN15,
        'producer_authority':'FS PASS R5-R18 authorized integration',
        'sensor_write_sources':[1,2,3],
        'sensor_write_boundaries':[2,3,4],
        'scheduler_unit_test':'PASS_G1_G18_WRITES3',
        'camera_runtime_performed':False,
        'same_boot_retry_performed':False,
        'continuous_aec_claimed':False,
    }
    (HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
