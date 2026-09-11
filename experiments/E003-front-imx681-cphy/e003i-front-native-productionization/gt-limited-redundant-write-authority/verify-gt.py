#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,statistics,struct,subprocess,tempfile
HERE=Path(__file__).resolve().parent; BASE=HERE.parent
CQ=BASE/'cq-aec-output-imx681-control-adapter'; CH=BASE/'ch-native-aec-t681-preview-arbitration'; GP=BASE/'gp-go-control-timing-authority'
A=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gs/attempt1-pass-continuous-shadow-20260911T221117')
RUN=A/'runtime-output/RUN.txt'; ATT=A/'ATTEMPT1-PASS.json'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
subprocess.run(['sha256sum','-c','MANIFEST.sha256'],cwd=A,check=True,stdout=subprocess.DEVNULL)
att=json.loads(ATT.read_text()); need(att['status']=='PASS_CAPTURE_GS_CONTINUOUS_SHADOW_R27' and att['shadow_release_count']==23 and att['physical_sensor_writes']==3,'GS authority')
gp=json.loads((GP/'RESULT.json').read_text()); need(gp['status']=='PASS_OFFLINE_GO_CONTROL_TIMING_AUTHORITY','GP timing')
s=RUN.read_text(errors='replace')
# Reconstruct exact logged control tuples, including float bit identity.
pat=re.compile(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+) FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) ISP=0x([0-9a-fA-F]{8})')
rows=[]
for m in pat.finditer(s):
    g,req,fll,vb,exp,ag,dg,isp=m.groups(); rows.append({'g':int(g),'req':int(req),'line':int(exp),'fll':int(fll),'vb':int(vb),'exp':int(exp),'ag':int(ag),'dg':int(dg),'isp':int(isp,16)})
need([x['g'] for x in rows]==list(range(1,28)),'G1..G27 controls')
def key(x): return (x['line'],x['fll'],x['vb'],x['exp'],x['ag'],x['dg'],x['isp'])
for g in range(4,28): need(key(rows[g-1])==key(rows[2]),f'GS G{g} differs from G3')
# Shadow release timing relative to logged DQBUF boundary.
bounds={int(m.group(1))+1:int(m.group(3)) for m in re.finditer(r'POLL(\d+)_START_NS=(\d+) END_NS=(\d+)',s)}
shadow=[]
for m in re.finditer(r'GS_SENSOR_WRITE_SHADOW SOURCE=(\d+) AFTER_G=(\d+).*?MONO_NS=(\d+) COMPLETED_G=(\d+)',s):
    src,after,t,c=map(int,m.groups()); need(c==after,'shadow exact boundary'); shadow.append({'source':src,'after':after,'gate_latency_ms':(t-bounds[after])/1e6})
