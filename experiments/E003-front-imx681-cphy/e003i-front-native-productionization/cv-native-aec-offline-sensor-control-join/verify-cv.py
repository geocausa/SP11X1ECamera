#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[3]
CU = BASE / 'cu-native-aec-raw-stats-request-loop'
CQ = BASE / 'cq-aec-output-imx681-control-adapter'
CT = BASE / 'ct-native-aec-bhist-bank4-replay'
CR = BASE / 'cr-native-aec-effective-analyzer-producer'
CP = BASE / 'cp-native-aec-self-contained-cold-init'
CF = BASE / 'cf-native-aec-final-exposure-si'
CE = BASE / 'ce-native-aec-final-target-producer'
CC = BASE / 'cc-native-aec-adrc-darkboost-tail'
BY = BASE / 'by-native-aec-method11-point-aggregation'
CG = BASE / 'cg-native-aec-qword-convergence-input'
CH = BASE / 'ch-native-aec-t681-preview-arbitration'
BK = BASE / 'bk-native-aec-history-state'
BJ = BASE / 'bj-native-aec-log103-coordinate'
W = BASE / 'w-request-stats-selection-trigger-oracle'
AV = BASE / 'av-windows-imx681-sensor-delay'
AP = BASE / 'ap-bounded-imx681-control-runtime'
PARENT = '8c660bf'
LOCAL = os.environ.get('E003I_CV_LOCAL') == '1'


