#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, tempfile, textwrap
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE=HERE.parent
CY=BASE/'cy-bounded-imx681-latch-runtime'
CX=BASE/'cx-windows-imx681-sof-i2c-apply-boundary'
CV=BASE/'cv-native-aec-offline-sensor-control-join'
CH=BASE/'ch-native-aec-t681-preview-arbitration'
CQ=BASE/'cq-aec-output-imx681-control-adapter'
CP=BASE/'cp-native-aec-self-contained-cold-init'
def need(x,m):
    if not x: raise AssertionError(m)
need(subprocess.check_output(['git','-C',str(ROOT),'rev-parse','--abbrev-ref','HEAD'],text=True).strip()=='experiment/e003-front-imx681-cphy','branch')
cy=json.loads((CY/'RESULT.json').read_text()); cx=json.loads((CX/'RESULT.json').read_text()); cv=json.loads((CV/'RESULT.json').read_text())
need(cy['status']=='PASS_LIVE_LATCH_BOUNDARY','CY parent')
need(cy['measurement']['first_significant_drop_generation']==3,'CY first effect')
need(cy['runtime']['step_after_v4l2_sequence']==0,'CY step coordinate')
need(cy['runtime']['hardware_step_transaction_count']==1,'CY one transaction')
need(cy['golden_return']['status']=='PASS','CY golden')
need(cx['status']=='PASS','CX parent')
need(cx['windows']['packet_apply_coordinate']=='packet F selected while current SOF request is F-1','CX selection')
need(cv['ownership']['windows_request_stats_law']=='stats_owned_request_frame = source_generation + 3','W/CV ownership')
# Algebra: CY write after completed generation N -> first effect N+2. To make G affect G+3, write after N=G+1.
for g in range(1,100):
    write_after=g+1
    first_effect=write_after+2
    windows_request=g+3
    need(first_effect==windows_request,'schedule algebra')
# Compile exact CH/CQ cold bootstrap.
c=textwrap.dedent(r'''
#include <stdio.h>
#include "native-t681.h"
#include "native-imx681-control.h"
int main(void){struct e003i_t681_result t; struct e003i_imx681_controls c;
 if(e003i_t681_preview_arbitrate(33333332ULL,&t)) return 2;
 if(e003i_imx681_controls_from_t681(&t,&c)) return 3;
 printf("GAIN=%.9g TIME=%llu RET=%llu FLL=%u VB=%u EXP=%u AGAIN=%u DGAIN=%u ISP=%.9g\n",t.gain,(unsigned long long)t.exposure_time_ns,(unsigned long long)t.retained_exposure,c.frame_length_lines,c.vertical_blanking,c.exposure_lines,c.analogue_gain_code,c.digital_gain_code,c.isp_gain); return 0;}
''')
with tempfile.TemporaryDirectory() as td:
    td=Path(td); hp=td/'b.c'; hp.write_text(c); exe=td/'b'
    subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off','-I',str(CH),'-I',str(CQ),str(CH/'native-t681.c'),str(CQ/'native-imx681-control.c'),str(hp),'-lm','-o',str(exe)],check=True)
    out=subprocess.check_output([str(exe)],text=True).strip()
need(out=='GAIN=1 TIME=33333332 RET=33333332 FLL=3562 VB=1402 EXP=3554 AGAIN=0 DGAIN=256 ISP=1','cold bootstrap')
# Guard the important scope fact: CH is still only proven for in-table targets; DA does not alter it.
ch=(CH/'README.md').read_text()
need('positive in-table linear exposure target' in ch,'CH scope')
print('DA_WINDOWS_STATS_REQUEST=G_to_G_plus_3')
print('DA_CY_WRITE_EFFECT=N_to_N_plus_2')
print('DA_PARITY_WRITE_AFTER=G_plus_1')
print('DA_FIRST_EFFECT=G_plus_3')
print('DA_COLD_BOOTSTRAP=FLL3562_VB1402_EXP3554_AGAIN0_DGAIN256_ISP1')
print('DA_CY_SEQUENCE_CONTINUOUS_FIXTURE=NO')
print('DA_RUNTIME=0 SENSOR_WRITES=0')
print('DA_VERIFY=PASS')
