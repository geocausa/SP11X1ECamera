#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-common-lifecycle-0044-candidate'
OLD=REPO/'experiments/E003-front-imx681-cphy/e003h-bounded-vfe1-pix-runtime-candidate'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
CAMSS=ROOT/'02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/qcom-camss.ko'
SENSOR=REPO/'experiments/E003-front-imx681-cphy/e003h-bounded-front-first-frame-runtime/imx681.ko'
DTB=OLD/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'
CAP=OLD/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin'
HELPER=OLD/'e003h-pix-one-shot'
BOOT=Path('/boot/sp11-7.1.5-camera-e003h-csid1-0044')
ENTRY=Path('/etc/grub.d/99n_sp11_camera_e003h_csid1_0044')
EXPECTED={
 'camss':'98b3252e9d1e8c46e81ea48fe0a6b4b0ecea77e1206915b4b1378040dc473cbc',
 'sensor':'389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'capsule':'6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20',
 'helper':'d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09',
 'setup_oracle':'666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f',
 'watcher_oracle':'8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84',
 'golden_kernel':'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
 'golden_initrd':'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
 'linux_inspection':'4d1dfc9d264e3b19d6e7e688b9c0d56f7db40a6f238b50856c26072fc9447ac7',
 'windows_common_reset':'43a265f0cd63fa9e01406e8b5ff0b62c756dc2bc2f8c3a24df74a4f832b76996',
 'windows_ipp_start':'01960da41376809d694c6aa2336ecef6ff4c010abfa29e4674b1a68d303c3cda',
 'patch':'a96339ab84094cfa0d103d73e6c04294dce5f211738fcbbe2bd370b9c5bb3340',
 'provenance':'5b016ae79b599a4675f7c5fde31619d53ef2c9c6143791f683504513058e78b1',
}
SCRIPT_EXPECTED={
 'install-candidate.sh':'1a23b370faed0e402f5961192c6868474c7e32a01f027885150b77ceb3f42228',
 'load-candidate.sh':'1f7be8b1b252ad8268edd09dd4f1a22fced2e38911367ec5e2fb64162ff3072e',
 'runtime-preflight.sh':'63611d2cf887145db0be950880d2a0b2d4f5c8651ba99ee011a1040b91aa62ff',
 'preflight.sh':'f9bf2c51561d51dc3986fdae0abb82db1da56ca40ee1f34c768f37667c2699b4',
 'run-once.sh':'b001583638120696990ffe45d81c70d6eac5e12eb4d088b7600f0e79b61a7f0a',
 'setup-media.sh':'4761ecfd1eb1dbd91582d687a7380c922d451e0ad2b7d03253dfedbe1380fe71',
 'start-observer.sh':'1068b954462d6f75bf8776ea2900b13c90f6bfcdf3263d7fdbc52a142e0fce6c',
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
 if sha(STATIC/'csid1-common-lifecycle-linux-inspection.json')!=EXPECTED['linux_inspection']: die('0044 Linux inspection drift')
 if sha(STATIC/'windows-csid1-common-reset-oracle.json')!=EXPECTED['windows_common_reset']: die('Windows common reset oracle drift')
 if sha(STATIC/'windows-csid1-ipp-start-oracle.json')!=EXPECTED['windows_ipp_start']: die('Windows IPP start oracle drift')
 if sha(STATIC/'0044-x1e-csid1-common-lifecycle-windows-parity.patch')!=EXPECTED['patch']: die('0044 patch drift')
 if sha(REPO/'provenance/front-parity.json')!=EXPECTED['provenance']: die('provenance manifest drift')
 for n,h in SCRIPT_EXPECTED.items():
  if sha(NEW/n)!=h: die(n+' drift')
 if sha(NEW/'AUTHORIZATION-BOOT1-CONSUMED.json')!='94d4c1b8eb34e42990ed02ea5c228d37a2521cc44417bba64c97cc70ae9d6162': die('boot1 authorization history drift')
 if sha(NEW/'BOOT1-CONSUMPTION.json')!='b462e7688d81dd710fd62ae1244419df9d542b7841de5afefadfa5a2ff9f07f9': die('boot1 consumption drift')
 boot1=json.loads((NEW/'BOOT1-CONSUMPTION.json').read_text())
 if not boot1.get('accepted') or boot1.get('hardware_run_executed') is not False or boot1.get('helper_invocations') != 0 or boot1.get('camera_modules_loaded') is not False or boot1.get('golden_return_verified') is not True: die('boot1 no-hardware record drift')
 if sha(NEW/'AUTHORIZATION-BOOT2-CONSUMED.json')!='6fc9802e64d1ba16b5b30c961e1a0ceceb9e270131d8cb28b609e53e962f4f53': die('boot2 authorization history drift')
 if sha(NEW/'BOOT2-CONSUMPTION.json')!='4743403e99bc2f4a15864aabd7915906f8a29bd2b3623f91005fd56d086f4ef0': die('boot2 consumption drift')
 boot2=json.loads((NEW/'BOOT2-CONSUMPTION.json').read_text())
 if not boot2.get('accepted') or boot2.get('hardware_run_executed') is not False or boot2.get('helper_invocations') != 0 or boot2.get('camera_modules_loaded') is not False or boot2.get('golden_return_verified') is not True: die('boot2 no-hardware record drift')
 if (NEW/'AUTHORIZATION.json').exists(): die('authorization exists at package-only gate')
 runtime_pre=(NEW/'runtime-preflight.sh').read_text()
 for r in ('AUTHORIZATION.json','check-front-parity-provenance.py','repo/origin divergence','RUN log already exists; refusing retry','module already loaded','sp11_camera_e003h_csid1_0044=1','next_entry must be empty'):
  if r not in runtime_pre: die('runtime preflight missing gate '+r)
 if 'insmod ' in runtime_pre or 'modprobe ' in runtime_pre or 'tee "$TRIGGER"' in runtime_pre or 'echo RUN' in runtime_pre: die('runtime preflight contains hardware activation')
 if "['git','-C',repo,'merge-base','--is-ancestor'" not in runtime_pre: die('runtime preflight git ancestry check is not cwd-independent')
 load=(NEW/'load-candidate.sh').read_text()
 call=load.find('"$NEW/runtime-preflight.sh"')
 first_mod=min(x for x in (load.find('modprobe '),load.find('insmod ')) if x >= 0)
 if call < 0 or call > first_mod: die('runtime preflight is not before first module load')
 install=(NEW/'install-candidate.sh').read_text()
 if any('grub-reboot ' in l and not l.lstrip().startswith('#') for l in install.splitlines()): die('installer arms next boot')
 run=(NEW/'run-once.sh').read_text()
 if run.count('sudo -n "$HELPER"')!=1: die('helper invocation count drift')
 if 'echo RUN' in run or 'printf RUN' in run or 'tee "$TRIGGER"' in run: die('wrapper directly writes trigger')
 for r in ('AUTHORIZATION.json','check-front-parity-provenance.py','RUN log already exists; refusing retry','watcher not ready','RT-CDM diagnostic not idle before RUN'):
  if r not in run: die('run wrapper missing gate '+r)
 if "['git','-C',repo,'merge-base','--is-ancestor'" not in run: die('run wrapper git ancestry check is not cwd-independent')
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
 installed={'kernel':sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+'),'initrd':sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-csid1-0044'),'dtb':sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')}
 expected_inst={'kernel':EXPECTED['golden_kernel'],'initrd':EXPECTED['golden_initrd'],'dtb':EXPECTED['dtb']}
 if installed!=expected_inst: die('installed boot drift')
 entry=cmd(['sudo','-n','cat',str(ENTRY)])
 for t in ('sp11-camera-e003h-csid1-0044-one-shot','sp11_camera_e003h_csid1_0044=1',str(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')):
  if t not in entry: die('installed entry missing '+t)
 subprocess.check_call(['python3',str(REPO/'tools/check-front-parity-provenance.py'),'--repo',str(REPO),'--target','bounded_first_pix'],stdout=subprocess.DEVNULL)
 out={'accepted':True,'schema':'sp11-e003h-csid1-0044-package-v3','hashes':EXPECTED,'runtime_scripts':SCRIPT_EXPECTED,
      'installed_boot':installed,'boot_id':'sp11-camera-e003h-csid1-0044-one-shot','front_only_ports':ports,
      'iommu_set':['0x800/0x60','0x820/0x60','0x840/0x60','0x860/0x60','0x18a0/0'],
      'golden_saved_default':True,'candidate_boot_installed':True,'candidate_boot_armed':False,'camera_modules_loaded':False,
      'authorization_present':False,'single_helper_invocation_enforced':True,'same_boot_retry_refused_by_runlog':True,
      'bounded_provenance_green':True,'runtime_authorized':False,'runtime_preflight_before_module_load':True,
      'boot1_consumed_without_hardware_run':True,'boot2_consumed_without_hardware_run':True,'cwd_independent_git_checks':True,
      'next':'commit/push corrected v3 harness checkpoint; any hardware run requires a fresh authorization'}
 (NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: 0044 common-lifecycle package v3 is installed, hash-pinned, Golden-safe and unarmed')
if __name__=='__main__': main()
