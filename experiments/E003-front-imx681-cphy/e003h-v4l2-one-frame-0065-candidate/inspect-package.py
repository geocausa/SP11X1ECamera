#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
N=R/'experiments/E003-front-imx681-cphy/e003h-v4l2-one-frame-0065-candidate'
S=R/'experiments/E003-front-imx681-cphy/e003h-v4l2-one-frame-0065-static'
B=R/'experiments/E003-front-imx681-cphy/e003h-csid-bufdone-video-0064-candidate/runtime-0064-analysis.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.load(open(N/'asset-manifest.json')); si=json.load(open(S/'0065-static-inspection.json')); b=json.load(open(B))
assert m['accepted'] and not m['runtime_authorized'] and si['accepted'] and not si['runtime_authorized'] and b['accepted']
for r,h in m['assets'].items(): assert sha(N/r)==h,(r,h,sha(N/r))
assert sha(S/'0065-static-inspection.json')==m['static_inspection_sha256']; assert sha(B)==m['base_0064_analysis_sha256']; assert si['module_sha256']==m['assets']['qcom-camss.ko']
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(); origin=subprocess.check_output(['git','-C',str(R),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip(); assert head==origin
pkg=subprocess.check_output(['git','-C',str(R),'log','-1','--format=%H','--',str(N/'asset-manifest.json')],text=True).strip(); assert pkg
subprocess.check_call(['git','-C',str(R),'merge-base','--is-ancestor',pkg,head],stdout=subprocess.DEVNULL)
env=subprocess.check_output(['grub-editenv','list'],text=True); assert 'saved_entry=sp11-audio-fullio-v19c\n' in env and not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines())
boot=Path('/boot/sp11-7.1.5-camera-e003h-v4l2one-0065'); entry=Path('/etc/grub.d/99y_sp11_camera_e003h_v4l2one_0065'); assert boot.is_dir() and entry.is_file()
assert sha(boot/'vmlinuz-7.1.5-sp11-render-parity-v4+')==m['golden_boot_identity']['vmlinuz_sha256']
assert sha(boot/'initrd.img-7.1.5-sp11-camera-e003h-v4l2one-0065')==m['golden_boot_identity']['initrd_sha256']
assert sha(boot/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')==m['assets']['x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb']
e=entry.read_text(); assert 'sp11-camera-e003h-v4l2one-0065-one-shot' in e and 'sp11_camera_e003h_v4l2one_0065=1' in e and 'systemd.unit=multi-user.target' in e and 'plymouth.enable=0' in e and 'modprobe.blacklist=qcom_camss,imx681,ov13858' in e
for mod in ('qcom_camss','imx681','ov13858'): assert not Path('/sys/module',mod).exists()
for f in ('AUTHORIZATION.json','RUNTIME-V4L2-0065-RUN.txt','RUNTIME-V4L2-0065-QC10C.bin'): assert not (N/f).exists()
d=si['delta']; assert d['hardware_delta']=='NONE' and d['new_mmio_reads']==d['new_mmio_writes']==d['new_register_values']==0 and d['generic_x1e_pix_one_wm_guard_retained'] and d['qbuf_count_exact']==2
out={'schema':'sp11-e003h-v4l2-one-frame-0065-package-inspection-v1','accepted':True,'runtime_authorized':False,'package_commit':pkg,'head':head,'asset_manifest_sha256':sha(N/'asset-manifest.json'),'static_inspection_sha256':sha(S/'0065-static-inspection.json'),'base_0064_analysis_sha256':sha(B),'candidate_boot_installed':True,'candidate_boot_armed':False,'golden_saved_default':True,'camera_modules_loaded':False,'prior_run_present':False,'delta':d,'module_sha256':m['assets']['qcom-camss.ko'],'dtb_unchanged_from_0064':True,'sensor_unchanged_from_0064':True,'firmware_unchanged_from_0064':True,'v4l2_helper_sha256':m['assets']['e003h-v4l2-one-frame'],'one_v4l2_helper_invocation_enforced':True,'sysfs_trigger_invocations':0,'same_boot_retry_refused':True,'mandatory_golden_reboot':True,'unsafe_dma_pin_preserved_until_reboot':True}
(N/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