need([x['source'] for x in shadow]==list(range(4,27)),'shadow sources')
# Build policy and test exact GS tuples + negative mutations.
inits=[]
for x in rows: inits.append('    {%du,%du,%du,%du,%du,%du,0x%08xu},' % (x['line'],x['fll'],x['vb'],x['exp'],x['ag'],x['dg'],x['isp']))
harness=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "redundant-write-policy.h"
struct row { uint32_t line,fll,vb,exp,ag,dg,isp; };
static const struct row rows[27]={
ROWS
};
static float fb(uint32_t u){ float f; memcpy(&f,&u,4); return f; }
static struct e003i_imx681_controls cv(const struct row*r){ struct e003i_imx681_controls c={0}; c.line_count_before_even=r->line;c.frame_length_lines=r->fll;c.vertical_blanking=r->vb;c.exposure_lines=r->exp;c.analogue_gain_code=r->ag;c.digital_gain_code=r->dg;c.isp_gain=fb(r->isp);return c; }
int main(void){
 struct e003i_imx681_controls last=cv(&rows[2]),c;
 for(uint32_t g=1;g<=3;g++){c=cv(&rows[g-1]); if(e003i_redundant_write_decide(g,&last,&c)!=E003I_WRITE_PROVEN_STARTUP)return 10+g;}
 for(uint32_t g=4;g<=6;g++){c=cv(&rows[g-1]); if(e003i_redundant_write_decide(g,&last,&c)!=E003I_WRITE_REDUNDANT_ALLOWED)return 20+g;}
 for(uint32_t g=7;g<=27;g++){c=cv(&rows[g-1]); if(e003i_redundant_write_decide(g,&last,&c)!=E003I_WRITE_SHADOW_BOUND)return 40+g;}
 c=cv(&rows[3]); c.digital_gain_code++; if(e003i_redundant_write_decide(4,&last,&c)!=E003I_WRITE_SHADOW_CHANGED)return 80;
 c=cv(&rows[3]); c.isp_gain=fb(rows[3].isp^1u); if(e003i_redundant_write_decide(4,&last,&c)!=E003I_WRITE_SHADOW_CHANGED)return 81;
 if(e003i_redundant_write_decide(4,NULL,&last)!=E003I_WRITE_SHADOW_CHANGED)return 82;
 puts("GT_POLICY_G4_G6_REDUNDANT=PASS"); puts("GT_CHANGED_CONTROL_BLOCK=PASS"); puts("GT_G7_PLUS_SHADOW=PASS"); return 0;
}
'''.replace('ROWS','\n'.join(inits))
with tempfile.TemporaryDirectory(prefix='e003i-gt-') as td0:
    td=Path(td0); hp=td/'t.c'; exe=td/'t'; hp.write_text(harness)
    subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-I',str(HERE),'-I',str(CQ),'-I',str(CH),str(hp),str(HERE/'redundant-write-policy.c'),'-o',str(exe)],check=True)
    out=subprocess.check_output([str(exe)],text=True); need('GT_POLICY_G4_G6_REDUNDANT=PASS' in out and 'GT_CHANGED_CONTROL_BLOCK=PASS' in out and 'GT_G7_PLUS_SHADOW=PASS' in out,'policy unit')
    binsha=sha(exe)
# Conservative timing estimate uses GP worst observed real ioctl time and actual GS gate latency.
max_write=gp['observed_write_elapsed_ms']['maximum']
interval={g:(bounds[g+1]-bounds[g])/1e6 for g in range(1,27)}
planned=[]
for src in range(4,7):
    after=src+1; gate=next(x['gate_latency_ms'] for x in shadow if x['source']==src); margin=interval[after]-gate-max_write; need(margin>0,f'G{src} estimated margin'); planned.append({'source':src,'write_after_generation':after,'expected_effect_generation':src+3,'gs_shadow_gate_latency_ms':gate,'next_boundary_interval_ms':interval[after],'conservative_margin_ms':margin})
result={'schema':'sp11-e003i-gt-limited-redundant-write-authority-v1','status':'PASS_OFFLINE_LIMITED_REDUNDANT_WRITE_AUTHORITY','source_archive':str(A),'gs_controls_g4_g27_equal_g3':True,'proven_startup_sources':[1,2,3],'new_redundant_write_sources':[4,5,6],'changed_g4_g6_policy':'shadow-only no physical write','source_g7_plus_policy':'shadow-only','planned_timing':planned,'gs_shadow_gate_latency_ms':{'minimum':min(x['gate_latency_ms'] for x in shadow),'median':statistics.median(x['gate_latency_ms'] for x in shadow),'maximum':max(x['gate_latency_ms'] for x in shadow)},'policy_source_sha256':sha(HERE/'redundant-write-policy.c'),'policy_header_sha256':sha(HERE/'redundant-write-policy.h'),'unit_binary_sha256':binsha,'camera_runtime_performed':False,'changed_post_g3_controls_authorized':False,'safe_next_step':'integrate policy into a fresh helper: physical G4..G6 only on exact equality; all changed/later controls shadow'}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GT_GS_CONTROL_EQUALITY_G4_G27=PASS')
print('GT_POLICY_G4_G6_REDUNDANT=PASS')
print('GT_CHANGED_CONTROL_BLOCK=PASS')
print('GT_TIMING_ESTIMATE=PASS')
print('GT_VERIFY=PASS')
