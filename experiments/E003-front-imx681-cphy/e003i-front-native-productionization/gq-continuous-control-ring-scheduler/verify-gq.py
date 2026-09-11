#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,struct,subprocess,tempfile,textwrap
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
CQ=BASE/'cq-aec-output-imx681-control-adapter'
CH=BASE/'ch-native-aec-t681-preview-arbitration'
GP=BASE/'gp-go-control-timing-authority'
A=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-go/attempt1-pass-twentyseven-frame-20260911T2145')
RUN=A/'runtime-output/RUN.txt'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
subprocess.run(['sha256sum','-c','MANIFEST.sha256'],cwd=A,check=True,stdout=subprocess.DEVNULL)
gp=json.loads((GP/'RESULT.json').read_text())
need(gp['status']=='PASS_OFFLINE_GO_CONTROL_TIMING_AUTHORITY','GP authority')
s=RUN.read_text(errors='replace')
pat=re.compile(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+) FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) ISP=0x([0-9a-fA-F]{8})')
controls=[]
for m in pat.finditer(s):
    g,req,fll,vb,exp,ag,dg,isp=m.groups(); g=int(g); req=int(req)
    need(req==g+3,'request mapping')
    controls.append({'g':g,'request':req,'fll':int(fll),'vb':int(vb),'line':int(exp),'exp':int(exp),'ag':int(ag),'dg':int(dg),'isp_bits':int(isp,16)})
need([x['g'] for x in controls]==list(range(1,28)),'GO controls G1..G27')
# C replay uses exact logged register values and exact float bit patterns.
inits=[]
for x in controls:
    inits.append('    {%du,%du,%du,%du,%du,%du,0x%08xu},' % (x['line'],x['fll'],x['vb'],x['exp'],x['ag'],x['dg'],x['isp_bits']))
