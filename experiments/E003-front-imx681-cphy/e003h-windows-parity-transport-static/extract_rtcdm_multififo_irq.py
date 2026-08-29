#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
EXPECTED='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
BASE=0x140000000; TEXT_RAW=0x400; TEXT_RVA=0x1000; TEXT_SIZE=0x3d48c

def die(s): raise SystemExit('FAIL: '+s)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('binary',type=Path); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
 b=a.binary.read_bytes(); h=hashlib.sha256(b).hexdigest()
 if h!=EXPECTED or len(b)!=376560: die('binary identity')
 md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.skipdata=True; xs={i.address-BASE:i for i in md.disasm(b[TEXT_RAW:TEXT_RAW+TEXT_SIZE],BASE+TEXT_RVA)}
 checks={
  0x2919c:('ldr','[x9, #0x44]'), 0x291a0:('and','#0x70007'),
  0x291ac:('ldr','[x8, #0x144]'),0x291b0:('and','#0x70007'),
  0x291bc:('ldr','[x8, #0x244]'),0x291c0:('and','#0x70007'),
  0x291cc:('ldr','[x8, #0x344]'),0x291d8:('and','#0x70007'),
  0x29208:('cbnz','w21'),
  0x29228:('str','[x8, #0x34]'),0x29230:('str','[x8, #0x134]'),0x29238:('str','[x8, #0x234]'),0x29240:('str','[x8, #0x334]'),
  0x29248:('str','[x8, #0x38]'),0x29250:('str','[x8, #0x138]'),0x29258:('str','[x8, #0x238]'),0x29260:('str','[x8, #0x338]'),
  0x29264:('str','w21'), 0x29268:('str','x19'), 0x292a8:('bl','#0x14002bef8'),
 }
 for r,(mn,sub) in checks.items():
  i=xs.get(r)
  if not i or i.mnemonic!=mn or sub not in i.op_str: die(f'RVA 0x{r:x}: {i.mnemonic if i else None} {i.op_str if i else None}')
 # CBNZ must target first clear block exactly.
 if '0x140029220' not in xs[0x29208].op_str: die('FIFO0 status gate target drift')
 # Ensure no IRQ_CONTEXT_STATUS +0x2c read in handler.
 for r,i in xs.items():
  if 0x29120 <= r < 0x2930c and i.mnemonic=='ldr' and '#0x2c]' in i.op_str: die('context status read appeared')
 out={
  'accepted':True,'schema':'sp11-e003h-windows-rtcdm1-multififo-irq-v1',
  'source':{'sha256':h,'bytes':len(b),'driver':'qccamisp8380.sys'},
  'handler_rva':'0x29120..0x2930c',
  'status_reads':{'fifo0':'0x44','fifo1':'0x144','fifo2':'0x244','fifo3':'0x344'},
  'mask':'0x00070007',
  'dispatch_gate':'masked FIFO0 status (w21) must be nonzero; CBNZ 0x29208 -> clear block 0x29220',
  'clear_values':'masked status0/1/2/3 written to +0x34/+0x134/+0x234/+0x334',
  'clear_commands':'1 written to +0x38/+0x138/+0x238/+0x338',
  'callback_payload':'stack pair at +0x20 contains masked FIFO0 status w21 and CDM context x19; async enqueue call RVA 0x292a8',
  'irq_context_status_read':False,
  'linux_consequence':'When FIFO0 has known status, mirror Windows by sampling and acknowledging all four FIFO status banks. Completion remains driven by FIFO0. Record other banks but do not invent front-path semantics from them.',
  'runtime_authorized':False,
 }
 a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS: Windows RT-CDM1 IRQ gate is masked FIFO0 status and acknowledges all four FIFO status banks')
if __name__=='__main__': main()
