#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent;BASE=D.parent;REPO=D.parents[3]
HV=BASE/'hv-current-golden-camera-dtb-merge';HS=BASE/'hs-production-install-rollback-contract'
def need(v,m):
    if not v:raise AssertionError(m)
hv=json.loads((HV/'RESULT.json').read_text());hs=json.loads((HS/'RESULT.json').read_text());r=json.loads((D/'RESULT.json').read_text())
need(hv['status']=='PASS_OFFLINE_CURRENT_GOLDEN_CAMERA_DTB_MERGE','HV parent');need(hs['status']=='PASS_OFFLINE_PRODUCTION_INSTALL_ROLLBACK_CONTRACT','HS parent')
need(hv['merged_dtb_sha256']==r['hv_merged_dtb_sha256'],'HV hash');need(hs['runtime_package_manifest_sha256']==r['production_package_manifest_sha256'],'package hash')
menu=(D/'99zzzzzz_sp11_camera_e003i_hw_prod_activation').read_text();gold=subprocess.check_output(['sudo','-n','cat','/etc/grub.d/76_sp11_audio_fullio_v19c'],text=True)
def linux_args(txt):
    line=next(x.strip() for x in txt.splitlines() if x.strip().startswith('linux '));parts=line.split();return parts[1],parts[2:]
gpath,gargs=linux_args(gold);cpath,cargs=linux_args(menu)
need(gpath=='/boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+','Golden linux path')
need(cpath=='/boot/sp11-7.1.5-camera-e003i-hw-prod-activation/vmlinuz-7.1.5-sp11-render-parity-v4+','candidate linux path')
normalized=[]
for x in cargs:
    if x in ('modprobe.blacklist=qcom_camss,imx681,ov13858','sp11_camera_e003i_hw_prod_activation=1'):continue
    if x=='sp11_entry=7.1.5-sp11-camera-e003i-hw-prod-activation':x='sp11_entry=7.1.5-sp11-fullio-v19c'
    normalized.append(x)
need(normalized==gargs,'Golden cmdline semantic drift')
need('firmware_class.path=' not in menu,'legacy firmware path')
need('sp11-camera-e003i-hw-prod-activation-one-shot' in menu and 'sp11_camera_e003i_hw_prod_activation=1' in menu,'fresh identity')
need('x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb' in menu,'HV DTB')
for f in ('prearm-check.sh','install-candidate.sh','arm-once.sh','runtime-preflight.sh','load.sh','golden-return-check.sh','retire-candidate.sh'):
    cp=subprocess.run(['bash','-n',str(D/f)],text=True,capture_output=True);need(cp.returncode==0,f+' syntax '+cp.stderr)
cp=subprocess.run(['shellcheck','-x','-S','warning',*[str(p) for p in sorted(D.glob('*.sh'))]],text=True,capture_output=True);need(cp.returncode==0,'shellcheck '+cp.stdout+cp.stderr)
for f in ('verify.py','verify-installed.py'):
    cp=subprocess.run(['python3','-m','py_compile',str(D/f)],text=True,capture_output=True);need(cp.returncode==0,f+' compile '+cp.stderr)
critical='\n'.join((D/f).read_text() for f in ('prearm-check.sh','install-candidate.sh','arm-once.sh','runtime-preflight.sh','load.sh'))
for stale in ('sp11-camera-e003i-hq-four-stream-shadow-r27-one-shot','sp11_camera_e003i_hq_four_stream_shadow_r27=1'):
    need(stale not in critical,'stale identity/path '+stale)
need('front-imx681-discover.py" --json' in (D/'load.sh').read_text(),'discovery activation')
need('front-imx681-launcher.py' not in (D/'load.sh').read_text(),'stream launcher must not execute')
need(r['status']=='PREPARED_NOT_INSTALLED_PRODUCTION_ACTIVATION' and r['candidate_installed'] is False and r['candidate_armed'] is False,'prep lifecycle')
need(r['stream_authorized'] is False and r['camera_runtime_performed'] is False and r['same_boot_retry_authorized'] is False,'authority')
print('HW_STATIC_VERIFY=PASS STATUS='+r['status']+' GOLDEN_CMDLINE_PRESERVED=YES STREAM_AUTHORIZED=NO')
