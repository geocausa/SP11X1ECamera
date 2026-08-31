#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera'); P=REPO/'experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-candidate'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def cmd(a): return subprocess.check_output(a,text=True,stderr=subprocess.DEVNULL).strip()
def main():
 au=json.loads((P/'AUTHORIZATION.json').read_text()); rv=json.loads((P/'AUTHORIZATION-REVIEW.json').read_text()); pkg=json.loads((P/'package-inspection.json').read_text()); man=json.loads((P/'asset-manifest.json').read_text())
 if not au.get('accepted') or not au.get('runtime_authorized') or au.get('production_parity_authorized') is not False: die('authorization policy')
 if not rv.get('accepted') or au['authorization_review_sha256']!=sha(P/'AUTHORIZATION-REVIEW.json'): die('review binding')
 if au['package_commit']!='95ee1d3feddf623004f92375de80f20f30822236' or rv['package_commit']!=au['package_commit']: die('package commit')
 if au['package_inspection_sha256']!=sha(P/'package-inspection.json') or not pkg.get('accepted') or pkg.get('candidate_boot_armed') is not False or pkg.get('runtime_authorized') is not False: die('package inspection binding')
 if au['bounded_provenance_sha256']!=sha(REPO/'provenance/front-parity.json'): die('provenance')
 subprocess.check_call(['git','-C',str(REPO),'merge-base','--is-ancestor',au['package_commit'],cmd(['git','-C',str(REPO),'rev-parse','HEAD'])],stdout=subprocess.DEVNULL)
 ex=au['execution_contract']
 if not (ex['boot_count']==1 and ex['root_helper_invocation_count']==1 and ex['same_boot_retry'] is False and ex['existing_run_log_refuses_execution'] is True and ex['persistent_rtcdm_observer_required'] is True and ex['after_any_helper_result']=='archive evidence then immediately reboot to Golden'): die('execution contract')
 if au['boot']!={'candidate_was_unarmed_at_authorization':True,'cmdline_marker':'sp11_camera_e003h_mode2_0054=1','golden_saved_default':'sp11-audio-fullio-v19c','id':'sp11-camera-e003h-mode2-0054-one-shot'}: die('boot contract')
 for k,rel in [('camss_sha256','qcom-camss.ko'),('sensor_sha256','imx681.ko'),('dtb_sha256','x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'),('capsule_sha256','firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin'),('helper_sha256','e003h-pix-one-shot')]:
  if au['candidate'][k]!=man['assets'][rel] or sha(P/rel)!=man['assets'][rel]: die('candidate '+k)
 st=au['static_evidence']
 if not (st['sensor_resolution_index']==2 and st['sensor_geometry']=='3840x2160@30' and st['sensor_mode_pairs']==68 and st['sensor_changed_values']==7 and st['windows_pair_equality'] is True and st['camss_geometry_gate_changes']==3 and st['new_camss_mmio_writes']==0 and st['csid_programming_values_changed'] is False): die('static evidence contract')
 if (P/'RUNTIME-MODE2-0054-RUN.txt').exists(): die('prior RUN')
 env=cmd(['grub-editenv','list']).splitlines()
 if 'saved_entry=sp11-audio-fullio-v19c' not in env or any(x.startswith('next_entry=') and x!='next_entry=' for x in env): die('candidate not unarmed at authorization inspection')
 for m in ('qcom_camss','imx681','ov13858'):
  if Path('/sys/module/'+m).exists(): die(m+' loaded')
 out={'schema':'sp11-e003h-imx681-mode2-0054-authorization-inspection-v1','accepted':True,'package_commit':au['package_commit'],'authorization_sha256':sha(P/'AUTHORIZATION.json'),'authorization_review_sha256':sha(P/'AUTHORIZATION-REVIEW.json'),'package_inspection_sha256':sha(P/'package-inspection.json'),'candidate_unarmed':True,'golden_saved_default':True,'camera_modules_loaded':False,'prior_run_present':False,'boot_count':1,'root_helper_invocation_count':1,'same_boot_retry':False,'sensor_resolution_index':2,'sensor_geometry':'3840x2160@30','windows_pair_equality':True,'sensor_changed_values':7,'camss_geometry_gate_changes':3,'new_camss_mmio_writes':0,'production_parity_authorized':False}
 (P/'authorization-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print('PASS: 0054 authorization binds exactly one mode2 diagnostic; candidate remains unarmed; no retry; Golden rollback required')
if __name__=='__main__':main()
