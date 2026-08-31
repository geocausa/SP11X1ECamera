#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,subprocess
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera'); N=R/'experiments/E003-front-imx681-cphy/e003h-vfe1-ubwc-static-0061-candidate'; P='ae29aa203f80d7544ae186fd6286df05b6eb3253'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest(); cmd=lambda a:subprocess.check_output(a,text=True,stderr=subprocess.DEVNULL).strip()
a=json.loads((N/'AUTHORIZATION.json').read_text()); r=json.loads((N/'AUTHORIZATION-REVIEW.json').read_text()); p=json.loads((N/'package-inspection.json').read_text()); m=json.loads((N/'asset-manifest.json').read_text()); checks={}
checks['public_package']=cmd(['git','-C',str(R),'rev-parse','HEAD'])==P==cmd(['git','-C',str(R),'rev-parse','origin/experiment/e003-front-imx681-cphy'])
checks['review_bound']=r['reviewed_public_package_commit']==P and a['package_commit']==P
checks['hashes']=a['package_inspection_sha256']==sha(N/'package-inspection.json') and a['asset_manifest_sha256']==sha(N/'asset-manifest.json') and a['authorization_review_sha256']==sha(N/'AUTHORIZATION-REVIEW.json') and a['bounded_provenance_sha256']==sha(R/'provenance/front-parity.json')
checks['policy']=a['accepted'] and a['runtime_authorized'] and not a['production_parity_authorized']
e=a['execution_contract']; checks['contract']=e['boot_count']==1 and e['root_helper_invocation_count']==1 and e['same_boot_retry'] is False and e['persistent_rtcdm_observer_required'] and e['post_run_reboot']=='immediate Golden' and e['hardware_delta']=='VFE1_UBWC_STATIC_0061_ONLY'
c=a['candidate']; checks['delta']=p['new_mmio_writes']==1 and p['new_direct_mmio_reads']==0 and c['new_mmio_writes']==1 and c['new_direct_mmio_reads']==0 and c['write_offset']=='0x0c58' and c['write_value']=='0x00001046' and c['camera_programming_delta_only_ubwc_static'] and c['retains_0060_readonly_telemetry']
forbidden=['any register write other than published BUS +0xc58=0x00001046','IRQ event substitution','second helper invocation','same-boot retry']; checks['forbidden']=all(x in a['forbidden_programming'] for x in forbidden)
env=cmd(['grub-editenv','list']).splitlines(); checks['safe']='saved_entry=sp11-audio-fullio-v19c' in env and not any(x.startswith('next_entry=') and x!='next_entry=' for x in env) and not (N/'RUNTIME-VFEUBWC-0061-RUN.txt').exists() and all(not Path('/sys/module/'+x).exists() for x in ('qcom_camss','imx681','ov13858'))
assert all(checks.values()),checks
out={'schema':'sp11-e003h-vfeubwc-0061-authorization-inspection-v1','accepted':True,'package_commit':P,'authorization_sha256':sha(N/'AUTHORIZATION.json'),'authorization_review_sha256':sha(N/'AUTHORIZATION-REVIEW.json'),'package_inspection_sha256':sha(N/'package-inspection.json'),'checks':checks,'runtime_authorized':True,'candidate_boot_armed':False}
(N/'AUTHORIZATION-INSPECTION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); print('INSPECTION_SHA='+sha(N/'AUTHORIZATION-INSPECTION.json'))
