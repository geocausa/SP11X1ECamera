#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-timeout-readonly-0046-candidate'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
BOOT=Path('/boot/sp11-7.1.5-camera-e003h-vfe1-0046')
ENTRY=Path('/etc/grub.d/99n_sp11_camera_e003h_vfe1_0046')
EXPECTED={
 'camss':'f1b5ce5dc973a140b29257927c02b2749f96f379fc01b78a10841443a15ab4be',
 'sensor':'389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'capsule':'6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20',
 'helper':'d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09',
 'setup':'666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f',
 'watch':'8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84',
 'asset_manifest':'1ff11cfafa93d6fd14c7b45ca2eb3e121231a43dd807e8b366d7e6296d1ade7e',
 'patch':'6ce9d732d73e6a09d73b756b1726b6f0e13702bede1d9ba0b61f9a5805d3b709',
 'oracle':'403f762c4d161823ca10deec27df733a50ca7d9d0d4aec4fb2cac05863ca6705',
 'linux_inspection':'2e9e0460e72567db162eaeac382fa7912656a85c2441ad582351e267f00edeca',
 'golden_kernel':'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
 'golden_initrd':'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
}
SCRIPTS={
 'preflight.sh':'ad8e5e596eacffaeb15e90aa92f6559ceae2a2bff40ce35c4f101aaa535d180d',
 'install-candidate.sh':'a205af7baf4ab45be4259a6944dc616615066c88ae34180ed0b265878947265c',
 'runtime-preflight.sh':'c187fdff230f92b80386622d1b03f5bf59720aaef0736d3648dd42149d250172',
 'load-candidate.sh':'e490791374d740e7ff5b0ddbd552926d5b678154082b0228887aea2cfe5ab54f',
 'setup-media.sh':'1eea4f94efe1648aac7a80a476ab51d7f1a23303a433b2bdcaac10ceed9b600b',
 'start-observer.sh':'7630bc0b2cd6bdcfa0bddddac6bea4197e482c95ccadb82d6e13a30fc6219940',
 'run-once.sh':'2f1548024fb18d75dfef8da8d6642c066d42b1dfd6a51cbb9e0d028a3738a36a',
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
 if sha(STATIC/'0046-x1e-vfe1-timeout-readonly-telemetry.patch')!=EXPECTED['patch']: die('patch drift')
 if sha(STATIC/'vfe1-timeout-readonly-telemetry-oracle.json')!=EXPECTED['oracle']: die('oracle drift')
 if sha(STATIC/'linux-0046-vfe1-timeout-readonly-inspection.json')!=EXPECTED['linux_inspection']: die('Linux inspection drift')
 li=json.loads((STATIC/'linux-0046-vfe1-timeout-readonly-inspection.json').read_text())
 if not li.get('accepted') or li.get('runtime_authorized') is not False or li.get('telemetry_read_count')!=30 or li.get('mmio_writes_added')!=0 or li.get('polling_primitives_added')!=0: die('0046 telemetry inspection policy drift')
 if (NEW/'AUTHORIZATION.json').exists(): die('authorization exists at package-only gate')
 pre=(NEW/'preflight.sh').read_text()
 if any(x in pre for x in ('insmod ','modprobe ','e003h_pix_run_once')): die('package preflight contains activation')
 install=(NEW/'install-candidate.sh').read_text()
 if any('grub-reboot ' in l and not l.lstrip().startswith('#') for l in install.splitlines()): die('installer can arm next boot')
 runtime=(NEW/'runtime-preflight.sh').read_text()
 for x in ('AUTHORIZATION.json','repo/origin divergence','RUN log already exists; refusing retry','module already loaded','sp11_camera_e003h_vfe1_0046=1','next_entry must be empty'):
  if x not in runtime: die('runtime preflight missing '+x)
 if 'insmod ' in runtime or 'modprobe ' in runtime or 'tee "$TRIGGER"' in runtime: die('runtime preflight activates hardware')
 load=(NEW/'load-candidate.sh').read_text(); call=load.find('"$NEW/runtime-preflight.sh"'); first=min(x for x in (load.find('modprobe '),load.find('insmod ')) if x>=0)
 if call<0 or call>first: die('runtime preflight is not before first module load')
 run=(NEW/'run-once.sh').read_text()
 if run.count('sudo -n "$HELPER"')!=1: die('helper invocation count drift')
 for x in ('AUTHORIZATION.json','RUN log already exists; refusing retry','watcher not ready','RT-CDM diagnostic not idle before RUN'):
  if x not in run: die('run wrapper missing '+x)
 if 'systemctl reboot' not in run: die('mandatory reboot missing')
 ports=cmd(['fdtget','-l',str(files['dtb']),'/soc@0/isp@acb7000/ports']).split()
 if ports!=['port@2']: die('DT not front-only')
 if cmd(['fdtget','-t','x',str(files['dtb']),'/soc@0/isp@acb7000','iommus']).split()!=['3d','800','60','3d','820','60','3d','840','60','3d','860','60','3d','18a0','0']: die('IOMMU set drift')
 env=cmd(['grub-editenv','list']).splitlines()
 if 'saved_entry=sp11-audio-fullio-v19c' not in env: die('Golden saved_entry drift')
 if any(x.startswith('next_entry=') and x!='next_entry=' for x in env): die('candidate already armed')
 for m in ('qcom_camss','imx681','ov13858'):
  if Path('/sys/module/'+m).exists(): die(m+' loaded during inspection')
 installed={'kernel':sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+'),'initrd':sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-vfe1-0046'),'dtb':sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')}
 if installed!={'kernel':EXPECTED['golden_kernel'],'initrd':EXPECTED['golden_initrd'],'dtb':EXPECTED['dtb']}: die('installed boot drift')
 entry=cmd(['sudo','-n','cat',str(ENTRY)])
 for x in ('sp11-camera-e003h-vfe1-0046-one-shot','sp11_camera_e003h_vfe1_0046=1',str(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')):
  if x not in entry: die('installed entry missing '+x)
 subprocess.check_call(['python3',str(REPO/'tools/check-front-parity-provenance.py'),'--repo',str(REPO),'--target','bounded_first_pix'],stdout=subprocess.DEVNULL)
 out={'schema':'sp11-e003h-vfe1-timeout-0046-package-v1','accepted':True,'hashes':EXPECTED,'runtime_scripts':SCRIPTS,'installed_boot':installed,'boot_id':'sp11-camera-e003h-vfe1-0046-one-shot','front_only_ports':ports,'golden_saved_default':True,'candidate_boot_installed':True,'candidate_boot_armed':False,'camera_modules_loaded':False,'authorization_present':False,'bounded_provenance_green':True,'frozen_runtime_assets':True,'telemetry_only_delta':True,'telemetry_reads':30,'mmio_writes_added':0,'runtime_preflight_before_module_load':True,'single_helper_invocation_enforced':True,'same_boot_retry_refused_by_runlog':True,'runtime_authorized':False,'next':'commit/push unarmed package; fresh authorization review required'}
 (NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: 0046 VFE1 telemetry package is installed, frozen, Golden-safe and unarmed')
if __name__=='__main__': main()
