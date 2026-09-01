#!/usr/bin/env python3
import hashlib,json,pathlib,subprocess
R=pathlib.Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera'); N=R/'experiments/E003-front-imx681-cphy/e003h-five-frame-request5-0070-candidate'; S=R/'experiments/E003-front-imx681-cphy/e003h-request5-exact-oracle-0070-static'; B=R/'experiments/E003-front-imx681-cphy/e003h-four-frame-steady-0069r1-candidate/runtime-0069r1-analysis.json'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); m=json.load(open(N/'asset-manifest.json')); si=json.load(open(S/'0070-static-inspection.json')); wo=json.load(open(S/'WINDOWS-REQUEST5-ORACLE.json')); b=json.load(open(B))
assert m['accepted'] and not m['runtime_authorized']; assert si['accepted'] and wo['accepted'] and b['accepted']
for r,h in m['assets'].items(): assert sha(N/r)==h
assert sha(S/'0070-static-inspection.json')==m['static_inspection_sha256']; assert sha(S/'WINDOWS-REQUEST5-ORACLE.json')==m['windows_request5_oracle_sha256']; assert sha(B)==m['base_0069r1_analysis_sha256']
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(); origin=subprocess.check_output(['git','-C',str(R),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip(); assert head==origin
subprocess.check_call(['git','-C',str(R),'merge-base','--is-ancestor',m['static_commit'],head],stdout=subprocess.DEVNULL)
env=subprocess.check_output(['grub-editenv','list'],text=True); assert 'saved_entry=sp11-audio-fullio-v19c\n' in env and not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines())
boot=pathlib.Path('/boot/sp11-7.1.5-camera-e003h-frame5-0070'); entry=pathlib.Path('/etc/grub.d/99y_sp11_camera_e003h_frame5_0070'); assert boot.is_dir() and entry.is_file()
assert sha(boot/'vmlinuz-7.1.5-sp11-render-parity-v4+')==m['golden_boot_identity']['vmlinuz_sha256']; assert sha(boot/'initrd.img-7.1.5-sp11-camera-e003h-frame5-0070')==m['golden_boot_identity']['initrd_sha256']; assert sha(boot/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')==m['assets']['x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb']
e=entry.read_text(); assert m['boot']['id'] in e and m['boot']['marker'] in e and 'systemd.unit=multi-user.target' in e and 'modprobe.blacklist=qcom_camss,imx681,ov13858' in e
for mod in ('qcom_camss','imx681','ov13858'): assert not pathlib.Path('/sys/module',mod).exists()
for x in ('AUTHORIZATION.json','RUNTIME-V4L2-0070-RUN.txt'): assert not (N/x).exists()
out={'schema':'sp11-e003h-five-frame-request5-0070-package-inspection-v1','accepted':True,'runtime_authorized':False,'package_commit':head,'head':head,'asset_manifest_sha256':sha(N/'asset-manifest.json'),'static_inspection_sha256':sha(S/'0070-static-inspection.json'),'windows_request5_oracle_sha256':sha(S/'WINDOWS-REQUEST5-ORACLE.json'),'base_0069r1_analysis_sha256':sha(B),'candidate_boot_installed':True,'candidate_boot_armed':False,'golden_saved_default':True,'camera_modules_loaded':False,'prior_run_present':False,'expected_dqbuf_count':5,'slot_reuse':True,'continuous_requeue':False,'asynchronous_streamon':False,'request5':True,'same_boot_retry_refused':True,'mandatory_golden_reboot':True,'authorized_hardware_actions':m['behavior_delta']['authorized_hardware_actions']}
(N/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
