#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-startup-csid-companion-rtcdm-0053-candidate'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
EXPECTED={
 'package_commit':'d533d03b25601e30419d7266f62728877b97e74f',
 'package_inspection':'d283bbe2884aa1a31189c3cbb5c65fdeb9ee7c50e59190b3f55da0bce45bcedb',
 'review':'0ee3620ccaea747c208672d195ae1727d659d1836075cfadb12f7f6bcfc89770',
 'authorization':'ce172a7b39ef88c0c5f57531dd77b296338bcd9431e38152c072cd1714bcc3fc',
 'provenance':'803d09be7a18b321b07db7dac5a81d837dd09b1f6dfd883b2f27daefa7e8ffb6',
 'static_inspection':'72ceb0880f673bc1d17698eb228612a88b8bf4683b8f034a9de4f1b784120fea',
 'transport_oracle':'4b70a61a2e226b37d9310b4b4dee4d77c7516f975498973ee89dc29d772e2e5c',
 'camss':'f04189d766f478083e09fd38b26e73c99c03306ce1f2fb81d68b2ebd0d2be876',
 'sensor':'389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'capsule':'6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20',
 'helper':'d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09'}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def cmd(a): return subprocess.check_output(a,text=True,stderr=subprocess.DEVNULL).strip()
def main():
 paths={'package_inspection':NEW/'package-inspection.json','review':NEW/'AUTHORIZATION-REVIEW.json','authorization':NEW/'AUTHORIZATION.json','provenance':REPO/'provenance/front-parity.json','static_inspection':STATIC/'linux-0053-startup-csid-companion-rtcdm-transport-inspection.json','transport_oracle':STATIC/'csid1-startup-companion-transport-0053/startup-companion-transport-0053-oracle.json','camss':NEW/'qcom-camss.ko','sensor':NEW/'imx681.ko','dtb':NEW/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb','capsule':NEW/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin','helper':NEW/'e003h-pix-one-shot'}
 for k,p in paths.items():
  g=sha(p)
  if g!=EXPECTED[k]: die(f'{k} hash drift {g}')
 head=cmd(['git','-C',str(REPO),'rev-parse','HEAD']); origin=cmd(['git','-C',str(REPO),'rev-parse','origin/experiment/e003-front-imx681-cphy'])
 if head!=EXPECTED['package_commit'] or origin!=head: die('authorization not based on exact public package commit')
 subprocess.check_call(['git','-C',str(REPO),'diff','--quiet'])
 subprocess.check_call(['git','-C',str(REPO),'diff','--cached','--quiet'])
 review=json.loads(paths['review'].read_text()); au=json.loads(paths['authorization'].read_text()); pkg=json.loads(paths['package_inspection'].read_text()); li=json.loads(paths['static_inspection'].read_text()); o=json.loads(paths['transport_oracle'].read_text())
 if not review.get('accepted') or review['package_commit']!=head or review['package_inspection_sha256']!=EXPECTED['package_inspection']: die('review package binding drift')
 for k in ('authorization_present_before_review','candidate_boot_armed','camera_modules_loaded','prior_0053_run_present','crop_failure_causality_proven'):
  if review[k] is not False: die('review false invariant drift '+k)
 if review['startup_packets']!=4 or review['startup_rtcdm_commits_per_packet']!=4 or review['new_mmio_reads']!=0 or review['new_mmio_writes']!=0 or review['new_register_values']!=0: die('review delta drift')
 if not au.get('accepted') or au.get('runtime_authorized') is not True or au.get('production_parity_authorized') is not False: die('authorization policy drift')
 if au['authorization_review_sha256']!=EXPECTED['review'] or au['package_commit']!=head or au['package_inspection_sha256']!=EXPECTED['package_inspection'] or au['bounded_provenance_sha256']!=EXPECTED['provenance']: die('authorization binding drift')
 if au['static_evidence']!={'linux_0053_inspection_sha256':EXPECTED['static_inspection'],'transport_oracle_sha256':EXPECTED['transport_oracle'],'crop_failure_causality_proven':False}: die('static evidence binding drift')
 if au['candidate']!={'camss_sha256':EXPECTED['camss'],'sensor_sha256':EXPECTED['sensor'],'dtb_sha256':EXPECTED['dtb'],'capsule_sha256':EXPECTED['capsule'],'helper_sha256':EXPECTED['helper']}: die('candidate binding drift')
 if au['boot']!={'id':'sp11-camera-e003h-csidcomp-0053-one-shot','cmdline_marker':'sp11_camera_e003h_csidcomp_0053=1','golden_saved_default':'sp11-audio-fullio-v19c','candidate_was_unarmed_at_authorization':True}: die('boot contract drift')
 ex=au['execution_contract']
 if ex['boot_count']!=1 or ex['root_helper_invocation_count']!=1 or ex['same_boot_retry'] is not False or ex['existing_run_log_refuses_execution'] is not True or ex['persistent_rtcdm_observer_required'] is not True: die('execution contract drift')
 if 'No new register value' not in au['purpose'] or 'RT-CDM' not in au['purpose']: die('purpose scope drift')
 if not pkg.get('accepted') or pkg['candidate_boot_installed'] is not True or pkg['candidate_boot_armed'] is not False or pkg['runtime_authorized'] is not False or pkg['authorization_present'] is not False: die('frozen package state drift')
 if not li.get('accepted') or li['classification']['crop_failure_causality_proven'] is not False: die('static inspection drift')
 if not o.get('accepted') or o['classification']['transport_ownership_mismatch_proven'] is not True or o['classification']['crop_failure_causality_proven'] is not False: die('transport oracle drift')
 env=cmd(['grub-editenv','list']).splitlines()
 if 'saved_entry=sp11-audio-fullio-v19c' not in env: die('Golden saved entry drift')
 if any(x.startswith('next_entry=') and x!='next_entry=' for x in env): die('candidate already armed')
 for m in ('qcom_camss','imx681','ov13858'):
  if Path('/sys/module/'+m).exists(): die(m+' loaded before authorization publish')
 if (NEW/'RUNTIME-CSIDCOMP-0053-RUN.txt').exists(): die('0053 RUN already exists')
 out={'schema':'sp11-e003h-0053-authorization-inspection-v1','accepted':True,'package_commit':head,'authorization_sha256':EXPECTED['authorization'],'authorization_review_sha256':EXPECTED['review'],'package_inspection_sha256':EXPECTED['package_inspection'],'candidate_unarmed':True,'golden_saved_default':True,'camera_modules_loaded':False,'prior_run_present':False,'boot_count':1,'root_helper_invocation_count':1,'same_boot_retry':False,'crop_failure_causality_proven':False,'production_parity_authorized':False}
 (NEW/'authorization-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: 0053 authorization binds exactly one helper to the frozen startup-CSID RT-CDM transport package; candidate remains unarmed; no retry; Golden rollback required')
if __name__=='__main__': main()
