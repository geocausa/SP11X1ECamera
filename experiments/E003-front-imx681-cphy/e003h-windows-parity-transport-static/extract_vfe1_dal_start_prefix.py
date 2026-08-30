#!/usr/bin/env python3
import csv, hashlib, json, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
BIN=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys')
EXPECTED_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
EXPECTED_BYTES=376560
IMAGE_BASE=0x140000000
TEXT_RAW=0x400
TEXT_RVA=0x1000
TEXT_SIZE=0x3d48c
CROSS=STATIC/'vfe1-bus-cdm-crossorder-oracle.json'
EXPECTED_CROSS_SHA='b495cc833c45e97b1467749bf094bb3035c5e6070bd0ea13d26a99ceec6acce6'
EXPECTED_PACKET_CSV_SHA={
 0:'e031eeaf777fc366761b4d0fa7bead961d5c9e1a63c70d92b3c21b1391ac766f',
 1:'222bee6fe98b9df847df616d0ccb2fad11c680189d1f3484003df83a298a2420',
 2:'282bb0f140c5b7ec916823511aca5cd14296bb80b3d519a7f028a79a9f584917',
 3:'72f800492e990d678c880d540c748279e3b3abc900dc83c8e2d4fa5495a1d127',
}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)

def main():
 data=BIN.read_bytes(); got=hashlib.sha256(data).hexdigest()
 if got!=EXPECTED_SHA or len(data)!=EXPECTED_BYTES: die(f'binary drift sha={got} bytes={len(data)}')
 cross_sha=sha(CROSS)
 if cross_sha!=EXPECTED_CROSS_SHA: die(f'cross-order source hash drift {cross_sha}')
 cross=json.loads(CROSS.read_text())
 if not cross.get('accepted'): die('cross-order oracle not accepted')
 want=['CDM_START','IFE_START','IFE803_PACKET0','IFE803_PACKET1','VFE1_BUS_STATIC_CONFIG','VFE1_BUS_ENABLE','VFE1_INITIAL_DYNAMIC_ADDRESSES','IFE803_PACKET2','IFE803_PACKET3','CSID_START','ISP_START_DONE']
 if cross.get('cross_layer_order')!=want: die('cross-order drift')

 md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.detail=True; md.skipdata=True
 xs=list(md.disasm(data[TEXT_RAW:TEXT_RAW+TEXT_SIZE],IMAGE_BASE+TEXT_RVA))
 ins={x.address-IMAGE_BASE:x for x in xs if x.mnemonic!='.byte'}
 def need(rva,mn,sub=None):
  x=ins.get(rva)
  if not x or x.mnemonic!=mn or (sub is not None and sub not in x.op_str):
   die(f'anchor drift 0x{rva:x}: {None if x is None else (x.mnemonic,x.op_str)}')
  return {'rva':f'0x{rva:x}','mnemonic':mn,'operands':x.op_str}

 # Generation-selected callback table slots.
 anchors=[]
 for a in [
  (0x19fec,'adrp','0x14001b000'),(0x19ff0,'add','#0xe80'),
  (0x19ff4,'adrp','0x14001d000'),(0x19ff8,'add','#0x2b0'),
  (0x19ffc,'csel','ne'),(0x1a000,'add','#0x6b, lsl #12'),(0x1a004,'str','#0x690'),
  (0x1a008,'adrp','0x14001c000'),(0x1a00c,'add','#0xe0'),
  (0x1a010,'adrp','0x14001d000'),(0x1a014,'add','#0x820'),
  (0x1a018,'csel','ne'),(0x1a01c,'add','#0x6b, lsl #12'),(0x1a020,'str','#0x698'),
 ]: anchors.append(need(*a))

 # Exact VFE680 mask writer. Literal contains pair top mask0/top mask1.
 if struct.unpack_from('<Q',data,0x1c740)[0] != 0x000000000007f051:
  die('TOP mask pair literal drift')
 for a in [
  (0x1d2bc,'ldr','0x14001d340'),(0x1d2c0,'add','#0x15c'),(0x1d2c4,'mov','#0xd0000000'),
  (0x1d2c8,'str','[x10]'),(0x1d2cc,'add','#0x164'),(0x1d2d0,'str','[x11]'),
  (0x1d2d4,'ldr','[x0, #0x140]'),(0x1d2dc,'str','[x8, #0x34]'),
  (0x1d2e8,'ldr','[x0, #0x140]'),(0x1d2f4,'str','[x9, #0x38]'),
  (0x1d300,'ldr','[x11]'),(0x1d304,'ldr','[x0, #0x150]'),(0x1d308,'str','[x9, #0x18]'),
  (0x1d30c,'ldr','[x0, #0x168]'),(0x1d310,'ldr','[x0, #0x150]'),(0x1d314,'str','[x9, #0x1c]'),
  (0x1d318,'add','#0x6b, lsl #12'),(0x1d31c,'ldrb','#0x6f0'),(0x1d320,'cbz','0x14001d330'),
  (0x1d324,'ldr','[x0, #0x150]'),(0x1d328,'mov','#0xfffffff'),(0x1d32c,'str','[x9, #8]')
 ]: anchors.append(need(*a))

 # Current-generation pre-BUS top transition.
 for a in [(0x1d820,'ldr','[x0, #0x140]'),(0x1d824,'str','wzr, [x8, #0x24]'),(0x1d828,'ret',None)]:
  anchors.append(need(*a))

 # Normal DAL_ife_start first-start gate and callback order.
 for a in [
  (0x270d4,'ldrb',None),(0x270d8,'cbnz','0x140027128'),
  (0x270dc,'add','#0x6b, lsl #12'),(0x270e8,'ldr','[x8, #0x690]'),
  (0x270ec,'mov','x0, x20'),(0x27100,'blr','x15'),
  (0x27104,'add','#0x6b, lsl #12'),(0x27110,'ldr','[x8, #0x698]'),
  (0x2710c,'mov','x0, x20'),(0x27124,'blr','x15'),
  (0x27128,'mov','x1, x22'),(0x2712c,'mov','x0, x20'),(0x27130,'bl','0x1400274c8'),
 ]: anchors.append(need(*a))

 # Packet-local VFE TOP +0x24 writes are exact and all equal 0x6000.
 packet_writes=[]
 for n in range(4):
  p=STATIC/'windows-ife-cdm'/f'packet{n}-register-writes.csv'
  psha=sha(p)
  if psha!=EXPECTED_PACKET_CSV_SHA[n]: die(f'packet{n} CSV hash drift {psha}')
  rows=list(csv.DictReader(p.open()))
  hits=[r for r in rows if int(r['absolute_address'],16)==0x0ac71024]
  if len(hits)!=1: die(f'packet{n}: expected one VFE1 +0x24 hit got {len(hits)}')
  r=hits[0]
  if int(r['register_offset'],16)!=0x24 or int(r['value'],16)!=0x6000:
   die(f'packet{n}: +0x24 write drift {r}')
  packet_writes.append({'packet':n,'command_offset':r['stream_offset'],'register_offset':'0x24','physical_address':'0x0ac71024','value':'0x00006000','csv_sha256':psha})

 out={
  'schema':'sp11-e003h-windows-vfe1-dal-start-prefix-v1','accepted':True,'date':'2026-08-30',
  'driver':{'name':'qccamisp8380.sys','bytes':len(data),'sha256':got},
  'callback_table':{
   'generation_selector_context_field':'IFE context +0x6b678 == 0 selects VFE680 callback family',
   'irq_mask_callback_slot':'IFE context +0x6b690','irq_mask_callback_rva':'0x1d2b0',
   'pre_bus_top_callback_slot':'IFE context +0x6b698','pre_bus_top_callback_rva':'0x1d820'},
  'normal_first_start':{
   'function_rva':'0x26838','first_start_gate_rva':'0x270d4','first_start_flag':'IFE context +0x3488',
   'order':['callback +0x6b690','callback +0x6b698','DAL_ife_bus_start (FUN_1400274c8)'],
   'mask_callback_call_rva':'0x270e8 / BLR at 0x27100',
   'top_zero_callback_call_rva':'0x27110 / BLR at 0x27124',
   'bus_start_call_rva':'0x27130'},
  'irq_mask_callback':{
   'rva':'0x1d2b0',
   'writes':[
    {'base':'VFE TOP','offset':'0x34','value':'0x0007f051','role':'TOP IRQ mask0'},
    {'base':'VFE TOP','offset':'0x38','value':'0x00000000','role':'TOP IRQ mask1'},
    {'base':'VFE BUS','offset':'0x18','value':'0xd0000000','role':'BUS IRQ mask0'},
    {'base':'VFE BUS','offset':'0x1c','value':'0x00000000','role':'BUS IRQ mask1'}],
   'optional_write':{
    'base':'VFE BUS','offset':'0x08','value':'0x0fffffff','guard':'IFE context +0x6b6f0 != 0',
    'linux_status':'not authorized; same-machine SP11 flag/value not proven for this use case'}},
  'pre_bus_top_callback':{'rva':'0x1d820','write':{'base':'VFE TOP','offset':'0x24','value':'0x00000000','semantic_name':'intentionally unresolved'}},
  'cross_layer_order':cross['cross_layer_order'],
  'bus_split':{'before':'IFE803_PACKET1','phase':['VFE mask callback','VFE TOP +0x24=0','VFE1 BUS static config','VFE1 BUS enable','VFE1 initial dynamic addresses'],'after':'IFE803_PACKET2'},
  'startup_packet_top_0x24_writes':packet_writes,
  'top_0x24_transition':'packet0/1 leave 0x6000 -> DAL_ife_start writes 0 -> BUS start -> packet2/3 restore 0x6000',
  'linux_consequence':'Immediately before the existing private X1E VFE1 PIX bus_prepare between startup packets 1 and 2, reproduce only the four proven IRQ-mask writes and VFE TOP +0x24=0. Do not add the optional BUS +0x08 write. Keep BUS prepare, startup packet bytes/order, CSID, RT-CDM payloads and sensor lifecycle unchanged.',
  'runtime_authorized':False,
  'source_evidence':{'bus_cdm_crossorder':str(CROSS.relative_to(REPO)),'bus_cdm_crossorder_sha256':cross_sha},
  'instruction_anchors':anchors,
 }
 op=STATIC/'windows-vfe1-dal-start-prefix-oracle.json'
 op.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2,sort_keys=True))
 print('PASS: Windows VFE1 DAL_ife_start prefix and packet1/BUS/packet2 placement pinned')

if __name__=='__main__': main()
