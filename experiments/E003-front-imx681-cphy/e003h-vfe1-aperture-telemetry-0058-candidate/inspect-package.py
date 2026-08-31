#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera'); NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-aperture-telemetry-0058-candidate'; STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-aperture-telemetry-0058-static'; BASE=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-sp11-active-start-prefix-0057-candidate/runtime-0057-analysis.json'; BOOT=Path('/boot/sp11-7.1.5-camera-e003h-vfeap-0058'); ENTRY=Path('/etc/grub.d/99v_sp11_camera_e003h_vfeap_0058')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cmd(x): return subprocess.check_output(x,text=True,stderr=subprocess.DEVNULL).strip()
def die(x): raise SystemExit('FAIL: '+x)
m=json.loads((NEW/'asset-manifest.json').read_text()); si=json.loads((STATIC/'0058-static-inspection.json').read_text()); b=json.loads(BASE.read_text())
if not m['accepted'] or m['runtime_authorized'] or m['static_commit']!='d7fe3bc4b98fab0b39c6f2681459f4acf28f3a72': die('manifest policy')
for r,h in m['assets'].items():
    if sha(NEW/r)!=h: die('asset '+r)
if sha(STATIC/'0058-static-inspection.json')!=m['static_inspection_sha256'] or not si['accepted'] or si['hardware_programming_delta']!='none': die('static')
if sha(BASE)!=m['consumed_0057_analysis_sha256'] or not b['accepted'] or not b['authorization_consumed']: die('0057 baseline')
if m['assets']['qcom-camss.ko']!='3fd0ebdc8a3f17fdc49e117d77fa10e03711dfbd27bc552e79230540f1cef80c' or m['assets']['imx681.ko']!='a12693a18bf2e4108dd309af68da189a2ea394a734a0c6a3c1d624ac44dea3dc': die('camera binary drift')
if m['behavior_delta']!={'camera_programming':'none_vs_0057','external_vfe_reads':True,'new_mmio_reads_in_camera_module':0,'new_mmio_writes':0,'vfe_base':'0x0ac71000','vfe_size':'0x4000'}: die('behavior delta')
watch=(NEW/'watch-vfe1-aperture.py').read_text()
for bad in ('O_RDWR','PROT_WRITE','mm.write'):
    if bad in watch: die('watcher writable '+bad)
if 'os.O_RDONLY|os.O_SYNC' not in watch or 'prot=mmap.PROT_READ' not in watch: die('watcher read-only contract')
for s in ['preflight.sh','install-candidate.sh','runtime-preflight.sh','load-candidate.sh','setup-pix-media.sh','start-observer.sh','start-vfe-observer.sh','run-once.sh']:
    subprocess.check_call(['bash','-n',str(NEW/s)],stdout=subprocess.DEVNULL)
install=(NEW/'install-candidate.sh').read_text(); run=(NEW/'run-once.sh').read_text(); load=(NEW/'load-candidate.sh').read_text(); runtime=(NEW/'runtime-preflight.sh').read_text()
if 'grub-reboot' in install: die('installer can arm')
if load.find('"$NEW/runtime-preflight.sh"') > min(x for x in [load.find('modprobe'),load.find('insmod')] if x>=0): die('preflight order')
if run.count('sudo -n "$HELPER"')!=1 or 'CAMERA_PROGRAMMING_DELTA=NONE_VS_0057' not in run or 'VFE watcher not ready' not in run or 'RT-CDM watcher not ready' not in run or "trap 'sync; sudo -n systemctl reboot' EXIT" not in run: die('run contract')
for q in ('persistent_vfe_aperture_observer_required','NONE_VS_CONSUMED_0057_READ_ONLY_VFE_APERTURE_TELEMETRY','prior runtime artifact exists'):
    if q not in runtime: die('runtime contract '+q)
if (NEW/'AUTHORIZATION.json').exists() or (NEW/'RUNTIME-VFEAP-0058-RUN.txt').exists(): die('auth/runtime exists')
env=cmd(['grub-editenv','list']).splitlines()
if 'saved_entry=sp11-audio-fullio-v19c' not in env or any(x.startswith('next_entry=') and x!='next_entry=' for x in env): die('GRUB state')
for mod in ('qcom_camss','imx681','ov13858'):
    if Path('/sys/module/'+mod).exists(): die('module loaded '+mod)
if not BOOT.is_dir() or not ENTRY.is_file(): die('not installed')
if sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+')!='bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a': die('kernel')
if sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-vfeap-0058')!='ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d': die('initrd')
if sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')!=m['assets']['x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb']: die('dtb')
entry=cmd(['sudo','-n','cat',str(ENTRY)])
for q in ('sp11-camera-e003h-vfeap-0058-one-shot','sp11_camera_e003h_vfeap_0058=1','read-only VFE1 aperture telemetry 0058'):
    if q not in entry: die('entry '+q)
head=cmd(['git','-C',str(REPO),'rev-parse','HEAD']); origin=cmd(['git','-C',str(REPO),'rev-parse','origin/experiment/e003-front-imx681-cphy'])
if head!=origin: die('origin')
subprocess.check_call(['git','-C',str(REPO),'merge-base','--is-ancestor',m['static_commit'],head],stdout=subprocess.DEVNULL)
out={'schema':'sp11-e003h-vfe1-aperture-0058-package-inspection-v1','accepted':True,'static_commit':m['static_commit'],'asset_manifest_sha256':sha(NEW/'asset-manifest.json'),'static_inspection_sha256':sha(STATIC/'0058-static-inspection.json'),'consumed_0057_analysis_sha256':sha(BASE),'camera_modules_byte_identical_to_0057':True,'camera_programming_delta':'none_vs_0057','external_vfe_aperture_read_only':True,'candidate_boot_installed':True,'candidate_boot_armed':False,'golden_saved_default':True,'authorization_present':False,'prior_run_present':False,'persistent_rtcdm_observer_required':True,'persistent_vfe_aperture_observer_required':True,'single_helper_invocation_enforced':True,'same_boot_retry_refused':True,'mandatory_golden_reboot':True,'runtime_authorized':False}
(NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); print('PASS: 0058 installed, Golden-safe, unarmed, telemetry-only')
