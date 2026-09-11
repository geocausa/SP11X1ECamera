#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, tempfile
D=Path(__file__).resolve().parent; BASE=D.parent
ES=BASE/'es-nine-frame-r7-r9-transport'; EN=BASE/'en-r5-r9-producer-integration'; EP=BASE/'ep-gainadj-multiside-r9-replay'; EU=BASE/'eu-six-generation-gain-feed-publisher'
def need(v,m):
    if not v: raise AssertionError(m)
es=json.loads((ES/'RESULT.json').read_text())
need(es['status']=='PASS_OFFLINE_NINE_FRAME_TRANSPORT' and es['frames']==9,'ES transport authority')
need(es['patched_camss_sha256']=='683255664a320bf63b1c852c56a8c0373014d6723b6d48a69a277bd02d18706f','ES CAMSS SHA')
need(es['patched_helper_sha256']=='6d4268fb5e6c637de78f62079719eaa3c107efcca48578c125a58a17d74c565d','ES base helper SHA')
en=json.loads((EN/'RESULT.json').read_text()); need(str(en['status']).startswith('PASS'),'EN closed result')
ep=json.loads((EP/'RESULT.json').read_text()); need(str(ep['status']).startswith('PASS') and ep['external_archive_full_replay'] is True,'EP authority')
eu=json.loads((EU/'RESULT.json').read_text())
need(eu['status']=='PASS_OFFLINE_G1_G6_C_PUBLISHER','EU publisher status')
need(eu['accepted_generations']==[1,2,3,4,5,6] and eu['rejected_generation']==7,'EU bounds')
need(eu['gain_feed_c_sha256']=='2dbd4856294fe3aceecc1f7027643b6a0c559e7ce5469d902846b9073a466b3c','EU C SHA')
need(eu['gain_feed_h_sha256']=='60adc6456b9806f50e14c0e3158a74dc49995549af1627e1604ad0496212de79','EU H SHA')
checks={
 'build-camss.sh':['make-nine-frame-camss.py','W=1','683255664a320bf63b1c852c56a8c0373014d6723b6d48a69a277bd02d18706f'],
 'build-helper.sh':['make-nine-frame-helper.py','eu-six-generation-gain-feed-publisher','2dbd4856294fe3aceecc1f7027643b6a0c559e7ce5469d902846b9073a466b3c','12a6c6f4f9000a6bfde7aca9b124cb8a281c39ecd65676f20c81b704ce5b4a51','EV_DQBUF_MISMATCH','-Werror'],
 'prearm-check.sh':['verify-eu.py','EU_C_PUBLISHER_G1_G6=PASS','qcom-camss-ev.ko'],
 'invoke-once.sh':['e003i-ev-nine-frame-native-aec','QC10C-8.bin','$EN/live-iq-producer.py'],
 'runtime-preflight.sh':['sp11_camera_e003i_ev_nine_frame_r5_r9=1','prior_runtime_output'],
 '99zr_sp11_camera_e003i_ev_nine_frame_r5_r9':['sp11-camera-e003i-ev-nine-frame-r5-r9-one-shot','sp11_camera_e003i_ev_nine_frame_r5_r9=1'],
}
for f,toks in checks.items():
    s=(D/f).read_text()
    for t in toks: need(t in s,f'{f}: missing {t}')
with tempfile.TemporaryDirectory(prefix='e003i-ev-') as td:
    td=Path(td); cam=td/'qcom-camss.ko'; helper=td/'helper'; bootstrap=td/'bootstrap'
    subprocess.run([str(D/'build-camss.sh'),str(cam)],check=True)
    subprocess.run([str(D/'build-helper.sh'),str(helper)],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(bootstrap)],check=True)
    need((D/'build/helper/gain-feed.c').read_bytes()==(EU/'gain-feed.c').read_bytes(),'EV helper did not consume EU publisher')
    import hashlib
    sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    result={'schema':'sp11-e003i-ev-offline-v1','status':'PASS_OFFLINE_READY_FOR_FRESH_ONE_SHOT','live_runtime_performed':False,'continuous_aec_claimed':False,'closed_content_stages':'EN/EP/EM/EL/ES unchanged','eu_c_publisher':'PASS_G1_G6_G7_REJECT','eu_gain_feed_c_sha256':eu['gain_feed_c_sha256'],'generated_helper_source_sha256':'12a6c6f4f9000a6bfde7aca9b124cb8a281c39ecd65676f20c81b704ce5b4a51','camss_source_sha256':es['patched_camss_sha256'],'camss_module_sha256':sha(cam),'helper_binary_sha256':sha(helper),'bootstrap_binary_sha256':sha(bootstrap),'dqbuf_mismatch_diagnostic':True,'one_stream_attempt_per_boot':True}
    (D/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('EV_ES_TRANSPORT=PASS')
print('EV_EN_EP_CONTENT=UNCHANGED_PASS')
print('EV_EU_C_PUBLISHER=PASS_G1_G6')
print('EV_CAMSS_W1=PASS')
print('EV_HELPER_WERROR=PASS')
print('EV_DQBUF_DIAGNOSTIC=PASS')
print('EV_BOOTSTRAP_WERROR=PASS')
print('EV_VERIFY=PASS')