def fresh(path: Path, script: str, marker: str):
    cp = subprocess.run([sys.executable, str(path / script)], cwd=path,
                        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cp.returncode:
        raise AssertionError(f'{path.name}/{script} failed\\n{cp.stdout}\\n{cp.stderr}')
    assert marker in cp.stdout, (path.name, marker, cp.stdout[-4000:])
    return cp.stdout


assert subprocess.run(['git','merge-base','--is-ancestor',PARENT,'HEAD'], cwd=REPO).returncode == 0
if LOCAL:
    assert json.loads((CU/'RESULT.json').read_text())['status'] == 'PASS'
    assert json.loads((CQ/'RESULT.json').read_text())['status'].startswith('PASS_')
    print('PARENTS_LOCAL_PIN=CU,CQ,AV')
else:
    fresh(CU, 'verify-cu.py', 'CU_VERIFY=PASS')
    fresh(CQ, 'verify-cq.py', 'CQ_VERIFY=PASS')
    fresh(AV, 'verify-av.py', 'AV_VERIFY=PASS')

w = (W/'README.md').read_text()
assert 'request_frame = source_generation + 3' in w
assert 'request4 selects source generation1' in w
assert 'request5 selects generation2' in w
assert 'request6 selects generation3' in w
assert '104/104 selected-stats pointers matched' in w

ap = json.loads((AP/'runtime-output/producer/RESULT.json').read_text())
assert ap['source_generation_is_request_id'] is False
assert ap['selection_law'] == 'R5<-G2, R6<-G3'
assert [(r['generation'],r['request_target']) for r in ap['rows']] == [(1,None),(2,5),(3,6)]

av = (AV/'README.md').read_text()
assert 'linecount=2, gain=2, frameLengthLines=2, maxPipeline=2; frameSkip=0' in av
assert 'HandleDelayInfo performs zero request-history realignment' in av
assert 'sensor application pipeline depth = 2 frame intervals' in av
assert 'final optical-frame label/latch statement is intentionally kept separate' in av

src = (HERE/'native-raw-control-join.c').read_text()
hdr = (HERE/'native-raw-control-join.h').read_text()
for forbidden in ('open(', 'ioctl(', 'VIDIOC_', 'cci_write', 'i2c_', '/dev/'):
    assert forbidden not in src + hdr, forbidden
for required in ('shadow = *state;', '*state = shadow;',
                 'E003I_STATS_TO_REQUEST_DELAY_FRAMES',
                 'E003I_IMX681_SENSOR_PIPELINE_DELAY_FRAMES',
                 'E003I_IMX681_CAMX_HISTORY_REALIGN_FRAMES'):
    assert required in src + hdr, required

harness = r'''
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "native-raw-control-join.h"

#define PIXELS UINT32_C(2073600)

static void wr16(void *p, uint16_t v){ memcpy(p,&v,2); }
static void wr32(void *p, uint32_t v){ memcpy(p,&v,4); }
static void wr64(void *p, uint64_t v){ memcpy(p,&v,8); }
static uint32_t fbits(float f){ uint32_t u; memcpy(&u,&f,4); return u; }

static void make_stats(uint8_t *d, uint64_t generation, uint32_t slot,
                       uint64_t sum_value)
{
    unsigned i;
    memset(d,0,E003I_STATS3A_BYTES);
    wr32(d+0, E003I_STATS3A_MAGIC); wr16(d+4,1); wr16(d+6,E003I_STATS3A_HEADER_BYTES);
    wr64(d+8,generation); wr32(d+16,(uint32_t)generation); wr32(d+20,slot);
    wr32(d+24,0); wr32(d+28,E003I_STATS3A_AEC_BYTES);
    wr32(d+32,E003I_STATS3A_AEC_BYTES); wr32(d+36,E003I_STATS3A_BHIST_BYTES);
    wr32(d+40,E003I_STATS3A_AEC_BYTES+E003I_STATS3A_BHIST_BYTES);
    wr32(d+44,E003I_STATS3A_AWB_BYTES); wr32(d+48,1);
    for(i=0;i<1024;i++){
        uint8_t *r=d+E003I_STATS3A_HEADER_BYTES+i*0x50u;
        wr64(r+0x00,sum_value); wr64(r+0x08,sum_value);
        wr64(r+0x10,sum_value); wr64(r+0x18,sum_value);
        wr16(r+0x06,1980); wr16(r+0x1e,1980); wr16(r+0x0e,1980); wr16(r+0x16,1980);
    }
    wr32(d+E003I_STATS3A_HEADER_BYTES+E003I_STATS3A_AEC_BYTES+700u*4u, PIXELS);
}

int main(void)
{
    static const uint64_t sums[4]={101375995,93265916,91200000,90000000};
    struct e003i_request_loop_state sw, sm, before;
    uint8_t *stats=malloc(E003I_STATS3A_BYTES);
    unsigned f;
    if(!stats) return 90;
    if(e003i_request_loop_init(&sw) || e003i_request_loop_init(&sm)) return 91;
    for(f=0;f<4;f++){
        struct e003i_raw_request_input in;
        struct e003i_raw_control_output cw;
        struct e003i_raw_request_output rm;
        struct e003i_imx681_controls cm;
        uint64_t request_target;
        int rc;
        make_stats(stats,(uint64_t)f+1u,f&1u,sums[f]);
        in.frame_id=f; in.stats3a=stats; in.stats3a_bytes=E003I_STATS3A_BYTES;
        memset(&cw,0,sizeof(cw)); memset(&rm,0,sizeof(rm)); memset(&cm,0,sizeof(cm));
        rc=e003i_raw_request_to_imx681_controls(&sw,&in,&cw); if(rc) return 10+(int)f;
        rc=e003i_raw_request_loop_process(&sm,&in,&rm); if(rc) return 20+(int)f;
        rc=e003i_imx681_controls_from_t681(&rm.request.short_arbitration,&cm); if(rc) return 30+(int)f;
        request_target=rm.stats_generation+3u;
        if(memcmp(&cw.raw,&rm,sizeof(rm))) return 40+(int)f;
        if(memcmp(&cw.controls,&cm,sizeof(cm))) return 50+(int)f;
        if(memcmp(&sw,&sm,sizeof(sw))) return 60+(int)f;
        if(cw.stats_owned_request_frame!=request_target ||
           cw.sensor_pipeline_delay_frames!=2u || cw.camx_history_realign_frames!=0u) return 70+(int)f;
        printf("F=%u G=%" PRIu64 " REQUEST=%" PRIu64
               " SENSOR_PIPE=2 REALIGN=0 FLL=%u VBLANK=%u EXP=%u AGAIN=0x%03x DGAIN=0x%04x ISP=0x%08x\n",
               f,cw.raw.stats_generation,cw.stats_owned_request_frame,
               cw.controls.frame_length_lines,cw.controls.vertical_blanking,
               cw.controls.exposure_lines,cw.controls.analogue_gain_code,
               cw.controls.digital_gain_code,fbits(cw.controls.isp_gain));
    }

    before=sw;
    {
        struct e003i_raw_request_input bad={sw.next_frame_id,stats,E003I_STATS3A_BYTES-1u};
        struct e003i_raw_control_output out;
        if(e003i_raw_request_to_imx681_controls(&sw,&bad,&out)==0) return 80;
        if(memcmp(&sw,&before,sizeof(sw))) return 81;
    }
    puts("CV_HARNESS=PASS");
    free(stats);
    return 0;
}
'''

with tempfile.TemporaryDirectory(prefix='e003i-cv-') as tds:
    td=Path(tds)
    hp=td/'harness.c'; hp.write_text(harness)
    exe=td/'cv-harness'
    incs=[HERE,CU,CQ,CR,CT,CP,CF,CE,CC,BY,CG,CH,BK,BJ]
    srcs=[
        HERE/'native-raw-control-join.c', CU/'native-raw-aec-loop.c', CU/'native-stats3a.c',
        CQ/'native-imx681-control.c', CR/'native-effective-analyzers.c', CT/'native-bhist-bank4.c',
        CP/'native-aec-request-loop.c', CF/'native-final-exposure.c', CE/'native-final-target.c',
        CC/'native-aec-tail.c', BY/'native-target-aggregate.c', CG/'native-convergence.c',
        CH/'native-t681.c', BK/'native-aec-state.c', BJ/'native-log103.c', hp]
    cmd=['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
    for x in incs: cmd += ['-I',str(x)]
    cmd += [str(x) for x in srcs] + ['-lm','-o',str(exe)]
    subprocess.run(cmd,check=True)
    run=subprocess.run([str(exe)],text=True,capture_output=True,check=True)

lines=[x for x in run.stdout.splitlines() if x.startswith('F=')]
assert len(lines)==4 and 'CV_HARNESS=PASS' in run.stdout
rows=[]
rx=re.compile(r'F=(\d+) G=(\d+) REQUEST=(\d+) SENSOR_PIPE=2 REALIGN=0 FLL=(\d+) VBLANK=(\d+) EXP=(\d+) AGAIN=0x([0-9a-f]+) DGAIN=0x([0-9a-f]+) ISP=0x([0-9a-f]+)')
for line in lines:
    m=rx.fullmatch(line); assert m,line
    f,g,r,fll,vb,exp,again,dgain,isp=m.groups()
    f=int(f);g=int(g);r=int(r)
    assert g==f+1 and r==g+3
    rows.append({'aec_sequence_frame':f,'stats_generation':g,'stats_owned_request_frame':r,
                 'sensor_pipeline_delay_frames':2,'camx_history_realign_frames':0,
                 'controls':{'frame_length_lines':int(fll),'vertical_blanking':int(vb),
                             'exposure_lines':int(exp),'analogue_gain_code':f'0x{int(again,16):03x}',
                             'digital_gain_code':f'0x{int(dgain,16):04x}','isp_gain_bits':f'0x{int(isp,16):08x}'}})

result={
 'schema':'sp11-e003i-cv-native-aec-offline-sensor-control-join-v1',
 'status':'PASS',
 'parent_cu_commit':PARENT,
 'pipeline':['CU generation-tagged STATS3A -> native AEC request','CQ Short T681 -> IMX681 controls'],
 'ownership':{
   'cu_cold_sequence_law':'stats_generation == source_seq == aec_sequence_frame + 1',
   'windows_request_stats_law':'stats_owned_request_frame = source_generation + 3',
   'w_oracle_matches':104,
   'ap_live_examples':['R5<-G2','R6<-G3'],
   'source_generation_is_request_id':False,
 },
 'sensor_delay':{
   'linecount_frames':2,'gain_frames':2,'fll_frames':2,'max_pipeline_frames':2,'frame_skip':0,
   'camx_history_realign_frames':0,
   'optical_latch_frame_claimed':False,
 },
 'composition':{'generated_frames':4,'wrapper_vs_independent_cu_plus_cq':'byte-exact','rows':rows},
 'failure_atomicity':{'shadow_state_commit_after_cq':True,'bad_stats_state_unchanged':True},
 'safety':{'device_open':False,'ioctl':False,'cci_i2c':False,'streamon':False,'sensor_control_writes':False,'runtime_performed':False},
 'next_gate':'join CV tuple to AM group-held Linux control transport and frame-boundary/latch semantics in a bounded no-write/offline proof before any new live runtime',
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print('PARENT_CU_COMMIT='+PARENT)
print('REQUEST_STATS_LAW=request=source_generation+3 W=104/104 AP=G2->R5,G3->R6')
print('SENSOR_DELAY=linecount/gain/FLL=2 maxPipeline=2 history-realign=0')
print('OPTICAL_LATCH_FRAME_CLAIMED=0')
for x in lines: print(x)
print('FAILURE_ATOMICITY=shadow-state PASS')
print('SENSOR_CONTROL_WRITES=0')
print('CV_VERIFY=PASS')
