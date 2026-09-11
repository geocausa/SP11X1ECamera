#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,struct,subprocess,tempfile
HERE=Path(__file__).resolve().parent; BASE=HERE.parent
CQ=BASE/'cq-aec-output-imx681-control-adapter'; CH=BASE/'ch-native-aec-t681-preview-arbitration'; CW=BASE/'cw-imx681-atomic-dynamic-control-cluster'; GP=BASE/'gp-go-control-timing-authority'
A=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gv/attempt1-helper-pass-verifier-audit-20260911T222625')
RUN=A/'runtime-output/RUN.txt'; ADJ=A/'ADJUDICATED-LIVE-RESULT.json'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
subprocess.run(['sha256sum','-c','MANIFEST.sha256'],cwd=A,check=True,stdout=subprocess.DEVNULL)
live=json.loads(ADJ.read_text()); need(live['status']=='PASS_CAPTURE_GV_REDUNDANT_IOCTL_DEDUPE_R27' and live['new_post_g3_sensor_hardware_write_count']==0,'GV authority')
gp=json.loads((GP/'RESULT.json').read_text()); need(gp['status']=='PASS_OFFLINE_GO_CONTROL_TIMING_AUTHORITY','GP timing')
subprocess.run(['python3',str(CW/'prove-cw.py')],check=True,stdout=subprocess.DEVNULL)
s=RUN.read_text(errors='replace')
pat=re.compile(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+) FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) ISP=0x([0-9a-fA-F]{8})')
rows=[]
for m in pat.finditer(s):
    g,req,fll,vb,exp,ag,dg,isp=m.groups(); rows.append({'g':int(g),'req':int(req),'line':int(exp),'fll':int(fll),'vb':int(vb),'exp':int(exp),'ag':int(ag),'dg':int(dg),'isp':int(isp,16)})
need([x['g'] for x in rows]==list(range(1,28)),'G1..G27 controls')
def key(x): return (x['line'],x['fll'],x['vb'],x['exp'],x['ag'],x['dg'],x['isp'])
need(key(rows[2])==key(rows[3]),'GV G3/G4 equality precondition')
base=rows[3]; need(base['dg']==1471 and base['fll']==7116 and base['exp']==7108 and base['ag']==960,'expected GV G4 base')
# Compile policy and prove exact one-field mutation plus all fail-closed branches.
row='{%du,%du,%du,%du,%du,%du,0x%08xu}'%(base['line'],base['fll'],base['vb'],base['exp'],base['ag'],base['dg'],base['isp'])
h=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "minimal-dgain-sentinel.h"
struct row { uint32_t line,fll,vb,exp,ag,dg,isp; };
static const struct row r=ROW;
static float fb(uint32_t u){float f;memcpy(&f,&u,4);return f;}
static struct e003i_imx681_controls cv(void){struct e003i_imx681_controls c={0};c.line_count_before_even=r.line;c.frame_length_lines=r.fll;c.vertical_blanking=r.vb;c.exposure_lines=r.exp;c.analogue_gain_code=r.ag;c.digital_gain_code=r.dg;c.isp_gain=fb(r.isp);return c;}
int main(void){struct e003i_imx681_controls last=cv(),native=cv(),out={0};uint32_t a,b;
 if(e003i_gw_make_sentinel(4,&last,&native,&out)!=E003I_GW_APPLY_SENTINEL)return 10;
 memcpy(&a,&native.isp_gain,4);memcpy(&b,&out.isp_gain,4);
 if(out.line_count_before_even!=native.line_count_before_even||out.frame_length_lines!=native.frame_length_lines||out.vertical_blanking!=native.vertical_blanking||out.exposure_lines!=native.exposure_lines||out.analogue_gain_code!=native.analogue_gain_code||out.digital_gain_code!=native.digital_gain_code+1||a!=b)return 11;
 if(e003i_gw_make_sentinel(5,&last,&native,&out)!=E003I_GW_SHADOW_NOT_SOURCE)return 12;
 native.digital_gain_code++; if(e003i_gw_make_sentinel(4,&last,&native,&out)!=E003I_GW_SHADOW_BASE_CHANGED)return 13;
 native=last; native.digital_gain_code=0x0f00; last=native; if(e003i_gw_make_sentinel(4,&last,&native,&out)!=E003I_GW_SHADOW_RANGE)return 14;
 if(e003i_gw_make_sentinel(4,NULL,&native,&out)!=E003I_GW_SHADOW_BASE_CHANGED)return 15;
 puts("GW_SENTINEL_EXACT_ONE_LSB=PASS");puts("GW_FAIL_CLOSED=PASS");return 0;}
