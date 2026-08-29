#!/usr/bin/env python3
import argparse, hashlib, json, re, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

DRIVER_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
DRIVER_BYTES=376560
LOG_SHA='52a5546e9d908cb6a0a8cb41879cea9b4e4aabb0fa8f83194a97c2c0c14e18e4'
LOG_BYTES=668
BASE=0x140000000

def die(s): raise SystemExit('FAIL: '+s)
def sha(b): return hashlib.sha256(b).hexdigest()
def pe_text(data):
    pe=struct.unpack_from('<I',data,0x3c)[0]
    n=struct.unpack_from('<H',data,pe+6)[0]
    opt=struct.unpack_from('<H',data,pe+20)[0]
    sh=pe+24+opt
    for i in range(n):
        o=sh+i*40
        name=data[o:o+8].rstrip(b'\0').decode('ascii',errors='ignore')
        vs,va,rs,raw=struct.unpack_from('<IIII',data,o+8)
        if name=='.text': return va,raw,rs
    die('.text missing')

def verify_driver(path):
    b=path.read_bytes()
    if len(b)!=DRIVER_BYTES or sha(b)!=DRIVER_SHA: die('driver identity drift')
    va,raw,rs=pe_text(b)
    md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.skipdata=True
    ins={x.address-BASE:(x.mnemonic,x.op_str) for x in md.disasm(b[raw:raw+rs],BASE+va) if x.mnemonic!='.byte'}
    anchors={
      0x1dc38:('ldr','[x19, #0x140]'), 0x1dc40:('ldr','[x8, #0x44]'), 0x1dc44:('str','[x20, #4]'),
      0x1dc48:('ldr','[x19, #0x140]'), 0x1dc4c:('ldr','[x8, #0x48]'), 0x1dc50:('str','[x20, #8]'),
      0x1dc54:('ldr','[x19, #0x150]'), 0x1dc58:('ldr','[x8, #0x28]'), 0x1dc5c:('str','[x20, #0xc]'),
      0x1dc60:('ldr','[x19, #0x150]'), 0x1dc64:('ldr','[x8, #0x2c]'), 0x1dc68:('str','[x20, #0x10]'),
      0x1dcb4:('str','[x8, #0x3c]'), 0x1dcc8:('str','[x8, #0x40]'), 0x1dce0:('str','[x8, #0x30]'),
      0x1dcf0:('str','[x9, #0x3c]'), 0x1dcfc:('str','[x9, #0x40]'), 0x1dd04:('str','[x8, #0x30]'),
      0x1eff0:('ldp','[x23, #4]'), 0x1f010:('and','w1, w2, #1'),
      0x1f0d0:('ubfx','w25, w2, #0x15, #1'), 0x1f3e8:('cbz','w25'), 0x1f410:('bl','#0x140025268'),
    }
    got={}
    for r,(mn,frag) in anchors.items():
        x=ins.get(r)
        if not x or x[0]!=mn or frag not in x[1]: die(f'anchor drift 0x{r:x}: {x}')
        got[f'0x{r:x}']=f'{x[0]} {x[1]}'
    return got

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--driver',type=Path,required=True); ap.add_argument('--log',type=Path,required=True); ap.add_argument('-o','--output',type=Path); a=ap.parse_args()
    anchors=verify_driver(a.driver)
    raw=a.log.read_bytes()
    if len(raw)!=LOG_BYTES or sha(raw)!=LOG_SHA: die('live log identity drift')
    text=raw.decode('utf-16')
    m=re.search(r'IFE=([0-9a-f]+) TOP0=([0-9a-f]{8}) TOP1=([0-9a-f]{8}) BUS0=([0-9a-f]{8}) BUS1=([0-9a-f]{8}) W25=([0-9a-f]+)',text,re.I)
    if not m: die('live event line missing')
    ife,top0,top1,bus0,bus1,w25=[int(x,16) for x in m.groups()]
    if ife!=1 or w25!=1 or not (bus1 & (1<<21)): die('IFE1 Epoch0 live signature drift')
    if '# ac71034 0007f051 00000000' not in text: die('TOP masks live drift')
    if '# ac71c18 d0000000 00000000' not in text: die('BUS masks live drift')
    out={
      'schema':'sp11-e003h-vfe1-raw-irq-mapping-v1','accepted':True,
      'source':{'driver_bytes':DRIVER_BYTES,'driver_sha256':DRIVER_SHA,'live_log_bytes':len(raw),'live_log_sha256':sha(raw)},
      'kmd_irq_reader':{
        'rva':'0x1dc20',
        'top_base_object_field':'0x140','bus_base_object_field':'0x150',
        'message_mapping':{
          '+0x04':'TOP status0 = TOP+0x44','+0x08':'TOP status1 = TOP+0x48',
          '+0x0c':'BUS status0 = BUS+0x28','+0x10':'BUS status1 = BUS+0x2c'},
        'top_clear':'status0 -> TOP+0x3c; status1 -> TOP+0x40; 1 -> TOP+0x30',
        'bus_clear':'status0 -> BUS+0x3c; status1 -> BUS+0x40; 1 -> BUS+0x30'},
      'events':{
        'video':{'raw':'TOP status1 bit0','event_id':3},
        'epoch0':{'raw':'BUS status1 bit21','dpc_register':'w25','handler_rva':'0x25268','isr_callsite_rva':'0x1f410'}},
      'live_hit':{'ife':ife,'top0':f'0x{top0:08x}','top1':f'0x{top1:08x}','bus0':f'0x{bus0:08x}','bus1':f'0x{bus1:08x}','epoch0_bit_set':bool(bus1&(1<<21))},
      'live_masks':{'top_mask0':'0x0007f051','top_mask1':'0x00000000','bus_mask0':'0xd0000000','bus_mask1':'0x00000000'},
      'linux_consequence':'A bounded X1E VFE1 PIX candidate may keep the normal IRQ path untouched and poll raw BUS status1 bit21 for Epoch0 and TOP status1 bit0 for VIDEO, then clear with the exact Windows clear registers. Do not infer other event bits from this oracle.',
      'runtime_authorized':False}
    txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.output:a.output.write_text(txt)
    else:print(txt,end='')
    print('PASS: VFE1 raw IRQ mapping closes Epoch0=BUS status1 bit21 and VIDEO=TOP status1 bit0')
if __name__=='__main__': main()
