#!/usr/bin/env python3
import hashlib, json, pathlib, subprocess, sys
R=pathlib.Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
D=R/'experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0076-longpoll-candidate'
sha=lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=json.load(open(D/'MANIFEST.json')); c=json.load(open(D/'CONTRACT.json')); a=json.load(open(D/'AUTHORIZATION.json'))
assert m['accepted'] and m['delta']=='HELPER_POLL_1S_TO_5S_PLUS_TIMESTAMPS_ONLY' and m['request6']
assert c['accepted'] and c['helper_invocations']==1 and c['same_boot_retry'] is False
assert a['accepted'] and a['runtime_authorized'] and a['request6'] and a['helper_invocations']==1 and a['same_boot_retry'] is False
assert a['manifest_sha256']==sha(D/'MANIFEST.json') and a['contract_sha256']==sha(D/'CONTRACT.json')
for k,p in m['asset_paths'].items():
    assert sha(R/p)==m['asset_sha256'][k], (k,p)
r=json.load(open(R/m['atomic_r45_control_result_path']))
assert r['accepted'] and r['classification']=='ATOMIC_R4_R5_CLEARED_ON_ACCEPTED_0072_FIVE_FRAME_RUNTIME'
assert sha(R/m['atomic_r45_control_result_path'])==m['atomic_r45_control_result_sha256']
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()
origin=subprocess.check_output(['git','-C',str(R),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip()
assert head==origin
print('VERIFY_0076=PASS')
