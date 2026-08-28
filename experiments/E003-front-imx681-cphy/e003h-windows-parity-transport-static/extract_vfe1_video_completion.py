#!/usr/bin/env python3
import argparse, hashlib, json, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

EXPECTED_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
EXPECTED_BYTES=376560
IMAGE_BASE=0x140000000
TEXT_RAW=0x400
TEXT_RVA=0x1000
TEXT_SIZE=0x3d48c

def die(s): raise SystemExit('FAIL: '+s)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('binary',type=Path)
 ap.add_argument('-o','--output',type=Path)
 a=ap.parse_args(); data=a.binary.read_bytes(); sha=hashlib.sha256(data).hexdigest()
 if sha!=EXPECTED_SHA or len(data)!=EXPECTED_BYTES: die(f'binary mismatch sha={sha} bytes={len(data)}')
 md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.detail=True; md.skipdata=True
 xs=list(md.disasm(data[TEXT_RAW:TEXT_RAW+TEXT_SIZE],IMAGE_BASE+TEXT_RVA)); m={x.address-IMAGE_BASE:x for x in xs if x.mnemonic!='.byte'}
 def need(rva,mn,sub=None):
  x=m.get(rva)
  if not x or x.mnemonic!=mn or (sub is not None and sub not in x.op_str): die(f'anchor drift 0x{rva:x}: {x}')
  return x
 # Mask programming: literal pool 0x7f051 -> TOP mask0; immediate d0000000 -> BUS mask0.
 if struct.unpack_from('<Q',data,0x1c740)[0] != 0x000000000007f051: die('TOP mask literal drift')
 for rva,mn,sub in [
  (0x1d2bc,'ldr','0x14001d340'),(0x1d2c0,'add','#0x15c'),(0x1d2c4,'mov','#0xd0000000'),
  (0x1d2d4,'ldr','[x0, #0x140]'),(0x1d2dc,'str','[x8, #0x34]'),
  (0x1d2e8,'ldr','[x0, #0x140]'),(0x1d2f4,'str','[x9, #0x38]'),
  (0x1d300,'ldr','[x11]'),(0x1d304,'ldr','[x0, #0x150]'),(0x1d308,'str','[x9, #0x18]')]: need(rva,mn,sub)
 # DPC: x23+4 status0, x23+8 status1. status1 bit0 -> w1, then event id 3 into first list slot.
 for rva,mn,sub in [
  (0x1eff0,'ldp','[x23, #4]'),(0x1f010,'and','w1, w2, #1'),
  (0x1f114,'cmp','w1, #0'),(0x1f118,'mov','w0, #3'),(0x1f11c,'csel','w2, w0, w2, ne'),
  (0x1f120,'str','[sp, #0x58]'),(0x1f434,'ldr','[x9, w8, sxtw #2]'),
  (0x1f438,'cmp','w8, #3'),(0x1f43c,'b.ne',None),
  (0x1f444,'adrp','0x140037000'),(0x1f448,'add','#0xa80')]: need(rva,mn,sub)
 # Exact diagnostic string at mapped RVA 0x37a80/raw 0x36e80.
 s=b'IFE%d IFE VIDEO buf done Irq occured.\x00'
 if data[0x36e80:0x36e80+len(s)] != s: die('VIDEO completion diagnostic string drift')
 out={
  'schema':'sp11-e003h-windows-vfe1-video-completion-v1','accepted':True,
  'source':{'binary':'qccamisp8380.sys','bytes':len(data),'sha256':sha},
  'irq_masks':{
   'top_mask0':'0x0007f051','top_mask0_mmio_offset':'0x0034',
   'bus_mask0':'0xd0000000','bus_mask0_mmio_offset_from_bus_base':'0x0018',
   'top_mask1':'object-derived; not frozen by this oracle'},
  'video_completion':{
   'top_status_word':'status1','top_status_bit':0,'event_id':3,
   'diagnostic':'IFE%d IFE VIDEO buf done Irq occured.',
   'interpretation':'Windows emits one VIDEO completion event for the VIDEO/FULL path; do not model FULL_Y and FULL_C as two independent vb2 frames.'},
  'linux_consequence':'Future X1E PIX/QC10C completion must complete the one contiguous Y/C surface once per Windows VIDEO event. Keep VFE680 RDI completion behavior untouched.'}
 txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
 if a.output: a.output.write_text(txt)
 else: print(txt,end='')
 print('PASS: Windows VFE VIDEO completion is TOP status1 bit0 -> event 3; TOP/BUS masks pinned')
if __name__=='__main__': main()
