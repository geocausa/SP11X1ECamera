#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-prepare-rup-enable-parity-candidate'
OLD=REPO/'experiments/E003-front-imx681-cphy/e003h-bounded-vfe1-pix-runtime-candidate'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
CAMSS=ROOT/'02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/qcom-camss.ko'
SENSOR=REPO/'experiments/E003-front-imx681-cphy/e003h-bounded-front-first-frame-runtime/imx681.ko'
DTB=OLD/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'
CAP=OLD/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin'
HELPER=OLD/'e003h-pix-one-shot'
BOOT=Path('/boot/sp11-7.1.5-camera-e003h-csid1-0043')
ENTRY=Path('/etc/grub.d/99n_sp11_camera_e003h_csid1_0043')
EXPECTED={
 'camss':'23cc63f742f70ca3f70e25d89b34c9e8cef531ed6f3c9562f2f7b0d3a7ac05a9',
 'sensor':'389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'capsule':'6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20',
 'helper':'d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09',
 'setup_oracle':'666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f',
 'watcher_oracle':'8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84',
 'golden_kernel':'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
 'golden_initrd':'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
 'linux_inspection':'df96044920913e6a6fdb0518baf4109af232c9c3c4060f2f83a0ae7998e51cf0',
 'windows_order_oracle':'d433307f97f97d2a1bdcf27b47fd9010e78b7fbb3ab75dfe78aad78c886cd19d',
 'provenance':'293c1dd909237d4cff44582b862cd165543547e2dcad285506d9463a6ace7b7e',
}
SCRIPT_EXPECTED={
 'install-candidate.sh':'db31ef1727bae59a2ca3c205572cf069dfa5af6c3b037905e61270441ba07d5c',
 'load-candidate.sh':'3ebda0b3b016001bc0bf70ec2d23e9067b555c3bab84b9872388465aebb5c38c',
 'preflight.sh':'5c280f6252cc6d2f9a623f5d050d1df53fd9f7743b803c3512e6863117e67dce',
 'run-once.sh':'3e9eedf6301f46922d2d93a111db475ac20cdf5cb6159fd9fb15010c5775ee34',
 'setup-media.sh':'4761ecfd1eb1dbd91582d687a7380c922d451e0ad2b7d03253dfedbe1380fe71',
 'start-observer.sh':'cf3bd747c5cf8966813111b743f8ad205081226938015bf8303055f113094387',
}
IOMMUS=['3d','800','60','3d','820','60','3d','840','60','3d','860','60','3d','18a0','0']
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def cmd(a): return subprocess.check_output(a,text=True,stderr=subprocess.DEVNULL).strip()
def main():
 for k,p in [('camss',CAMSS),('sensor',SENSOR),('dtb',DTB),('capsule',CAP),('helper',HELPER)]:
  if sha(p)!=EXPECTED[k]: die(k+' hash drift')
 if sha(OLD/'setup-pix-media.sh')!=EXPECTED['setup_oracle']: die('setup oracle drift')
 if sha(OLD/'watch-rtcdm-stage.py')!=EXPECTED['watcher_oracle']: die('watcher oracle drift')
 if sha(STATIC/'csid1-prepare-rup-enable-linux-inspection.json')!=EXPECTED['linux_inspection']: die('0043 Linux inspection drift')
 if sha(STATIC/'windows-csid1-config-rup-enable-order-oracle.json')!=EXPECTED['windows_order_oracle']: die('Windows order oracle drift')
 if sha(REPO/'provenance/front-parity.json')!=EXPECTED['provenance']: die('provenance manifest drift')
 for n,h in SCRIPT_EXPECTED.items():
  if sha(NEW/n)!=h: die(n+' drift')
 if (NEW/'AUTHORIZATION.json').exists(): die('authorization exists at package-only gate')
 install=(NEW/'install-candidate.sh').read_text()
 if any('grub-reboot ' in l and not l.lstrip().startswith('#') for l in install.splitlines()): die('installer arms next boot')
 run=(NEW/'run-once.sh').read_text()
 if run.count('sudo -n "$HELPER"')!=1: die('helper invocation count drift')
 if 'echo RUN' in run or 'printf RUN' in run or 'tee "$TRIGGER"' in run: die('wrapper directly writes trigger')
 for r in ('AUTHORIZATION.json','check-front-parity-provenance.py','RUN log already exists; refusing retry','watcher not ready','RT-CDM diagnostic not idle before RUN'):
  if r not in run: die('run wrapper missing gate '+r)
 ports=cmd(['fdtget','-l',str(DTB),'/soc@0/isp@acb7000/ports']).split()
 if ports!=['port@2']: die('DT not front-only')
 reg=cmd(['fdtget','-t','x',str(DTB),'/soc@0/isp@acb7000','reg'])
 if 'ac71000 0 f000' not in reg or 'ac26000 0 1000' not in reg: die('DT resource drift')
 if cmd(['fdtget','-t','x',str(DTB),'/soc@0/isp@acb7000','iommus']).split()!=IOMMUS: die('IOMMU set drift')
 env=cmd(['grub-editenv','list']).splitlines()
 if 'saved_entry=sp11-audio-fullio-v19c' not in env: die('Golden saved_entry drift')
 if any(x.startswith('next_entry=') and x!='next_entry=' for x in env): die('candidate already armed')
 for m in ('qcom_camss','imx681','ov13858'):
  if Path('/sys/module/'+m).exists(): die(m+' loaded on package inspection')
 installed={
  'kernel':sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+'),
  'initrd':sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-csid1-0043'),
  'dtb':sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')}
 expected_inst={'kernel':EXPECTED['golden_kernel'],'initrd':EXPECTED['golden_initrd'],'dtb':EXPECTED['dtb']}
 if installed!=expected_inst: die('installed boot drift')
 entry=cmd(['sudo','-n','cat',str(ENTRY)])
 for t in ('sp11-camera-e003h-csid1-0043-one-shot','sp11_camera_e003h_csid1_0043=1',str(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')):
  if t not in entry: die('installed entry missing '+t)
 subprocess.check_call(['python3',str(REPO/'tools/check-front-parity-provenance.py'),'--repo',str(REPO),'--target','bounded_first_pix'],stdout=subprocess.DEVNULL)
 out={'accepted':True,'schema':'sp11-e003h-csid1-0043-package-v1','hashes':EXPECTED,'runtime_scripts':SCRIPT_EXPECTED,
      'installed_boot':installed,'boot_id':'sp11-camera-e003h-csid1-0043-one-shot','front_only_ports':ports,
      'iommu_set':['0x800/0x60','0x820/0x60','0x840/0x60','0x860/0x60','0x18a0/0'],
      'golden_saved_default':True,'candidate_boot_installed':True,'candidate_boot_armed':False,'camera_modules_loaded':False,
      'authorization_present':False,'single_helper_invocation_enforced':True,'same_boot_retry_refused_by_runlog':True,
      'bounded_provenance_green':True,'runtime_authorized':False,
      'next':'commit/push exact installed package checkpoint; then create separate one-run authorization'}
 (NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: 0043 prepare-RUP-enable package is installed, hash-pinned, Golden-safe and unarmed')
if __name__=='__main__': main()
