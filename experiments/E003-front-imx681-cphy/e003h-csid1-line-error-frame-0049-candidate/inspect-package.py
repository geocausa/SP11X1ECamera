#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-line-error-frame-0049-candidate'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
BOOT=Path('/boot/sp11-7.1.5-camera-e003h-csidframe-0049')
ENTRY=Path('/etc/grub.d/99p_sp11_camera_e003h_csidframe_0049')
EXPECTED={
 "asset_manifest": "6cf7a9f6985b9e584f323455c363d9e9b1b83085b7a7c3d97a46216aba5e53e9",
 "camss": "610c0def762e6449c342452ffc436b195cd1330a41055076d25cca95f077a1f5",
 "capsule": "6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20",
 "dtb": "019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f",
 "golden_initrd": "ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d",
 "golden_kernel": "bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a",
 "helper": "d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09",
 "linux_inspection": "e5d53e72e90406023616c2658f413ca80d6c49e9ff1f4622929012299eb17afe",
 "observer": "2081159e5a28a02fa79a933c83fe0838a6efe778f1ccdd85a804c6f3d8ec9b3e",
 "patch": "58f9080b7ae1e9addbfb035930374d073a1694c0a666132dcd1604e13b14f4e3",
 "sensor": "389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388",
 "setup": "666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f",
 "watch": "8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84"
}
SCRIPTS={
 "install-candidate.sh": "3815c1da8f9dd6bb17d1e1f2a66eadf5b2ceb9028684a82e1a9d1d596461b1b4",
 "load-candidate.sh": "fb575ac7f5b70df7a2f55887249e9d41298ac65a7dcfe8f2d0fde44d23a053e5",
 "preflight.sh": "50dde818be68610c3c39fe9a1fcb909f28ce3f670262c91975a68f30e742dcd4",
 "run-once.sh": "7d3918a120670b9d0f62c733bcc361027eff718f7befb865c5edefe4421e8d41",
 "runtime-preflight.sh": "3b2af8145eca9b69b7ea4a66b9b1180aa39a69d9636d988eeaadb083370dae54",
 "setup-media.sh": "b37d7f725b8aa4bcb8fb2b415c47c7c4c0f76f1101cb34b97dc57a6956c8284c",
 "start-observer.sh": "e30fd5d7943505b887d68b5bc602afa68af735dc9b77d9dfb80770cb31f96d2a"
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
 if sha(STATIC/'0049-x1e-csid1-line-error-frame-readonly.patch')!=EXPECTED['patch']: die('patch drift')
 if sha(STATIC/'windows-csid1-line-count-error/windows-csid1-line-count-error-oracle.json')!=EXPECTED['observer']: die('observer oracle drift')
 if sha(STATIC/'linux-0049-csid1-line-error-frame-readonly-inspection.json')!=EXPECTED['linux_inspection']: die('Linux inspection drift')
 li=json.loads((STATIC/'linux-0049-csid1-line-error-frame-readonly-inspection.json').read_text())
 if not li.get('accepted') or li.get('runtime_authorized') is not False: die('0049 inspection policy drift')
 if li.get('new_mmio_reads')!=3 or li.get('new_mmio_writes')!=0 or li.get('hardware_programming_changed') is not False: die('0049 read-only contract drift')
 am=json.loads((NEW/'asset-manifest.json').read_text())
 if not am.get('accepted') or am.get('runtime_authorized') is not False: die('asset manifest policy drift')
 if am.get('static_commit')!='073f6ee053eefa80493e80a85f5cfa80e9207b91': die('asset static commit drift')
 if (NEW/'AUTHORIZATION.json').exists(): die('authorization exists at package-only gate')
 pre=(NEW/'preflight.sh').read_text()
 if any(x in pre for x in ('insmod ','modprobe ','e003h_pix_run_once')): die('package preflight contains activation')
 install=(NEW/'install-candidate.sh').read_text()
 if any('grub-reboot ' in l and not l.lstrip().startswith('#') for l in install.splitlines()): die('installer can arm next boot')
 runtime=(NEW/'runtime-preflight.sh').read_text()
 for x in ('AUTHORIZATION.json','repo/origin divergence','RUN log already exists; refusing retry','module already loaded','sp11_camera_e003h_csidframe_0049=1','next_entry must be empty'):
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
 installed={'kernel':sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+'),'initrd':sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-csidframe-0049'),'dtb':sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')}
 if installed!={'kernel':EXPECTED['golden_kernel'],'initrd':EXPECTED['golden_initrd'],'dtb':EXPECTED['dtb']}: die('installed boot drift')
 entry=cmd(['sudo','-n','cat',str(ENTRY)])
 for x in ('sp11-camera-e003h-csidframe-0049-one-shot','sp11_camera_e003h_csidframe_0049=1','CSID1 line-error frame telemetry 0049',str(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')):
  if x not in entry: die('installed entry missing '+x)
 subprocess.check_call(['python3',str(REPO/'tools/check-front-parity-provenance.py'),'--repo',str(REPO),'--target','bounded_first_pix'],stdout=subprocess.DEVNULL)
 out={'schema':'sp11-e003h-csid1-line-error-frame-0049-package-v1','accepted':True,'hashes':EXPECTED,'runtime_scripts':SCRIPTS,'installed_boot':installed,'boot_id':'sp11-camera-e003h-csidframe-0049-one-shot','front_only_ports':ports,'golden_saved_default':True,'candidate_boot_installed':True,'candidate_boot_armed':False,'camera_modules_loaded':False,'authorization_present':False,'bounded_provenance_green':True,'frozen_runtime_assets':True,'new_mmio_reads':3,'new_mmio_writes':0,'hardware_programming_changed':False,'runtime_preflight_before_module_load':True,'single_helper_invocation_enforced':True,'same_boot_retry_refused_by_runlog':True,'runtime_authorized':False,'next':'commit/push unarmed package; fresh authorization review required'}
 (NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: 0049 line-error frame telemetry package is installed, frozen, Golden-safe and unarmed')
if __name__=='__main__': main()
