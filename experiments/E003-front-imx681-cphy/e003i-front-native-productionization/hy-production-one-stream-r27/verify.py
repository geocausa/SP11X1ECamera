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
if r['status']=='PREPARED_NOT_INSTALLED_PRODUCTION_ONE_STREAM_R27':
    need(r.get('candidate_installed') is False and r.get('candidate_armed') is False and r.get('camera_runtime_performed') is False,'prep lifecycle')
if r['status']=='INSTALLED_UNARMED_PRODUCTION_ONE_STREAM_R27':
    need(r.get('candidate_installed') is True and r.get('candidate_armed') is False and r.get('camera_runtime_performed') is False,'installed lifecycle')
    need((D/'INSTALL.txt').is_file() and not (D/'ARM.txt').exists() and not (D/'runtime-output').exists(),'installed evidence')
if r['status']=='PASS_CAPTURE_HY_PRODUCTION_ONE_STREAM_R27_GOLDEN_RESTORED_RETIRED':
    need(r.get('candidate_installed') is False and r.get('candidate_retired') is True and r.get('one_shot_boot_consumed') is True,'pass lifecycle')
    need(r.get('stream_attempts')==1 and r.get('streams_completed')==1 and r.get('frames')==27,'pass stream count')
    need(r.get('first_snapshot_generation')==1 and r.get('producer_generations')==24 and r.get('producer_requests')==23,'pass producer')
    need(r.get('startup_native_writes')==3 and r.get('post_g3_native_writes')==0 and r.get('hardware_control_transactions_including_bootstrap')==4,'pass write authority')
    need(r.get('streamoff_count')==1 and r.get('kernel_health')=='PASS' and r.get('golden_return')=='PASS','pass health')
    need(r.get('same_stream_retry_performed') is False and r.get('same_boot_retry_performed') is False,'pass retry')
    need(r.get('archive_manifest_sha256')=='e411c04ad30f9b4c9816aa6743ccf137e4a8e552dec4ef2f34a761755008ca63','pass archive')
    need(r.get('production_stream_on_current_golden_merge_proven') is True and r.get('production_native_changed_post_g3_feedback_proven') is False,'pass proof scope')
    for f in ('ATTEMPT1-PASS.json','ATTEMPT1-CONSUMED.marker','ARM.txt','DISCOVERY.json','POST.txt','GOLDEN-RETURN.txt','RETIRE.txt'):
        need((D/f).is_file(),'pass evidence '+f)
print('HY_STATIC_VERIFY=PASS STATUS='+r['status']+' STREAMS=1 POLICY=shadow RETRY=NO')
