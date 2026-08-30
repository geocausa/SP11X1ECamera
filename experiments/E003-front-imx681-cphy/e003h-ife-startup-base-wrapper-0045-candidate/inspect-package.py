#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-ife-startup-base-wrapper-0045-candidate'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
BOOT=Path('/boot/sp11-7.1.5-camera-e003h-ife-base-0045')
ENTRY=Path('/etc/grub.d/99n_sp11_camera_e003h_ife_base_0045')
STATIC_COMMIT='4bcde9a4e04d2e568ecd659b8a6351d4bcbc0163'
EXPECTED={
 'manifest':'9a615d1252c087065f450966941d6bb6f93ae8bb7bc039321e7fb850d8f5c341',
 'camss':'cfdd66c9d2c56533993f5f73831d77b3f5018c1d552183da634971378aa06923',
 'sensor':'389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'capsule':'6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20',
 'helper':'d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09',
 'setup_oracle':'666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f',
 'watcher':'8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84',
 'golden_kernel':'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
 'golden_initrd':'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
 'patch':'9fd8ddd43013441a2bedc2a603f9373a42559da17cc113ab8bbe959f38d7be4e',
 'linux_inspection':'bacbb046f5442b0542393302df42e4cbb2f2e2ca544c716d1c43434b9f2d9937',
 'windows_wrapper':'93b793d4bb13bc9d0abc09b667502466681f1a3e81d39bc837700d50ada96d03',
 'provenance':'803d09be7a18b321b07db7dac5a81d837dd09b1f6dfd883b2f27daefa7e8ffb6',
}
SCRIPT_EXPECTED={
 'preflight.sh':'d3ebc9f3b3184cf451f9ffe5d42ffb4b406aacb83fc042a4774138da08d937db',
 'install-candidate.sh':'70010a1bacc9328cb2d2f59ef98a4de574b1efcb6464aee3d8fa4d549e58e3bc',
 'runtime-preflight.sh':'90f9ca4b378af28eaf3739e3a9872c06dcf9fd888a9e79543ce886b90a5a5248',
 'load-candidate.sh':'2f0f42e5c3e45e878b654d7b7b8b611c7c85e78d47f266f3c197baf06a4cb751',
 'setup-media.sh':'05db8b70d3db48fc34ebefc9f71d113b401de73e4deee1b7d55a4982954a6ca2',
 'start-observer.sh':'e0523a3f6ba096ddaec7ecb572e836e060164c269724ceb0ac42e347e9e30f66',
 'run-once.sh':'7e1761c3ef9467112aefe49e7bc793b17369dd396b26bbecd551ffd274958ff1',
}
IOMMUS=['3d','800','60','3d','820','60','3d','840','60','3d','860','60','3d','18a0','0']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def cmd(a): return subprocess.check_output(a,text=True,stderr=subprocess.DEVNULL).strip()

