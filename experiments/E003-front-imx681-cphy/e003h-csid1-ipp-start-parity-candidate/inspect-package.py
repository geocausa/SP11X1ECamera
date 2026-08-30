#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path

ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-ipp-start-parity-candidate'
OLD=REPO/'experiments/E003-front-imx681-cphy/e003h-bounded-vfe1-pix-runtime-candidate'
CAMSS=ROOT/'02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/qcom-camss.ko'
SENSOR=REPO/'experiments/E003-front-imx681-cphy/e003h-bounded-front-first-frame-runtime/imx681.ko'
DTB=OLD/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'
CAP=OLD/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin'
HELPER=OLD/'e003h-pix-one-shot'
BOOT=Path('/boot/sp11-7.1.5-camera-e003h-csid1-0042')
ENTRY=Path('/etc/grub.d/99m_sp11_camera_e003h_csid1_0042')
EXPECTED={
 'camss':'c67ce602f88be5db2ffecd816879081d74f996f7884e8661bea252d924f7098e',
 'sensor':'389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'capsule':'6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20',
 'helper':'d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09',
 'setup':'666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f',
 'watcher':'8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84',
 'golden_kernel':'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
 'golden_initrd':'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
 'linux_inspection':'6d79f9ba9ff1265a372f37dd49717cf44208cbe3e413ccb3f0b0b385b3823430',
 'provenance':'4690bd278ec92de5556d793e49f8de287d3ae212e5180564172037d80d71e278',
}
SCRIPT_EXPECTED={
 'install-candidate.sh':'f5e59f89e44ac32ed45e7da383558d797f9fb378ef793d7719a53b8d9b5ee8d5',
 'load-candidate.sh':'747d58141890416837126e68e0f56cce2f2c05a149511782f38fe36906c65f6c',
 'preflight.sh':'6cd18c2ffe9dff9070adf9519e366df19d3e72d7e7a7cea449588eeb5b13992a',
 'run-once.sh':'d64410d0c3e4793e0967bde7ddae1df8323c21bf0953bd08d4698a2a391f124c',
 'setup-media.sh':'4761ecfd1eb1dbd91582d687a7380c922d451e0ad2b7d03253dfedbe1380fe71',
 'start-observer.sh':'40a5fbabc84c98c8dbe9cab0f6975786810f242d94c33900de3bfb1b2b27b526',
}
IOMMUS=['3d','800','60','3d','820','60','3d','840','60','3d','860','60','3d','18a0','0']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def cmd(args): return subprocess.check_output(args,text=True,stderr=subprocess.DEVNULL).strip()

def main():
 for k,p in [('camss',CAMSS),('sensor',SENSOR),('dtb',DTB),('capsule',CAP),('helper',HELPER)]:
  if sha(p)!=EXPECTED[k]: die(k+' hash drift')
 if sha(OLD/'setup-pix-media.sh')!=EXPECTED['setup']: die('setup script drift')
 if sha(OLD/'watch-rtcdm-stage.py')!=EXPECTED['watcher']: die('watcher drift')
 if sha(REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/csid1-ipp-start-linux-inspection.json')!=EXPECTED['linux_inspection']: die('0042 Linux inspection drift')
 if sha(REPO/'provenance/front-parity.json')!=EXPECTED['provenance']: die('provenance manifest drift')
 for name,h in SCRIPT_EXPECTED.items():
  if sha(NEW/name)!=h: die(name+' drift')
 if (NEW/'AUTHORIZATION.json').exists(): die('authorization exists at package-only gate')
 install=(NEW/'install-candidate.sh').read_text()
 if any('grub-reboot ' in line and not line.lstrip().startswith('#') for line in install.splitlines()): die('installer arms next boot')
 run=(NEW/'run-once.sh').read_text()
 if run.count('sudo -n "$HELPER"')!=1: die('run wrapper helper invocation count drift')
 if 'echo RUN' in run or 'printf RUN' in run or 'tee "$TRIGGER"' in run: die('run wrapper directly writes trigger')
 for required in ('AUTHORIZATION.json','check-front-parity-provenance.py','RUN log already exists; refusing retry','watcher not ready','RT-CDM diagnostic not idle before RUN'):
  if required not in run: die('run wrapper missing gate '+required)
 ports=cmd(['fdtget','-l',str(DTB),'/soc@0/isp@acb7000/ports']).split()
 if ports!=['port@2']: die('DT is not front-only')
 reg=cmd(['fdtget','-t','x',str(DTB),'/soc@0/isp@acb7000','reg'])
 if 'ac71000 0 f000' not in reg or 'ac26000 0 1000' not in reg: die('DT resource drift')
 iom=cmd(['fdtget','-t','x',str(DTB),'/soc@0/isp@acb7000','iommus']).split()
 if iom!=IOMMUS: die('IOMMU set drift '+repr(iom))
 env=cmd(['grub-editenv','list'])
 lines=env.splitlines()
 if 'saved_entry=sp11-audio-fullio-v19c' not in lines: die('Golden saved_entry drift')
 if any(x.startswith('next_entry=') and x!='next_entry=' for x in lines): die('candidate already armed')
 for m in ('qcom_camss','imx681','ov13858'):
  if Path('/sys/module/'+m).exists(): die(m+' loaded on package inspection')
 installed={
  'kernel':sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+'),
  'initrd':sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-csid1-0042'),
  'dtb':sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'),
 }
 if installed!={'kernel':EXPECTED['golden_kernel'],'initrd':EXPECTED['golden_initrd'],'dtb':EXPECTED['dtb']}: die('installed boot drift')
 entry=cmd(['sudo','-n','cat',str(ENTRY)])
 for text in ('sp11-camera-e003h-csid1-0042-one-shot','sp11_camera_e003h_csid1_0042=1',str(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')):
  if text not in entry: die('installed entry missing '+text)
 if 'grub-reboot' in entry: die('installed entry contains grub-reboot')
 subprocess.check_call(['python3',str(REPO/'tools/check-front-parity-provenance.py'),'--repo',str(REPO),'--target','bounded_first_pix'],stdout=subprocess.DEVNULL)
 out={
  'accepted':True,
  'schema':'sp11-e003h-csid1-0042-package-v1',
  'hashes':EXPECTED,
  'runtime_scripts':SCRIPT_EXPECTED,
  'installed_boot':installed,
  'boot_id':'sp11-camera-e003h-csid1-0042-one-shot',
  'front_only_ports':ports,
  'iommu_set':['0x800/0x60','0x820/0x60','0x840/0x60','0x860/0x60','0x18a0/0'],
  'golden_saved_default':True,
  'candidate_boot_installed':True,
  'candidate_boot_armed':False,
  'camera_modules_loaded':False,
  'authorization_present':False,
  'single_helper_invocation_enforced':True,
  'same_boot_retry_refused_by_runlog':True,
  'bounded_provenance_green':True,
  'runtime_authorized':False,
  'next':'commit/push exact package checkpoint; then create separate authorization review',
 }
 (NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: fresh 0042 one-shot package installed, hash-pinned, Golden-safe and unarmed')
if __name__=='__main__': main()
