#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path('/home/geoca/Documents/SP11-PROJECT'); REPO=ROOT/'06-camera/SP11X1ECamera'
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-candidate'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-static'
CAP=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-imx681-mode-selection-capture-20260831/windows-imx681-mode-selection-oracle.json'
BOOT=Path('/boot/sp11-7.1.5-camera-e003h-mode2-0054'); ENTRY=Path('/etc/grub.d/99r_sp11_camera_e003h_mode2_0054')
STATIC_COMMIT='c690f67548dcce57ba6f017d98be836233a575e7'; GOLDEN_K='bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a'; GOLDEN_I='ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def cmd(a): return subprocess.check_output(a,text=True,stderr=subprocess.DEVNULL).strip()
def main():
 m=json.loads((NEW/'asset-manifest.json').read_text());
 if not m.get('accepted') or m.get('runtime_authorized') is not False or m.get('static_commit')!=STATIC_COMMIT: die('manifest policy/static commit')
 for rel,h in m['assets'].items():
  if sha(NEW/rel)!=h: die('asset hash '+rel)
 si=json.loads((STATIC/'0054-static-inspection.json').read_text())
 if sha(STATIC/'0054-static-inspection.json')!=m['static_proof']['0054_inspection'] or not si.get('accepted') or si.get('runtime_authorized') is not False: die('static inspection')
 if si['sensor']['module_sha256']!=m['assets']['imx681.ko'] or si['camss']['module_sha256']!=m['assets']['qcom-camss.ko']: die('module/static binding')
 if not si['sensor']['windows_pair_equality'] or si['sensor']['mode_pairs']!=68 or si['sensor']['changed_values']!=7: die('sensor mode2 proof')
 if si['camss']['geometry_gate_changes']!=3 or si['camss']['new_mmio_writes']!=0 or si['camss']['hardware_programming_values_changed'] is not False: die('CAMSS static contract')
 cap=json.loads(CAP.read_text())
 if sha(CAP)!=m['static_proof']['windows_mode_selection_oracle'] or cap['full_firmware_match']['matching_resolution_indices']!=[2]: die('Windows selection oracle')
 b=m['behavior_delta']
 if not (b['sensor_resolution_index_old']==0 and b['sensor_resolution_index_new']==2 and b['sensor_geometry_new']=='3840x2160' and b['sensor_changed_register_values']==7 and b['sensor_mode_pairs']==68 and b['windows_pair_equality'] is True and b['camss_geometry_gate_changes']==3 and b['new_camss_mmio_writes']==0 and b['csid_programming_values_changed'] is False): die('manifest behavior delta')
 if (NEW/'AUTHORIZATION.json').exists(): die('authorization exists at package gate')
 if (NEW/'RUNTIME-MODE2-0054-RUN.txt').exists(): die('prior RUN exists')
 scripts=['preflight.sh','install-candidate.sh','runtime-preflight.sh','load-candidate.sh','setup-media.sh','setup-pix-media.sh','start-observer.sh','run-once.sh']
 shashes={x:sha(NEW/x) for x in scripts}
 for x in scripts: subprocess.check_call(['bash','-n',str(NEW/x)],stdout=subprocess.DEVNULL)
 pre=(NEW/'preflight.sh').read_text(); install=(NEW/'install-candidate.sh').read_text(); runtime=(NEW/'runtime-preflight.sh').read_text(); load=(NEW/'load-candidate.sh').read_text(); run=(NEW/'run-once.sh').read_text(); setup=(NEW/'setup-pix-media.sh').read_text()
 for q in ('insmod "$CAMSS"','insmod "$SENSOR"','sudo -n "$HELPER"','tee "$TRIGGER"'):
  if q in pre: die('preflight activates '+q)
 if any('grub-reboot ' in x and not x.lstrip().startswith('#') for x in install.splitlines()): die('installer arms boot')
 for q in ('AUTHORIZATION.json','RUN log already exists; refusing retry','module already loaded','sp11_camera_e003h_mode2_0054=1','next_entry must be empty'):
  if q not in runtime: die('runtime preflight missing '+q)
 call=load.find('"$NEW/runtime-preflight.sh"'); starts=[x for x in (load.find('sudo -n modprobe'),load.find('sudo -n insmod'),load.find('modprobe "$m"'),load.find('insmod "$CAMSS"')) if x>=0]
 if call<0 or not starts or call>min(starts): die('runtime preflight not before module load')
 if run.count('sudo -n "$HELPER"')!=1 or 'RUN log already exists; refusing retry' not in run or 'watcher not ready' not in run or 'RT-CDM diagnostic not idle before RUN' not in run or 'systemctl reboot' not in run: die('run-once contract')
 if '3840x2160' not in setup or '3840x2640' in setup: die('media geometry contract')
 dtb=NEW/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'; ports=cmd(['fdtget','-l',str(dtb),'/soc@0/isp@acb7000/ports']).split();
 if ports!=['port@2']: die('front-only DT')
 iommu=cmd(['fdtget','-t','x',str(dtb),'/soc@0/isp@acb7000','iommus']).split();
 if iommu!=['3d','800','60','3d','820','60','3d','840','60','3d','860','60','3d','18a0','0']: die('IOMMU set')
 env=cmd(['grub-editenv','list']).splitlines();
 if 'saved_entry=sp11-audio-fullio-v19c' not in env or any(x.startswith('next_entry=') and x!='next_entry=' for x in env): die('GRUB default/arming')
 for mod in ('qcom_camss','imx681','ov13858'):
  if Path('/sys/module/'+mod).exists(): die(mod+' loaded')
 if sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+')!=GOLDEN_K or sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-mode2-0054')!=GOLDEN_I or sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')!=m['assets']['x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb']: die('installed boot hashes')
 entry=cmd(['sudo','-n','cat',str(ENTRY)])
 for q in ('sp11-camera-e003h-mode2-0054-one-shot','sp11_camera_e003h_mode2_0054=1','Windows-selected IMX681 mode2 0054',str(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')):
  if q not in entry: die('entry missing '+q)
 subprocess.check_call(['python3',str(REPO/'tools/check-front-parity-provenance.py'),'--repo',str(REPO),'--target','bounded_first_pix'],stdout=subprocess.DEVNULL)
 head=cmd(['git','-C',str(REPO),'rev-parse','HEAD']); origin=cmd(['git','-C',str(REPO),'rev-parse','origin/experiment/e003-front-imx681-cphy'])
 if head!=origin: die('HEAD/origin divergence')
 subprocess.check_call(['git','-C',str(REPO),'merge-base','--is-ancestor',STATIC_COMMIT,head],stdout=subprocess.DEVNULL)
 out={'schema':'sp11-e003h-imx681-mode2-0054-package-v1','accepted':True,'static_commit':STATIC_COMMIT,'asset_manifest_sha256':sha(NEW/'asset-manifest.json'),'assets':m['assets'],'runtime_scripts':shashes,'static_inspection_sha256':sha(STATIC/'0054-static-inspection.json'),'windows_oracle_sha256':sha(CAP),'candidate_boot_installed':True,'candidate_boot_armed':False,'boot_id':'sp11-camera-e003h-mode2-0054-one-shot','cmdline_marker':'sp11_camera_e003h_mode2_0054=1','golden_saved_default':True,'camera_modules_loaded':False,'authorization_present':False,'prior_run_present':False,'bounded_provenance_green':True,'sensor_resolution_index':2,'sensor_geometry':'3840x2160@30','sensor_windows_pairs':68,'sensor_changed_values':7,'camss_geometry_gate_changes':3,'new_camss_mmio_writes':0,'csid_programming_values_changed':False,'runtime_preflight_before_module_load':True,'single_helper_invocation_enforced':True,'same_boot_retry_refused_by_runlog':True,'persistent_rtcdm_observer_required':True,'mandatory_golden_reboot_after_run':True,'runtime_authorized':False,'next':'commit/push unarmed package; fresh authorization review required'}
 (NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print('PASS: 0054 mode2 package is installed, Golden-safe, inspected and unarmed')
if __name__=='__main__': main()