def main():
 if sha(NEW/'asset-manifest.json') != EXPECTED['manifest']: die('asset manifest drift')
 manifest=json.loads((NEW/'asset-manifest.json').read_text())
 if manifest.get('runtime_authorized') is not False or manifest.get('static_commit') != STATIC_COMMIT: die('manifest policy drift')
 assets={
  'qcom-camss.ko':'camss','imx681.ko':'sensor',
  'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb':'dtb',
  'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin':'capsule',
  'e003h-pix-one-shot':'helper','setup-pix-media.sh':'setup_oracle','watch-rtcdm-stage.py':'watcher'}
 for rel,key in assets.items():
  if sha(NEW/rel) != EXPECTED[key]: die(rel+' hash drift')
  if manifest['assets'][rel] != EXPECTED[key]: die(rel+' manifest drift')
 for n,h in SCRIPT_EXPECTED.items():
  if sha(NEW/n) != h: die(n+' drift')
 if sha(STATIC/'0045-x1e-ife-startup-change-base-wrapper.patch') != EXPECTED['patch']: die('0045 patch drift')
 if sha(STATIC/'linux-0045-startup-base-wrapper-inspection.json') != EXPECTED['linux_inspection']: die('0045 Linux inspection drift')
 if sha(STATIC/'windows-ife-startup-base-wrapper-oracle.json') != EXPECTED['windows_wrapper']: die('Windows startup wrapper oracle drift')
 if sha(REPO/'provenance/front-parity.json') != EXPECTED['provenance']: die('provenance drift')
 x=json.loads((STATIC/'linux-0045-startup-base-wrapper-inspection.json').read_text())
 if not x.get('accepted') or x.get('runtime_authorized') is not False: die('0045 static inspection policy drift')
 if x['startup_wrapper']['word']!='0x0800f000' or x['startup_wrapper']['entries']!=4: die('0045 wrapper contract drift')
 if x['late_csid_mask_repair_added'] is not False: die('late CSID repair unexpectedly present')
 if (NEW/'AUTHORIZATION.json').exists(): die('authorization exists at package-only gate')
 for rel in ('RUNTIME-IFE-BASE-0045-RUN.txt','RUNTIME-IFE-BASE-0045-QC10C.bin'):
  if (NEW/rel).exists(): die('runtime evidence already exists: '+rel)
 install=(NEW/'install-candidate.sh').read_text()
 if any('grub-reboot ' in l and not l.lstrip().startswith('#') for l in install.splitlines()): die('installer can arm next boot')
 if 'next_entry intentionally empty' not in install: die('installer lacks explicit unarmed postcondition')
 pre=(NEW/'preflight.sh').read_text()
 if 'AUTHORIZATION.json' not in pre or 'authorization exists at package-only gate' not in pre: die('package preflight lacks authorization rejection')
 runtime=(NEW/'runtime-preflight.sh').read_text()
 for token in ('AUTHORIZATION.json','repo/origin divergence','module already loaded','RUN log already exists; refusing retry','next_entry must be empty','sp11_camera_e003h_ife_base_0045=1'):
  if token not in runtime: die('runtime preflight missing gate '+token)
 if 'insmod ' in runtime or 'modprobe ' in runtime or 'tee "$TRIGGER"' in runtime or 'echo RUN' in runtime: die('runtime preflight activates hardware')
 if "['git','-C',repo,'merge-base','--is-ancestor'" not in runtime: die('runtime preflight ancestry check not cwd-independent')
 load=(NEW/'load-candidate.sh').read_text()
 call=load.find('"$NEW/runtime-preflight.sh"')
 mod_positions=[x for x in (load.find('modprobe '),load.find('insmod ')) if x >= 0]
 if call < 0 or not mod_positions or call > min(mod_positions): die('runtime preflight is not before first module load')
 run=(NEW/'run-once.sh').read_text()
 if run.count('sudo -n "$HELPER"') != 1: die('helper invocation count drift')
 for token in ('AUTHORIZATION.json','repo/origin divergence','RUN log already exists; refusing retry','watcher not ready','RT-CDM diagnostic not idle before RUN'):
  if token not in run: die('run wrapper missing gate '+token)
 if 'echo RUN' in run or 'printf RUN' in run or 'tee "$TRIGGER"' in run: die('run wrapper directly writes trigger')
 if "['git','-C',repo,'merge-base','--is-ancestor'" not in run: die('run wrapper ancestry check not cwd-independent')
 dtb=NEW/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'
 if cmd(['fdtget','-l',str(dtb),'/soc@0/isp@acb7000/ports']).split() != ['port@2']: die('DT not front-only')
 reg=cmd(['fdtget','-t','x',str(dtb),'/soc@0/isp@acb7000','reg'])
 if 'ac71000 0 f000' not in reg or 'ac26000 0 1000' not in reg: die('DT resources drift')
 if cmd(['fdtget','-t','x',str(dtb),'/soc@0/isp@acb7000','iommus']).split()!=IOMMUS: die('IOMMU set drift')
 head=cmd(['git','-C',str(REPO),'rev-parse','HEAD'])
 if subprocess.call(['git','-C',str(REPO),'merge-base','--is-ancestor',STATIC_COMMIT,head],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL): die('static commit not ancestor of current HEAD')
 env=cmd(['grub-editenv','list']).splitlines()
 if 'saved_entry=sp11-audio-fullio-v19c' not in env: die('Golden saved_entry drift')
 if any(v.startswith('next_entry=') and v!='next_entry=' for v in env): die('candidate already armed')
 for m in ('qcom_camss','imx681','ov13858'):
  if Path('/sys/module/'+m).exists(): die(m+' loaded on package inspection')
 installed={
  'kernel':sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+'),
  'initrd':sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-ife-base-0045'),
  'dtb':sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')}
 expected_inst={'kernel':EXPECTED['golden_kernel'],'initrd':EXPECTED['golden_initrd'],'dtb':EXPECTED['dtb']}
 if installed != expected_inst: die('installed boot drift')
 entry=cmd(['sudo','-n','cat',str(ENTRY)])
 for token in ('sp11-camera-e003h-ife-base-0045-one-shot','sp11_camera_e003h_ife_base_0045=1',str(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'),str(NEW/'firmware')):
  if token not in entry: die('installed entry missing '+token)
 subprocess.check_call(['python3',str(REPO/'tools/check-front-parity-provenance.py'),'--repo',str(REPO),'--target','bounded_first_pix'],stdout=subprocess.DEVNULL)
 out={
  'schema':'sp11-e003h-ife-startup-base-0045-package-v1','accepted':True,
  'static_commit':STATIC_COMMIT,'hashes':EXPECTED,'runtime_scripts':SCRIPT_EXPECTED,
  'installed_boot':installed,'boot_id':'sp11-camera-e003h-ife-base-0045-one-shot',
  'front_only_ports':['port@2'],'iommu_set':['0x800/0x60','0x820/0x60','0x840/0x60','0x860/0x60','0x18a0/0'],
  'frozen_runtime_assets':True,'golden_saved_default':True,'candidate_boot_installed':True,
  'candidate_boot_armed':False,'camera_modules_loaded':False,'authorization_present':False,
  'runtime_preflight_before_module_load':True,'single_helper_invocation_enforced':True,
  'same_boot_retry_refused_by_runlog':True,'bounded_provenance_green':True,
  'cwd_independent_git_checks':True,'runtime_authorized':False,
  'next':'commit/push unarmed package checkpoint; any hardware run requires a separate authorization'}
 (NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: 0045 startup-base package is installed, frozen, hash-pinned, Golden-safe and unarmed')

if __name__=='__main__': main()
