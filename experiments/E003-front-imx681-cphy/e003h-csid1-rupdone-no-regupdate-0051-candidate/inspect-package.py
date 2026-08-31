#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-rupdone-no-regupdate-0051-candidate'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
BOOT=Path('/boot/sp11-7.1.5-camera-e003h-rupclear-0051')
ENTRY=Path('/etc/grub.d/99p_sp11_camera_e003h_rupclear_0051')
STATIC_COMMIT='01d17d96a1882e6d3462c1b9e2caa261f8750821'
EXPECTED={
 'asset_manifest':'3f802bfc48327ec402ab2e84ad6ad11f613998f4c16cd3f82e5b737b8191c592',
 'camss':'6b7287e6eb96c44060d58691333b82f4e4103df929f98ad39ec50347b379f020',
 'capsule':'6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'golden_initrd':'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
 'golden_kernel':'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
 'helper':'d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09',
 'linux_inspection':'a0595d75392871542812ec185e632af37e8da889d6758e61cea794f25517d132',
 'patch':'7d658f5a0c57aa5749aaa76078cce0fb05b35918ec62430786b4d9bd20c7952d',
 'runtime0050':'bc8c2fd7033121592e540e3eedde134e56cab6d2525526f7771a74ec7b424459',
 'sensor':'389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388',
 'setup':'666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f',
 'watch':'8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84',
 'windows':'4ec65044495ea7040b8fa350bee67b83c563eae824ba6e171e7e7b8e8e9b8eb8',
 'provenance':'803d09be7a18b321b07db7dac5a81d837dd09b1f6dfd883b2f27daefa7e8ffb6',
}
SCRIPTS={
 'install-candidate.sh':'9d11ebb2cdc06f1ab30470709df8a0602b4eb54b38a961284fcfff64e708792b',
 'load-candidate.sh':'a7854921d65e764669882aae2c40f8e3ac8fb3fe763c08860743c06492adc8e1',
 'preflight.sh':'a49340786bbf81c2112dcffa32b41f934d212f03d5423552cc88ede8595d885e',
 'run-once.sh':'3ae309f91d9486ba2dd29bd719919632bdb175c008683251e96ceeaaec95eb09',
 'runtime-preflight.sh':'9e88ce2f4b19fd2694a8586adbae0534878345eebf7ee2bf24e3f8485eb844c1',
 'setup-media.sh':'cb90e1f52699321321abb2243fbefaa193a3a975d108d69983fb42d0bf55a6a6',
 'start-observer.sh':'d42736ffcc5a2ad0cf2b72b237c0e0042cbd2e19665800aafe0484639fb91020',
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s):raise SystemExit('FAIL: '+s)
def cmd(a):return subprocess.check_output(a,text=True,stderr=subprocess.DEVNULL).strip()
def main():
 files={'camss':NEW/'qcom-camss.ko','sensor':NEW/'imx681.ko','dtb':NEW/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb','capsule':NEW/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin','helper':NEW/'e003h-pix-one-shot','setup':NEW/'setup-pix-media.sh','watch':NEW/'watch-rtcdm-stage.py','asset_manifest':NEW/'asset-manifest.json'}
 for k,p in files.items():
  if sha(p)!=EXPECTED[k]:die(k+' hash drift '+sha(p))
 for n,h in SCRIPTS.items():
  if sha(NEW/n)!=h:die(n+' drift '+sha(NEW/n))
 if sha(REPO/'provenance/front-parity.json')!=EXPECTED['provenance']:die('provenance hash drift')
 if sha(STATIC/'0051-x1e-csid1-rupdone-no-regupdate-write.patch')!=EXPECTED['patch']:die('patch drift')
 if sha(STATIC/'linux-0051-csid1-rupdone-no-regupdate-write-inspection.json')!=EXPECTED['linux_inspection']:die('Linux inspection drift')
 if sha(STATIC/'windows-csid1-rupdone-irq-ownership/windows-csid1-rupdone-irq-ownership-oracle.json')!=EXPECTED['windows']:die('Windows ownership drift')
 if sha(STATIC.parent/'e003h-csid1-first-irq-geometry-0050-candidate/runtime-0050-analysis.json')!=EXPECTED['runtime0050']:die('0050 runtime boundary drift')
 li=json.loads((STATIC/'linux-0051-csid1-rupdone-no-regupdate-write-inspection.json').read_text())
 if not li.get('accepted') or li.get('runtime_authorized') is not False:die('0051 inspection policy drift')
 if li.get('new_mmio_reads')!=0 or li.get('new_mmio_writes')!=0 or li.get('new_register_values')!=0:die('0051 access/value drift')
 if li.get('software_shadow_clear_retained') is not True or li.get('rdi_rup_done_behavior_retained') is not True:die('0051 bookkeeping/RDI drift')
 if li.get('ipp_irq_clear_0xb4_retained') is not True or li.get('generic_reg_update_clear_retained') is not True:die('0051 clear behavior drift')
 for k in ('crop_changed','irq_masks_changed','rtcdm_changed','vfe_changed','sensor_changed','csiphy_changed','dt_changed'):
  if li.get(k) is not False:die('0051 changed forbidden domain '+k)
 am=json.loads((NEW/'asset-manifest.json').read_text())
 if not am.get('accepted') or am.get('runtime_authorized') is not False or am.get('static_commit')!=STATIC_COMMIT:die('asset manifest policy/static drift')
 if (NEW/'AUTHORIZATION.json').exists():die('authorization exists at package-only gate')
 pre=(NEW/'preflight.sh').read_text()
 if any(x in pre for x in ('insmod ','modprobe ','e003h_pix_run_once')):die('package preflight contains activation')
 install=(NEW/'install-candidate.sh').read_text()
 if any('grub-reboot ' in l and not l.lstrip().startswith('#') for l in install.splitlines()):die('installer can arm next boot')
 runtime=(NEW/'runtime-preflight.sh').read_text()
 for x in ('AUTHORIZATION.json','repo/origin divergence','RUN log already exists; refusing retry','module already loaded','sp11_camera_e003h_rupclear_0051=1','next_entry must be empty'):
  if x not in runtime:die('runtime preflight missing '+x)
 if 'insmod ' in runtime or 'modprobe ' in runtime or 'tee "$TRIGGER"' in runtime:die('runtime preflight activates hardware')
 load=(NEW/'load-candidate.sh').read_text(); call=load.find('"$NEW/runtime-preflight.sh"'); starts=[x for x in (load.find('modprobe '),load.find('insmod ')) if x>=0]
 if call<0 or not starts or call>min(starts):die('runtime preflight is not before first module load')
 run=(NEW/'run-once.sh').read_text()
 if run.count('sudo -n "$HELPER"')!=1:die('helper invocation count drift')
 for x in ('AUTHORIZATION.json','RUN log already exists; refusing retry','watcher not ready','RT-CDM diagnostic not idle before RUN'):
  if x not in run:die('run wrapper missing '+x)
 if 'systemctl reboot' not in run:die('mandatory reboot missing')
 ports=cmd(['fdtget','-l',str(files['dtb']),'/soc@0/isp@acb7000/ports']).split()
 if ports!=['port@2']:die('DT not front-only')
 iommu=cmd(['fdtget','-t','x',str(files['dtb']),'/soc@0/isp@acb7000','iommus']).split()
 if iommu!=['3d','800','60','3d','820','60','3d','840','60','3d','860','60','3d','18a0','0']:die('IOMMU set drift')
 env=cmd(['grub-editenv','/boot/grub/grubenv','list']).splitlines()
 if 'saved_entry=sp11-audio-fullio-v19c' not in env:die('Golden saved_entry drift')
 if any(x.startswith('next_entry=') and x!='next_entry=' for x in env):die('candidate already armed')
 for m in ('qcom_camss','imx681','ov13858'):
  if Path('/sys/module/'+m).exists():die(m+' loaded during inspection')
 installed={'kernel':sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+'),'initrd':sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-rupclear-0051'),'dtb':sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')}
 if installed!={'kernel':EXPECTED['golden_kernel'],'initrd':EXPECTED['golden_initrd'],'dtb':EXPECTED['dtb']}:die('installed boot drift')
 entry=cmd(['sudo','-n','cat',str(ENTRY)])
 for x in ('sp11-camera-e003h-rupclear-0051-one-shot','sp11_camera_e003h_rupclear_0051=1','CSID1 RUP_DONE ownership 0051',str(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')):
  if x not in entry:die('installed entry missing '+x)
 subprocess.check_call(['python3',str(REPO/'tools/check-front-parity-provenance.py'),'--repo',str(REPO),'--target','bounded_first_pix'],stdout=subprocess.DEVNULL)
 head=cmd(['git','-C',str(REPO),'rev-parse','HEAD']); subprocess.check_call(['git','-C',str(REPO),'merge-base','--is-ancestor',STATIC_COMMIT,head],stdout=subprocess.DEVNULL)
 out={'schema':'sp11-e003h-csid1-rupdone-no-regupdate-0051-package-v1','accepted':True,'hashes':EXPECTED,'runtime_scripts':SCRIPTS,'static_commit':STATIC_COMMIT,'installed_boot':installed,'boot_id':'sp11-camera-e003h-rupclear-0051-one-shot','front_only_ports':ports,'golden_saved_default':True,'candidate_boot_installed':True,'candidate_boot_armed':False,'camera_modules_loaded':False,'authorization_present':False,'bounded_provenance_green':True,'frozen_runtime_assets':True,'new_mmio_reads':0,'new_mmio_writes':0,'new_register_values':0,'suppressed_front_post_rup_reg_update_write':True,'rdi_rup_done_behavior_retained':True,'runtime_preflight_before_module_load':True,'single_helper_invocation_enforced':True,'same_boot_retry_refused_by_runlog':True,'runtime_authorized':False,'next':'commit/push unarmed package; fresh authorization review required'}
 (NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: 0051 RUP_DONE ownership package is installed, frozen, Golden-safe and unarmed')
if __name__=='__main__':main()
