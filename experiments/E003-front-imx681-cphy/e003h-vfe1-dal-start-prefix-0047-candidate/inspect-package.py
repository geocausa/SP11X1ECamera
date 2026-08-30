#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-dal-start-prefix-0047-candidate'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
BOOT=Path('/boot/sp11-7.1.5-camera-e003h-vfe1-0047')
ENTRY=Path('/etc/grub.d/99n_sp11_camera_e003h_vfe1_0047')
EXPECTED={
 'camss':'5e7bdadf76f293b48e4efb54a69c011cb00ff9af75806e9558176cd925dd5007',
 'sensor':'389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'capsule':'6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20',
 'helper':'d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09',
 'setup':'666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f',
 'watch':'8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84',
 'asset_manifest':'12a21ff0aeead670ff96a95f59592d7a9d9d12bd0e669f51651edc27828cf6ec',
 'patch':'f5192c50c15e1ab8d92659b3735d70f5dfeeff0bbae961d90e1dbf27486ffee4',
 'oracle':'75738af53bf5845f28e8c279dad573b0e8e052c4aa2fed9e11d0685fc9455cd7',
 'linux_inspection':'f45276a3dd7033930f80bf5d04247a638d8dfcfd2144d8e142cfe440671224bc',
 'golden_kernel':'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
 'golden_initrd':'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
}
SCRIPTS={
 'preflight.sh':'0b4753c110867a32f685b581c7d2aa37a8c2384841583847822b1e48747a4e7b',
 'install-candidate.sh':'2fbd88bea3b882d9dcbe5028659399c16bca286640fc498c1696204473241def',
 'runtime-preflight.sh':'78773f00fd756e2106a4e2dfe28827209139836448877c5aa5c732979fc972bb',
 'load-candidate.sh':'2ce2c5e3374ed93dbe313d00f0795c3c84697518ebf2beedaea76561b9c39ede',
 'setup-media.sh':'03a20b192fce44aab3aef1f2e0daa787fbe35263db969c8c572601f74ef30e35',
 'start-observer.sh':'44119de1c591b0ffd6c58161c8093e6731255752d1c72be042cc9140a22e2a59',
 'run-once.sh':'72c89bb8db62ed4beaaec53205a7d9f108dda7a0554f106f1178a584fca35f3c',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def cmd(a): return subprocess.check_output(a,text=True,stderr=subprocess.DEVNULL).strip()
def main():
 files={'camss':NEW/'qcom-camss.ko','sensor':NEW/'imx681.ko','dtb':NEW/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb','capsule':NEW/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin','helper':NEW/'e003h-pix-one-shot','setup':NEW/'setup-pix-media.sh','watch':NEW/'watch-rtcdm-stage.py','asset_manifest':NEW/'asset-manifest.json'}
 for k,p in files.items():
  if sha(p)!=EXPECTED[k]: die(k+' hash drift')
 for n,h in SCRIPTS.items():
  if sha(NEW/n)!=h: die(n+' drift')
 if sha(STATIC/'0047-x1e-vfe1-dal-start-prefix-windows-parity.patch')!=EXPECTED['patch']: die('patch drift')
 if sha(STATIC/'windows-vfe1-dal-start-prefix-oracle.json')!=EXPECTED['oracle']: die('oracle drift')
 if sha(STATIC/'linux-0047-vfe1-dal-start-prefix-inspection.json')!=EXPECTED['linux_inspection']: die('Linux inspection drift')
 li=json.loads((STATIC/'linux-0047-vfe1-dal-start-prefix-inspection.json').read_text())
 if not li.get('accepted') or li.get('runtime_authorized') is not False: die('0047 inspection policy drift')
 if li.get('write_count')!=5 or li.get('optional_bus_0x08_added') is not False: die('0047 write contract drift')
 if li.get('write_order')!=['TOP mask0=0x0007f051','TOP mask1=0','BUS mask0=0xd0000000','BUS mask1=0','VFE TOP +0x24=0']: die('0047 write order drift')
 if (NEW/'AUTHORIZATION.json').exists(): die('authorization exists at package-only gate')
 pre=(NEW/'preflight.sh').read_text()
 if any(x in pre for x in ('insmod ','modprobe ','e003h_pix_run_once')): die('package preflight contains activation')
 install=(NEW/'install-candidate.sh').read_text()
 if any('grub-reboot ' in l and not l.lstrip().startswith('#') for l in install.splitlines()): die('installer can arm next boot')
 runtime=(NEW/'runtime-preflight.sh').read_text()
 for x in ('AUTHORIZATION.json','repo/origin divergence','RUN log already exists; refusing retry','module already loaded','sp11_camera_e003h_vfe1_0047=1','next_entry must be empty'):
  if x not in runtime: die('runtime preflight missing '+x)
 if 'insmod ' in runtime or 'modprobe ' in runtime or 'tee "$TRIGGER"' in runtime: die('runtime preflight activates hardware')
 load=(NEW/'load-candidate.sh').read_text(); call=load.find('"$NEW/runtime-preflight.sh"'); starts=[x for x in (load.find('modprobe '),load.find('insmod ')) if x>=0]
 if call<0 or not starts or call>min(starts): die('runtime preflight is not before first module load')
 run=(NEW/'run-once.sh').read_text()
 if run.count('sudo -n "$HELPER"')!=1: die('helper invocation count drift')
 for x in ('AUTHORIZATION.json','RUN log already exists; refusing retry','watcher not ready','RT-CDM diagnostic not idle before RUN'):
  if x not in run: die('run wrapper missing '+x)
 if 'systemctl reboot' not in run: die('mandatory reboot missing')
 ports=cmd(['fdtget','-l',str(files['dtb']),'/soc@0/isp@acb7000/ports']).split()
 if ports!=['port@2']: die('DT not front-only')
 iommu=cmd(['fdtget','-t','x',str(files['dtb']),'/soc@0/isp@acb7000','iommus']).split()
 if iommu!=['3d','800','60','3d','820','60','3d','840','60','3d','860','60','3d','18a0','0']: die('IOMMU set drift')
 env=cmd(['grub-editenv','list']).splitlines()
 if 'saved_entry=sp11-audio-fullio-v19c' not in env: die('Golden saved_entry drift')
 if any(x.startswith('next_entry=') and x!='next_entry=' for x in env): die('candidate already armed')
 for m in ('qcom_camss','imx681','ov13858'):
  if Path('/sys/module/'+m).exists(): die(m+' loaded during inspection')
 installed={'kernel':sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+'),'initrd':sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-vfe1-0047'),'dtb':sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')}
 if installed!={'kernel':EXPECTED['golden_kernel'],'initrd':EXPECTED['golden_initrd'],'dtb':EXPECTED['dtb']}: die('installed boot drift')
 entry=cmd(['sudo','-n','cat',str(ENTRY)])
 for x in ('sp11-camera-e003h-vfe1-0047-one-shot','sp11_camera_e003h_vfe1_0047=1','VFE1 DAL start prefix 0047',str(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')):
  if x not in entry: die('installed entry missing '+x)
 subprocess.check_call(['python3',str(REPO/'tools/check-front-parity-provenance.py'),'--repo',str(REPO),'--target','bounded_first_pix'],stdout=subprocess.DEVNULL)
 out={'schema':'sp11-e003h-vfe1-dal-start-prefix-0047-package-v1','accepted':True,'hashes':EXPECTED,'runtime_scripts':SCRIPTS,'installed_boot':installed,'boot_id':'sp11-camera-e003h-vfe1-0047-one-shot','front_only_ports':ports,'golden_saved_default':True,'candidate_boot_installed':True,'candidate_boot_armed':False,'camera_modules_loaded':False,'authorization_present':False,'bounded_provenance_green':True,'frozen_runtime_assets':True,'dal_start_prefix_write_count':5,'optional_bus_0x08_added':False,'runtime_preflight_before_module_load':True,'single_helper_invocation_enforced':True,'same_boot_retry_refused_by_runlog':True,'runtime_authorized':False,'next':'commit/push unarmed package; fresh authorization review required'}
 (NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: 0047 VFE1 DAL start-prefix package is installed, frozen, Golden-safe and unarmed')
if __name__=='__main__': main()
