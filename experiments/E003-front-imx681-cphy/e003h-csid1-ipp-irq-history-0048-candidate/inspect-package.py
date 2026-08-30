#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-ipp-irq-history-0048-candidate'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
BOOT=Path('/boot/sp11-7.1.5-camera-e003h-csidirq-0048')
ENTRY=Path('/etc/grub.d/99o_sp11_camera_e003h_csidirq_0048')
EXPECTED={
 "asset_manifest": "b2a14e6491b16b22f6bc0bf9e44917c31ff4f7ab6d68204bc87a035b9f96f797",
 "camss": "94cc14d9702492bffa2b4e72989db45356cf59ffcce7f4c382be13e7130030b7",
 "capsule": "6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20",
 "dtb": "019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f",
 "golden_initrd": "ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d",
 "golden_kernel": "bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a",
 "helper": "d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09",
 "linux_inspection": "6e98360aa0a83c8c61db1e67bd5c12f4fb6c7856698f48aea404a23100de8eb2",
 "observer": "23bc970a9bacff901e1336208282904cb9c0add0dfd5bea311194caeacb5451d",
 "patch": "91d292888e563c2d4e0ffc65664cfa4b0a3225cb1f56af9053652998ff0be1d7",
 "sensor": "389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388",
 "setup": "666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f",
 "watch": "8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84"
}
SCRIPTS={
 "install-candidate.sh": "d34b063028aa13e771be141647cf4bae81f196d1d1002ae1e6a50e331d2506cf",
 "load-candidate.sh": "ae7372c025deb4386e1fdfa1d9fca0830380e953e9b274b8d3f16d3f7358f10a",
 "preflight.sh": "5a935a7b1af139802b8a78c99842c50d7b4b1f17fb1acd7491534001525d9f7b",
 "run-once.sh": "368afcb0974a3cbfeba3cd3737f22af7ff738a602049a84f837bea5d54970cc5",
 "runtime-preflight.sh": "30c219ad43196dd2ad594a3435927219fca91233a6022d7f24453f1101f6f83f",
 "setup-media.sh": "e0ed20ec5bd4356f45d78db282064872fefc12985d0edf77d94076a0c2a947ec",
 "start-observer.sh": "ca355595fdf8dff82d7397ab4323c2b8d90246a099a9f2922e8da85181706822"
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
 if sha(STATIC/'0048-x1e-csid1-ipp-irq-history-readonly.patch')!=EXPECTED['patch']: die('patch drift')
 if sha(STATIC/'windows-linux-irq-observer-integrity/irq-observer-integrity-oracle.json')!=EXPECTED['observer']: die('observer oracle drift')
 if sha(STATIC/'linux-0048-csid1-ipp-irq-history-inspection.json')!=EXPECTED['linux_inspection']: die('Linux inspection drift')
 li=json.loads((STATIC/'linux-0048-csid1-ipp-irq-history-inspection.json').read_text())
 if not li.get('accepted') or li.get('runtime_authorized') is not False: die('0048 inspection policy drift')
 if li.get('new_mmio_reads')!=0 or li.get('new_mmio_writes')!=0 or li.get('hardware_behavior_changed') is not False: die('0048 diagnostic-only contract drift')
 am=json.loads((NEW/'asset-manifest.json').read_text())
 if not am.get('accepted') or am.get('runtime_authorized') is not False: die('asset manifest policy drift')
 if am.get('static_commit')!='cbf40db7557e4a52e220494f633bc933abf3a079': die('asset static commit drift')
 if (NEW/'AUTHORIZATION.json').exists(): die('authorization exists at package-only gate')
 pre=(NEW/'preflight.sh').read_text()
 if any(x in pre for x in ('insmod ','modprobe ','e003h_pix_run_once')): die('package preflight contains activation')
 install=(NEW/'install-candidate.sh').read_text()
 if any('grub-reboot ' in l and not l.lstrip().startswith('#') for l in install.splitlines()): die('installer can arm next boot')
 runtime=(NEW/'runtime-preflight.sh').read_text()
 for x in ('AUTHORIZATION.json','repo/origin divergence','RUN log already exists; refusing retry','module already loaded','sp11_camera_e003h_csidirq_0048=1','next_entry must be empty'):
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
 installed={'kernel':sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+'),'initrd':sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-csidirq-0048'),'dtb':sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')}
 if installed!={'kernel':EXPECTED['golden_kernel'],'initrd':EXPECTED['golden_initrd'],'dtb':EXPECTED['dtb']}: die('installed boot drift')
 entry=cmd(['sudo','-n','cat',str(ENTRY)])
 for x in ('sp11-camera-e003h-csidirq-0048-one-shot','sp11_camera_e003h_csidirq_0048=1','CSID1 IPP IRQ history 0048',str(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')):
  if x not in entry: die('installed entry missing '+x)
 subprocess.check_call(['python3',str(REPO/'tools/check-front-parity-provenance.py'),'--repo',str(REPO),'--target','bounded_first_pix'],stdout=subprocess.DEVNULL)
 out={'schema':'sp11-e003h-csid1-ipp-irq-history-0048-package-v1','accepted':True,'hashes':EXPECTED,'runtime_scripts':SCRIPTS,'installed_boot':installed,'boot_id':'sp11-camera-e003h-csidirq-0048-one-shot','front_only_ports':ports,'golden_saved_default':True,'candidate_boot_installed':True,'candidate_boot_armed':False,'camera_modules_loaded':False,'authorization_present':False,'bounded_provenance_green':True,'frozen_runtime_assets':True,'new_mmio_reads':0,'new_mmio_writes':0,'hardware_behavior_changed':False,'runtime_preflight_before_module_load':True,'single_helper_invocation_enforced':True,'same_boot_retry_refused_by_runlog':True,'runtime_authorized':False,'next':'commit/push unarmed package; fresh authorization review required'}
 (NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: 0048 CSID IRQ-history package is installed, frozen, Golden-safe and unarmed')
if __name__=='__main__': main()
