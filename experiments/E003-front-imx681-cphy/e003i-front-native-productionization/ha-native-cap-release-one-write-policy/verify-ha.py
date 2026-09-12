#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile
HERE=Path(__file__).resolve().parent; BASE=HERE.parent
GZ=BASE/'gz-native-response-threshold-analysis'; CV=BASE/'cv-native-aec-offline-sensor-control-join'; CU=BASE/'cu-native-aec-raw-stats-request-loop'; CQ=BASE/'cq-aec-output-imx681-control-adapter'; CR=BASE/'cr-native-aec-effective-analyzer-producer'; CT=BASE/'ct-native-aec-bhist-bank4-replay'; DN=BASE/'dn-native-aec-internal-cap'; CF=BASE/'cf-native-aec-final-exposure-si'; CE=BASE/'ce-native-aec-final-target-producer'; CC=BASE/'cc-native-aec-adrc-darkboost-tail'; BY=BASE/'by-native-aec-method11-point-aggregation'; CG=BASE/'cg-native-aec-qword-convergence-input'; CH=BASE/'ch-native-aec-t681-preview-arbitration'; BK=BASE/'bk-native-aec-history-state'; BJ=BASE/'bj-native-aec-log103-coordinate'
A=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gy/attempt1-pass-minimal-changed-sentinel-20260911T224155')
CAP=6133333088

