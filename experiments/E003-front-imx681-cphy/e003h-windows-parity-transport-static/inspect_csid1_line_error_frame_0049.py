#!/usr/bin/env python3
import hashlib,json,re,subprocess,tempfile,shutil
from pathlib import Path
SRC=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss')
PATCH=Path(__file__).resolve().parent/'0049-x1e-csid1-line-error-frame-readonly.patch'
ORACLE=Path(__file__).resolve().parent/'windows-csid1-line-count-error/windows-csid1-line-count-error-oracle.json'
EXPECTED={
 'patch':'58f9080b7ae1e9addbfb035930374d073a1694c0a666132dcd1604e13b14f4e3',
 'oracle':'2081159e5a28a02fa79a933c83fe0838a6efe778f1ccdd85a804c6f3d8ec9b3e',
 'csid680':'e207f5d8f522829c4bd45058ede1387fc064b16f7f1d2b649b62465601e5c261',
 'csidh':'3088e0013292d6765b8d76cdde8407bd298b4941a67a67c9d28a7a3be2f13f47',
 'camss':'5a920032e138eee1154c4b9ae1846a445e02fbac3e7626a4245797502e73b793',
 'vfe680':'0dc6269d8b7c0e57e1442dfea374f0e90bdf14b8e8ef58117a505cda6d643036',
 'module':'610c0def762e6449c342452ffc436b195cd1330a41055076d25cca95f077a1f5',
}
BASE={'camss-csid-680.c':'7ce2ec82c7bdf40a72385937c5a4a4412781b7a2e7fb321e4cbf35fd6b486950','camss-csid.h':'f2315c29cdde351f2f82b3f2db27934b76e0e8ee04f37c793f21120043fc96f5'}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def main():
 for k,p in [('patch',PATCH),('oracle',ORACLE),('csid680',SRC/'camss-csid-680.c'),('csidh',SRC/'camss-csid.h'),('camss',SRC/'camss.c'),('vfe680',SRC/'camss-vfe-680.c'),('module',SRC/'qcom-camss.ko')]:
  if sha(p)!=EXPECTED[k]: die(f'{k} hash drift {sha(p)} != {EXPECTED[k]}')
 o=json.loads(ORACLE.read_text())
 if not o.get('accepted') or o['classification']['causal_link_to_missing_vfe_epoch0_proven'] is not False: die('oracle policy drift')
 if o['next_gate'].split()[0:2]!=['Read-only','Linux']: die('oracle no longer justifies read-only telemetry')
 patch=PATCH.read_text()
 touched=sorted(set(re.findall(r'^\+\+\+ b/(.+)$',patch,re.M)))
 if touched!=['drivers/media/platform/qcom/camss/camss-csid-680.c','drivers/media/platform/qcom/camss/camss-csid.h']: die('patch scope drift '+repr(touched))
 added=[l[1:] for l in patch.splitlines() if l.startswith('+') and not l.startswith('+++')]
 access=[l.strip() for l in added if 'readl' in l or 'writel' in l]
 reads=[l for l in access if 'readl_relaxed' in l]
 writes=[l for l in access if 'writel' in l]
 if len(reads)!=3 or writes: die(f'hardware-access delta drift reads={reads!r} writes={writes!r}')
 if [re.search(r'CSID_IPP_FORMAT_MEASURE([012])',x).group(1) for x in reads]!=['0','1','2']: die('read order drift')
 s=(SRC/'camss-csid-680.c').read_text(); h=(SRC/'camss-csid.h').read_text()
 for a in ('#define CSID_IPP_FORMAT_MEASURE0','0x38c','#define CSID_IPP_FORMAT_MEASURE1','0x390','#define CSID_IPP_FORMAT_MEASURE2','0x394','#define\t\tCSID_IPP_ERROR_LINE_COUNT\t\t\tBIT(14)'):
  if a not in s: die('source anchor missing '+a)
 err=s.index('if (ipp_val & CSID_IPP_ERROR_LINE_COUNT)')
 r0=s.index('readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE0)',err)
 r1=s.index('readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE1)',err)
 r2=s.index('readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE2)',err)
 clear=s.index('writel(ipp_val, csid->base + CSID_IPP_IRQ_CLEAR)',err)
 if not err<r0<r1<r2<clear: die('error telemetry is not before existing clear in exact order')
 if s.count('readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE0)')!=1 or s.count('readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE1)')!=1 or s.count('readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE2)')!=1: die('unexpected extra result reads')
 for a in ('x1e_ipp_line_error_frame','x1e_ipp_line_error_hbi','x1e_ipp_line_error_vbi'):
  if a not in h or a not in s: die('software latch missing '+a)
 vermag=subprocess.check_output(['modinfo','-F','vermagic',str(SRC/'qcom-camss.ko')],text=True).strip()
 expected_ver='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
 if vermag!=expected_ver: die('vermagic drift '+vermag)
 out={
  'schema':'sp11-e003h-linux-0049-csid1-line-error-frame-readonly-inspection-v1','accepted':True,
  'base_0048_source_sha256':BASE,'source_sha256':{'camss-csid-680.c':EXPECTED['csid680'],'camss-csid.h':EXPECTED['csidh'],'camss.c':EXPECTED['camss'],'camss-vfe-680.c':EXPECTED['vfe680']},
  'patch_sha256':EXPECTED['patch'],'oracle_sha256':EXPECTED['oracle'],'module_sha256':EXPECTED['module'],'module_vermagic':vermag,
  'touched_files':touched,'new_mmio_reads':3,'new_mmio_read_offsets':['0x38c','0x390','0x394'],'new_mmio_writes':0,
  'capture_condition':'front-mode0 existing ISR and IPP bit14 ERROR_LINE_COUNT','capture_order':['existing read IPP status','software OR/last/count','if bit14: read actual frame +0x38c','read HBI +0x390','read VBI +0x394','existing IPP clear'],
  'hardware_programming_changed':False,'rtcdm_changed':False,'vfe_changed':False,'sensor_changed':False,'csiphy_changed':False,
  'runtime_authorized':False,
 }
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
