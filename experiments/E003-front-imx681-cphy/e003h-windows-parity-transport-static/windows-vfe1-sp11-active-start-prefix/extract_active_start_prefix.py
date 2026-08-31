#!/usr/bin/env python3
import csv, hashlib, json, re, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
OUT=STATIC/'windows-vfe1-sp11-active-start-prefix'
BIN=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys')
ROUTE=REPO/'experiments/E003-front-imx681-cphy/e003g-windows-csid-vfe-oracle/raw/E003G_ROUTE_ORACLE_20260828.log'
DISPATCH=STATIC/'windows-vfe1-generation-dispatch/windows-vfe1-generation-dispatch-static.json'
CROSS=STATIC/'vfe1-bus-cdm-crossorder-oracle.json'
KD=OUT/'KD-THRESHOLD-EXCERPT.txt'
EXPECTED={
 'bin':'64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c',
 'route':'fd8edcee46e794dffa0e2305331f19d4e9d2cd5b9ba5197484aa1cc7fa6c6fca',
 'dispatch':'63f2ef14cff98f3f97b8bcbe6f6aed9a9ce0cbaefa011952ca7d985489af1acd',
 'cross':'b495cc833c45e97b1467749bf094bb3035c5e6070bd0ea13d26a99ceec6acce6',
 'kd_source':'58759b789a84b30fa5189f4641f1146d7c3ef63d4207fcc2ba603de2f1945af4',
}
PACKET_SHA={0:'e031eeaf777fc366761b4d0fa7bead961d5c9e1a63c70d92b3c21b1391ac766f',1:'222bee6fe98b9df847df616d0ccb2fad11c680189d1f3484003df83a298a2420',2:'282bb0f140c5b7ec916823511aca5cd14296bb80b3d519a7f028a79a9f584917',3:'72f800492e990d678c880d540c748279e3b3abc900dc83c8e2d4fa5495a1d127'}
IMAGE_BASE=0x140000000; TEXT_RAW=0x400; TEXT_RVA=0x1000; TEXT_SIZE=0x3d48c

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
for p,k in [(BIN,'bin'),(ROUTE,'route'),(DISPATCH,'dispatch'),(CROSS,'cross')]:
 g=sha(p)
 if g!=EXPECTED[k]: die(f'{k} hash drift {g}')
kd=KD.read_text()
if f'SOURCE_SHA256={EXPECTED["kd_source"]}' not in kd: die('KD source hash missing')
if 'fffff803`59dd70f0  00000002 00000001 00010002 00000002' not in kd: die('KD threshold row drift')
threshold=2

raw=BIN.read_bytes(); md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.detail=False; md.skipdata=True
ins={x.address-IMAGE_BASE:x for x in md.disasm(raw[TEXT_RAW:TEXT_RAW+TEXT_SIZE],IMAGE_BASE+TEXT_RVA) if x.mnemonic != '.byte'}
def need(rva,mn,op=None):
 x=ins.get(rva)
 if not x or x.mnemonic!=mn or (op and op not in x.op_str): die(f'anchor 0x{rva:x} drift: {None if not x else (x.mnemonic,x.op_str)}')
 return {'rva':f'0x{rva:x}','mnemonic':x.mnemonic,'operands':x.op_str}
anchors=[]
for a in [
 (0x22464,'ldr','[x20, #0x349c]'),(0x2246c,'cmp','w24, w8'),(0x22474,'cset','hs'),(0x22478,'str','[x8, #0x678]'),
 (0x19fac,'ldr','[x8, #0x678]'),(0x19fb0,'cmp','w8, #0'),(0x19ff0,'add','#0xe80'),(0x19ff8,'add','#0x2b0'),(0x19ffc,'csel','ne'),(0x1a004,'str','#0x690'),
 (0x1a00c,'add','#0xe0'),(0x1a014,'add','#0x820'),(0x1a018,'csel','ne'),(0x1a020,'str','#0x698'),
 (0x1be8c,'mov','#-0x24000000'),(0x1be90,'str','[x0, #0x164]'),(0x1be98,'mov','#7'),(0x1be9c,'str','[x0, #0x15c]'),
 (0x1bea4,'str','[x8, #0x24]'),(0x1beb8,'ldr','[x0, #0x160]'),(0x1bebc,'str','[x9, #0x28]'),
 (0x1becc,'ldr','[x0, #0x164]'),(0x1bed0,'str','[x9, #0x18]'),(0x1bed8,'mov','#0x1ff'),(0x1bedc,'str','[x9, #8]'),
 (0x1c0e0,'ret',None),
 (0x270d4,'ldrb',None),(0x270d8,'cbnz','0x140027128'),(0x270e8,'ldr','[x8, #0x690]'),(0x27100,'blr','x15'),(0x27110,'ldr','[x8, #0x698]'),(0x27124,'blr','x15'),(0x27130,'bl','0x1400274c8')]:
 anchors.append(need(*a))

