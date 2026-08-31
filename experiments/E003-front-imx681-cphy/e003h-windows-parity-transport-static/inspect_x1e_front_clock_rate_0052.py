#!/usr/bin/env python3
import hashlib,json,subprocess,tempfile,shutil
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
SRC=ROOT/'02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss'
CSID=SRC/'camss-csid.c'; CSID680=SRC/'camss-csid-680.c'; CAMSS=SRC/'camss.c'; VFE=SRC/'camss-vfe-680.c'
MODULE=SRC/'qcom-camss.ko'; PATCH=STATIC/'0052-x1e-front-csid-link-clock-rate.patch'
CLOCK_ORACLE=STATIC/'x1e-csid-clock-hbi-correlation/x1e-csid-clock-hbi-correlation-oracle.json'
EOF_ORACLE=STATIC/'windows-linux-first-eof-geometry-boundary/first-eof-geometry-boundary-oracle.json'
CHECK=STATIC/'CAMSS-X1E-CLOCK-RATE-0052-CHECKPATCH.txt'
EXPECTED={
 'base_csid':'df0d2a0aa92078da7d86e1a96d2ff3b9c0876e702e14f8e172676a1f0371acd2',
 'new_csid':'fc316d35114a23e29333b22a6fb10f9af2f5dfb15ae829a963ecd05c53d6b229',
 'csid680':'683c0d5c042d3a8f24be211cda7dc02d06befe31e42aeb29fcd14f117397c81c',
 'camss':'5a920032e138eee1154c4b9ae1846a445e02fbac3e7626a4245797502e73b793',
 'vfe':'0dc6269d8b7c0e57e1442dfea374f0e90bdf14b8e8ef58117a505cda6d643036',
 'patch':'55c27634af4837e615145a7df9f4e92119b75c7a5b53957fa5864ddd16266788',
 'module':'42662121c848d863b06e3aba737e0f80a35fc047faf8cf5b0f47e2554ba3e92a',
 'clock_oracle':'f913e0dd3766077cfa9cf6875f77d7494bfe60a1bceea0ffe9f9c928d7d00dd0',
 'eof_oracle':'db4476e159872f9005a127d84ea41032191402de2709a0835d2c2c5fbc9dffde',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def check(k,p):
 g=sha(p)
 if g!=EXPECTED[k]: die(f'{k} hash drift {g}')
def main():
 for k,p in [('new_csid',CSID),('csid680',CSID680),('camss',CAMSS),('vfe',VFE),('patch',PATCH),('module',MODULE),('clock_oracle',CLOCK_ORACLE),('eof_oracle',EOF_ORACLE)]: check(k,p)
 if '0 errors, 0 warnings' not in CHECK.read_text(): die('checkpatch not clean')
 co=json.loads(CLOCK_ORACLE.read_text()); eo=json.loads(EOF_ORACLE.read_text())
 if not co.get('accepted') or co['classification']['linux_x1e_front_csid_300mhz_request_proven'] is not True: die('clock oracle drift')
 if co['classification']['linux_link_derived_required_rate_is_400mhz'] is not True: die('400MHz requirement drift')
 if co['classification']['direct_windows_400mhz_clock_vote_observed'] is not False: die('Windows direct-vote provenance drift')
 if not eo.get('accepted') or not eo['classification']['prior_first_epoch_geometry_divergence_boundary_superseded']: die('EOF boundary drift')
 s=CSID.read_text()
 required=[
  'csid->camss->res->version == CAMSS_X1E80100', 'csid->id == 1', 'csid->phy.csiphy_id == 2',
  'cphy && csid->phy.lane_cnt == 1', '!strcmp(clock->name, "csid")', '!strcmp(clock->name, "csid_csiphy_rx")',
  'x1e_front_link_clock', 'u64 min_rate = link_freq / 4;', 'camss_add_clock_margin(&min_rate);']
 for q in required:
  if q not in s: die('missing bounded 0052 condition '+q)
 if s.count('x1e_front_link_clock')!=2: die('0052 scope count drift')
 # Round-trip exact source boundary using patch.
 with tempfile.TemporaryDirectory() as td:
  td=Path(td); tree=td/'t'; (tree/'drivers/media/platform/qcom/camss').mkdir(parents=True)
  shutil.copy2(CSID,tree/'drivers/media/platform/qcom/camss/camss-csid.c')
  subprocess.check_call(['patch','-R','-p1','-i',str(PATCH)],cwd=tree,stdout=subprocess.DEVNULL)
  b=tree/'drivers/media/platform/qcom/camss/camss-csid.c'
  if sha(b)!=EXPECTED['base_csid']: die('reverse patch does not reproduce 0051/base csid.c')
  subprocess.check_call(['patch','-p1','-i',str(PATCH)],cwd=tree,stdout=subprocess.DEVNULL)
  if sha(b)!=EXPECTED['new_csid']: die('forward patch does not reproduce 0052 csid.c')
 vm=subprocess.check_output(['modinfo','-F','vermagic',str(MODULE)],text=True).strip()
 if vm!='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64': die('vermagic drift '+vm)
 out={
  'schema':'sp11-e003h-linux-0052-x1e-front-link-clock-rate-v1','accepted':True,
  'patch_sha256':EXPECTED['patch'],'module_sha256':EXPECTED['module'],'module_vermagic':vm,
  'source_sha256':{'camss-csid.c':EXPECTED['new_csid'],'camss-csid-680.c':EXPECTED['csid680'],'camss.c':EXPECTED['camss'],'camss-vfe-680.c':EXPECTED['vfe']},
  'base_0051_csid_sha256':EXPECTED['base_csid'],
  'evidence':{'clock_hbi_oracle_sha256':EXPECTED['clock_oracle'],'completed_eof_oracle_sha256':EXPECTED['eof_oracle']},
  'touched_files':['drivers/media/platform/qcom/camss/camss-csid.c'],
  'scope':{'soc':'X1E80100','csid':1,'csiphy':2,'phy':'C-PHY','trios':1,'clock_names':['csid','csid_csiphy_rx']},
  'front_link_freq_hz':1200000000,'old_requested_rate_hz':300000000,'new_link_derived_rate_hz':400000000,
  'clock_tables_changed':False,'clock_margin_changed':False,'new_mmio_reads':0,'new_mmio_writes':0,'new_register_values':0,
  'crop_changed':False,'rup_aup_changed':False,'irq_changed':False,'vfe_changed':False,'rtcdm_changed':False,'csiphy_programming_changed':False,'sensor_changed':False,'dt_changed':False,
  'hardware_behavior_changed':True,'hardware_behavior_change':'exact bounded X1E front CSID core/RX clock requests move from generic 300MHz first-entry selection to existing link-derived 400MHz selection',
  'direct_windows_400mhz_vote_proven':False,'hbi_400_300_correlation_proven':True,
  'runtime_authorized':False,
  'next':'package a distinct unarmed 0052 candidate; publish; then fresh one-shot authorization review before hardware execution'
 }
 blob=json.dumps(out,indent=2,sort_keys=True)+'\n'
 (STATIC/'linux-0052-x1e-front-link-clock-rate-inspection.json').write_text(blob)
 (STATIC/'CAMSS-X1E-CLOCK-RATE-0052-INSPECT.txt').write_text(blob)
 print(blob,end='')
if __name__=='__main__': main()
