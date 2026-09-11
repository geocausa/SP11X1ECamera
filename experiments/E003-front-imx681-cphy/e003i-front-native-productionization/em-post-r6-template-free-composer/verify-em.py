#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json,sys
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('em',HERE/'compose_em.py');em=importlib.util.module_from_spec(s);sys.modules['em']=em;s.loader.exec_module(em)
def need(x,m):
    if not x: raise AssertionError(m)
rows=em.replay_ea();need([r['request'] for r in rows]==[7,8,9],'request mapping')
# EA G4-G6 all carry the same CQ residual gain and held AWB decision.
for r in rows:
    need(r['isp_gain_bits']=='0x3f801646',f"R{r['request']} ISP")
    need(r['decision_bits']==['0x3f1129ca','0x3f00e486'],f"R{r['request']} held XY")
    need(r['demux_regs']==['0x04270427','0x04280427'],f"R{r['request']} Demux")
    need(r['gtm_sha256']==em.GTM_SHA,f"R{r['request']} GTM")
    need(r['section_count']==36 and r['capsule_bytes']==41088,f"R{r['request']} shape")
    need(r['section_sha256'][0]['sha256']=='076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560','PDPC0 invariant')
    need(r['section_sha256'][3]['sha256']=='6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e','LSC2 invariant')
    need(r['section_sha256'][5]['sha256']=='c48a9ca4c0431ee4d98b78f9c59858a53adacd5604c88bd0c7f591ff2858e6ed','BPC_ABF invariant')
# LSC/GIC must evolve with sequential Tintless state even though all scalar AEC/AWB controls are steady.
for idx in (1,2,4):need(len({r['section_sha256'][idx]['sha256'] for r in rows})==3,f'{idx} must evolve R7-R9')
# Bank parity and module recurrence: R7/R9 same module, R8 opposite parity.
need(rows[0]['module_sha256']==rows[2]['module_sha256'] and rows[0]['module_sha256']!=rows[1]['module_sha256'],'module parity recurrence')
for r in rows:
    even=(r['request']%2)==0
    for ro in ('0x3d58','0x3d5c','0x4358','0x435c','0x4758','0x475c','0x4958','0x495c','0xa058','0xa05c','0xa258','0xa25c'):
        need(r['bank_regs'][ro]==(1 if even else 0),f"R{r['request']} bank {ro}")
    for ro in ('0x5a58','0x5a5c','0x5f58','0x5f5c'):
        need(r['bank_regs'][ro]==(0 if even else 1),f"R{r['request']} inverse bank {ro}")
# Exact deterministic hashes become the offline regression baseline for the next bounded candidate.
expected={7:'681f17d83d289fba57548241bbb7db4219afbfde48495d680de969274720ea2e',8:'79804d678235f53429e4690c0d5e4a905873edde6652f002c878e2fad8634d2e',9:'1bd2e7cd98eb6ebc6c4161a34b3b8c72343d6e69232b11346f65496f79e33fda'}
for r in rows:need(r['capsule_sha256']==expected[r['request']],f"R{r['request']} deterministic capsule")
out={'schema':'sp11-e003i-em-post-r6-template-free-composer-v1','status':'PASS_OFFLINE_R7_R9_COMPOSITION','capsule_template_reads_r7_r9':0,
 'requests':[7,8,9],'source_generations':[4,5,6],'ea_live_stats_replayed':True,'sequential_tintless_state':True,
 'demux_source':'EA generation-tagged CQ residual ISP gain via DV','awb_scalar_source':'EL calibrated GainAdj -> PDPC/WB',
 'gtm_source':'EB R6-R12 byte-stable payload','lsc_source':'DS DynamicLsc algorithm proven 9/9 by ED, driven by EA G1-G6',
 'invariant_dmi_source':'R6 only for indices proven identical R4/R5/R6','request_bank_parity':'derived R4-R6 and consistent EB/ED',
 'windows_full_capsule_r7_r9_differential':False,'linux_camera_runtime_performed':False,'continuous_aec_claimed':False,'rows':rows}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2))
