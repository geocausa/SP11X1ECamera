#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-clock-rate-0052-candidate'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
BOOT=Path('/boot/sp11-7.1.5-camera-e003h-csidclk-0052')
ENTRY=Path('/etc/grub.d/99p_sp11_camera_e003h_csidclk_0052')
STATIC_COMMIT='23ea4ce8b6ddc2bc76e15f2121087eeef34b8484'
EXPECTED={
 'asset_manifest':'18d65aa6734ca1634a19607e1c377ac7b281bb26f1891bcf758e4594fea06974',
 'camss':'42662121c848d863b06e3aba737e0f80a35fc047faf8cf5b0f47e2554ba3e92a',
 'sensor':'389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'capsule':'6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20',
 'helper':'d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09',
 'setup':'666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f',
 'watch':'8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84',
 'patch':'55c27634af4837e615145a7df9f4e92119b75c7a5b53957fa5864ddd16266788',
 'linux_inspection':'e20bf446fde42298988c586b941e4c96ec8017f8c67bc4a396b824f359f676ad',
 'clock_hbi_oracle':'f913e0dd3766077cfa9cf6875f77d7494bfe60a1bceea0ffe9f9c928d7d00dd0',
 'completed_eof_oracle':'db4476e159872f9005a127d84ea41032191402de2709a0835d2c2c5fbc9dffde',
 'runtime0051':'2e1fbd740073b98e9e86ef477f1986d9b7e94a26a5e486f4386197b8e331f9d1',
 'provenance':'803d09be7a18b321b07db7dac5a81d837dd09be7e8ffb6a20' if False else '803d09be7a18b321b07db7dac5a81d837dd09b1f6dfd883b2f27daefa7e8ffb6',
 'golden_kernel':'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
 'golden_initrd':'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
}
SCRIPTS={
 'install-candidate.sh':'7e038947391b77aead3bd3801821bc414168f1de35be6d3236969d0c366137a0',
 'load-candidate.sh':'cab8c68067de894ac141b139879d2041f46a5dd8ff9589d2c17d96667e26721b',
 'preflight.sh':'6e3f9f3974291930742a152629cfd18e1201feade2318ee4e4603b89cbc9be04',
 'run-once.sh':'8c1ce2b252e1be96f708bb357c7f7fef6224e8222e8617fbd4eb19ec720220ed',
 'runtime-preflight.sh':'0ed598ad9799ed5c74a2932a2e701c4a96edf360cbf2e325c9fcc39abcebdd55',
 'setup-media.sh':'0d38ec3c1831678d1679018670ce221f7924b9e3287146820ffe449b42113e3d',
 'start-observer.sh':'8815c76864934c838a46a093179e9f8c2c1529182b4518dd602a442a8f0f934f',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def cmd(a): return subprocess.check_output(a,text=True,stderr=subprocess.DEVNULL).strip()
def main():
 files={
  'camss':NEW/'qcom-camss.ko','sensor':NEW/'imx681.ko','dtb':NEW/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb',
  'capsule':NEW/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin','helper':NEW/'e003h-pix-one-shot',
  'setup':NEW/'setup-pix-media.sh','watch':NEW/'watch-rtcdm-stage.py','asset_manifest':NEW/'asset-manifest.json'}
 for k,p in files.items():
  g=sha(p)
  if g!=EXPECTED[k]: die(f'{k} hash drift {g}')
 for n,h in SCRIPTS.items():
  g=sha(NEW/n)
  if g!=h: die(f'{n} hash drift {g}')
 proof={
  'patch':STATIC/'0052-x1e-front-csid-link-clock-rate.patch',
  'linux_inspection':STATIC/'linux-0052-x1e-front-link-clock-rate-inspection.json',
  'clock_hbi_oracle':STATIC/'x1e-csid-clock-hbi-correlation/x1e-csid-clock-hbi-correlation-oracle.json',
  'completed_eof_oracle':STATIC/'windows-linux-first-eof-geometry-boundary/first-eof-geometry-boundary-oracle.json',
  'runtime0051':REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-rupdone-no-regupdate-0051-candidate/runtime-0051-analysis.json',
  'provenance':REPO/'provenance/front-parity.json'}
 for k,p in proof.items():
  g=sha(p)
  if g!=EXPECTED[k]: die(f'{k} proof hash drift {g}')
 li=json.loads(proof['linux_inspection'].read_text())
 if not li.get('accepted') or li.get('runtime_authorized') is not False: die('0052 inspection policy drift')
 if li.get('module_sha256')!=EXPECTED['camss']: die('0052 module binding drift')
 if li.get('old_requested_rate_hz')!=300000000 or li.get('new_link_derived_rate_hz')!=400000000: die('0052 rate delta drift')
 if li.get('scope')!={'soc':'X1E80100','csid':1,'csiphy':2,'phy':'C-PHY','trios':1,'clock_names':['csid','csid_csiphy_rx']}: die('0052 scope drift')
 if li.get('new_mmio_reads')!=0 or li.get('new_mmio_writes')!=0 or li.get('new_register_values')!=0: die('0052 MMIO contract drift')
 if li.get('clock_tables_changed') is not False or li.get('clock_margin_changed') is not False: die('0052 clock policy drift')
 for k in ('crop_changed','rup_aup_changed','irq_changed','vfe_changed','rtcdm_changed','csiphy_programming_changed','sensor_changed','dt_changed'):
  if li.get(k) is not False: die('0052 changed forbidden domain '+k)
 if li.get('direct_windows_400mhz_vote_proven') is not False or li.get('hbi_400_300_correlation_proven') is not True: die('0052 evidence provenance drift')
 co=json.loads(proof['clock_hbi_oracle'].read_text())
 if not co.get('accepted') or co['classification']['linux_x1e_front_csid_300mhz_request_proven'] is not True or co['classification']['linux_link_derived_required_rate_is_400mhz'] is not True: die('clock/HBI oracle drift')
 eo=json.loads(proof['completed_eof_oracle'].read_text())
 if not eo.get('accepted') or eo['classification']['prior_first_epoch_geometry_divergence_boundary_superseded'] is not True: die('EOF boundary oracle drift')
 am=json.loads((NEW/'asset-manifest.json').read_text())
 if not am.get('accepted') or am.get('runtime_authorized') is not False or am.get('static_commit')!=STATIC_COMMIT: die('asset manifest policy drift')
 if am['behavior_delta']!={'old_clock_request_hz':300000000,'new_link_derived_clock_request_hz':400000000,'direct_windows_400mhz_vote_proven':False}: die('asset behavior delta drift')
 if (NEW/'AUTHORIZATION.json').exists(): die('authorization exists at package-only gate')
 pre=(NEW/'preflight.sh').read_text()
 for q in ('insmod "$CAMSS"','insmod "$SENSOR"','sudo -n "$HELPER"','tee "$TRIGGER"'):
  if q in pre: die('package preflight contains activation '+q)
 install=(NEW/'install-candidate.sh').read_text()
 if any('grub-reboot ' in l and not l.lstrip().startswith('#') for l in install.splitlines()): die('installer can arm next boot')
 runtime=(NEW/'runtime-preflight.sh').read_text()
 for q in ('AUTHORIZATION.json','repo/origin divergence','RUN log already exists; refusing retry','module already loaded','sp11_camera_e003h_csidclk_0052=1','next_entry must be empty'):
  if q not in runtime: die('runtime preflight missing '+q)
 if 'insmod "$CAMSS"' in runtime or 'modprobe "$m"' in runtime or 'tee "$TRIGGER"' in runtime: die('runtime preflight activates hardware')
 load=(NEW/'load-candidate.sh').read_text()
 call=load.find('"$NEW/runtime-preflight.sh"')
 starts=[x for x in (load.find('sudo -n modprobe'),load.find('sudo -n insmod'),load.find('modprobe "$m"'),load.find('insmod "$CAMSS"')) if x>=0]
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
 installed={
  'kernel':sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+'),
  'initrd':sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-csidclk-0052'),
  'dtb':sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')}
 if installed!={'kernel':EXPECTED['golden_kernel'],'initrd':EXPECTED['golden_initrd'],'dtb':EXPECTED['dtb']}: die('installed boot drift')
 entry=cmd(['sudo','-n','cat',str(ENTRY)])
 for q in ('sp11-camera-e003h-csidclk-0052-one-shot','sp11_camera_e003h_csidclk_0052=1','CSID1 clock-rate correction 0052',str(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')):
  if q not in entry: die('installed entry missing '+q)
 subprocess.check_call(['python3',str(REPO/'tools/check-front-parity-provenance.py'),'--repo',str(REPO),'--target','bounded_first_pix'],stdout=subprocess.DEVNULL)
 head=cmd(['git','-C',str(REPO),'rev-parse','HEAD'])
 subprocess.check_call(['git','-C',str(REPO),'merge-base','--is-ancestor',STATIC_COMMIT,head],stdout=subprocess.DEVNULL)
 out={
  'schema':'sp11-e003h-csid1-clock-rate-0052-package-v1','accepted':True,'hashes':EXPECTED,'runtime_scripts':SCRIPTS,
  'static_commit':STATIC_COMMIT,'installed_boot':installed,'boot_id':'sp11-camera-e003h-csidclk-0052-one-shot',
  'cmdline_marker':'sp11_camera_e003h_csidclk_0052=1','front_only_ports':ports,
  'golden_saved_default':True,'candidate_boot_installed':True,'candidate_boot_armed':False,'camera_modules_loaded':False,
  'authorization_present':False,'bounded_provenance_green':True,'frozen_runtime_assets':True,
  'old_clock_request_hz':300000000,'new_link_derived_clock_request_hz':400000000,
  'direct_windows_400mhz_vote_proven':False,'hbi_400_300_correlation_proven':True,
  'new_mmio_reads':0,'new_mmio_writes':0,'new_register_values':0,'camera_register_programming_changed':False,
  'runtime_preflight_before_module_load':True,'single_helper_invocation_enforced':True,'same_boot_retry_refused_by_runlog':True,
  'runtime_authorized':False,'next':'commit/push unarmed package; fresh authorization review required'}
 (NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: 0052 CSID clock-rate package is installed, frozen, Golden-safe and unarmed')
if __name__=='__main__': main()
