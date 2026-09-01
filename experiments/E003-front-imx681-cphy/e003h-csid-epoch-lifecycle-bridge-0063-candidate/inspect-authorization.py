#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera'); N=R/'experiments/E003-front-imx681-cphy/e003h-csid-epoch-lifecycle-bridge-0063-candidate'; sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=json.load(open(N/'AUTHORIZATION.json')); r=json.load(open(N/'AUTHORIZATION-REVIEW.json')); p=json.load(open(N/'package-inspection.json')); m=json.load(open(N/'asset-manifest.json'))
assert a['accepted'] and a['runtime_authorized'] and not a['production_parity_authorized']; assert r['accepted'] and p['accepted'] and not p['runtime_authorized'] and m['accepted'] and not m['runtime_authorized']
assert a['authorization_review_sha256']==sha(N/'AUTHORIZATION-REVIEW.json') and a['package_inspection_sha256']==sha(N/'package-inspection.json') and a['asset_manifest_sha256']==sha(N/'asset-manifest.json') and a['bounded_provenance_sha256']==sha(R/'provenance/front-parity.json')
e=a['execution_contract']; assert e=={'boot_count':1,'root_helper_invocation_count':1,'same_boot_retry':False,'persistent_rtcdm_observer_required':True,'post_run_reboot':'immediate Golden','hardware_delta':'NONE','software_delta':'CSID_EPOCH_LIFECYCLE_BRIDGE_0063_ONLY'}
assert a['candidate']['new_mmio_reads']==a['candidate']['new_mmio_writes']==a['candidate']['new_register_values']==0
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(); subprocess.check_call(['git','-C',str(R),'merge-base','--is-ancestor',a['package_commit'],head])
env=subprocess.check_output(['grub-editenv','list'],text=True); assert 'saved_entry=sp11-audio-fullio-v19c' in env and 'next_entry=\n' in env
for x in ('RUNTIME-CSIDEPOCH-0063-RUN.txt','RUNTIME-CSIDEPOCH-0063-QC10C.bin'): assert not (N/x).exists()
print('PASS: 0063 authorization binds one boot/one helper/no retry/no hardware delta to the inspected package')
