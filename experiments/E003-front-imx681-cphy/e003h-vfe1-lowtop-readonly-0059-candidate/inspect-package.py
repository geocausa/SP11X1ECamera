#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera'); NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-lowtop-readonly-0059-candidate'; STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-lowtop-readonly-0059-static'; BASE=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-aperture-telemetry-0058-candidate/runtime-0058-analysis.json'
BOOT=Path('/boot/sp11-7.1.5-camera-e003h-vfelowtop-0059'); ENTRY=Path('/etc/grub.d/99w_sp11_camera_e003h_vfelowtop_0059'); STATIC_COMMIT='9d93a5e1362e2bce9f0a85b7f0977e1821c2f9b0'
GOLDEN_K='bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a'; GOLDEN_I='ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cmd(a): return subprocess.check_output(a,text=True,stderr=subprocess.DEVNULL).strip()
def die(s): raise SystemExit('FAIL: '+s)
m=json.loads((NEW/'asset-manifest.json').read_text()); si=json.loads((STATIC/'0059-static-inspection.json').read_text()); b=json.loads(BASE.read_text())
if not m['accepted'] or m['runtime_authorized'] is not False or m['static_commit']!=STATIC_COMMIT: die('manifest policy/static')
for r,h in m['assets'].items():
 if sha(NEW/r)!=h: die('asset hash '+r)
if sha(STATIC/'0059-static-inspection.json')!=m['static_inspection_sha256'] or not si['accepted'] or si['runtime_authorized'] is not False: die('static inspection')
if si['module_sha256']!=m['assets']['qcom-camss.ko'] or si['new_direct_mmio_reads']!=13 or si['new_mmio_writes']!=0 or si['camera_programming_changed'] is not False: die('static delta')
if sha(BASE)!=m['consumed_0058_analysis_sha256'] or not b['accepted'] or not b['authorization_consumed']: die('0058 baseline')
if b['classification']['new_programming_write_justified'] is not False: die('0058 programming classification')
bd=m['behavior_delta']
if bd['new_direct_mmio_reads']!=13 or bd['new_mmio_writes']!=0 or bd['camera_programming_changed'] is not False: die('manifest delta')
if (NEW/'AUTHORIZATION.json').exists(): die('authorization exists')
if (NEW/'RUNTIME-VFELOWTOP-0059-RUN.txt').exists(): die('prior RUN')
for x in ['preflight.sh','install-candidate.sh','runtime-preflight.sh','load-candidate.sh','setup-pix-media.sh','start-observer.sh','run-once.sh']:
 subprocess.check_call(['bash','-n',str(NEW/x)],stdout=subprocess.DEVNULL)
pre=(NEW/'preflight.sh').read_text(); ins=(NEW/'install-candidate.sh').read_text(); rp=(NEW/'runtime-preflight.sh').read_text(); load=(NEW/'load-candidate.sh').read_text(); run=(NEW/'run-once.sh').read_text(); setup=(NEW/'setup-pix-media.sh').read_text()
if 'grub-reboot' in ins: die('installer can arm')
for q in ('AUTHORIZATION.json','sp11_camera_e003h_vfelowtop_0059=1','next_entry'):
 if q not in rp: die('runtime preflight missing '+q)
call=load.find('"$NEW/runtime-preflight.sh"'); starts=[x for x in (load.find('modprobe'),load.find('insmod')) if x>=0]
if call<0 or not starts or call>min(starts): die('preflight after activation')
if run.count('sudo -n "$HELPER"')!=1 or 'RUN log already exists; refusing retry' not in run or "trap 'sync; sudo -n systemctl reboot' EXIT" not in run or 'TELEMETRY=IN_DRIVER_VFE1_LOWTOP_0059' not in run: die('run contract')
if '3840x2160' not in setup or '3840x2640' in setup: die('geometry')
dtb=NEW/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'
if cmd(['fdtget','-l',str(dtb),'/soc@0/isp@acb7000/ports']).split()!=['port@2']: die('front-only DT')
if cmd(['fdtget','-t','x',str(dtb),'/soc@0/isp@acb7000','iommus']).split()!=['3d','800','60','3d','820','60','3d','840','60','3d','860','60','3d','18a0','0']: die('IOMMU')
env=cmd(['grub-editenv','list']).splitlines()
if 'saved_entry=sp11-audio-fullio-v19c' not in env or any(x.startswith('next_entry=') and x!='next_entry=' for x in env): die('GRUB')
for mod in ('qcom_camss','imx681','ov13858'):
 if Path('/sys/module/'+mod).exists(): die(mod+' loaded')
if not BOOT.is_dir() or not ENTRY.is_file(): die('candidate not installed')
if sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+')!=GOLDEN_K or sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-vfelowtop-0059')!=GOLDEN_I or sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')!=m['assets']['x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb']: die('installed boot hashes')
entry=cmd(['sudo','-n','cat',str(ENTRY)])
for q in ('sp11-camera-e003h-vfelowtop-0059-one-shot','sp11_camera_e003h_vfelowtop_0059=1','VFE1 low-TOP read-only telemetry 0059'):
 if q not in entry: die('entry '+q)
subprocess.check_call(['python3',str(REPO/'tools/check-front-parity-provenance.py'),'--repo',str(REPO),'--target','bounded_first_pix'],stdout=subprocess.DEVNULL)
head=cmd(['git','-C',str(REPO),'rev-parse','HEAD']); origin=cmd(['git','-C',str(REPO),'rev-parse','origin/experiment/e003-front-imx681-cphy'])
if head!=origin: die('HEAD/origin')
subprocess.check_call(['git','-C',str(REPO),'merge-base','--is-ancestor',STATIC_COMMIT,head],stdout=subprocess.DEVNULL)
out={'schema':'sp11-e003h-vfe1-lowtop-0059-package-inspection-v1','accepted':True,'static_commit':STATIC_COMMIT,'static_inspection_sha256':sha(STATIC/'0059-static-inspection.json'),'consumed_0058_analysis_sha256':sha(BASE),'asset_manifest_sha256':sha(NEW/'asset-manifest.json'),'candidate_boot_installed':True,'candidate_boot_armed':False,'boot_id':'sp11-camera-e003h-vfelowtop-0059-one-shot','cmdline_marker':'sp11_camera_e003h_vfelowtop_0059=1','golden_saved_default':True,'authorization_present':False,'prior_run_present':False,'camera_modules_loaded':False,'new_direct_mmio_reads':13,'new_mmio_writes':0,'camera_programming_changed':False,'runtime_preflight_before_module_load':True,'single_helper_invocation_enforced':True,'same_boot_retry_refused':True,'persistent_rtcdm_observer_required':True,'mandatory_golden_reboot':True,'runtime_authorized':False}
(NEW/'package-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); print('PASS: 0059 installed, Golden-safe, unarmed, read-only telemetry')
