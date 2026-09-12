#!/usr/bin/env python3
from pathlib import Path
import hashlib,re,subprocess
D=Path(__file__).resolve().parent; REPO=D.parents[3]
BOOT=Path('/boot/sp11-7.1.5-camera-ic-unified-rear-r16'); ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_ic_unified_rear_r16'); ID='sp11-camera-ic-unified-rear-r16-one-shot'
WANT={'vmlinuz-7.1.5-sp11-render-parity-v4+':'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a','initrd.img-7.1.5-sp11-camera-ic-unified-rear-r16':'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d','x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb':'5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321'}
def need(v,m):
 if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ssha(p): return subprocess.check_output(['sudo','-n','sha256sum',str(p)],text=True).split()[0]
head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(); origin=subprocess.check_output(['git','-C',str(REPO),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip(); need(head==origin,'origin')
need(subprocess.run(['sudo','-n','test','-f',str(ENTRY)]).returncode==0 and ssha(ENTRY)==sha(D/'99zzzzzz_sp11_camera_ic_unified_rear_r16'),'entry')
for n,h in WANT.items(): need(subprocess.run(['sudo','-n','test','-f',str(BOOT/n)]).returncode==0 and ssha(BOOT/n)==h,n)
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True); need('saved_entry=sp11-audio-fullio-v19c' in env and not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines()),'grub env')
need(ID in subprocess.check_output(['sudo','-n','cat','/boot/grub/grub.cfg'],text=True),'grub id')
need(not (D/'ARM.txt').exists() and not (D/'runtime-output').exists(),'arm/runtime evidence')
t=(D/'INSTALL.txt').read_text(); mm=re.search(r'^head=([0-9a-f]{40})$',t,re.M); need(mm,'install head'); need(subprocess.run(['git','-C',str(REPO),'merge-base','--is-ancestor',mm.group(1),head]).returncode==0,'install ancestry')
for h in ('7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95','ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6','13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309'): need(h in t,'module hash '+h)
print('IC_INSTALLED_VERIFY=PASS INSTALLED=YES ARMED=NO RUNTIME=NO INSTALL_HEAD='+mm.group(1)+' CURRENT_HEAD='+head)
