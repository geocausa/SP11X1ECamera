#!/usr/bin/env python3
import hashlib, json, re, subprocess
from pathlib import Path

REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
SRC=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss')
PATCH=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/0048-x1e-csid1-ipp-irq-history-readonly.patch'
OBSERVER=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-linux-irq-observer-integrity/irq-observer-integrity-oracle.json'
MOD=SRC/'qcom-camss.ko'
BASE={
 'camss-csid.h':'e581e9a43a74a577aa535a7e33af4f5cd7e8c7af455d3c3fccd083dac2766f44',
 'camss-csid-680.c':'59e07a1b8322c7279a051bc1255f8912452300aadbf9bf8086312aec4daca1d0',
 'camss.c':'5a920032e138eee1154c4b9ae1846a445e02fbac3e7626a4245797502e73b793',
 'camss-vfe-680.c':'0dc6269d8b7c0e57e1442dfea374f0e90bdf14b8e8ef58117a505cda6d643036',
}
NEW={
 'camss-csid.h':'f2315c29cdde351f2f82b3f2db27934b76e0e8ee04f37c793f21120043fc96f5',
 'camss-csid-680.c':'7ce2ec82c7bdf40a72385937c5a4a4412781b7a2e7fb321e4cbf35fd6b486950',
 'camss.c':BASE['camss.c'],
 'camss-vfe-680.c':BASE['camss-vfe-680.c'],
}
PATCH_SHA='91d292888e563c2d4e0ffc65664cfa4b0a3225cb1f56af9053652998ff0be1d7'
OBSERVER_SHA='23bc970a9bacff901e1336208282904cb9c0add0dfd5bea311194caeacb5451d'
MODULE_SHA='94cc14d9702492bffa2b4e72989db45356cf59ffcce7f4c382be13e7130030b7'
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)

def main():
 if sha(PATCH)!=PATCH_SHA: die('patch hash drift')
 if sha(OBSERVER)!=OBSERVER_SHA: die('observer oracle hash drift')
 observer=json.loads(OBSERVER.read_text())
 if not observer.get('accepted'): die('observer oracle not accepted')
 for f,want in NEW.items():
  got=sha(SRC/f)
  if got!=want: die(f'{f} source hash drift {got}')
 if sha(MOD)!=MODULE_SHA: die('module hash drift')
 vm=subprocess.check_output(['modinfo','-F','vermagic',str(MOD)],text=True).strip()
 if vm!=VERMAGIC: die('module vermagic drift '+vm)

 # Patch scope: only two files, additions only, and zero added MMIO/hardware operations.
 text=PATCH.read_text().splitlines()
 touched=[]; added=[]; removed=[]
 for line in text:
  if line.startswith('+++ b/'):
   touched.append(line[6:])
  elif line.startswith('+') and not line.startswith('+++'):
   added.append(line[1:])
  elif line.startswith('-') and not line.startswith('---'):
   removed.append(line[1:])
 if sorted(touched)!=sorted(['drivers/media/platform/qcom/camss/camss-csid.h','drivers/media/platform/qcom/camss/camss-csid-680.c']):
  die('patch touched-file scope drift '+repr(touched))
 if removed: die('0048 must not remove source lines')
 forbidden=re.compile(r'\b(?:readl|readl_relaxed|writel|writel_relaxed)\b|RTCDM|CSIPHY|SP11_CSID_.*MASK|sensor',re.I)
 bad=[x for x in added if forbidden.search(x)]
 if bad: die('hardware-affecting addition found '+repr(bad))

 c=(SRC/'camss-csid-680.c').read_text(); h=(SRC/'camss-csid.h').read_text()
 fields=['x1e_ipp_irq_seen_or','x1e_ipp_irq_last','x1e_ipp_irq_count']
 for x in fields:
  if h.count(x)!=1: die('telemetry field count drift '+x)
 # Reset must occur after successful software-reset wait and before full-config return,
 # which itself precedes all bounded startup/RUP traffic.
 reset_block='''csid->x1e_ipp_irq_seen_or = 0;\n\t\tcsid->x1e_ipp_irq_last = 0;\n\t\tcsid->x1e_ipp_irq_count = 0;'''
 ri=c.find(reset_block); fi=c.find('return __csid_sp11_front_ipp_full_config(csid);',ri)
 if ri<0 or fi<0 or ri>fi: die('software history reset placement drift')
 # Existing read -> software latch -> existing clear order is mandatory.
 read='ipp_val = readl(csid->base + CSID_IPP_IRQ_STATUS);'
 latch='csid->x1e_ipp_irq_seen_or |= ipp_val;'
 clear='writel(ipp_val, csid->base + CSID_IPP_IRQ_CLEAR);'
 a=c.find(read, c.find('static irqreturn_t csid_isr')); b=c.find(latch,a); d=c.find(clear,b)
 if min(a,b,d)<0 or not a<b<d: die('ISR read/latch/clear order drift')
 if c.count(read)!=1 or c.count(clear)!=1: die('IPP ISR MMIO access count drift')
 if 'ipp-history=%08x/%08x/%u' not in c: die('timeout history print missing')

 out={
  'schema':'sp11-e003h-linux-0048-csid1-ipp-irq-history-inspection-v1',
  'accepted':True,
  'date':'2026-08-30',
  'base_0047_source_sha256':BASE,
  'source_sha256':NEW,
  'patch_sha256':PATCH_SHA,
  'observer_integrity_oracle_sha256':OBSERVER_SHA,
  'module_sha256':MODULE_SHA,
  'module_vermagic':vm,
  'patch_scope':touched,
  'source_lines_removed':0,
  'new_mmio_reads':0,
  'new_mmio_writes':0,
  'history_epoch':'after CSID1 software-reset completion and before full front configuration/startup/RUP traffic',
  'isr_order':['existing IPP status read','software-only OR/last/count latch','existing IPP status clear','existing RUP_DONE bookkeeping'],
  'hardware_behavior_changed':False,
  'runtime_authorized':False,
  'purpose':'Distinguish whether CSID CAMIF/RUP/Epoch events occurred and were consumed by the existing ISR before the 0047 timeout snapshot; VFE Epoch0 absence remains independently observer-safe.'
 }
 op=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/linux-0048-csid1-ipp-irq-history-inspection.json'
 op.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2,sort_keys=True))
 print('PASS: 0048 is software-only CSID IPP IRQ history telemetry on exact 0047 transport')
if __name__=='__main__': main()
