#!/usr/bin/env python3
import hashlib,json,re,subprocess,tempfile,shutil,struct,yaml
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
D=STATIC/'csid1-startup-companion-transport-0053'
SRC=ROOT/'02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss'
CAMSS=SRC/'camss.c'; CSID=SRC/'camss-csid.c'; CSID680=SRC/'camss-csid-680.c'; CSIDH=SRC/'camss-csid.h'; VFE=SRC/'camss-vfe-680.c'
MODULE=SRC/'qcom-camss.ko'
PATCH=STATIC/'0053-x1e-startup-csid-companion-rtcdm-transport.patch'
ORACLE=D/'startup-companion-transport-0053-oracle.json'
EXTRACT=D/'extract_startup_companion_transport_0053.py'
CHECK=STATIC/'CAMSS-STARTUP-CSID-COMPANION-0053-CHECKPATCH.txt'
BUILD=STATIC/'CAMSS-STARTUP-CSID-COMPANION-0053-BUILD.raw.txt'
STATE=REPO/'state/project.yaml'
EXPECTED={
 'base_camss':'5a920032e138eee1154c4b9ae1846a445e02fbac3e7626a4245797502e73b793',
 'new_camss':'b8cb256514337f1767ba5dab002cc59ff4f0c8f73f9be03f83de77ab8b3507c9',
 'csid':'fc316d35114a23e29333b22a6fb10f9af2f5dfb15ae829a963ecd05c53d6b229',
 'csid680':'683c0d5c042d3a8f24be211cda7dc02d06befe31e42aeb29fcd14f117397c81c',
 'csidh':'5869c6721ebec550d5d3e21e6503fd1f580ebb1aa0991ea25532cfb12156b46d',
 'vfe':'0dc6269d8b7c0e57e1442dfea374f0e90bdf14b8e8ef58117a505cda6d643036',
 'module':'f04189d766f478083e09fd38b26e73c99c03306ce1f2fb81d68b2ebd0d2be876',
 'patch':'dba1d21fdc01f4091af89ce051283464661952ce2d1acd1f59afb75c8b52cfd6',
 'oracle':'4b70a61a2e226b37d9310b4b4dee4d77c7516f975498973ee89dc29d772e2e5c',
 'extractor':'3dfe96a9b900e98e4ee93168df65eb2db0fbea1d180a85ddc7239a85f6d76d68',
 'checkpatch':'93f527d4a6aada3d9b1abce993a88e82e044e2ae1b12add309de2efb260ec289',
 'build':'b60f8dccadc64ca83283b878633d1d88eb1f2c95956691b750bc214f335c2565',
}
P0=[0x03000001,0x00000330,0x00000000,0x03000002,0x0000037c,0x00000001,0x00000000,0x03000002,0x0000035c,0x0eff0000,0x086f0000,0x03000002,0x00000384,0x0000001f,0x08700f00]
PC=[0x03000002,0x0000035c,0x0eff0000,0x086f0000]
P0SHA='1872731eaa3eb2233436029c2658682097c61ebf97e3facf46e31224ee25e2a2'
PCSHA='45d059ec64587ea4f55eb8df64704520782801418c4a754f512831c7473fb5c7'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def check(k,p):
 g=sha(p)
 if g!=EXPECTED[k]: die(f'{k} hash drift {g} != {EXPECTED[k]}')
def func(text,name,next_name):
 a=text.index(name); b=text.index(next_name,a); return text[a:b]
def words(block,name):
 m=re.search(r'static const u32 '+re.escape(name)+r'\[\] = \{(.*?)\n\t\};',block,re.S)
 if not m: die('array missing '+name)
 return [int(x,16) for x in re.findall(r'0x[0-9a-fA-F]+',m.group(1))]
