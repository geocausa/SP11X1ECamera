#!/usr/bin/env python3
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
m=json.loads((HERE/'MANIFEST.json').read_text())
u=json.loads((BASE/'u-corrected-tlbg-runtime'/'TLBG-OFFLINE-ANALYSIS.json').read_text())
def need(v,msg):
    if not v: raise SystemExit('FAIL: '+msg)
need(m['status']=='PASS','manifest status')
need(m['offline_only'] and not m['runtime_performed'],'offline safety')
need(not m['source_generation_is_request_id'],'source generation mislabeled')
need(not m['dynamic_r5_r6_substitution_authorized'],'dynamic substitution accidentally authorized')
need(m['raw_authority_bytes']==0xF000 and m['parsed_bytes']==76832,'raw/parsed size')
need([x['generation'] for x in m['source_snapshots']]==[1,2,3,4,5,6],'generation sequence')
need([x['source_seq'] for x in m['source_snapshots']]==[1,2,3,4,5,6],'source sequence')
need([x['slot'] for x in m['source_snapshots']]==[0,1,0,1,0,1],'slot sequence')
for a,b in zip(m['source_snapshots'],u['snapshots']):
    for k in ('snapshot_sha256','raw_sha256','parsed_sha256'):
        need(a[k]==b[k],f'U evidence identity {a["generation"]} {k}')
need(set(m['trigger_fixtures'])=={'ratio_0p342_fixture','ratio_0p000_fixture'},'trigger fixtures')
for label,f in m['trigger_fixtures'].items():
    need(len(f['forward'])==6,'six forward outputs '+label)
    need(f['unique_forward_lsc0_outputs']==6,'live stats did not generate six distinct LSC0 '+label)
    need(f['forward'][-1]['lsc0_sha256']!=f['reverse_final_lsc0_sha256'],'order sensitivity '+label)
    need(len(f['counterfactual_cases'])==4,'counterfactual coverage '+label)
need(m['proofs']['hostile_initial_state_counterfactuals'],'counterfactual proof')
need(m['proofs']['trigger_state_is_separate_effective_input'],'trigger separability')
need(m['proofs']['trigger_fixture_changed_generations']==[1,2,3,4,5,6],'trigger sensitivity all generations')
s=(HERE/'prove-live-tlbg-clean-lsc.py').read_text()
for forbidden in ('/dev/video','VIDIOC_','ioctl(','reboot','grub-reboot'):
    need(forbidden not in s,'hardware/runtime primitive in offline proof: '+forbidden)
print('PASS: E003i-V live TL_BG -> clean LSC offline proof')
