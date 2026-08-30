#!/usr/bin/env python3
import hashlib, json, re
from pathlib import Path

REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
KSRC=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src')
VFE=KSRC/'drivers/media/platform/qcom/camss/camss-vfe-680.c'
CSID=KSRC/'drivers/media/platform/qcom/camss/camss-csid-680.c'
CSID_H=KSRC/'drivers/media/platform/qcom/camss/camss-csid.h'
RAWIRQ=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/vfe1-epoch0-raw-irq-oracle.json'
EXPECTED={
 'vfe':'0dc6269d8b7c0e57e1442dfea374f0e90bdf14b8e8ef58117a505cda6d643036',
 'csid':'59e07a1b8322c7279a051bc1255f8912452300aadbf9bf8086312aec4daca1d0',
 'csid_h':'e581e9a43a74a577aa535a7e33af4f5cd7e8c7af455d3c3fccd083dac2766f44',
 'rawirq':'103d1bd11a5ac24d99602a909e24469e1b2bd177cdc499b857bda340308f0322',
}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)

def main():
 for k,p in [('vfe',VFE),('csid',CSID),('csid_h',CSID_H),('rawirq',RAWIRQ)]:
  got=sha(p)
  if got!=EXPECTED[k]: die(f'{k} identity drift {got}')
 v=VFE.read_text(); c=CSID.read_text(); raw=json.loads(RAWIRQ.read_text())
 if 'static irqreturn_t vfe_isr(int irq, void *dev)\n{\n\treturn IRQ_HANDLED;\n}' not in v:
  die('VFE680 ISR no-op contract drift')
 csid_need=[
  'ipp_val = readl(csid->base + CSID_IPP_IRQ_STATUS);',
  'if (ipp_val)\n\t\t\twritel(ipp_val, csid->base + CSID_IPP_IRQ_CLEAR);',
  'if (ipp_val & CSID_IPP_RUP_DONE)\n\t\t\tcsid_reg_update_clear(csid, MSM_CSID_STREAM_PIX);',
  'enable_irq(csid->irq)',
 ]
 # enable_irq lives in camss-csid.c; first three are the decisive CSID clearing contract.
 for x in csid_need[:3]:
  if x not in c: die('CSID ISR contract drift: '+x)
 if raw['events']['epoch0']['raw']!='BUS status1 bit21': die('Windows Epoch0 raw mapping drift')
 if raw['events']['video']['raw']!='TOP status1 bit0': die('Windows VIDEO raw mapping drift')
 out={
  'schema':'sp11-e003h-linux-irq-observer-integrity-v1','accepted':True,'date':'2026-08-30',
  'source_sha256':EXPECTED,
  'vfe680':{
   'isr':'no-op; returns IRQ_HANDLED without reading or clearing TOP/BUS status',
   'epoch0_observer_integrity':'strong: normal Linux VFE ISR cannot consume BUS status1 bit21 before the private poll',
   'consequence':'0047 absence of VFE1 BUS status1 bit21 / Epoch0 remains a valid hardware-observation result'},
  'csid680':{
   'irq_enabled_while_powered':True,
   'isr_order':['read TOP','clear TOP','read RX','clear RX','read BUF_DONE','clear BUF_DONE','read IPP +0xac','clear full nonzero IPP value through +0xb4','process RUP_DONE','read/clear RDI statuses','global clear'],
   'ipp_timeout_snapshot_integrity':'weak: a later timeout read of IPP +0xac is not an OR-history and cannot prove bits were never asserted earlier',
   'superseded_inference':'0042-0047 final IPP_IRQ_STATUS=0x00011e00 alone does not prove CAMIF_SOF/CAMIF_EOF/CAMIF_EPOCH0/CAMIF_EPOCH1/RUP_DONE never occurred',
   'preserved_facts':['37,016 received packets in the bounded runs','zero ECC/CRC in the bounded runs','final live IPP status 0x00011e00 at each captured timeout','VFE1 raw BUS Epoch0 absent in 0047']},
  'next_diagnostic':{
   'name':'0048 CSID IPP IRQ history telemetry',
   'allowed_delta':['software-only OR of each already-read nonzero IPP IRQ value before existing clear','software-only last IPP IRQ value','software-only nonzero IPP IRQ sample count','reset these software fields immediately before bounded IPP enable','print fields in existing timeout dump'],
   'forbidden_delta':['IRQ mask change','IRQ clear change','new MMIO read in ISR','new MMIO write','RT-CDM byte/order change','VFE/BUS change','CSID configuration/start change','sensor/CSIPHY change'],
   'runtime_authorized':False},
  'runtime_authorized':False,
 }
 op=Path(__file__).with_name('irq-observer-integrity-oracle.json')
 op.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2,sort_keys=True))
 print('PASS: VFE Epoch0 polling is observer-safe; CSID final IPP status is not historical evidence')
if __name__=='__main__': main()
