#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
D=Path(__file__).resolve().parent;R=D.parents[2]
def need(v,m):
    if not v:raise AssertionError(m)
r=json.loads((D/'RESULT.json').read_text());need(r['status']=='PASS_CANONICAL_OFFLINE_PROTECTED_WORKER_EXACT_TRUST_BLOCK_UNCHANGED','status')
subprocess.run(['python3',str(R/'src/sp11-camera-protected-worker/verify-source.py')],check=True,stdout=subprocess.DEVNULL)
need('GAUSSIAN_WIRE_FULL_LUMA_DIFF=0' in (D/'evidence/FULLFRAME-DIFFERENTIAL.txt').read_text(),'luma')
need('GAUSSIAN_WIRE_NEUTRAL_TAIL_DIFF=0' in (D/'evidence/FULLFRAME-DIFFERENTIAL.txt').read_text(),'tail')
need('E004dj shipped-proxy call contract: PASS' in (D/'evidence/PROXY-CONTRACT.txt').read_text(),'proxy')
need('E004dj Gaussian-wire vectors: PASS' in (D/'evidence/WIRE-VECTORS.txt').read_text(),'vectors')
expected={'dsc_verify_buffer','get_secure_channel_handle','qurt_sleep','secure_pd_mapping_create_64','secure_pd_mapping_delete_64','secure_pd_mb_delete','secure_pd_mb_get','secure_pd_mb_receive','secure_pd_mb_send','secure_pd_thread_create'}
actual={x.split()[-1] for x in (D/'evidence/UNRESOLVED.txt').read_text().splitlines() if x.strip()};need(actual==expected,'unresolved')
need((D/'evidence/HEXAGON-OBJECT.sha256').read_text().split()[0]=='4d413d54fb29d898b0a662edcc957eb02ccf4769e7036aa4c986b0c8be6afc48','object hash')
for rel,status in (
 ('e004de-cpz-securepd-worker-trust-admission-feasibility','PASS_NO_AUTHORIZED_SOURCE_CONTROLLED_CPZ_WORKER_ADMISSION_PATH'),
 ('e004df-parity-worker-admission-alternatives-closure','PASS_CPZ_IS_ONLY_PARITY_SHAPED_BACKEND_RUNTIME_BLOCKED_ON_WORKER_TRUST_ADMISSION'),
 ('e004dj-securepd-native-binding','PASS_OFFLINE_NATIVE_SECUREPD_BINDING_REUSES_SHIPPED_PROXY_WINDOWS_EXACT')):
    j=json.loads((R/'experiments/E004-front-ir-vd55g0'/rel/'RESULT.json').read_text());need(j['status']==status,rel)
need(r['trust']=={'signed':False,'production_admitted':False,'runtime_authorized':False,'verification_bypass_allowed':False},'trust')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0'):need(not Path('/sys/module',m).exists(),'loaded '+m)
print('E004ea VERIFY: PASS (canonical protected worker exact; offline/unadmitted only)')
