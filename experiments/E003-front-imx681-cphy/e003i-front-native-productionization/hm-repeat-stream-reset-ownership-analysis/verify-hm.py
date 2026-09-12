#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
HL=HERE.parent/'hl-repeated-stream-shadow-r27'
ARCH=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-hl/attempt1-stream2-repeat-state-failure-20260912T075406')
VIDEO=REPO/'src/front-imx681/kernel/camss/camss-video.c'
CAMSS=REPO/'src/front-imx681/kernel/camss/camss.c'
CSID=REPO/'src/front-imx681/kernel/camss/camss-csid-680.c'
CAP=REPO/'src/front-imx681/userspace/runtime/front-imx681-production-capture.c'
PROD=REPO/'src/front-imx681/userspace/iq/live-iq-producer.py'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def body(text,name):
    m=re.search(r'void\s+'+re.escape(name)+r'\([^)]*\)\s*\{(.*?)\n\}',text,re.S)
    need(m,name+' body'); return m.group(1)
video=VIDEO.read_text(); camss=CAMSS.read_text(); csid=CSID.read_text(); cap=CAP.read_text(); prod=PROD.read_text()
# Snapshot reset ownership: open/release call reset, but reset omits generation zeroing.
for fn,gen in [('camss_x1e_3a_reset','x1e_3a_generation'),('camss_x1e_tlbg_reset','x1e_tlbg_generation')]:
    b=body(video,fn)
    need(gen not in b,fn+' unexpectedly resets generation before HN')
    need(re.search(r'video->'+re.escape(gen)+r'\+\+',video),gen+' publish increment missing')
need(video.count('camss_x1e_3a_reset(video);')>=2,'3A open/release reset calls')
need(video.count('camss_x1e_tlbg_reset(video);')>=2,'TLBG open/release reset calls')
# Producer requires each fresh live session to begin at generation one.
need('self.next_generation=1' in prod,'producer generation baseline')
need("need(i3[0]==target,f'missed 3A generation {target}, now {i3[0]}')" in prod,'3A strict generation guard')
# Runtime evidence.
r1=(ARCH/'runtime-output/RUN1.txt').read_text(errors='replace')
r2=(ARCH/'runtime-output/RUN2.txt').read_text(errors='replace')
need(r1.count('DQBUF')>=27 and 'E003I_GM_PRODUCER=PASS' in r1 and 'STREAMOFF_OK' in r1,'stream1 authority')
need('E003I_GM_PRODUCER=FAIL RuntimeError: missed 3A generation 1, now 28' in r2,'stream2 stale generation')
need('DQBUF0_INDEX=0' in r2 and 'DQBUF1_INDEX=1' in r2 and 'DQBUF2_INDEX=2' in r2,'stream2 first three completions')
need('GN_DQBUF_MISMATCH LOOP=3 EXPECT_INDEX=3 EXPECT_BYTES=7778304 EXPECT_SEQUENCE=3 ACTUAL_INDEX=3 ACTUAL_BYTES=7778304 ACTUAL_SEQUENCE=0' in r2,'stream2 error-buffer mismatch')
# Causal ordering: frame3 completes, then request5 is demanded before frame4 can complete.
pos_f3=camss.index('camss_x1e_pix_v4l2_complete_live(result, req->video[2], 2);')
pos_r5=camss.index('camss_x1e_pix_iq_provider_next_steady(\n\t\t\t\tcamss, req->live_video, 5')
pos_f4=camss.index('camss_x1e_pix_v4l2_complete_live(result, req->video[3], 3);')
need(pos_f3 < pos_r5 < pos_f4,'frame3/request5/frame4 ordering')
# On failure after only three completions video3 is returned as ERROR, and error completion does not assign sequence.
need('if (result.live_completed < 4)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(video3);' in camss,'video3 fail completion')
err=body(camss,'camss_x1e_pix_v4l2_error_buffer')
need('vb2_buffer_done' in err and '.sequence' not in err,'error buffer sequence semantics')
need('b.sequence != i' in cap and 'pin_until_reboot("unexpected completed buffer ordering")' in cap,'capture strict mismatch gate')
# CSID software counters have a dedicated reset epoch in csid_reset; HL does not prove they were stale.
for field in ('x1e_ipp_epoch0_count','x1e_buf_done_video_count','x1e_buf_done_aec_bhist_count','x1e_buf_done_tintless_count','x1e_buf_done_awb_count','x1e_buf_done_rs_count'):
    need(re.search(r'csid->'+field+r'\s*=\s*0;',csid),field+' reset missing')
need('ret = csid->res->hw_ops->reset(csid);' in (REPO/'src/front-imx681/kernel/camss/camss-csid.c').read_text(),'CSID power-on reset call')
result={
 'schema':'sp11-e003i-hm-repeat-stream-reset-ownership-v1',
 'status':'PASS_OFFLINE_REPEAT_STREAM_RESET_OWNERSHIP',
 'parent':'HL repeat-stream attempt 1 failure',
 'camera_runtime_performed':False,
 'hl_archive_manifest_sha256':'ecd96ac7390a8bb873f57555bcdefb70dce92773ff4eaadb0dd954c4b85aebb5',
 'root_cause':{
   'component':'CAMSS front PIX exported 3A/TLBG snapshot generation state',
   'bug':'camss_x1e_3a_reset and camss_x1e_tlbg_reset clear payload/source/slot/valid but leave generation counters unchanged',
   'stream1_last_generation':27,
   'stream2_first_generation_observed':28,
   'producer_expected_generation':1,
 },
 'secondary_failure':{
   'dqbuf_sequence_mismatch_is_independent_reset_bug':False,
   'causal_chain':['producer rejects stale G28 while waiting for G1','no R5 capsule is submitted','runner completes frames 1..3 then blocks/fails waiting for request5 before frame4 completion','uncompleted video3 is returned with VB2_BUF_STATE_ERROR without assigning sequence','capture sees buffer index3 sequence0 and pins fail-closed'],
 },
 'csid_counter_conclusion':'source has explicit software-counter zeroing in csid_reset; HL supplies no independent evidence of stale CSID completion generations',
 'required_fix':['set x1e_3a_generation=0 in camss_x1e_3a_reset under its lock','set x1e_tlbg_generation=0 in camss_x1e_tlbg_reset under its lock'],
 'required_regression':['two logical sessions each publish first snapshot as generation1','reset preserves invalid-until-publish behavior','producer strict generation contract unchanged','no live runtime until rebuilt module/package authority passes'],
 'source_sha256':{'camss-video.c':sha(VIDEO),'camss.c':sha(CAMSS),'camss-csid-680.c':sha(CSID),'front-imx681-production-capture.c':sha(CAP),'live-iq-producer.py':sha(PROD)},
 'next_gate':'HN implement snapshot-generation reset and prove rebuilt production package offline'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HM_ROOT_CAUSE=PASS STALE_SNAPSHOT_GENERATION=27_TO_28')
print('HM_DQBUF_CAUSALITY=PASS SECONDARY_ERROR_BUFFER_NOT_INDEPENDENT_SEQUENCE_RESET')
print('HM_CSID_STALE_EVIDENCE=NO')
print('HM_VERIFY=PASS')
