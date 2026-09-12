#!/usr/bin/env python3
from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent;BASE=D.parent
HX=BASE/'hx-production-one-stream-acceptance-policy'
def need(v,m):
    if not v:raise AssertionError(m)
hx=json.loads((HX/'RESULT.json').read_text());r=json.loads((D/'RESULT.json').read_text())
need(hx['status']=='PASS_OFFLINE_PRODUCTION_ONE_STREAM_ACCEPTANCE_POLICY','HX parent')
need(hx['future_candidate_stream_count']==1 and hx['frames']==27 and hx['post_g3_policy']=='shadow' and hx['post_g3_native_writes']==0,'HX contract')
menu=(D/'99zzzzzz_sp11_camera_e003i_hy_prod_stream_r27').read_text();gold=subprocess.check_output(['sudo','-n','cat','/etc/grub.d/76_sp11_audio_fullio_v19c'],text=True)
def linux_args(txt):
    line=next(x.strip() for x in txt.splitlines() if x.strip().startswith('linux '));parts=line.split();return parts[1],parts[2:]
_,gargs=linux_args(gold);cpath,cargs=linux_args(menu);need(cpath=='/boot/sp11-7.1.5-camera-e003i-hy-prod-stream-r27/vmlinuz-7.1.5-sp11-render-parity-v4+','candidate linux path')
normalized=[]
for x in cargs:
    if x in ('modprobe.blacklist=qcom_camss,imx681,ov13858','sp11_camera_e003i_hy_prod_stream_r27=1'):continue
    if x=='sp11_entry=7.1.5-sp11-camera-e003i-hy-prod-stream-r27':x='sp11_entry=7.1.5-sp11-fullio-v19c'
    normalized.append(x)
need(normalized==gargs,'Golden cmdline semantic drift');need('firmware_class.path=' not in menu,'legacy firmware path')
for f in ('prearm-check.sh','install-candidate.sh','arm-once.sh','runtime-preflight.sh','load.sh','invoke-one.sh','archive.sh','finalize-archive.sh','golden-return-check.sh','retire-candidate.sh'):
    cp=subprocess.run(['bash','-n',str(D/f)],capture_output=True,text=True);need(cp.returncode==0,f+' syntax '+cp.stderr)
cp=subprocess.run(['shellcheck','-x','-S','warning',*[str(p) for p in sorted(D.glob('*.sh'))]],capture_output=True,text=True);need(cp.returncode==0,'shellcheck '+cp.stdout+cp.stderr)
for f in ('verify.py','verify-installed.py','verify-live.py'):
    cp=subprocess.run(['python3','-m','py_compile',str(D/f)],capture_output=True,text=True);need(cp.returncode==0,f+' compile '+cp.stderr)
critical='\n'.join((D/f).read_text() for f in ('runtime-preflight.sh','load.sh','invoke-one.sh'))
need('sp11_camera_e003i_hy_prod_stream_r27=1' in critical,'fresh token');need('--post-g3-write-policy shadow' in critical,'explicit shadow');need('cap-release-one-shot' not in critical,'cap release leaked')
need('ATTEMPT1-CONSUMED.marker' in (D/'invoke-one.sh').read_text(),'consumed marker');need((D/'invoke-one.sh').read_text().count('front-imx681-launcher.py')==1,'single launcher site')
static={'candidate_id':'sp11-camera-e003i-hy-prod-stream-r27-one-shot','candidate_marker':'sp11_camera_e003i_hy_prod_stream_r27=1','stream_count':1,'frames':27,'post_g3_policy':'shadow','post_g3_native_writes_authorized':0,'same_stream_retry_authorized':False,'same_boot_retry_authorized':False,'hv_merged_dtb_sha256':'34880dc20d349bf966ebf62d6d8bb3f0130f436c88d9e4838585624a869e04c7','production_package_manifest_sha256':'57aa9cc2ad85131881416d7795603ab777a70e7c5877828986ff279266a5a757'}
for k,v in static.items():need(r.get(k)==v,'RESULT '+k)
need(r.get('status') in ('PREPARED_NOT_INSTALLED_PRODUCTION_ONE_STREAM_R27','INSTALLED_UNARMED_PRODUCTION_ONE_STREAM_R27','PASS_CAPTURE_HY_PRODUCTION_ONE_STREAM_R27_GOLDEN_RESTORED_RETIRED','FAIL_HY_GOLDEN_RESTORED_RETIRED'),'status')
if r['status']=='PREPARED_NOT_INSTALLED_PRODUCTION_ONE_STREAM_R27':need(r.get('candidate_installed') is False and r.get('candidate_armed') is False and r.get('camera_runtime_performed') is False,'prep lifecycle')
print('HY_STATIC_VERIFY=PASS STATUS='+r['status']+' STREAMS=1 POLICY=shadow RETRY=NO')
