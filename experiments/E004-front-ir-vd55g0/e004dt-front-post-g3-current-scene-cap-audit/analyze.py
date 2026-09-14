#!/usr/bin/env python3
from pathlib import Path
import json,re
D=Path(__file__).resolve().parent
T=(D/'evidence/E004DS-FRONT-F1.txt').read_text(errors='replace')
CAP=6133333088
HA_CAP_ACTIVE=2; HA_UNCHANGED=3; HA_APPLY=4; HA_ALREADY=5
def need(v,m):
    if not v: raise AssertionError(m)
# Source G4..G24 are the only post-startup sources eligible for a bounded later write.
shadow_rx=r'HB_NATIVE_CAP_RELEASE_SHADOW SOURCE=(\d+) AFTER_G=(\d+) DECISION=(\d+) CONV=(\d+) CAP=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+)'
sh=[tuple(map(int,m.groups())) for m in re.finditer(shadow_rx,T)]
allow=[tuple(map(int,m.groups())) for m in re.finditer(r'HB_NATIVE_CAP_RELEASE_ALLOW SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) CONV=(\d+) CAP=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+)',T)]
policy_disabled=[m.group(0) for m in re.finditer(r'PROD_POST_G3_POLICY_SHADOW[^\n]*',T)]
horizon=[tuple(map(int,m.groups())) for m in re.finditer(r'HC_CAP_RELEASE_HORIZON_SHADOW SOURCE=(\d+) AFTER_G=(\d+) CONV=(\d+) CAP=(\d+) EFFECT_G=(\d+)',T)]
need([x[0] for x in sh]==list(range(4,25)),'expected G4..G24 decisions')
need(not allow,'unexpected native allow in shadow run')
need(not policy_disabled,'APPLY_ONE_NATIVE was reached but policy-disabled; this would be a real opportunity')
need([x[0] for x in horizon]==[25,26],'horizon')
for src,after,decision,conv,cap,fll,exp,ag,dg in sh:
    need(decision==HA_CAP_ACTIVE,f'G{src} decision {decision}')
    need(conv>=CAP and cap==CAP and cap!=conv,f'G{src} not cap-active conv={conv} cap={cap}')
mr=re.search(r'PROD_NATIVE_SCHEDULE_PASS ACCEPTED_G=1\.\.27 RELEASED_SOURCES=G1\.\.G26 POLICY=shadow CONTROL_IOCTLS=(\d+) LATER_NATIVE_WRITES=(\d+) LATER_SHADOW=(\d+) POLICY_DISABLED_SHADOW=(\d+) CAP_ACTIVE_SHADOW=(\d+) UNCHANGED_SHADOW=(\d+) ALREADY_APPLIED_SHADOW=(\d+) HORIZON_SHADOW=(\d+) PENDING=G27 APPLY_EFFECT_MAX=G27',T)
need(mr,'final accounting')
ci,lw,ls,pds,cas,us,aas,hs=map(int,mr.groups())
need((ci,lw,ls,pds,cas,us,aas,hs)==(3,0,23,0,21,0,0,2),'accounting '+repr((ci,lw,ls,pds,cas,us,aas,hs)))
# RELEASED_SOURCES is scheduler ownership release, not preview-cap release.
res={
 'schema':'sp11-camera-e004dt-current-scene-cap-audit-v1',
 'status':'PASS_CURRENT_SCENE_CAP_ACTIVE_NO_POST_G3_NATIVE_WRITE_OPPORTUNITY',
 'source_experiment':'E004ds',
 'preview_cap_max':CAP,
 'eligible_sources':list(range(4,25)),
 'eligible_source_count':21,
 'cap_active_sources':[x[0] for x in sh],
 'apply_one_native_sources':[],
 'policy_disabled_apply_sources':[],
 'horizon_shadow_sources':[25,26],
 'later_native_writes':0,
 'control_ioctls':3,
 'released_sources_semantics':'continuous delayed scheduler sources released G1..G26; not preview-cap release',
 'native_feedback_proof_possible_from_same_scene_evidence':False,
 'runtime_performed':False,
 'next_gate':'wait for a naturally brighter/changed scene that yields APPLY_ONE_NATIVE (decision 4 / PROD_POST_G3_POLICY_SHADOW under shadow policy), then use fresh cap-release-one-shot candidate; do not synthesize the condition'
}
(D/'RESULT.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
print('E004dt CAP AUDIT: PASS — G4..G24 all SHADOW_CAP_ACTIVE; no native-write opportunity')
print('E004dt NOTE: RELEASED_SOURCES=G1..G26 is scheduler release, not preview-cap release')
