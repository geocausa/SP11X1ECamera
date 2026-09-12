#!/usr/bin/env python3
from pathlib import Path
import hashlib,subprocess,re
D=Path(__file__).resolve().parent;REPO=D.parents[3]
BOOT=Path('/boot/sp11-7.1.5-camera-e003i-hl-repeat-shadow-r27')
ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e003i_hl_repeat_shadow_r27')
ID='sp11-camera-e003i-hl-repeat-shadow-r27-one-shot'
ENTRY_SHA='441b7548265b45c2bbd85455e7b8d86303d514d6104268018118fa22b141e084'
WANT={
 'vmlinuz-7.1.5-sp11-render-parity-v4+':'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
 'initrd.img-7.1.5-sp11-camera-e003i-hl-repeat-shadow-r27':'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
 'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f'}
def need(v,m):
    if not v:raise AssertionError(m)
def sudo_sha(p):return subprocess.check_output(['sudo','-n','sha256sum',str(p)],text=True).split()[0]
def sudo_exists(p):return subprocess.run(['sudo','-n','test','-f',str(p)]).returncode==0
head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
origin=subprocess.check_output(['git','-C',str(REPO),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip();need(head==origin,'origin mismatch')
need(sudo_exists(ENTRY) and sudo_sha(ENTRY)==ENTRY_SHA,'entry hash')
for n,h in WANT.items():need(sudo_exists(BOOT/n) and sudo_sha(BOOT/n)==h,n)
grub=subprocess.check_output(['sudo','-n','cat','/boot/grub/grub.cfg'],text=True);need(ID in grub,'grub id absent')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c' in env and not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines()),'grub env')
for m in ('qcom_camss','imx681','ov13858'):need(not Path('/sys/module',m).exists(),'module '+m)
need(not (D/'runtime-output').exists(),'runtime output before arm');need(not (D/'ARM.txt').exists(),'already armed')
install=(D/'INSTALL.txt');need(install.is_file(),'install record absent');txt=install.read_text()
m=re.search(r'^head=([0-9a-f]{40})$',txt,re.M);need(m,'install head absent');install_head=m.group(1)
need(subprocess.run(['git','-C',str(REPO),'merge-base','--is-ancestor',install_head,head]).returncode==0,'install head not ancestor')
print('HL_INSTALLED_VERIFY=PASS INSTALLED=YES ARMED=NO RUNTIME=NO INSTALL_HEAD='+install_head+' CURRENT_HEAD='+head)