def bsha(ws): return hashlib.sha256(b''.join(struct.pack('<I',x) for x in ws)).hexdigest()
def main():
 for k,p in [('new_camss',CAMSS),('csid',CSID),('csid680',CSID680),('csidh',CSIDH),('vfe',VFE),('module',MODULE),('patch',PATCH),('oracle',ORACLE),('extractor',EXTRACT),('checkpatch',CHECK),('build',BUILD)]: check(k,p)
 if '0 errors, 0 warnings, 0 checks' not in CHECK.read_text(): die('strict checkpatch not clean')
 if 'CC [M]  camss.o' not in BUILD.read_text() or 'LD [M]  qcom-camss.ko' not in BUILD.read_text(): die('build log drift')
 vm=subprocess.check_output(['modinfo','-F','vermagic',str(MODULE)],text=True).strip()
 if vm!='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64': die('vermagic drift '+vm)
 o=json.loads(ORACLE.read_text())
 if not o.get('accepted') or not o['classification']['transport_ownership_mismatch_proven']: die('0053 oracle drift')
 if o['classification']['crop_failure_causality_proven'] is not False: die('causality overclaim')
 s=CAMSS.read_text(); patch=PATCH.read_text()
 mats=func(s,'static int camss_x1e_pix_startup_wrapper_materialize','static void camss_x1e_pix_prime_write')
 submit=func(s,'static int camss_x1e_pix_submit_startup','static int camss_x1e_pix_submit_prime')
 runner=func(s,'static int camss_x1e_pix_runner_once','static int camss_x1e_pix_trigger_buffer')
 if words(mats,'companion_packet0')!=P0 or words(mats,'companion_common')!=PC: die('materialized companion words drift')
 if bsha(P0)!=P0SHA or bsha(PC)!=PCSHA: die('companion SHA reconstruction drift')
 for q in ('#define CAMSS_X1E_PIX_STARTUP_CSID_CHANGE_BASE\t0x08057000',
           '#define CAMSS_X1E_PIX_STARTUP_WRAPPER_SIZE\tSZ_4K'):
  if q not in s: die('startup transport definition missing '+q)
 if submit.count('camss_rtcdm1_windows_fifo0_commit')!=4: die('startup commit count is not four')
 seq=['wrapper->vfe_base_dma[packet]','corpus->packet_dma[packet]','wrapper->csid_base_dma[packet]','wrapper->companion_dma[packet]']
 pos=[submit.index(x) for x in seq]
 if pos!=sorted(pos): die('startup RT-CDM order drift')
 if runner.count('camss_x1e_pix_submit_startup(camss,')!=4: die('startup packet call count drift')
 if 'csid680_x1e_front_ipp_companion(csid,' in runner or 'csid680_x1e_front_ipp_companion(csid,' in s: die('CPU startup companion still active from camss.c')
 if patch.count('-\tret = csid680_x1e_front_ipp_companion(csid,')!=4: die('patch does not remove exactly four CPU companion calls')
 added='\n'.join(x[1:] for x in patch.splitlines() if x.startswith('+') and not x.startswith('+++'))
 if 'writel(' in added or 'readl(' in added or 'readl_relaxed(' in added: die('0053 adds direct MMIO')
 diffs=[x for x in patch.splitlines() if x.startswith('diff --git ')]
 if diffs!=['diff --git a/drivers/media/platform/qcom/camss/camss.c b/drivers/media/platform/qcom/camss/camss.c']: die('patch touches files outside camss.c')
 # Patch round-trip exact boundary.
 with tempfile.TemporaryDirectory() as td:
  tree=Path(td); q=tree/'drivers/media/platform/qcom/camss'; q.mkdir(parents=True)
  shutil.copy2(CAMSS,q/'camss.c')
  subprocess.check_call(['patch','-R','-s','-p1','-i',str(PATCH)],cwd=tree)
  if sha(q/'camss.c')!=EXPECTED['base_camss']: die('reverse patch does not recover 0052 baseline')
  subprocess.check_call(['patch','-s','-p1','-i',str(PATCH)],cwd=tree)
  if sha(q/'camss.c')!=EXPECTED['new_camss']: die('forward patch does not recover 0053 source')
 state=yaml.safe_load(STATE.read_text())
 gate=state.get('e003h',{})
 if gate.get('runtime_authorized') is not False or gate.get('sensor_stream_authorized') is not False:
  die('active E003h runtime gate unexpectedly open')
 out={
  'schema':'sp11-e003h-linux-0053-startup-csid-companion-rtcdm-transport-v1','accepted':True,
  'patch_sha256':EXPECTED['patch'],'module_sha256':EXPECTED['module'],'module_vermagic':vm,
  'source_sha256':{'camss.c':EXPECTED['new_camss'],'camss-csid.c':EXPECTED['csid'],'camss-csid-680.c':EXPECTED['csid680'],'camss-csid.h':EXPECTED['csidh'],'camss-vfe-680.c':EXPECTED['vfe']},
  'base_0052_camss_sha256':EXPECTED['base_camss'],
  'oracle_sha256':EXPECTED['oracle'],'oracle_extractor_sha256':EXPECTED['extractor'],
  'strict_checkpatch_sha256':EXPECTED['checkpatch'],'build_log_sha256':EXPECTED['build'],
  'touched_files':['drivers/media/platform/qcom/camss/camss.c'],
  'proved':{
   'patch_roundtrip_byte_identical':True,'strict_checkpatch_clean':True,'module_build_clean':True,
   'startup_packet_count':4,'startup_rtcdm_commits_per_packet':4,
   'startup_rtcdm_order':['CHANGE_BASE(VFE1)','IFE startup main','CHANGE_BASE(CSID1)','exact CSID descriptor-1 companion'],
   'csid1_change_base':'0x08057000','packet0_companion_bytes':60,'packet0_companion_sha256':P0SHA,
   'packet1_3_companion_bytes':16,'packet1_3_companion_sha256':PCSHA,
   'cpu_startup_companion_calls_removed':4,'new_direct_mmio_reads':0,'new_direct_mmio_writes':0,
   'new_register_values':0,'crop_coordinates_changed':False,'rup_aup_changed':False,'vfe_programming_changed':False,'sensor_programming_changed':False,'csiphy_programming_changed':False,
  },
  'classification':{
   'transport_ownership_delta_executed_in_module':True,'windows_transport_parity_improved':True,
   'crop_failure_causality_proven':False,'active_shadow_latch_causality_proven':False,
  },
  'runtime_authorized':False,
  'next_gate':'record/publish static 0053 checkpoint, then build and inspect a distinct unarmed one-shot package; a separate fresh authorization is required before any hardware execution'
 }
 blob=json.dumps(out,indent=2,sort_keys=True)+'\n'
 (STATIC/'linux-0053-startup-csid-companion-rtcdm-transport-inspection.json').write_text(blob)
 (STATIC/'CAMSS-STARTUP-CSID-COMPANION-0053-INSPECT.txt').write_text(blob)
 print(blob,end='')
if __name__=='__main__': main()