harness=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "continuous-db-schedule.h"
struct row { uint32_t line,fll,vb,exp,ag,dg,isp_bits; };
static const struct row rows[27] = {
ROWS
};
static float fb(uint32_t u){ float f; memcpy(&f,&u,sizeof(f)); return f; }
static int same_controls(const struct e003i_imx681_controls *c,const struct row *r){
 uint32_t b=0; memcpy(&b,&c->isp_gain,sizeof(b));
 return c->line_count_before_even==r->line && c->frame_length_lines==r->fll &&
 c->vertical_blanking==r->vb && c->exposure_lines==r->exp &&
 c->analogue_gain_code==r->ag && c->digital_gain_code==r->dg && b==r->isp_bits;
}
static struct e003i_imx681_controls cv(const struct row *r){
 struct e003i_imx681_controls c={0}; c.line_count_before_even=r->line; c.frame_length_lines=r->fll;
 c.vertical_blanking=r->vb; c.exposure_lines=r->exp; c.analogue_gain_code=r->ag;
 c.digital_gain_code=r->dg; c.isp_gain=fb(r->isp_bits); return c;
}
static unsigned pending_count(const struct e003i_cont_schedule_state *s){ unsigned n=0; for(unsigned i=0;i<E003I_CONT_PENDING_SLOTS;i++) n+=!!s->pending_valid[i]; return n; }
int main(void){
 struct e003i_cont_schedule_state st; struct e003i_cont_apply_event ev; e003i_cont_schedule_init(&st);
 struct e003i_imx681_controls c=cv(&rows[0]); if(e003i_cont_schedule_queue(&st,1,&c)||pending_count(&st)!=1) return 10;
 for(uint32_t g=2;g<=27;g++){
   c=cv(&rows[g-1]); if(e003i_cont_schedule_queue(&st,g,&c)) return 20+(int)g;
   if(pending_count(&st)!=2) return 60+(int)g;
   if(e003i_cont_schedule_release(&st,g,&ev)) return 100+(int)g;
   if(!ev.apply || ev.source_generation!=g-1 || ev.write_after_generation!=g ||
      ev.logical_request_frame!=(uint64_t)g+2 || ev.expected_effect_generation!=g+2 ||
      !same_controls(&ev.controls,&rows[g-2]) || pending_count(&st)!=1) return 140+(int)g;
 }
 if(st.queued_generation!=27 || st.released_source_generation!=26 || st.failed || pending_count(&st)!=1) return 180;
 /* Indefinite ring reuse stress with a valid stable tuple. */
 e003i_cont_schedule_init(&st); c=cv(&rows[23]);
 for(uint32_t g=1;g<=100000;g++){
   if(e003i_cont_schedule_queue(&st,g,&c)) return 181;
   if(g>=2 && e003i_cont_schedule_release(&st,g,&ev)) return 182;
 }
 if(e003i_cont_schedule_release(&st,100001,&ev) || ev.source_generation!=100000 || st.failed || pending_count(&st)!=0) return 183;
 /* Missed release must collide rather than overwrite source G1. */
 e003i_cont_schedule_init(&st); c=cv(&rows[0]);
 if(e003i_cont_schedule_queue(&st,1,&c)) return 184;
 c=cv(&rows[1]); if(e003i_cont_schedule_queue(&st,2,&c)) return 185;
 c=cv(&rows[2]); if(e003i_cont_schedule_queue(&st,3,&c)!=-5 || !st.failed) return 186;
 /* Skipped queue generation fails closed. */
 e003i_cont_schedule_init(&st); c=cv(&rows[0]); if(e003i_cont_schedule_queue(&st,1,&c)) return 187;
 c=cv(&rows[2]); if(e003i_cont_schedule_queue(&st,3,&c)!=-3 || !st.failed) return 188;
 /* Release that skips the next source fails closed. */
 e003i_cont_schedule_init(&st); c=cv(&rows[0]); if(e003i_cont_schedule_queue(&st,1,&c)) return 189;
 c=cv(&rows[1]); if(e003i_cont_schedule_queue(&st,2,&c)) return 190;
 if(e003i_cont_schedule_release(&st,3,&ev)!=-4 || !st.failed) return 191;
 /* Invalid controls never enter the ring. */
 e003i_cont_schedule_init(&st); c=cv(&rows[0]); c.digital_gain_code=0;
 if(e003i_cont_schedule_queue(&st,1,&c)!=-4 || !st.failed) return 192;
 puts("GQ_GO_REPLAY=PASS G1_G27 BOUNDARY_RELEASES=26");
 puts("GQ_RING_STRESS=PASS GENERATIONS=100000");
 puts("GQ_FAIL_CLOSED=PASS");
 return 0;
}
'''.replace('ROWS','\n'.join(inits))
with tempfile.TemporaryDirectory(prefix='e003i-gq-') as td0:
    td=Path(td0); hp=td/'test.c'; exe=td/'test'; hp.write_text(harness)
    subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-I',str(HERE),'-I',str(CQ),'-I',str(CH),str(hp),str(HERE/'continuous-db-schedule.c'),'-lm','-o',str(exe)],check=True)
    out=subprocess.check_output([str(exe)],text=True)
    need('GQ_GO_REPLAY=PASS G1_G27 BOUNDARY_RELEASES=26' in out,'GO replay')
    need('GQ_RING_STRESS=PASS GENERATIONS=100000' in out,'stress')
    need('GQ_FAIL_CLOSED=PASS' in out,'fail closed')
    binary_sha=sha(exe)
# Timing headroom simulation: only an estimate using the worst of the three actually measured write calls.
max_start=max(x['start_after_boundary_ms'] for x in gp['live_write_observations'])
max_write=gp['observed_write_elapsed_ms']['maximum']
# GP first_six contains G1->G2 ... G6->G7; full intervals are recovered from RUN here.
b=[]
for m in re.finditer(r'POLL(\d+)_START_NS=(\d+) END_NS=(\d+) ELAPSED_NS=(\d+) RC=1 REVENTS=0x1',s): b.append((int(m.group(1))+1,int(m.group(3))))
interval={(g):(t2-t)/1e6 for (g,t),(g2,t2) in zip(b,b[1:])}
# A write after completed G uses the G->G+1 interval. Captured release windows G2..G26 have a following boundary.
est={str(g):interval[g]-max_start-max_write for g in range(2,27)}
need(min(est.values())>0,'observed worst-case write estimate crosses a captured boundary')
result={
 'schema':'sp11-e003i-gq-continuous-control-ring-scheduler-v1','status':'PASS_OFFLINE_CONTINUOUS_RING_SCHEDULER',
 'pending_slots':2,'stats_to_request_delay_generations':3,'write_after_offset_generations':1,'write_to_effect_delay_generations':2,
 'go_replay_generations':27,'go_replay_boundary_release_events':26,'go_replay_released_sources':list(range(1,27)),
 'effects_inside_go_capture_sources':list(range(1,25)),'effects_beyond_go_capture_sources':[25,26],
 'long_run_synthetic_generations':100000,'fail_closed_cases':['ring collision after missed release','skipped queue generation','skipped release source','invalid controls'],
 'conservative_observed_timing_estimate':{'max_live_start_after_boundary_ms':max_start,'max_live_write_elapsed_ms':max_write,'minimum_estimated_margin_ms':min(est.values()),'release_window_margins_ms':est,'is_live_proof':False},
 'continuous_scheduler_source_sha256':sha(HERE/'continuous-db-schedule.c'),'continuous_scheduler_header_sha256':sha(HERE/'continuous-db-schedule.h'),'unit_binary_sha256':binary_sha,
 'camera_runtime_performed':False,'live_authorized':False,'safe_next_step':'integrate ring scheduler into an offline helper replay with exact-boundary miss simulation before any live candidate'}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GQ_GO_REPLAY=PASS G1_G27 BOUNDARY_RELEASES=26')
print('GQ_RING_STRESS=PASS GENERATIONS=100000')
print('GQ_FAIL_CLOSED=PASS')
print(f"GQ_MIN_ESTIMATED_MARGIN_MS={min(est.values()):.6f}")
print('GQ_VERIFY=PASS')
