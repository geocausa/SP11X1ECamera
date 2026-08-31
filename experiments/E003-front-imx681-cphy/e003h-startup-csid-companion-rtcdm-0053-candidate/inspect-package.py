#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-startup-csid-companion-rtcdm-0053-candidate'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
BOOT=Path('/boot/sp11-7.1.5-camera-e003h-csidcomp-0053')
ENTRY=Path('/etc/grub.d/99q_sp11_camera_e003h_csidcomp_0053')
STATIC_COMMIT='d977480aa80c4b5a115d263c15e5c79caa810e69'
EXPECTED={
 'asset_manifest':'7c113067728a99c46f8a01dd6e68d60fa77a09e810077e05c9ffab5dcf409d52',
 'camss':'f04189d766f478083e09fd38b26e73c99c03306ce1f2fb81d68b2ebd0d2be876',
 'sensor':'389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'capsule':'6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20',
 'helper':'d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09',
 'setup':'666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f',
 'watch':'8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84',
 'patch':'dba1d21fdc01f4091af89ce051283464661952ce2d1acd1f59afb75c8b52cfd6',
 'linux_inspection':'72ceb0880f673bc1d17698eb228612a88b8bf4683b8f034a9de4f1b784120fea',
 'transport_oracle':'4b70a61a2e226b37d9310b4b4dee4d77c7516f975498973ee89dc29d772e2e5c',
 'runtime0052':'4367b9fe31552baf59cd7212743585fc990a07638794a81da178a22e1591ddba',
 'provenance':'803d09be7a18b321b07db7dac5a81d837dd09b1f6dfd883b2f27daefa7e8ffb6',
 'golden_kernel':'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
 'golden_initrd':'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
}
SCRIPTS={
 'install-candidate.sh':'20b123fb67ef88329fbd93db3556a16b67ddabf72894b5d8a4a9e1adee2a251b',
 'load-candidate.sh':'bd4bb1cf3cd4d607f21e9d1ddad7d3a75100568d01577d71de2d861e7088cd18',
 'preflight.sh':'8ea0f2e3a098f8609b86e9bc91db05944128bd916373d2be1288a4d7ef7c150d',
 'run-once.sh':'3b9c017921b0c62fb9895082015d3f31a617dfd578d7952446571b5807fd45a1',
 'runtime-preflight.sh':'bca94af1fc8e910cbb8ca07b0137b29ac6cd018285582bd9851929bffd0d0fa9',
 'setup-media.sh':'8b9eb6b64d8cf8ea083246fbfbf7c72f5cb99227efe9f7037b222468d810eba0',
 'start-observer.sh':'043dce8fc430ef320662927fa756036ae79743d5190b6174e73fd40c74cfd057',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def cmd(a): return subprocess.check_output(a,text=True,stderr=subprocess.DEVNULL).strip()
def main():
 files={'camss':NEW/'qcom-camss.ko','sensor':NEW/'imx681.ko','dtb':NEW/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb','capsule':NEW/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin','helper':NEW/'e003h-pix-one-shot','setup':NEW/'setup-pix-media.sh','watch':NEW/'watch-rtcdm-stage.py','asset_manifest':NEW/'asset-manifest.json'}
 for k,p in files.items():
  g=sha(p)
  if g!=EXPECTED[k]: die(f'{k} hash drift {g}')
 for n,h in SCRIPTS.items():
  g=sha(NEW/n)
  if g!=h: die(f'{n} hash drift {g}')
 proof={'patch':STATIC/'0053-x1e-startup-csid-companion-rtcdm-transport.patch','linux_inspection':STATIC/'linux-0053-startup-csid-companion-rtcdm-transport-inspection.json','transport_oracle':STATIC/'csid1-startup-companion-transport-0053/startup-companion-transport-0053-oracle.json','runtime0052':REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-clock-rate-0052-candidate/runtime-0052-analysis.json','provenance':REPO/'provenance/front-parity.json'}
 for k,p in proof.items():
  g=sha(p)
  if g!=EXPECTED[k]: die(f'{k} proof hash drift {g}')
 li=json.loads(proof['linux_inspection'].read_text()); o=json.loads(proof['transport_oracle'].read_text()); base=json.loads(proof['runtime0052'].read_text())
 if not li.get('accepted') or li.get('runtime_authorized') is not False: die('0053 inspection policy drift')
 if li.get('module_sha256')!=EXPECTED['camss']: die('0053 module binding drift')
 p=li['proved']
 if p['startup_packet_count']!=4 or p['startup_rtcdm_commits_per_packet']!=4: die('0053 packet/commit count drift')
 if p['startup_rtcdm_order']!=['CHANGE_BASE(VFE1)','IFE startup main','CHANGE_BASE(CSID1)','exact CSID descriptor-1 companion']: die('0053 order drift')
 if p['csid1_change_base']!='0x08057000': die('0053 encoded CSID base drift')
 if p['packet0_companion_sha256']!='1872731eaa3eb2233436029c2658682097c61ebf97e3facf46e31224ee25e2a2' or p['packet1_3_companion_sha256']!='45d059ec64587ea4f55eb8df64704520782801418c4a754f512831c7473fb5c7': die('0053 companion SHA drift')
 if p['cpu_startup_companion_calls_removed']!=4 or p['new_direct_mmio_reads']!=0 or p['new_direct_mmio_writes']!=0 or p['new_register_values']!=0: die('0053 transport-only contract drift')
 if li['classification']['crop_failure_causality_proven'] is not False: die('0053 causality overclaim')
 if not o.get('accepted') or o['windows']['csid1_change_base']!='0x00057000' or not o['classification']['transport_ownership_mismatch_proven'] or o['classification']['crop_failure_causality_proven'] is not False: die('transport oracle drift')
 if not base.get('accepted') or base['comparison_0051']['sequence_identical'] is not True or base['classification']['clock_correction_is_causal_for_vertical_crop_failure'] is not False: die('consumed 0052 baseline drift')
 am=json.loads((NEW/'asset-manifest.json').read_text())
 if not am.get('accepted') or am.get('runtime_authorized') is not False or am.get('static_commit')!=STATIC_COMMIT: die('asset manifest policy drift')
 bd=am['behavior_delta']
 if bd['startup_packets']!=4 or bd['new_register_values']!=0 or bd['new_direct_mmio_reads']!=0 or bd['new_direct_mmio_writes']!=0 or bd['crop_failure_causality_proven'] is not False: die('manifest behavior delta drift')
 if (NEW/'AUTHORIZATION.json').exists(): die('authorization exists at package-only gate')
 pre=(NEW/'preflight.sh').read_text()
 for q in ('insmod "$CAMSS"','insmod "$SENSOR"','sudo -n "$HELPER"','tee "$TRIGGER"'):
  if q in pre: die('package preflight contains activation '+q)
 install=(NEW/'install-candidate.sh').read_text()
 if any('grub-reboot ' in l and not l.lstrip().startswith('#') for l in install.splitlines()): die('installer can arm next boot')
 runtime=(NEW/'runtime-preflight.sh').read_text()
 for q in ('AUTHORIZATION.json','repo/origin divergence','RUN log already exists; refusing retry','module already loaded','sp11_camera_e003h_csidcomp_0053=1','next_entry must be empty'):
  if q not in runtime: die('runtime preflight missing '+q)
 if 'insmod "$CAMSS"' in runtime or 'modprobe "$m"' in runtime or 'tee "$TRIGGER"' in runtime: die('runtime preflight activates hardware')
 load=(NEW/'load-candidate.sh').read_text(); call=load.find('"$NEW/runtime-preflight.sh"'); starts=[x for x in (load.find('sudo -n modprobe'),load.find('sudo -n insmod'),load.find('modprobe "$m"'),load.find('insmod "$CAMSS"')) if x>=0]
 if call<0 or not starts or call>min(starts): die('runtime preflight is not before first module load')
 run=(NEW/'run-once.sh').read_text()
 if run.count('sudo -n "$HELPER"')!=1: die('helper invocation count drift')
 for q in ('AUTHORIZATION.json','RUN log already exists; refusing retry','watcher not ready','RT-CDM diagnostic not idle before RUN'):
  if q not in run: die('run wrapper missing '+q)
 if 'systemctl reboot' not in run: die('mandatory reboot missing')
 ports=cmd(['fdtget','-l',str(files['dtb']),'/soc@0/isp@acb7000/ports']).split()
 if ports!=['port@2']: die('DT not front-only')
 iommu=cmd(['fdtget','-t','x',str(files['dtb']),'/soc@0/isp@acb7000','iommus']).split()
 if iommu!=['3d','800','60','3d','820','60','3d','840','60','3d','860','60','3d','18a0','0']: die('IOMMU set drift')
 reg=cmd(['fdtget','-t','x',str(files['dtb']),'/soc@0/isp@acb7000','reg'])
 if 'ac71000 0 f000' not in reg or 'ac26000 0 1000' not in reg: die('VFE1/RT-CDM1 resource drift')
 env=cmd(['grub-editenv','list']).splitlines()
 if 'saved_entry=sp11-audio-fullio-v19c' not in env: die('Golden saved_entry drift')
 if any(x.startswith('next_entry=') and x!='next_entry=' for x in env): die('candidate already armed')
 for m in ('qcom_camss','imx681','ov13858'):
  if Path('/sys/module/'+m).exists(): die(m+' loaded during inspection')
 installed={'kernel':sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+'),'initrd':sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-csidcomp-0053'),'dtb':sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')}
 if installed!={'kernel':EXPECTED['golden_kernel'],'initrd':EXPECTED['golden_initrd'],'dtb':EXPECTED['dtb']}: die('installed boot drift')
 entry=cmd(['sudo','-n','cat',str(ENTRY)])
 for q in ('sp11-camera-e003h-csidcomp-0053-one-shot','sp11_camera_e003h_csidcomp_0053=1','startup companion RT-CDM transport 0053',str(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')):
  if q not in entry: die('installed entry missing '+q)
 subprocess.check_call(['python3',str(REPO/'tools/check-front-parity-provenance.py'),'--repo',str(REPO),'--target','bounded_first_pix'],stdout=subprocess.DEVNULL)
 head=cmd(['git','-C',str(REPO),'rev-parse','HEAD']); origin=cmd(['git','-C',str(REPO),'rev-parse','origin/experiment/e003-front-imx681-cphy'])
 if head!=origin: die('HEAD/origin divergence at package inspection')
 subprocess.check_call(['git','-C',str(REPO),'merge-base','--is-ancestor',STATIC_COMMIT,head],stdout=subprocess.DEVNULL)
 out={'schema':'sp11-e003h-startup-csid-companion-rtcdm-0053-package-v1','accepted':True,'hashes':EXPECTED,'runtime_scripts':SCRIPTS,'static_commit':STATIC_COMMIT,'installed_boot':installed,'boot_id':'sp11-camera-e003h-csidcomp-0053-one-shot','cmdline_marker':'sp11_camera_e003h_csidcomp_0053=1','front_only_ports':ports,'golden_saved_default':True,'candidate_boot_installed':True,'candidate_boot_armed':False,'camera_modules_loaded':False,'authorization_present':False,'bounded_provenance_green':True,'frozen_runtime_assets':True,'startup_packets':4,'startup_rtcdm_commits_per_packet':4,'startup_transport':'VFE base -> main -> CSID1 base -> exact companion','new_mmio_reads':0,'new_mmio_writes':0,'new_register_values':0,'crop_failure_causality_proven':False,'runtime_preflight_before_module_load':True,'single_helper_invocation_enforced':True,'same_boot_retry_refused_by_runlog':True,'runtime_authorized':False,'next':'commit/push unarmed package; fresh authorization review required'}
 (NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: 0053 startup-CSID companion RT-CDM package is installed, frozen, Golden-safe and unarmed')
if __name__=='__main__': main()
