#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
N=R/'experiments/E003-front-imx681-cphy/e003h-live-requeue-0071-candidate'
S=R/'experiments/E003-front-imx681-cphy/e003h-live-requeue-0071-static'
B=R/'experiments/E003-front-imx681-cphy/e003h-five-frame-request5-0070r1-candidate/runtime-0070r1-analysis.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.load(open(N/'asset-manifest.json')); si=json.load(open(S/'0071-static-inspection.json')); b=json.load(open(B))
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(); origin=subprocess.check_output(['git','-C',str(R),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip(); assert head==origin
pkg='0305d211a26966f4f0a0a122155d3bb97754d9fe'; subprocess.check_call(['git','-C',str(R),'merge-base','--is-ancestor',pkg,head],stdout=subprocess.DEVNULL)
assert m['accepted'] and not m['runtime_authorized']; assert sha(S/'0071-static-inspection.json')==m['static_inspection_sha256']; assert si['accepted']; assert sha(B)==m['base_0070r1_analysis_sha256'] and b['accepted']
for r,h in m['assets'].items(): assert sha(N/r)==h,(r,sha(N/r),h)
env=subprocess.check_output(['grub-editenv','list'],text=True); assert 'saved_entry=sp11-audio-fullio-v19c\n' in env and not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines())
boot=Path('/boot/sp11-7.1.5-camera-e003h-requeue-0071'); entry=Path('/etc/grub.d/99y_sp11_camera_e003h_requeue_0071'); assert boot.is_dir() and entry.is_file()
assert sha(boot/'vmlinuz-7.1.5-sp11-render-parity-v4+')==m['golden_boot_identity']['vmlinuz_sha256']; assert sha(boot/'initrd.img-7.1.5-sp11-camera-e003h-requeue-0071')==m['golden_boot_identity']['initrd_sha256']; assert sha(boot/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')==m['assets']['x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb']
e=entry.read_text(); assert 'sp11-camera-e003h-requeue-0071-one-shot' in e and 'sp11_camera_e003h_requeue_0071=1' in e and 'systemd.unit=multi-user.target' in e
for x in ('AUTHORIZATION.json','RUNTIME-V4L2-0071-RUN.txt'): assert not (N/x).exists()
mods=subprocess.check_output(['bash','-lc',"for m in qcom_camss imx681 ov13858; do [ -d /sys/module/$m ] && echo $m; done; true"],text=True).strip(); assert not mods
out={'schema':'sp11-e003h-live-v4l2-requeue-0071-package-inspection-v1','accepted':True,'runtime_authorized':False,'package_commit':pkg,'head':head,'asset_manifest_sha256':sha(N/'asset-manifest.json'),'static_inspection_sha256':sha(S/'0071-static-inspection.json'),'base_0070r1_analysis_sha256':sha(B),'candidate_boot_installed':True,'candidate_boot_armed':False,'golden_saved_default':True,'camera_modules_loaded':False,'prior_run_present':False,'initial_qbuf_count':4,'expected_dqbuf_count':5,'expected_indices':[0,1,2,3,0],'live_requeue':True,'request6':False,'continuous_loop':False,'hardware_call_delta_from_0070':0,'same_boot_retry_refused':True,'mandatory_golden_reboot':True}
(N/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
