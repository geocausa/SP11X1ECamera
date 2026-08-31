#!/usr/bin/env python3
import hashlib,json,re,subprocess,tempfile,shutil
from pathlib import Path
SRC=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss')
HERE=Path(__file__).resolve().parent
PATCH=HERE/'0051-x1e-csid1-rupdone-no-regupdate-write.patch'
WIN=HERE/'windows-csid1-rupdone-irq-ownership/windows-csid1-rupdone-irq-ownership-oracle.json'
RUN=HERE.parent/'e003h-csid1-first-irq-geometry-0050-candidate/runtime-0050-analysis.json'
EXPECTED={
 'patch':'7d658f5a0c57aa5749aaa76078cce0fb05b35918ec62430786b4d9bd20c7952d',
 'windows':'4ec65044495ea7040b8fa350bee67b83c563eae824ba6e171e7e7b8e8e9b8eb8',
 'runtime0050':'bc8c2fd7033121592e540e3eedde134e56cab6d2525526f7771a74ec7b424459',
 'base_csid680':'c889caca3f794d671cf16fa91b08a6fe4566b257b9557933700317de2e06b90a',
 'base_csidh':'5869c6721ebec550d5d3e21e6503fd1f580ebb1aa0991ea25532cfb12156b46d',
 'csid680':'683c0d5c042d3a8f24be211cda7dc02d06befe31e42aeb29fcd14f117397c81c',
 'csidh':'5869c6721ebec550d5d3e21e6503fd1f580ebb1aa0991ea25532cfb12156b46d',
 'camss':'5a920032e138eee1154c4b9ae1846a445e02fbac3e7626a4245797502e73b793',
 'vfe680':'0dc6269d8b7c0e57e1442dfea374f0e90bdf14b8e8ef58117a505cda6d643036',
 'module':'6b7287e6eb96c44060d58691333b82f4e4103df929f98ad39ec50347b379f020',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def main():
 for k,p in [('patch',PATCH),('windows',WIN),('runtime0050',RUN),('csid680',SRC/'camss-csid-680.c'),('csidh',SRC/'camss-csid.h'),('camss',SRC/'camss.c'),('vfe680',SRC/'camss-vfe-680.c'),('module',SRC/'qcom-camss.ko')]:
  got=sha(p)
  if got!=EXPECTED[k]: die(f'{k} hash drift {got} != {EXPECTED[k]}')
 wo=json.loads(WIN.read_text()); ro=json.loads(RUN.read_text())
 if not wo.get('accepted') or wo['classification']['windows_rup_done_causes_reg_update_cmd_write'] is not False: die('Windows ownership oracle drift')
 if wo['classification']['windows_rup_done_causes_zero_write_to_reg_update_cmd'] is not False: die('Windows zero-write classification drift')
 if not ro.get('accepted') or ro['classification']['divergence_boundary']!='after the matching first RUP_DONE IRQ 0x00811dd0 and by the immediately following Epoch0/1-bearing IRQ': die('0050 boundary drift')
 patch=PATCH.read_text()
 touched=sorted(set(re.findall(r'^\+\+\+ b/(.+)$',patch,re.M)))
 if touched!=['drivers/media/platform/qcom/camss/camss-csid-680.c']: die('patch scope drift '+repr(touched))
 added=[x[1:] for x in patch.splitlines() if x.startswith('+') and not x.startswith('+++')]
 if [x for x in added if 'readl' in x or 'writel' in x]: die('0051 added MMIO access')
 s=(SRC/'camss-csid-680.c').read_text(); h=(SRC/'camss-csid.h').read_text()
 if sha(SRC/'camss-csid.h')!=EXPECTED['base_csidh']: die('header unexpectedly changed')
 anchor=s.index('if (ipp_val & CSID_IPP_RUP_DONE) {')
 front=s.index('if (csid->phy.en_ipp && __csid_sp11_front_ipp_mode0(csid))',anchor)
 shadow=s.index('csid->reg_update &= ~reg_update_ipp();',front)
 fallback=s.index('csid_reg_update_clear(csid, MSM_CSID_STREAM_PIX);',shadow)
 if not anchor < front < shadow < fallback: die('front RUP bookkeeping order drift')
 block=s[anchor:s.index('\n\t}',fallback)+3]
 if 'writel' in block: die('front RUP_DONE block gained MMIO write')
 # Generic helper and RDI path remain intact for all other ownership models.
 generic=s.index('static inline void csid_reg_update_clear')
 generic_end=s.index('\n}',generic)+2
 gb=s[generic:generic_end]
 if 'writel(csid->reg_update, csid->base + CSID_REG_UPDATE_CMD);' not in gb: die('generic clear MMIO path removed')
 rdi=s.index('if (val & CSID_CSI2_RDIN_RUP_DONE)')
 if 'csid_rup_complete(csid, i);' not in s[rdi:rdi+180]: die('RDI RUP completion drift')
 if s.count('writel(csid->reg_update, csid->base + CSID_REG_UPDATE_CMD);')!=2: die('global reg_update write callsite count drift')
 # Exact reverse/forward reconstruction of the sole touched source.
 with tempfile.TemporaryDirectory() as td:
  root=Path(td); d=root/'drivers/media/platform/qcom/camss'; d.mkdir(parents=True)
  shutil.copy2(SRC/'camss-csid-680.c',d/'camss-csid-680.c')
  subprocess.check_call(['patch','-s','-p1','-R','-i',str(PATCH)],cwd=root)
  if sha(d/'camss-csid-680.c')!=EXPECTED['base_csid680']: die('reverse does not reproduce 0050 source')
  subprocess.check_call(['patch','-s','-p1','-i',str(PATCH)],cwd=root)
  if sha(d/'camss-csid-680.c')!=EXPECTED['csid680']: die('forward does not reproduce 0051 source')
 vermag=subprocess.check_output(['modinfo','-F','vermagic',str(SRC/'qcom-camss.ko')],text=True).strip()
 ev='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
 if vermag!=ev: die('vermagic drift '+vermag)
 out={
  'schema':'sp11-e003h-linux-0051-front-rupdone-no-regupdate-write-inspection-v1','accepted':True,
  'evidence':{'windows_rupdone_oracle_sha256':EXPECTED['windows'],'runtime_0050_analysis_sha256':EXPECTED['runtime0050']},
  'base_0050_source_sha256':{'camss-csid-680.c':EXPECTED['base_csid680'],'camss-csid.h':EXPECTED['base_csidh']},
  'source_sha256':{'camss-csid-680.c':EXPECTED['csid680'],'camss-csid.h':EXPECTED['csidh'],'camss.c':EXPECTED['camss'],'camss-vfe-680.c':EXPECTED['vfe680']},
  'patch_sha256':EXPECTED['patch'],'module_sha256':EXPECTED['module'],'module_vermagic':vermag,'touched_files':touched,
  'new_mmio_reads':0,'new_mmio_writes':0,'new_register_values':0,
  'suppressed_mmio_write_path':'only exact X1E80100 front-mode0 IPP RUP_DONE bookkeeping: no generic software-shadow write to CSID REG_UPDATE_CMD +0x18',
  'software_shadow_clear_retained':True,'ipp_irq_clear_0xb4_retained':True,'generic_reg_update_clear_retained':True,'rdi_rup_done_behavior_retained':True,
  'crop_changed':False,'irq_masks_changed':False,'rtcdm_changed':False,'vfe_changed':False,'sensor_changed':False,'csiphy_changed':False,'dt_changed':False,
  'hardware_behavior_changed':True,'behavior_change':'remove one Windows-unmatched post-RUP MMIO command from fail-closed front IPP branch',
  'runtime_authorized':False,
 }
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
