#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
D=Path(__file__).resolve().parent;BASE=D.parent;REPO=D.parents[3]
HJ=BASE/'hj-package-install-repeated-stream-shadow-prep'

def need(v,m):
    if not v:raise AssertionError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
hj=json.loads((HJ/'RESULT.json').read_text());need(hj['status']=='PASS_OFFLINE_PACKAGE_INSTALL_STAGING','HJ parent')
menu=(D/'99zzzzzz_sp11_camera_e003i_hk_repeat_shadow_r27').read_text();need('sp11-camera-e003i-hk-repeat-shadow-r27-one-shot' in menu,'fresh id');need('sp11_camera_e003i_hk_repeat_shadow_r27=1' in menu,'cmdline marker')
need('sp11_camera_e003i_hc_caprelease_r27=1' not in menu,'HC marker reuse')
for f in ('prearm-check.sh','install-candidate.sh','arm-once.sh','runtime-preflight.sh','load.sh','invoke-twice.sh','golden-return-check.sh','retire-candidate.sh','archive.sh','finalize-archive.sh'):
    cp=subprocess.run(['bash','-n',str(D/f)],capture_output=True,text=True);need(cp.returncode==0,f+' syntax '+cp.stderr)
for f in ('verify.py','verify-two-streams.py'):
    cp=subprocess.run(['python3','-m','py_compile',str(D/f)],capture_output=True,text=True);need(cp.returncode==0,f+' compile '+cp.stderr)
launcher=(REPO/'src/front-imx681/bin/front-imx681-launcher.py').read_text();need("default='shadow'" in launcher,'launcher default shadow')
need('cap-release-one-shot' in launcher and '--allow-one-native-write' in launcher,'one-shot gate')
need(not (D/'runtime-output').exists(),'runtime output exists before arm')
result={'schema':'sp11-e003i-hk-repeated-stream-shadow-r27-prep-v1','status':'PREPARED_NOT_INSTALLED_REPEAT_SHADOW_R27','parent':'HJ package/install staging','candidate_id':'sp11-camera-e003i-hk-repeat-shadow-r27-one-shot','candidate_marker':'sp11_camera_e003i_hk_repeat_shadow_r27=1','streams_authorized_per_candidate':2,'frames_per_stream':27,'post_g3_policy':'shadow','post_g3_native_writes_authorized':0,'same_stream_retry_authorized':False,'production_artifacts':hj['build']['hashes'],'package_manifest_sha256':hj['package']['manifest_sha256'],'camera_runtime_performed':False,'candidate_installed':False,'candidate_armed':False,'golden_return_required':True,'next_gate':'install candidate unarmed, commit/push exact prep, then one-shot arm/reboot and exactly two sequential shadow streams'}
(D/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HK_PREP_VERIFY=PASS POLICY=shadow STREAMS=2 INSTALLED=NO ARMED=NO RUNTIME=NO')
