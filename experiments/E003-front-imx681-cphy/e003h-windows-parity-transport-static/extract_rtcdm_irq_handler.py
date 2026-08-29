#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
from capstone.arm64 import ARM64_OP_MEM

EXPECTED_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
IMAGE=0x140000000
TEXT_RAW=0x400; TEXT_RVA=0x1000; TEXT_SIZE=0x3d48c
START=0x29120; END=0x2930c

def die(s): raise SystemExit('FAIL: '+s)
def need(m,rva,mn,frag):
    x=m.get(rva)
    if not x: die(f'missing RVA {rva:#x}')
    if x.mnemonic!=mn or frag not in x.op_str:
        die(f'{rva:#x}: expected {mn} {frag}, got {x.mnemonic} {x.op_str}')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('binary',type=Path); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    data=a.binary.read_bytes(); h=hashlib.sha256(data).hexdigest()
    if h!=EXPECTED_SHA or len(data)!=376560: die('binary identity mismatch')
    md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.detail=True; md.skipdata=True
    xs=list(md.disasm(data[TEXT_RAW:TEXT_RAW+TEXT_SIZE],IMAGE+TEXT_RVA)); m={x.address-IMAGE:x for x in xs}
    checks=[
      (0x2915c,'ldr','[x19, #0x48]'),
      (0x2919c,'ldr','[x9, #0x44]'),(0x291a0,'and','#0x70007'),
      (0x291a8,'ldr','[x19, #0x48]'),(0x291ac,'ldr','[x8, #0x144]'),(0x291b0,'and','#0x70007'),
      (0x291b8,'ldr','[x19, #0x48]'),(0x291bc,'ldr','[x8, #0x244]'),(0x291c0,'and','#0x70007'),
      (0x291c8,'ldr','[x19, #0x48]'),(0x291cc,'ldr','[x8, #0x344]'),(0x291d8,'and','#0x70007'),
      (0x29220,'ldr','[x19, #0x48]'),(0x29228,'str','[x8, #0x34]'),
      (0x2922c,'ldr','[x19, #0x48]'),(0x29230,'str','[x8, #0x134]'),
      (0x29234,'ldr','[x19, #0x48]'),(0x29238,'str','[x8, #0x234]'),
      (0x2923c,'ldr','[x19, #0x48]'),(0x29240,'str','[x8, #0x334]'),
      (0x29244,'ldr','[x19, #0x48]'),(0x29248,'str','[x8, #0x38]'),
      (0x2924c,'ldr','[x19, #0x48]'),(0x29250,'str','[x8, #0x138]'),
      (0x29254,'ldr','[x19, #0x48]'),(0x29258,'str','[x8, #0x238]'),
      (0x2925c,'ldr','[x19, #0x48]'),(0x29260,'str','[x8, #0x338]'),
    ]
    for z in checks: need(m,*z)
    fn=[x for x in xs if IMAGE+START<=x.address<IMAGE+END]
    context_reads=[]; status_reads=[]; clear_writes=[]
    for x in fn:
        for op in x.operands:
            if op.type==ARM64_OP_MEM and op.mem.disp==0x2c:
                context_reads.append(hex(x.address-IMAGE))
        if x.mnemonic=='ldr' and any(t in x.op_str for t in ['#0x44]','#0x144]','#0x244]','#0x344]']): status_reads.append(hex(x.address-IMAGE))
        if x.mnemonic=='str' and any(t in x.op_str for t in ['#0x34]','#0x134]','#0x234]','#0x334]','#0x38]','#0x138]','#0x238]','#0x338]']): clear_writes.append(hex(x.address-IMAGE))
    if context_reads: die('IRQ_CONTEXT_STATUS +0x2c read appeared in handler: '+str(context_reads))
    # Confirm four literal status masks occur in the exact handler.
    masks=[x.address-IMAGE for x in fn if x.mnemonic=='and' and '#0x70007' in x.op_str]
    if masks != [0x291a0,0x291b0,0x291c0,0x291d8]: die('status mask sequence drift')
    out={
      'accepted':True,'schema':'sp11-e003h-windows-rtcdm1-irq-handler-v1',
      'source':{'driver':'qccamisp8380.sys','bytes':len(data),'sha256':h,'image_base':'0x140000000'},
      'handler':{'rva_start':'0x29120','rva_end_exclusive':'0x2930c','mapped_base_object_field':'0x48'},
      'irq_context_status_0x2c_read_in_handler':False,
      'fifo_status_reads':['FIFO0 +0x44','FIFO1 +0x144','FIFO2 +0x244','FIFO3 +0x344'],
      'status_mask':'0x00070007',
      'status_mask_rvas':[hex(x) for x in masks],
      'clear_behavior':'masked per-FIFO status -> CLEAR (+0x34/+0x134/+0x234/+0x334), then 1 -> CLEAR_CMD (+0x38/+0x138/+0x238/+0x338)',
      'clear_write_rvas':clear_writes,
      'linux_consequence':'Do not gate RT-CDM1 FIFO0 ISR on IRQ_CONTEXT_STATUS bit0. Read IRQ0_STATUS directly, derive handled bits with 0x00070007, and clear only the masked known status. Unknown/error raw bits may still fail closed after the known status is acknowledged.'
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: exact Windows RT-CDM1 handler uses FIFO status directly; no IRQ_CONTEXT_STATUS read; clears masked 0x00070007 status')
if __name__=='__main__': main()
