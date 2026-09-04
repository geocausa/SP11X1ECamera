#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,pathlib,subprocess
HERE=pathlib.Path(__file__).resolve().parent
REPO=HERE.parents[2]
BOOT=pathlib.Path('/boot/sp11-7.1.5-camera-e003h-request6-0074')
ENTRY=pathlib.Path('/etc/grub.d/99y_sp11_camera_e003h_request6_0074')
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-static/0074-static-inspection.json'
BASE=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-candidate/runtime-0072-analysis.json'
ATOMIC=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/atomic-runtime-capsules-manifest.json'
OUT=HERE/'package-inspection.json'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise RuntimeError(m)
m=json.loads((HERE/'asset-manifest.json').read_text()); s=json.loads(STATIC.read_text()); b=json.loads(BASE.read_text()); a=json.loads(ATOMIC.read_text())
need(m['accepted'] and not m['runtime_authorized'],'asset manifest state')
need(s['accepted'] and not s['runtime_authorized'] and not s['request6_runtime_authorized'],'static state')
need(b['accepted'] and b['execution']['golden_return_verified'],'0072 base')
need(a['accepted'],'atomic manifest')
for r,h in m['assets'].items(): need(sha(HERE/r)==h,f'asset drift {r}')
need(BOOT.is_dir(),'candidate boot directory absent'); need(ENTRY.is_file(),'candidate GRUB entry absent')
entry=ENTRY.read_text()
need('sp11-camera-e003h-request6-0074-one-shot' in entry,'GRUB id drift')
need('sp11_camera_e003h_request6_0074=1' in entry,'GRUB marker drift')
need(f'firmware_class.path={HERE}/firmware' in entry,'firmware path drift')
env=subprocess.check_output(['grub-editenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env or env.strip()=='saved_entry=sp11-audio-fullio-v19c','Golden saved default drift')
need(not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines()),'candidate already armed')
for mod in ('qcom_camss','imx681','ov13858'): need(not pathlib.Path('/sys/module',mod).exists(),f'module loaded: {mod}')
for i in range(6): need(not (HERE/f'RUNTIME-V4L2-0074-QC10C-{i}.bin').exists(),'prior output present')
for name in ('RUNTIME-V4L2-0074-RUN.txt','RUNTIME-V4L2-0074-RTCDM-STAGES.txt','RUNTIME-V4L2-0074-WATCHER.ready'):
    need(not (HERE/name).exists(),f'prior runtime present: {name}')
head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
origin=subprocess.check_output(['git','-C',str(REPO),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip()
need(head==origin,'repo not pushed')
bootfiles={
 'vmlinuz':BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+',
 'initrd':BOOT/'initrd.img-7.1.5-sp11-camera-e003h-request6-0074',
 'dtb':BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb',
}
for p in bootfiles.values(): need(p.is_file(),f'boot asset missing {p}')
need(sha(bootfiles['dtb'])==m['assets']['x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'],'boot DTB drift')
result={
 'schema':'sp11-e003h-six-frame-request6-0074-package-inspection-v1',
 'accepted':True,'runtime_authorized':False,'request6':True,
 'package_commit':head,
 'candidate_boot_installed':True,'candidate_boot_armed':False,'golden_saved_default':True,
 'camera_modules_loaded':False,'prior_run_present':False,'same_boot_retry_refused':True,'mandatory_golden_reboot':True,
 'expected_indices':[0,1,2,3,0,1],'expected_sequences':[0,1,2,3,4,5],
 'live_requeue_indices':[0,1],'provider_dequeue_ids':[5,6],
 'hardware_delta_from_0072':'EXACTLY_ONE_STEADY_REQUEST6_PLUS_SLOT1_REBIND_AND_SECOND_LIVE_REQUEUE',
 'asset_manifest_sha256':sha(HERE/'asset-manifest.json'),
 'static_inspection_sha256':sha(STATIC),'base_0072_runtime_sha256':sha(BASE),'atomic_manifest_sha256':sha(ATOMIC),
 'boot_hashes':{k:sha(v) for k,v in bootfiles.items()},
}
OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2,sort_keys=True))
