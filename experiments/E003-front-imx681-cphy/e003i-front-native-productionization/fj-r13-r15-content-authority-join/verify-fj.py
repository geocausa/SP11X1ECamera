#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;B=H.parent
def load(name): return json.loads((B/name/'RESULT.json').read_text())
def need(v,m):
    if not v: raise AssertionError(m)
fg=load('fg-r13-r15-continuation-authority')
fh=load('fh-recovered-windows-r18-awb-oracle')
fi=load('fi-windows-r4-r15-tintless-lsc-oracle')
eb=load('eb-windows-r4-r12-gtm-state-oracle')
need(fg['status']=='PASS_OFFLINE_R13_R15_COMPOSABLE_AUTHORITY_OPEN','FG')
need(fg['r5_r12_live_regression']=='8/8 exact FF live capsule hashes','FG regression')
need(fg['r13_r15_deterministic']=='3/3 two-run capsule hashes exact','FG deterministic')
need(fh['status']=='PASS_RECOVERED_WINDOWS_R4_R18_AWB_15_OF_15_BIT_EXACT','FH')
need(fh['requests']==list(range(4,19)) and fh['recovered_requests']==list(range(13,19)),'FH coverage')
need(fi['status']=='PASS_WINDOWS_ORACLE_CLEANROOM_REPLAY','FI')
need(fi['requests']==list(range(4,16)) and fi['clean_lsc_replay']=='12/12 byte-exact LSC0/LSC1/LSC2/GIC','FI coverage')
need(eb['status']=='PASS_WINDOWS_ORACLE' and eb['post_r6_gtm_output_law']=='stable','EB GTM law')
out={
 'schema':'sp11-e003i-fj-r13-r15-content-authority-join-v1',
 'status':'PASS_OFFLINE_R13_R15_CONTENT_AUTHORIZED',
 'requests':[13,14,15],
 'producer_composability':'FG deterministic R13-R15 from immutable FF G10-G12 continuation inputs',
 'awb_authority':'FH recovered same-stream Windows R4-R18 15/15 bit-exact',
 'lsc_tintless_authority':'FI Windows R4-R15 clean-room 12/12 byte-exact',
 'gtm_authority':'EB post-R6 stable Windows output law',
 'ff_live_regression':'FG reproduces FF R5-R12 capsules 8/8 byte-exact',
 'r13_r15_capsule_sha256':fg['r13_r15_capsule_sha256'],
 'windows_whole_capsule_same_scene':False,
 'component_differential_authority':True,
 'linux_camera_runtime_performed':False,
 'continuous_aec_claimed':False,
 'next_gate':'extend gain publisher to G12, integrate R5-R15 producer, and extend bounded transport to 15 frames offline before any fresh Linux live candidate'
}
(H/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
