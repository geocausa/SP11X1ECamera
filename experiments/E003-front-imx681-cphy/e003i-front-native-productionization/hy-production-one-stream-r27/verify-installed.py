#!/usr/bin/env python3
from pathlib import Path
import hashlib,re,subprocess
D=Path(__file__).resolve().parent;REPO=D.parents[3]
BOOT=Path('/boot/sp11-7.1.5-camera-e003i-hy-prod-stream-r27');ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e003i_hy_prod_stream_r27');ID='sp11-camera-e003i-hy-prod-stream-r27-one-shot'
WANT={'vmlinuz-7.1.5-sp11-render-parity-v4+':'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a','initrd.img-7.1.5-sp11-camera-e003i-hy-prod-stream-r27':'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d','x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb':'34880dc20d349bf966ebf62d6d8bb3f0130f436c88d9e4838585624a869e04c7'}
def need(v,m):
    if not v:raise AssertionError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ssha(p):return subprocess.check_output(['sudo','-n','sha256sum',str(p)],text=True).split()[0]
head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip();origin=subprocess.check_output(['git','-C',str(REPO),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip();need(head==origin,'origin')
need(subprocess.run(['sudo','-n','test','-f',str(ENTRY)]).returncode==0 and ssha(ENTRY)==sha(D/'99zzzzzz_sp11_camera_e003i_hy_prod_stream_r27'),'entry')
for n,h in WANT.items():need(subprocess.run(['sudo','-n','test','-f',str(BOOT/n)]).returncode==0 and ssha(BOOT/n)==h,n)
grub=subprocess.check_output(['sudo','-n','cat','/boot/grub/grub.cfg'],text=True);need(ID in grub,'grub id')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c' in env and not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines()),'grub env')
for m in ('qcom_camss','imx681','ov13858'):need(not Path('/sys/module',m).exists(),'module '+m)
need(not (D/'runtime-output').exists() and not (D/'ARM.txt').exists(),'runtime/arm evidence')
txt=(D/'INSTALL.txt').read_text();mm=re.search(r'^head=([0-9a-f]{40})$',txt,re.M);need(mm,'install head');ih=mm.group(1);need(subprocess.run(['git','-C',str(REPO),'merge-base','--is-ancestor',ih,head]).returncode==0,'install ancestry')
for h in ('7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95','ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6','57aa9cc2ad85131881416d7795603ab777a70e7c5877828986ff279266a5a757'):need(h in txt,'install authority '+h)
print('HY_INSTALLED_VERIFY=PASS INSTALLED=YES ARMED=NO RUNTIME=NO INSTALL_HEAD='+ih+' CURRENT_HEAD='+head)
