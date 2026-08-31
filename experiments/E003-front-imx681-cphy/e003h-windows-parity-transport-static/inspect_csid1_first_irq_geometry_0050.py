#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,shutil,subprocess,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SRC=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss')
PATCH=ROOT/'0050-x1e-csid1-first-irq-geometry-readonly.patch'
EXPECTED={
 'patch':'61440f2452badd0d01f312af4ef4e08505c2263a3557af1693f1a5e04db7020b',
 'csid680':'c889caca3f794d671cf16fa91b08a6fe4566b257b9557933700317de2e06b90a',
 'csidh':'5869c6721ebec550d5d3e21e6503fd1f580ebb1aa0991ea25532cfb12156b46d',
 'camss':'5a920032e138eee1154c4b9ae1846a445e02fbac3e7626a4245797502e73b793',
 'vfe680':'0dc6269d8b7c0e57e1442dfea374f0e90bdf14b8e8ef58117a505cda6d643036',
 'module':'b69a20b517953a96cf5ff806a26c78e52ce5e177ef8dcdf69afa0dd561e8439b',
}
BASE0049={
 'camss-csid-680.c':'e207f5d8f522829c4bd45058ede1387fc064b16f7f1d2b649b62465601e5c261',
 'camss-csid.h':'3088e0013292d6765b8d76cdde8407bd298b4941a67a67c9d28a7a3be2f13f47',
}
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
TRACE_MAX=8

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def die(s:str)->None:raise SystemExit('FAIL: '+s)
def run(cmd,**kw):return subprocess.run(cmd,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,**kw).stdout

def main():
 for k,p in [('patch',PATCH),('csid680',SRC/'camss-csid-680.c'),('csidh',SRC/'camss-csid.h'),('camss',SRC/'camss.c'),('vfe680',SRC/'camss-vfe-680.c'),('module',SRC/'qcom-camss.ko')]:
  got=sha(p)
  if got!=EXPECTED[k]: die(f'{k} hash drift {got} != {EXPECTED[k]}')
 patch=PATCH.read_text()
 touched=sorted(set(re.findall(r'^\+\+\+ b/(.+)$',patch,re.M)))
 want=['drivers/media/platform/qcom/camss/camss-csid-680.c','drivers/media/platform/qcom/camss/camss-csid.h']
 if touched!=want: die('patch scope drift '+repr(touched))
 added=[l[1:] for l in patch.splitlines() if l.startswith('+') and not l.startswith('+++')]
 accesses=[l.strip() for l in added if 'readl' in l or 'writel' in l]
 reads=[l for l in accesses if 'readl_relaxed' in l]
 writes=[l for l in accesses if 'writel' in l]
 if reads!=['readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE0);'] or writes:
  die(f'hardware access drift reads={reads!r} writes={writes!r}')
 s=(SRC/'camss-csid-680.c').read_text(); h=(SRC/'camss-csid.h').read_text()
 if '#define X1E_IPP_IRQ_TRACE_MAX 8' not in h: die('trace bound drift')
 for a in ('x1e_ipp_irq_trace_status[X1E_IPP_IRQ_TRACE_MAX]','x1e_ipp_irq_trace_actual[X1E_IPP_IRQ_TRACE_MAX]','x1e_ipp_irq_trace_count'):
  if a not in h: die('trace storage missing '+a)
 if '#define CSID_IPP_FORMAT_MEASURE0' not in s or '0x38c' not in s: die('measure0 offset anchor missing')
 reset=s.index('csid->x1e_ipp_irq_trace_count = 0;')
 cfg=s.index('return __csid_sp11_front_ipp_full_config(csid);',reset)
 if not reset<cfg: die('trace reset not before full config')
 status=s.index('ipp_val = readl(csid->base + CSID_IPP_IRQ_STATUS);')
 bound=s.index('if (csid->x1e_ipp_irq_trace_count < X1E_IPP_IRQ_TRACE_MAX)',status)
 save_status=s.index('csid->x1e_ipp_irq_trace_status[trace_idx] = ipp_val;',bound)
 save_actual=s.index('csid->x1e_ipp_irq_trace_actual[trace_idx] =',save_status)
 read_actual=s.index('readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE0);',save_actual)
 clear=s.index('writel(ipp_val, csid->base + CSID_IPP_IRQ_CLEAR)',status)
 if not status<bound<save_status<save_actual<read_actual<clear: die('capture/clear order drift')
 if 'ipp-seq[%u]=%08x/%08x' not in s: die('ordered dump format missing')
 if s.count('x1e_ipp_irq_trace_count++')!=1: die('trace count increment drift')
 # The new callsite is one of two FORMAT_MEASURE0 reads total: 0050 ordered trace + 0049 bit14 snapshot.
 if s.count('readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE0)')!=2: die('unexpected FORMAT_MEASURE0 callsite count')
 vermag=run(['modinfo','-F','vermagic',str(SRC/'qcom-camss.ko')]).strip()
 if vermag!=VERMAGIC: die('vermagic drift '+vermag)
 # Reverse the exact patch from current 0050 to prove exact 0049 base, then reapply.
 with tempfile.TemporaryDirectory() as td:
  td=Path(td); d=td/'drivers/media/platform/qcom/camss'; d.mkdir(parents=True)
  for fn in ('camss-csid-680.c','camss-csid.h'): shutil.copy2(SRC/fn,d/fn)
  run(['patch','-p1','-R','--batch','-i',str(PATCH)],cwd=td)
  for fn,wantsha in BASE0049.items():
   if sha(d/fn)!=wantsha: die(f'reverse does not reproduce 0049 {fn}')
  run(['patch','-p1','--batch','-i',str(PATCH)],cwd=td)
  if sha(d/'camss-csid-680.c')!=EXPECTED['csid680'] or sha(d/'camss-csid.h')!=EXPECTED['csidh']:
   die('forward reapply does not reproduce 0050')
 out={
  'schema':'sp11-e003h-linux-0050-csid1-first-irq-geometry-readonly-inspection-v1',
  'accepted':True,
  'base_0049_source_sha256':BASE0049,
  'source_sha256':{'camss-csid-680.c':EXPECTED['csid680'],'camss-csid.h':EXPECTED['csidh'],'camss.c':EXPECTED['camss'],'camss-vfe-680.c':EXPECTED['vfe680']},
  'patch_sha256':EXPECTED['patch'],'module_sha256':EXPECTED['module'],'module_vermagic':vermag,
  'touched_files':touched,'trace_max_entries':TRACE_MAX,
  'new_mmio_read_callsites':1,'new_mmio_read_offset':'0x38c','new_mmio_writes':0,
  'capture_condition':'first eight nonzero front-mode0 IPP IRQs after existing reset history boundary',
  'capture_order':['existing IPP IRQ status read','existing software OR/last/count','bounded status store','read actual frame +0x38c','existing 0049 bit14 telemetry if applicable','existing IPP clear'],
  'dump_format':'ipp-seq[N]=IRQ_STATUS/FORMAT_MEASURE0',
  'irq_masks_changed':False,'irq_clear_changed':False,'crop_programming_changed':False,'rup_aup_changed':False,
  'rtcdm_changed':False,'vfe_changed':False,'sensor_changed':False,'csiphy_changed':False,'dt_changed':False,
  'hardware_execution_performed':False,'runtime_authorized':False,
 }
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
