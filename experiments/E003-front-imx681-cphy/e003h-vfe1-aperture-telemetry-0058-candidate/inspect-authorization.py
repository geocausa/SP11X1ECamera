#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera'); NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-aperture-telemetry-0058-candidate'
PKG_COMMIT='cc0abdbac4d0adc0066efa3dbd627f2be68a69d6'
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cmd(a): return subprocess.check_output(a,text=True,stderr=subprocess.DEVNULL).strip()
def die(s): raise SystemExit('FAIL: '+s)
a=json.loads((NEW/'AUTHORIZATION.json').read_text()); r=json.loads((NEW/'AUTHORIZATION-REVIEW.json').read_text()); p=json.loads((NEW/'package-inspection.json').read_text()); m=json.loads((NEW/'asset-manifest.json').read_text())
checks={}
checks['package_public']=cmd(['git','-C',str(REPO),'rev-parse','origin/experiment/e003-front-imx681-cphy'])==PKG_COMMIT==cmd(['git','-C',str(REPO),'rev-parse','HEAD'])
checks['review_public_commit_bound']=r['reviewed_public_package_commit']==PKG_COMMIT
checks['package_hash_bound']=a['package_inspection_sha256']==r['package_inspection_sha256']==sha(NEW/'package-inspection.json')
checks['manifest_hash_bound']=a['asset_manifest_sha256']==r['asset_manifest_sha256']==sha(NEW/'asset-manifest.json')
checks['review_hash_bound']=a['authorization_review_sha256']==sha(NEW/'AUTHORIZATION-REVIEW.json')
checks['authorization_policy']=a['accepted'] and a['runtime_authorized'] and not a['production_parity_authorized']
e=a['execution_contract']; checks['one_boot']=e['boot_count']==1; checks['one_helper']=e['root_helper_invocation_count']==1; checks['no_retry']=e['same_boot_retry'] is False
checks['dual_observers']=e['persistent_rtcdm_observer_required'] is True and e['persistent_vfe_aperture_observer_required'] is True
checks['zero_camera_delta']=e['hardware_delta']=='NONE_VS_CONSUMED_0057_READ_ONLY_VFE_APERTURE_TELEMETRY' and p['camera_programming_delta']=='none_vs_0057' and m['behavior_delta']['new_mmio_writes']==0
checks['external_read_only']=p['external_vfe_aperture_read_only'] is True and a['candidate']['vfe_aperture_access']=='read_only'
env=cmd(['grub-editenv','list']).splitlines(); checks['golden_saved']='saved_entry=sp11-audio-fullio-v19c' in env; checks['unarmed']=not any(x.startswith('next_entry=') and x!='next_entry=' for x in env)
checks['modules_absent']=all(not Path('/sys/module/'+x).exists() for x in ('qcom_camss','imx681','ov13858'))
checks['run_absent']=not (NEW/'RUNTIME-VFEAP-0058-RUN.txt').exists()
if not all(checks.values()): die(str({k:v for k,v in checks.items() if not v}))
out={'schema':'sp11-e003h-vfeap-0058-authorization-inspection-v1','accepted':True,'package_commit':PKG_COMMIT,'package_inspection_sha256':sha(NEW/'package-inspection.json'),'asset_manifest_sha256':sha(NEW/'asset-manifest.json'),'authorization_review_sha256':sha(NEW/'AUTHORIZATION-REVIEW.json'),'authorization_sha256':sha(NEW/'AUTHORIZATION.json'),'checks':checks,'runtime_authorized':True,'candidate_boot_armed':False}
(NEW/'AUTHORIZATION-INSPECTION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); print('AUTH_INSPECTION_SHA256='+sha(NEW/'AUTHORIZATION-INSPECTION.json'))
