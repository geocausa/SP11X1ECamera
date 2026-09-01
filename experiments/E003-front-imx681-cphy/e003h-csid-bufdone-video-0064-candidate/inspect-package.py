#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
N=R/'experiments/E003-front-imx681-cphy/e003h-csid-bufdone-video-0064-candidate'
S=R/'experiments/E003-front-imx681-cphy/e003h-csid-bufdone-video-0064-static'
B=R/'experiments/E003-front-imx681-cphy/e003h-csid-epoch-lifecycle-bridge-0063-candidate/runtime-0063-analysis.json'
STATIC='a27ea8a22957413e7a2b1e96e989412074547a78'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.load(open(N/'asset-manifest.json')); si=json.load(open(S/'0064-static-inspection.json')); b=json.load(open(B))
assert m['accepted'] and not m['runtime_authorized'] and si['accepted'] and not si['runtime_authorized'] and b['accepted']
for r,h in m['assets'].items(): assert sha(N/r)==h,(r,h,sha(N/r))
assert sha(S/'0064-static-inspection.json')==m['static_inspection_sha256']
assert sha(B)==m['base_0063_analysis_sha256']
assert si['module_sha256']==m['assets']['qcom-camss.ko']
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()
origin=subprocess.check_output(['git','-C',str(R),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip(); assert head==origin
subprocess.check_call(['git','-C',str(R),'merge-base','--is-ancestor',STATIC,head])
env=subprocess.check_output(['grub-editenv','list'],text=True); assert 'saved_entry=sp11-audio-fullio-v19c\n' in env and not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines())
boot=Path('/boot/sp11-7.1.5-camera-e003h-csidvideo-0064'); entry=Path('/etc/grub.d/99y_sp11_camera_e003h_csidvideo_0064'); assert boot.is_dir() and entry.is_file()
assert sha(boot/'vmlinuz-7.1.5-sp11-render-parity-v4+')=='bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a'
assert sha(boot/'initrd.img-7.1.5-sp11-camera-e003h-csidvideo-0064')=='ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d'
assert sha(boot/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')==m['assets']['x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb']
e=entry.read_text(); assert 'sp11-camera-e003h-csidvideo-0064-one-shot' in e and 'sp11_camera_e003h_csidvideo_0064=1' in e and 'systemd.unit=multi-user.target' in e and 'plymouth.enable=0' in e and 'modprobe.blacklist=qcom_camss,imx681,ov13858' in e
for mod in ('qcom_camss','imx681','ov13858'): assert not Path('/sys/module',mod).exists()
for f in ('AUTHORIZATION.json','RUNTIME-CSIDVIDEO-0064-RUN.txt','RUNTIME-CSIDVIDEO-0064-QC10C.bin'): assert not (N/f).exists()
d=si['delta']; assert d['hardware_delta']=='NONE' and d['new_mmio_reads']==d['new_mmio_writes']==d['new_register_values']==0 and not d['new_hardware_programming'] and d['existing_csid_buf_done_read_reused'] and d['windows_video_bit']=='bit0' and d['old_vfe_video_poll_removed_from_runner'] and d['epoch_bridge_0063_retained'] and d['bus_slot1_retarget_retained'] and d['prime2_retained']
assert b['execution']['golden_return_verified'] and b['classification']['first_linux_qc10c_dma_completion_achieved'] and b['classification']['full_frame_not_achieved'] and b['classification']['premature_video_completion_is_current_boundary']
out={'schema':'sp11-e003h-csid-bufdone-video-0064-package-inspection-v1','accepted':True,'runtime_authorized':False,'package_commit':head,'head':head,'asset_manifest_sha256':sha(N/'asset-manifest.json'),'static_inspection_sha256':sha(S/'0064-static-inspection.json'),'base_0063_analysis_sha256':sha(B),'candidate_boot_installed':True,'candidate_boot_armed':False,'golden_saved_default':True,'camera_modules_loaded':False,'prior_run_present':False,'delta':d,'module_sha256':m['assets']['qcom-camss.ko'],'dtb_unchanged_from_0063':True,'sensor_unchanged_from_0063':True,'helper_unchanged_from_0063':True,'firmware_unchanged_from_0063':True,'single_helper_invocation_enforced':True,'same_boot_retry_refused':True,'mandatory_golden_reboot':True}
(N/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