def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
need(json.loads((GZ/'RESULT.json').read_text())['status']=='PASS_OFFLINE_RESPONSE_THRESHOLD_CENSORED_BY_PREVIEW_CAP','GZ authority')
subprocess.run(['sha256sum','-c','MANIFEST.sha256'],cwd=A,check=True,stdout=subprocess.DEVNULL)
harness=r'''
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "native-cap-release-policy.h"
static void *rf(const char *p,size_t*n){FILE*f=fopen(p,"rb");long z;void*b;if(!f)return NULL;fseek(f,0,SEEK_END);z=ftell(f);rewind(f);b=malloc((size_t)z);if(!b){fclose(f);return NULL;}if(fread(b,1,(size_t)z,f)!=(size_t)z){free(b);fclose(f);return NULL;}fclose(f);*n=(size_t)z;return b;}
int main(int argc,char**argv){struct e003i_request_loop_state st;struct e003i_imx681_controls last={0};unsigned valid=0,allowed=0;int g;if(argc!=2)return 2;if(e003i_request_loop_init(&st))return 3;
 for(g=1;g<=27;g++){char p[4096];size_t n;void*b;struct e003i_raw_request_input in;struct e003i_raw_control_output o;enum e003i_ha_decision d;snprintf(p,sizeof(p),"%s/STATS3A-%d.bin",argv[1],g-1);b=rf(p,&n);if(!b)return 10+g;memset(&o,0,sizeof(o));in.frame_id=g-1;in.stats3a=b;in.stats3a_bytes=n;if(e003i_raw_request_to_imx681_controls(&st,&in,&o)){free(b);return 50+g;}d=e003i_ha_decide((uint32_t)g,allowed,valid?&last:NULL,&o);printf("G=%d DEC=%u CONV=%llu CAP=%llu FLL=%u EXP=%u AGAIN=%u DGAIN=%u\n",g,(unsigned)d,(unsigned long long)o.raw.request.convergence.linear[0],(unsigned long long)o.raw.request.capped.linear[0],o.controls.frame_length_lines,o.controls.exposure_lines,o.controls.analogue_gain_code,o.controls.digital_gain_code);if(g<=3){last=o.controls;valid=1;}else if(d==E003I_HA_APPLY_ONE_NATIVE){last=o.controls;allowed=1;}free(b);}
 {struct e003i_raw_control_output x;struct e003i_imx681_controls l=last;enum e003i_ha_decision d;memset(&x,0,sizeof(x));x.raw.request.convergence.linear[0]=CAPVAL-1;x.raw.request.capped.linear[0]=CAPVAL-1;x.controls=l;x.controls.digital_gain_code=(uint16_t)(l.digital_gain_code>0x100?l.digital_gain_code-1:l.digital_gain_code+1);d=e003i_ha_decide(4,0,&l,&x);if(d!=E003I_HA_APPLY_ONE_NATIVE)return 90;if(e003i_ha_decide(5,1,&l,&x)!=E003I_HA_SHADOW_ALREADY_APPLIED)return 91;x.controls=l;if(e003i_ha_decide(4,0,&l,&x)!=E003I_HA_SHADOW_UNCHANGED)return 92;x.raw.request.convergence.linear[0]=CAPVAL;x.raw.request.capped.linear[0]=CAPVAL;if(e003i_ha_decide(4,0,&l,&x)!=E003I_HA_SHADOW_CAP_ACTIVE)return 93;}
 puts("HA_SYNTHETIC_BRANCHES=PASS");return 0;}
'''.replace('CAPVAL',str(CAP))
with tempfile.TemporaryDirectory(prefix='e003i-ha-') as td0:
    td=Path(td0); hp=td/'h.c'; exe=td/'ha'; hp.write_text(harness)
    inc=[HERE,CV,CU,CQ,CR,CT,DN,CF,CE,CC,BY,CG,CH,BK,BJ]
    src=[HERE/'native-cap-release-policy.c',CV/'native-raw-control-join.c',CU/'native-raw-aec-loop.c',CU/'native-stats3a.c',CQ/'native-imx681-control.c',CR/'native-effective-analyzers.c',CT/'native-bhist-bank4.c',DN/'native-aec-request-loop.c',DN/'native-internal-cap.c',CF/'native-final-exposure.c',CE/'native-final-target.c',CC/'native-aec-tail.c',BY/'native-target-aggregate.c',CG/'native-convergence.c',CH/'native-t681.c',BK/'native-aec-state.c',BJ/'native-log103.c',hp]
    cmd=['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
    for x in inc: cmd+=['-I',str(x)]
    cmd += [str(x) for x in src]+['-lm','-o',str(exe)]
    subprocess.run(cmd,check=True)
    out=subprocess.check_output([str(exe),str(A/'runtime-output')],text=True)
    binary_sha=sha(exe)
lines=[x for x in out.splitlines() if x.startswith('G=')]
need(len(lines)==27,'27 GY policy rows')
# G1..G3 startup-owned; every later GY generation must remain cap-active shadow.
for i,line in enumerate(lines,1):
    dec=int(line.split('DEC=')[1].split()[0])
    need(dec==(1 if i<=3 else 2),f'GY decision G{i}: {dec}')
need('HA_SYNTHETIC_BRANCHES=PASS' in out,'synthetic branch coverage')
result={'schema':'sp11-e003i-ha-native-cap-release-one-write-policy-v1','status':'PASS_OFFLINE_NATIVE_CAP_RELEASE_ONE_WRITE_POLICY','preview_cap_max':CAP,'startup_sources':[1,2,3],'post_g3_allow_conditions':['short convergence strictly below preview cap','capped short equals unconstrained short','native tuple differs from last applied','one later native write latch still clear'],'post_g3_fail_closed_conditions':['cap active or convergence at/above cap','native tuple unchanged','later native write already applied','invalid pointers'],'synthetic_control_delta_added':False,'gy_replay_post_g3_allowed_writes':0,'gy_replay_post_g3_shadow_cap_active':24,'synthetic_below_cap_changed_case':'APPLY_ONE_NATIVE','synthetic_second_write_case':'SHADOW_ALREADY_APPLIED','synthetic_unchanged_case':'SHADOW_UNCHANGED','compile':'PASS_WERROR','unit_binary_sha256':binary_sha,'policy_source_sha256':sha(HERE/'native-cap-release-policy.c'),'policy_header_sha256':sha(HERE/'native-cap-release-policy.h'),'camera_runtime_performed':False,'live_run_authorized':False,'safe_next_step':'integrate HA decision with exact-boundary continuous helper while carrying native convergence/cap metadata; preserve one-write latch'}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HA_GY_REPLAY=G4_G27_ALL_CAP_ACTIVE_SHADOW')
print('HA_BELOW_CAP_CHANGED=APPLY_ONE_NATIVE')
print('HA_ONE_WRITE_LATCH=PASS')
print('HA_SYNTHETIC_DELTA=NONE')
print('HA_VERIFY=PASS')
