#!/usr/bin/env python3
import argparse, hashlib, json, re, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

DRIVER_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
DRIVER_BYTES=376560
LOG_SHA='1e3e810ae170dabb003491b6b8522c3b77dbd5964a14445ce7bbd3636e5b77ec'
LOG_BYTES=3572
IMAGE=0x140000000
EXPECTED_CYCLE=[0x3,0xd,0xe,0x10,0x12]

def die(s): raise SystemExit('FAIL: '+s)
def sha(b): return hashlib.sha256(b).hexdigest()

def pe_sections(data):
    pe=struct.unpack_from('<I',data,0x3c)[0]
    n=struct.unpack_from('<H',data,pe+6)[0]
    opt=struct.unpack_from('<H',data,pe+20)[0]
    sh=pe+24+opt; out=[]
    for i in range(n):
        o=sh+i*40
        name=data[o:o+8].rstrip(b'\0').decode('ascii')
        vs,va,rs,raw=struct.unpack_from('<IIII',data,o+8)
        out.append((name,va,vs,raw,rs))
    return out

def rva_off(secs,rva):
    for _,va,vs,raw,rs in secs:
        if va <= rva < va+max(vs,rs): return raw+(rva-va)
    die(f'RVA unmapped 0x{rva:x}')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--driver',type=Path,required=True)
    ap.add_argument('--log',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args()
    data=a.driver.read_bytes(); logb=a.log.read_bytes()
    if len(data)!=DRIVER_BYTES or sha(data)!=DRIVER_SHA: die('driver identity drift')
    if len(logb)!=LOG_BYTES or sha(logb)!=LOG_SHA: die('live log identity drift')
    log=logb.decode('utf-16')
    ids=[int(x,16) for x in re.findall(r'^EV id=([0-9a-fA-F]+)\r?$',log,re.M)]
    if ids != EXPECTED_CYCLE*5: die(f'live completion sequence drift: {ids!r}')

    secs=pe_sections(data); text=next(s for s in secs if s[0]=='.text')
    _,va,vs,raw,rs=text
    md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.skipdata=True
    ins={x.address-IMAGE:x for x in md.disasm(data[raw:raw+rs],IMAGE+va) if x.mnemonic!='.byte'}
    def need(rva,mn,frag=None):
        x=ins.get(rva)
        if not x or x.mnemonic!=mn or (frag and frag not in x.op_str): die(f'anchor drift 0x{rva:x}: {x}')
    anchors=[
      (0x1f438,'cmp','w8, #3'),(0x1f468,'mov','w1, #0'),(0x1f470,'bl','#0x140026460'),
      (0x1f494,'mov','w21, #0x3001'),(0x1f498,'mov','w27, #0x3002'),(0x1f504,'mov','w8, #0x3000'),
      (0x1fd48,'cmp','w8, #0xd'),(0x1fd64,'mov','w1, #5'),(0x1fd6c,'bl','#0x140026460'),
      (0x1fd84,'cmp','w8, #0x10'),(0x1fda0,'mov','w1, #7'),(0x1fda8,'bl','#0x140026460'),
      (0x1fdc0,'cmp','w8, #0xe'),(0x1fddc,'mov','w1, #6'),(0x1fde4,'bl','#0x140026460'),
      (0x1fdfc,'cmp','w8, #0x12'),(0x1fe18,'mov','w1, #9'),(0x1fe20,'bl','#0x140026460'),
      # qccamisp8380+0x26460 is not a cross-group sequencer. The event branch
      # supplies its group index in w1; the helper uses that index to select
      # one independent queue pointer, pops one FIFO record, decrements that
      # queue's count, advances its own ring index, and wraps by its capacity.
      (0x26500,'sxtw','x21, w1'),(0x2650c,'add','x10, x21, #0x66b'),
      (0x26514,'ldr','x9, [x8, x10, lsl #3]'),(0x26524,'cbz','w9'),
      (0x26550,'ldr','w11, [x19, #0x2c]'),(0x26558,'ldr','w10, [x19, #0x14]'),
      (0x26570,'ldr','w8, [x19, #0x18]'),(0x26574,'sub','w8, w8, #1'),
      (0x26578,'str','w8, [x19, #0x18]'),(0x2657c,'ldr','w8, [x19, #0x2c]'),
      (0x26580,'add','w8, w8, #1'),(0x26584,'str','w8, [x19, #0x2c]'),
      (0x26588,'ldr','w10, [x19, #0x2c]'),(0x2658c,'ldr','w9, [x19, #0x10]'),
      (0x26598,'udiv','w8, w10, w9'),(0x265a0,'msub','w8, w8, w9, w10'),
      (0x265a4,'str','w8, [x19, #0x2c]')]
    for x in anchors: need(*x)

    strings={
      'video':(0x37a80,b'IFE%d IFE VIDEO buf done Irq occured.\0'),
      'aec_be':(0x37bb8,b'IFE%d IFE AEC_BE stats buf done Irq occured.\0'),
      'awb_bg':(0x37c18,b'IFE%d IFE AWB_BG stats buf done Irq occured.\0'),
      'tintless_bg':(0x37c48,b'IFE%d IFE Tintless_BG stats buf done Irq occured.\0'),
      'rs':(0x37c80,b'IFE%d IFE RS stats buf done Irq occured.\0')}
    for name,(rva,s) in strings.items():
        off=rva_off(secs,rva)
        if data[off:off+len(s)]!=s: die(name+' diagnostic drift')
    for s in (b'VIDEO\0',b'AEC_BE_BHIST\0',b'TINTLESS_BG\0',b'AWB_BG\0',b'RS\0'):
        if data.find(s)<0: die('group name missing '+repr(s))

    groups=[
      {'event_id':3,'group_index':0,'group':'VIDEO','clients':[0,1,2,3],
       'resources':['FULL_Y','FULL_C','DS4','DS16'],'ports':['0x3000:0','0x3000:1','0x3001','0x3002'],
       'user_visible':True},
      {'event_id':0xd,'group_index':5,'group':'AEC_BE_BHIST','clients':[11,12],
       'resources':['AEC_BE','BHIST'],'ports':['0x301c','0x300f'],'user_visible':False},
      {'event_id':0xe,'group_index':6,'group':'TINTLESS_BG','clients':[13],
       'resources':['TL_BG'],'ports':['0x300c'],'user_visible':False},
      {'event_id':0x10,'group_index':7,'group':'AWB_BG','clients':[14],
       'resources':['AWB_BG'],'ports':['0x300e'],'user_visible':False},
      {'event_id':0x12,'group_index':9,'group':'RS','clients':[18],
       'resources':['RS'],'ports':['0x3010'],'user_visible':False}]
    out={
      'schema':'sp11-e003h-windows-vfe1-completion-groups-v1','accepted':True,
      'driver':{'bytes':len(data),'sha256':sha(data)},
      'live_log':{'bytes':len(logb),'sha256':sha(logb),'complete_cycles':5,
                  'observed_cycle_event_ids':[hex(x) for x in EXPECTED_CYCLE],
                  'all_valid_event_ids':[hex(x) for x in ids],
                  'cross_group_order':'observed in five cycles; not a driver-enforced dependency'},
      'groups':groups,
      'group_queue_model':{
        'helper_rva':'0x26460','selector':'caller group index in w1',
        'queue_pointer_table':'object + (0x66b + group_index) * 8',
        'queue_fields':{'capacity':'+0x10','stride':'+0x14','count':'+0x18','read_index':'+0x2c'},
        'dequeue':'one independent FIFO pop per completion group',
        'cross_group_order_enforced':False},
      'linux_logical_completion_mask':{'VIDEO':'0x01','AEC_BE_BHIST':'0x02','TINTLESS_BG':'0x04','AWB_BG':'0x08','RS':'0x10','ALL':'0x1f'},
      'linux_consequence':{
        'video_event':'one userspace QC10C surface completion; FULL Y/C are not independent frames',
        'video_group_internal_outputs':'DS4 and DS16 share VIDEO completion ownership with FULL',
        'stats':'AEC_BE and BHIST share one completion group; TL_BG, AWB_BG and RS are distinct groups',
        'completion_order':'do not require the five observed groups to arrive in one fixed cross-group order; preserve FIFO order independently within each group',
        'slot_reuse':'a frame bundle containing VIDEO plus auxiliary buffers must not be reused until all five active completion groups have completed',
        'generic_vfe_buf_done':'single-WM generic completion is not a valid X1E VFE1 PIX model'} }
    txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.output: a.output.write_text(txt)
    else: print(txt,end='')
    print('PASS: five observed cycles repeat VIDEO -> AEC_BE_BHIST -> TINTLESS_BG -> AWB_BG -> RS; Windows dequeues each group through an independent FIFO')
if __name__=='__main__': main()
