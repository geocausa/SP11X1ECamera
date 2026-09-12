#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
D=Path(__file__).resolve().parent;REPO=D.parents[3]
BOOT=Path('/boot/sp11-7.1.5-camera-e003i-hk-repeat-shadow-r27')
ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e003i_hk_repeat_shadow_r27')
ID='sp11-camera-e003i-hk-repeat-shadow-r27-one-shot'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sudo_sha(p):
    return subprocess.check_output(['sudo','-n','sha256sum',str(p)],text=True).split()[0]
def sudo_exists(p):
    return subprocess.run(['sudo','-n','test','-f',str(p)]).returncode==0
def need(v,m):
    if not v:raise AssertionError(m)
head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip();origin=subprocess.check_output(['git','-C',str(REPO),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip();need(head==origin,'origin mismatch')
need(sudo_exists(ENTRY) and sudo_sha(ENTRY)=='71a19c05dd66dd4f35bac9c6c1a13e51de14dd0ec1bd518e0fca451d93fd9299','entry hash')
want={
 'vmlinuz-7.1.5-sp11-render-parity-v4+':'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
 'initrd.img-7.1.5-sp11-camera-e003i-hk-repeat-shadow-r27':'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
 'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f'}
for n,h in want.items():need(sudo_exists(BOOT/n) and sudo_sha(BOOT/n)==h,n)
grub=subprocess.check_output(['sudo','-n','cat','/boot/grub/grub.cfg'],text=True);need(ID in grub,'grub id absent')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c' in env and not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines()),'grub env')
for m in ('qcom_camss','imx681','ov13858'):need(not Path('/sys/module',m).exists(),'module '+m)
need(not (D/'runtime-output').exists(),'runtime output before arm');need(not (D/'ARM.txt').exists(),'already armed')
r=json.loads((D/'RESULT.json').read_text())
r.update({'status':'INSTALLED_UNARMED_REPEAT_SHADOW_R27','candidate_installed':True,'candidate_armed':False,'camera_runtime_performed':False,'install_source_head':head,'boot_artifacts_sha256':want,'grub_entry_sha256':sudo_sha(ENTRY),'next_gate':'fresh prearm reconciliation then arm exactly one one-shot boot; exactly two shadow streams, no same-stream retry'})
(D/'RESULT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
print('HK_INSTALLED_VERIFY=PASS INSTALLED=YES ARMED=NO RUNTIME=NO')
