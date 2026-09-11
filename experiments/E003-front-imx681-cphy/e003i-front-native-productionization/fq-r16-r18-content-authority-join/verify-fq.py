#!/usr/bin/env python3
from pathlib import Path
import json

H=Path(__file__).resolve().parent
B=H.parent

def load(name):
    return json.loads((B/name/'RESULT.json').read_text())

def need(v,m):
    if not v:
        raise AssertionError(m)

fo=load('fo-r16-r18-continuation-authority')
fh=load('fh-recovered-windows-r18-awb-oracle')
fp=load('fp-windows-r4-r18-tintless-lsc-oracle')
eb=load('eb-windows-r4-r12-gtm-state-oracle')

need(fo['status']=='PASS_OFFLINE_R16_R18_COMPOSABLE_LSC_AUTHORITY_OPEN','FO')
need(fo['r5_r15_live_regression']=='11/11 exact FN live capsule hashes','FO live regression')
need(fo['r16_r18_deterministic']=='3/3 two-run capsule hashes exact','FO deterministic')
need(fo['awb_windows_authority_through_request']==18,'FO AWB boundary')
need(fo['lsc_windows_authority_through_request']==15,'FO pre-FP LSC boundary')

need(fh['status']=='PASS_RECOVERED_WINDOWS_R4_R18_AWB_15_OF_15_BIT_EXACT','FH')
need(fh['requests']==list(range(4,19)) and fh['recovered_requests']==list(range(13,19)),'FH coverage')

need(fp['status']=='PASS_WINDOWS_ORACLE_CLEANROOM_REPLAY','FP')
need(fp['requests']==list(range(4,19)),'FP coverage')
need(fp['clean_lsc_replay']=='15/15 byte-exact LSC0/LSC1/LSC2/GIC','FP replay')

need(eb['status']=='PASS_WINDOWS_ORACLE' and eb['post_r6_gtm_output_law']=='stable','EB GTM law')

out={
  'schema':'sp11-e003i-fq-r16-r18-content-authority-join-v1',
  'status':'PASS_OFFLINE_R16_R18_CONTENT_AUTHORIZED',
  'requests':[16,17,18],
  'producer_composability':'FO deterministic R16-R18 from immutable FN G13-G15 continuation inputs',
  'awb_authority':'FH recovered same-stream Windows R4-R18 15/15 bit-exact',
  'lsc_tintless_authority':'FP Windows R4-R18 clean-room 15/15 byte-exact',
  'gtm_authority':'EB post-R6 stable Windows output law',
  'fn_live_regression':'FO reproduces real FN R5-R15 capsules 11/11 byte-exact',
  'r16_r18_capsule_sha256':fo['r16_r18_capsule_sha256'],
  'windows_whole_capsule_same_scene':False,
  'component_differential_authority':True,
  'linux_camera_runtime_performed':False,
  'continuous_aec_claimed':False,
  'next_gate':'extend compiled gain publisher through G15, integrate R5-R18 producer, and extend bounded transport to 18 frames offline before any fresh Linux live candidate'
}

(H/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
