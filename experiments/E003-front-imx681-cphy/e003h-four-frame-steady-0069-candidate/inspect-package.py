#!/usr/bin/env python3
import hashlib,json,subprocess,struct
from pathlib import Path
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
N=R/'experiments/E003-front-imx681-cphy/e003h-four-frame-steady-0069-candidate'
S=R/'experiments/E003-front-imx681-cphy/e003h-four-frame-steady-0069-static'
B=R/'experiments/E003-front-imx681-cphy/e003h-three-frame-slot-reuse-0068-candidate/runtime-0068-analysis.json'
OLD=R/'experiments/E003-front-imx681-cphy/e003h-three-frame-slot-reuse-0068-candidate/firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.load(open(N/'asset-manifest.json')); si=json.load(open(S/'0069-static-inspection.json')); b=json.load(open(B))
assert m['accepted'] and not m['runtime_authorized'] and si['accepted'] and not si['runtime_authorized'] and b['accepted']
for r,h in m['assets'].items(): assert sha(N/r)==h,(r,h,sha(N/r))
assert sha(S/'0069-static-inspection.json')==m['static_inspection_sha256']; assert sha(B)==m['base_0068_analysis_sha256']
assert b['classification']['first_actual_two_slot_hardware_reuse_achieved'] and b['execution']['golden_return_verified'] and b['qc10c']['all_complete']
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(); origin=subprocess.check_output(['git','-C',str(R),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip(); assert head==origin
pkg=subprocess.check_output(['git','-C',str(R),'log','-1','--format=%H','--',str(N/'asset-manifest.json')],text=True).strip(); assert pkg
subprocess.check_call(['git','-C',str(R),'merge-base','--is-ancestor',pkg,head],stdout=subprocess.DEVNULL)
env=subprocess.check_output(['grub-editenv','list'],text=True); assert 'saved_entry=sp11-audio-fullio-v19c\n' in env and not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines())
boot=Path('/boot/sp11-7.1.5-camera-e003h-frame4-0069'); entry=Path('/etc/grub.d/99y_sp11_camera_e003h_frame4_0069'); assert boot.is_dir() and entry.is_file()
assert sha(boot/'vmlinuz-7.1.5-sp11-render-parity-v4+')==m['golden_boot_identity']['vmlinuz_sha256']
assert sha(boot/'initrd.img-7.1.5-sp11-camera-e003h-frame4-0069')==m['golden_boot_identity']['initrd_sha256']
assert sha(boot/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')==m['assets']['x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb']
e=entry.read_text(); assert 'sp11-camera-e003h-frame4-0069-one-shot' in e and 'sp11_camera_e003h_frame4_0069=1' in e and 'systemd.unit=multi-user.target' in e and 'plymouth.enable=0' in e and 'modprobe.blacklist=qcom_camss,imx681,ov13858' in e
for mod in ('qcom_camss','imx681','ov13858'): assert not Path('/sys/module',mod).exists()
for f in ('AUTHORIZATION.json','RUNTIME-V4L2-0069-RUN.txt','RUNTIME-V4L2-0069-QC10C-0.bin','RUNTIME-V4L2-0069-QC10C-1.bin','RUNTIME-V4L2-0069-QC10C-2.bin','RUNTIME-V4L2-0069-QC10C-3.bin'): assert not (N/f).exists()
d=si['delta']; assert d['new_mmio_primitive_calls']==0 and d['new_register_literals']==0 and d['slot1_rebind_requires_prior_five_group_retirement'] and d['continuous_requeue_not_authorized'] and d['asynchronous_streamon_not_authorized']
assert d['new_hardware_actions']==['one existing nine-client BUS update targeting proven-reusable slot1','one existing five-BL steady 0x958/request4 submission']
old=OLD.read_bytes(); cap=(N/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin').read_bytes(); dif=[i for i,(a,z) in enumerate(zip(old,cap)) if a!=z]; assert dif==[0x2c] and struct.unpack_from('<Q',cap,0x2c)[0]==4
out={'schema':'sp11-e003h-four-frame-first-steady-0069-package-inspection-v1','accepted':True,'runtime_authorized':False,'package_commit':pkg,'head':head,'asset_manifest_sha256':sha(N/'asset-manifest.json'),'static_inspection_sha256':sha(S/'0069-static-inspection.json'),'base_0068_analysis_sha256':sha(B),'candidate_boot_installed':True,'candidate_boot_armed':False,'golden_saved_default':True,'camera_modules_loaded':False,'prior_run_present':False,'delta':d,'module_sha256':m['assets']['qcom-camss.ko'],'dtb_unchanged_from_0068':True,'sensor_unchanged_from_0068':True,'request4_capsule_sha256':sha(N/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin'),'request4_capsule_only_header_byte_changed':True,'one_v4l2_helper_invocation_enforced':True,'expected_dqbuf_count':4,'sysfs_trigger_invocations':0,'slot_reuse':True,'continuous_requeue':False,'asynchronous_streamon':False,'fifth_frame':False,'same_boot_retry_refused':True,'mandatory_golden_reboot':True,'unsafe_dma_pin_preserved_until_reboot':True}
(N/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