# IFE1 is instance index 1 from the already-proven Windows route. Runtime threshold 2 => selector 0.
ife_index=1
selector=1 if ife_index>=threshold else 0
if selector!=0: die('selector calculation drift')

# Stable stock-Windows core_cfg_1 live readback appears in both successful passes.
route=ROUTE.read_text(encoding='utf-16')
pat='00000000`0ac71020  00000000 00006000 00000010 00000000'
if route.count(pat)!=2: die(f'expected two stable +0x28 snapshots, got {route.count(pat)}')

# The four initial IFE CDM packets own +0x24 only among this core-config set; never +0x28/c08/c18/c1c/34/38.
packet_hits={}
want={0x0ac71024:'top_24',0x0ac71028:'top_28',0x0ac71034:'top_34',0x0ac71038:'top_38',0x0ac71c08:'bus_c08',0x0ac71c18:'bus_c18',0x0ac71c1c:'bus_c1c'}
for n in range(4):
 p=STATIC/'windows-ife-cdm'/f'packet{n}-register-writes.csv'
 if sha(p)!=PACKET_SHA[n]: die(f'packet{n} hash drift')
 hits=[]
 for r in csv.DictReader(p.open()):
  a=int(r['absolute_address'],16)
  if a in want: hits.append({'name':want[a],'address':f'0x{a:08x}','value':r['value'],'stream_offset':r['stream_offset']})
 if hits!=[{'name':'top_24','address':'0x0ac71024','value':'0x00006000','stream_offset':hits[0]['stream_offset']}] if hits else True:
  pass
 if len(hits)!=1 or hits[0]['name']!='top_24' or int(hits[0]['value'],16)!=0x6000: die(f'packet{n} ownership drift {hits}')
 packet_hits[str(n)]=hits

# Resolve +0x28=0x10: active callback has the direct store; stock Windows reads 0x10 twice; initial startup packets do not own it.
result={
 'schema':'sp11-e003h-windows-vfe1-sp11-active-start-prefix-v1','accepted':True,'date':'2026-08-31',
 'driver':{'sha256':EXPECTED['bin'],'bytes':len(raw)},
 'runtime_selector_proof':{'raw_kd_source_sha256':EXPECTED['kd_source'],'threshold_rva':'0x670fc','threshold':threshold,'ife1_instance_index':ife_index,'selector':selector},
 'active_callback_pair':{'slot_0x6b690':'0x1be80','slot_0x6b698':'0x1c0e0','second_callback_semantics':'ret/no MMIO'},
 'active_first_callback':{'rva':'0x1be80','writes_in_order':[
   {'space':'software shadow','offset':'context+0x164','value':'0xdc000000'},
   {'space':'software shadow','offset':'context+0x15c','value':'0x00000007'},
   {'space':'VFE1 TOP','offset':'0x24','value':'0x00000007','name':'core_cfg_0'},
   {'space':'VFE1 TOP','offset':'0x28','value':'0x00000010','name':'core_cfg_1','resolution':'sole active direct KMD store + two stable stock-Windows readbacks; initial IFE CDM packets do not own +0x28'},
   {'space':'VFE1 BUS','offset':'0xc18','value':'0xdc000000','name':'bus_irq_mask0'},
   {'space':'VFE1 BUS','offset':'0xc08','value':'0x000001ff','name':'bus_cgc_ovd'}]},
 'initial_ife_packet_relevant_writes':packet_hits,
 'stock_windows_live_core_cfg_1':{'physical':'0x0ac71028','value':'0x00000010','successful_passes':2,'route_raw_sha256':EXPECTED['route']},
 'supersedes_for_sp11_ife1':{'wrong_family':'0x1d2b0 -> 0x1d820','old_linux_effect':['TOP +0x34=0x0007f051','TOP +0x38=0','BUS +0xc18=0xd0000000','BUS +0xc1c=0','TOP +0x24=0'],'reason':'runtime threshold 2 and IFE1 index 1 select zero callback family'},
 'linux_next_gate':{'allowed':'replace/correct the private SP11 IFE1 DAL-start semantics while preserving separately proven IRQ-mask availability if Linux still depends on it','forbidden':['sensor timing changes','CSID crop changes','new speculative values','0056 rerun']},
 'runtime_authorized':False,
 'source_hashes':{'dispatch_oracle':EXPECTED['dispatch'],'crossorder_oracle':EXPECTED['cross'],'route_raw':EXPECTED['route'],'kd_raw_on_sp7':EXPECTED['kd_source']},
 'instruction_anchors':anchors}
(OUT/'windows-vfe1-sp11-active-start-prefix-oracle.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2,sort_keys=True))
print('PASS: active SP11 IFE1 callback pair and core_cfg_1 ownership pinned')
