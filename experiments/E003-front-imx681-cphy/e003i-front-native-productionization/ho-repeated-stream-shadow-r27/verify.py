#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent; BASE=D.parent; REPO=D.parents[3]; HN=BASE/'hn-snapshot-generation-reset-package'
def need(v,m):
    if not v: raise AssertionError(m)
hn=json.loads((HN/'RESULT.json').read_text()); need(hn['status']=='PASS_OFFLINE_SNAPSHOT_GENERATION_RESET_PACKAGE','HN parent')
need(hn['build']['hashes']['qcom-camss.ko']=='7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95','HN CAMSS')
need(hn['package']['manifest_sha256']=='8a2bf3116a9b37fbe4b213dae51cb0ff33968e591ff54c8235c36341607c32cf','HN package')
menu=(D/'99zzzzzz_sp11_camera_e003i_ho_repeat_shadow_r27').read_text(); need('sp11-camera-e003i-ho-repeat-shadow-r27-one-shot' in menu,'fresh id'); need('sp11_camera_e003i_ho_repeat_shadow_r27=1' in menu,'marker')
for f in ('prearm-check.sh','install-candidate.sh','arm-once.sh','runtime-preflight.sh','load.sh','invoke-twice.sh','test-invoke-harness.sh','golden-return-check.sh','retire-candidate.sh','archive.sh','finalize-archive.sh'):
    cp=subprocess.run(['bash','-n',str(D/f)],capture_output=True,text=True); need(cp.returncode==0,f+' syntax '+cp.stderr)
for f in ('verify.py','verify-two-streams.py'):
    cp=subprocess.run(['python3','-m','py_compile',str(D/f)],capture_output=True,text=True); need(cp.returncode==0,f+' compile '+cp.stderr)
sh=sorted(str(p) for p in D.glob('*.sh')); cp=subprocess.run(['shellcheck','-x','-S','warning',*sh],capture_output=True,text=True); need(cp.returncode==0,'shellcheck '+cp.stdout+cp.stderr)
cp=subprocess.run([str(D/'test-invoke-harness.sh')],capture_output=True,text=True); need(cp.returncode==0 and 'HO_INVOKE_HARNESS_SELFTEST=PASS' in cp.stdout,'harness '+cp.stdout+cp.stderr)
critical='\n'.join((D/f).read_text() for f in ('prearm-check.sh','install-candidate.sh','arm-once.sh','runtime-preflight.sh','load.sh','invoke-twice.sh','golden-return-check.sh','retire-candidate.sh'))
for forbidden in ('sp11-camera-e003i-hl-repeat-shadow-r27-one-shot','sp11_camera_e003i_hl_repeat_shadow_r27=1','/hl-repeated-stream-shadow-r27','sp11-camera-e003i-hk-repeat-shadow-r27-one-shot'):
    need(forbidden not in critical,'retired identity leak '+forbidden)
video=(REPO/'src/front-imx681/kernel/camss/camss-video.c').read_text(); need('video->x1e_3a_generation = 0;' in video and 'video->x1e_tlbg_generation = 0;' in video,'generation reset source')
r=json.loads((D/'RESULT.json').read_text())
static={'schema':'sp11-e003i-ho-repeated-stream-shadow-r27-prep-v1','parent':'HN snapshot-generation reset package','candidate_id':'sp11-camera-e003i-ho-repeat-shadow-r27-one-shot','candidate_marker':'sp11_camera_e003i_ho_repeat_shadow_r27=1','streams_authorized_per_candidate':2,'frames_per_stream':27,'post_g3_policy':'shadow','post_g3_native_writes_authorized':0,'same_stream_retry_authorized':False,'same_boot_retry_authorized':False,'snapshot_generation_reset_fix':True,'hn_camss_module_sha256':'7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95','hn_package_manifest_sha256':'8a2bf3116a9b37fbe4b213dae51cb0ff33968e591ff54c8235c36341607c32cf'}
for k,v in static.items(): need(r.get(k)==v,'RESULT '+k)
allowed=('PREPARED_NOT_INSTALLED_REPEAT_SHADOW_R27','INSTALLED_UNARMED_REPEAT_SHADOW_R27','PASS_CAPTURE_HO_TWO_STREAM_SHADOW_R27_GOLDEN_RESTORED_RETIRED','FAIL_HO_GOLDEN_RESTORED_RETIRED')
need(r.get('status') in allowed,'status')
if r['status']=='PREPARED_NOT_INSTALLED_REPEAT_SHADOW_R27': need(r.get('candidate_installed') is False and r.get('camera_runtime_performed') is False and not (D/'runtime-output').exists(),'prep lifecycle')
if r['status']=='INSTALLED_UNARMED_REPEAT_SHADOW_R27': need(r.get('candidate_installed') is True and r.get('camera_runtime_performed') is False and not (D/'runtime-output').exists(),'installed lifecycle')
print('HO_STATIC_VERIFY=PASS STATUS='+r['status'])