'''.replace('ROW',row)
with tempfile.TemporaryDirectory(prefix='e003i-gw-') as td0:
    td=Path(td0); hp=td/'t.c'; exe=td/'t'; hp.write_text(h)
    subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-I',str(HERE),'-I',str(CQ),'-I',str(CH),str(hp),str(HERE/'minimal-dgain-sentinel.c'),'-o',str(exe)],check=True)
    out=subprocess.check_output([str(exe)],text=True); need('GW_SENTINEL_EXACT_ONE_LSB=PASS' in out and 'GW_FAIL_CLOSED=PASS' in out,'unit'); binary_sha=sha(exe)
# The sentinel itself remains within the already-proved IMX681 constraints.
newdg=base['dg']+1; need(0x100<=newdg<=0xf00,'digital range')
need(base['vb']==base['fll']-2160 and base['exp']<=((base['fll']-4)&~1),'geometry')
old_gain=base['dg']/256.0; new_gain=newdg/256.0; rel=(new_gain/old_gain-1.0)*100.0
need(rel>0 and rel<0.1,'minimal gain delta')
# Exact-boundary timing estimate: source G4 writes after completed G5.
bounds={int(m.group(1))+1:int(m.group(3)) for m in re.finditer(r'POLL(\d+)_START_NS=(\d+) END_NS=(\d+)',s)}
sm=re.search(r'GU_REDUNDANT_WRITE_ALLOW SOURCE=4 AFTER_G=5.*?\nDB_SENSOR_WRITE_OK SOURCE=4 AFTER_G=5.*?START_NS=(\d+)',s,re.S); need(sm,'GV G4 gate timing')
start=int(sm.group(1)); gate_latency=(start-bounds[5])/1e6
interval=(bounds[6]-bounds[5])/1e6; worst=gp['observed_write_elapsed_ms']['maximum']; margin=interval-gate_latency-worst; need(margin>0,'timing margin')
result={'schema':'sp11-e003i-gw-minimal-changed-post-g3-authority-v1','status':'PASS_OFFLINE_MINIMAL_CHANGED_POST_G3_AUTHORITY','source_archive':str(A),'source_generation':4,'write_after_completed_generation':5,'expected_effect_generation':7,'precondition':'native G4 bit-identical to last applied G3','base_controls':{'fll':base['fll'],'vertical_blanking':base['vb'],'exposure':base['exp'],'analogue_gain_code':base['ag'],'digital_gain_code':base['dg'],'isp_gain_bits':f"0x{base['isp']:08x}"},'sentinel_controls':{'fll':base['fll'],'vertical_blanking':base['vb'],'exposure':base['exp'],'analogue_gain_code':base['ag'],'digital_gain_code':newdg,'isp_gain_bits':f"0x{base['isp']:08x}"},'only_changed_sensor_field':'digital_gain_code','digital_gain_lsb':1/256.0,'base_digital_gain_real':old_gain,'sentinel_digital_gain_real':new_gain,'relative_digital_gain_delta_percent':rel,'frame_timing_changed':False,'later_sensor_writes_authorized':False,'native_changed_g4_action':'shadow-only','v4l2_changed_cluster_will_reach_s_ctrl':True,'atomic_group_hold_authority':'CW PASS','timing':{'gv_g4_gate_start_after_g5_ms':gate_latency,'g5_to_g6_boundary_ms':interval,'conservative_write_elapsed_ms':worst,'conservative_margin_ms':margin},'policy_source_sha256':sha(HERE/'minimal-dgain-sentinel.c'),'policy_header_sha256':sha(HERE/'minimal-dgain-sentinel.h'),'unit_binary_sha256':binary_sha,'camera_runtime_performed':False,'safe_next_step':'integrate exactly one guarded G4 +1 digital-gain sentinel into the live helper; G5 onward shadow-only'}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(f"GW_DGAIN_OLD={base['dg']} NEW={newdg} RELATIVE_DELTA_PERCENT={rel:.6f}")
print(f"GW_CONSERVATIVE_MARGIN_MS={margin:.6f}")
print('GW_SENTINEL_POLICY=PASS')
print('GW_VERIFY=PASS')
