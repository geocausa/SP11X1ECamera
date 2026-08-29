#!/usr/bin/env python3
import argparse, hashlib, importlib.util, json, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

RAW_SHA='1e8dc9671296e35a0704315588669fc8ed97612fd4b72c1d71b11bb7244d9a7f'
BATCH_ORACLE_SHA='3bcf4efe34c891dcc6bc78c3cefc94d916ffd71e27dab81e75493f9ed320dce4'
PRODUCER_ORACLE_SHA='cbd8908d967f4831e67f8eb3c36ae9799c4bcb42e1923f0ee34c2152841c03ef'
UMD_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
STARTUP_SHA=[
 'dea5956975ba241fd3809a55a9005d1ba0055e92d31b73476ddb7942fdef4e89',
 '45e73b067b486762546018bb0c712aa156124ad2c458aca1e439bf92e09528ae',
 '03fa6fb28c23563b02d0cb8120afdfedcec186c0da2c9874408ff9c68e7459dc',
 '0a1cc423d7fca7acba6d1c4507d52fdb960221f19c6026468881334af4857a7e',
]
STARTUP_LEN=[0xe94,0xe34,0x904,0x4e8]
LCAC={(0x5408,1,0x44),(0x5408,2,0x44)}
BHIST={(0xb208,1,0x1000),(0xb208,2,0x50)}

def die(s): raise SystemExit('FAIL: '+s)
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_path(p): return sha_bytes(Path(p).read_bytes())
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def pe_layout(data):
 pe=struct.unpack_from('<I',data,0x3c)[0]; n=struct.unpack_from('<H',data,pe+6)[0]; opt=struct.unpack_from('<H',data,pe+20)[0]; so=pe+24+opt
 out=[]
 for i in range(n):
  o=so+i*40; name=data[o:o+8].rstrip(b'\0').decode(errors='replace'); vs,va,rs,rp=struct.unpack_from('<IIII',data,o+8); out.append((name,va,vs,rs,rp))
 return out

def fileoff(secs,rva):
 for _,va,vs,rs,rp in secs:
  if va<=rva<va+max(vs,rs): return rp+rva-va
 die(f'RVA 0x{rva:x} not mapped')

def verify_umd(path):
 data=path.read_bytes()
 if sha_bytes(data)!=UMD_SHA: die('QcDeviceMFT identity drift')
 for s in [b'CamX::IFELCAC111Titan680::CreateCmdList\0',b'camxifelcac111titan680.cpp\0',
           b'CamX::IFEBHistStats16Titan680::Initialize\0',b'camxifebhiststats16titan680.cpp\0',
           b'CamX::BHistStats16::CalculateRegionConfiguration\0',b'CamX::BHistStats16::PopulateSegmentConfiguration\0']:
  if s not in data: die('UMD semantic string missing: '+s[:-1].decode())
 secs=pe_layout(data); base=0x180000000; md=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
 def inst(rva):
  o=fileoff(secs,rva); x=next(md.disasm(data[o:o+4],base+rva),None)
  if not x: die(f'no instruction at 0x{rva:x}')
  return x.mnemonic+' '+x.op_str
 expected={
  0xb39dc8:'mov w5, #0x44',0xb39dd4:'mov w2, #1',0xb39dd8:'mov w1, #0x5408',
  0xb39dec:'mov w5, #0x44',0xb39df8:'mov w2, #2',0xb39dfc:'mov w1, #0x5408',
  0xa0728c:'movk x8, #0xb208, lsl #32',0xa07298:'stp x9, x8, [x19, #0x28]',
  0xb3fd84:'ldr w1, [x20, #0x34]',0xb3fd88:'mov w5, #0x1000',0xb3fd94:'mov w2, #1',
  0xb3fda8:'ldr w1, [x20, #0x34]',0xb3fdb0:'mov w5, #0x50',0xb3fdb8:'mov w2, #2',
 }
 got={hex(r):inst(r) for r in expected}
 for r,want in expected.items():
  if got[hex(r)]!=want: die(f'UMD instruction drift 0x{r:x}: {got[hex(r)]!r} != {want!r}')
 return got

def dmi_shape(dec):
 return {(x['dmi_register_offset'],x['dmi_sel'],x['payload_bytes']) for x in dec['dmis']}

def main():
 ap=argparse.ArgumentParser(); here=Path(__file__).resolve().parent
 ap.add_argument('--log',type=Path,default=here/'windows-vfe1-epoch0-cdm-batches'/'E003H_VFE1_EPOCH0_CDM_BATCHES_CLEAN_20260829.log')
 ap.add_argument('--startup-dir',type=Path,default=here/'windows-ife-cdm')
 ap.add_argument('--batch-oracle',type=Path,default=here/'vfe1-epoch0-cdm-batches-oracle.json')
 ap.add_argument('--producer-oracle',type=Path,default=here/'vfe1-upstream-iq-producer-oracle.json')
 ap.add_argument('--umd',type=Path,default=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll'))
 ap.add_argument('-o','--output',type=Path,default=here/'vfe1-epoch0-priming-replay-oracle.json')
 a=ap.parse_args()
 if sha_path(a.log)!=RAW_SHA: die('clean selector-2 log identity drift')
 if sha_path(a.batch_oracle)!=BATCH_ORACLE_SHA: die('batch oracle identity drift')
 if sha_path(a.producer_oracle)!=PRODUCER_ORACLE_SHA: die('producer oracle identity drift')
 ext=load(here/'extract_vfe1_epoch0_cdm_batches.py','epoch0_extract')
 _,batches=ext.parse_log(a.log)
 if len(batches)<5: die('too few batches')
 lines=a.log.read_bytes().decode('utf-16').splitlines()
 marks={}
 for idx,line in enumerate(lines):
  if line=='ISP_START_DONE': marks['isp_start_done']=idx
  if line.startswith('BATCH_BEGIN n='):
   try:n=int(line.split('n=')[1].split()[0])
   except:continue
   if n<=4: marks[f'batch{n}']=idx
 want_order=['batch0','batch1','isp_start_done','batch2','batch3','batch4']
 if any(k not in marks for k in want_order) or [marks[k] for k in want_order]!=sorted(marks[k] for k in want_order): die('priming/ISP marker order drift')

 startup=[]; replay=[]; diffs=[]
 for i in range(4):
  sp=a.startup_dir/f'packet{i}-main-cdm.bin'; sb=sp.read_bytes()
  if len(sb)!=STARTUP_LEN[i] or sha_bytes(sb)!=STARTUP_SHA[i]: die(f'startup packet{i} identity drift')
  rb=batches[i]['records'][1]['data']
  if len(rb)!=len(sb): die(f'replay packet{i} length drift')
  sd=ext.decode(sb); rd=ext.decode(rb)
  if ext.structure_signature(sd)!=ext.structure_signature(rd): die(f'replay packet{i} structure drift')
  dw=[o for o in range(0,len(sb),4) if sb[o:o+4]!=rb[o:o+4]]
  if len(dw)!=1: die(f'replay packet{i} differs in {len(dw)} dwords, expected period_cfg only')
  f=dw[0]
  if rd['reg_value_fields'].get(f)!=0x8c or sd['reg_value_fields'].get(f)!=0x8c: die(f'replay packet{i} difference is not period_cfg')
  # Stronger than normalized equality: DMI IOVA words are byte-identical in this same-session replay.
  for df in rd['dmi_addr_fields']:
   if rb[df:df+4]!=sb[df:df+4]: die(f'replay packet{i} DMI address drift at 0x{df:x}')
  sv=struct.unpack_from('<I',sb,f)[0]; rv=struct.unpack_from('<I',rb,f)[0]
  startup.append(sv); replay.append(rv)
  diffs.append({'packet':i,'main_bytes':len(rb),'period_field':f'0x{f:x}','startup_period_cfg':f'0x{sv:08x}','replay_period_cfg':f'0x{rv:08x}',
                'startup_sha256':sha_bytes(sb),'replay_sha256':sha_bytes(rb),'dmi_address_words_identical':True,
                'decoded_commands':len(rd['commands']),'ordinary_register_writes':len(rd['writes']),'dmi_commands':len(rd['dmis'])})
 if not (startup[1]==startup[2]==startup[3]): die('startup period 1/2/3 relation drift')
 if not (replay[1]==replay[2]==replay[3]): die('replay period 1/2/3 relation drift')
 if batches[4]['records'][1]['bytes']!=0x958: die('first steady shape drift')

 shapes=[dmi_shape(ext.decode(batches[i]['records'][1]['data'])) for i in range(5)]
 # Startup-only DMI ownership: LCAC exists in replay0/1 only; BHIST only replay0.
 if not LCAC.issubset(shapes[0]) or not LCAC.issubset(shapes[1]) or LCAC & shapes[2] or LCAC & shapes[3] or LCAC & shapes[4]: die('LCAC replay membership drift')
 if not BHIST.issubset(shapes[0]) or BHIST & shapes[1] or BHIST & shapes[2] or BHIST & shapes[3] or BHIST & shapes[4]: die('BHIST replay membership drift')
 umd_inst=verify_umd(a.umd)
 result={
  'schema':'sp11-e003h-vfe1-epoch0-priming-replay-v1','accepted':True,
  'source_evidence':{'clean_selector2_log_sha256':RAW_SHA,'batch_oracle_sha256':BATCH_ORACLE_SHA,'producer_oracle_sha256':PRODUCER_ORACLE_SHA,'qcdevicemft_sha256':UMD_SHA},
  'timeline':{'observed_selector2_order':'replay0 -> replay1 -> ISP_START_DONE -> replay2 -> replay3 -> first steady 0x958',
              'host_start_distinction':'these selector-2 replays are not the original 0022 host-start packet submissions; original IFE803 packet2/3 are already proven before ISP_START_DONE'},
  'replay':{'packet_count':4,'startup_template_lengths':[f'0x{x:x}' for x in STARTUP_LEN],
            'only_difference_vs_startup_each_packet':'one period_cfg +0x8c dword','period_packet_mapping':'packet0=value0; packets1,2,3=value1',
            'dmi_iovas_reused_identically_in_capture':True,'packets':diffs},
  'startup_only_dmi':{
    'LCAC111':{'dmi':['0x5408:1:0x44','0x5408:2:0x44'],'selector2_replays':[0,1],'steady_presence':False,
               'owner_proof':'IFELCAC111Titan680::CreateCmdList directly emits both 0x5408 DMI commands'},
    'BHistStats16':{'dmi':['0xb208:1:0x1000','0xb208:2:0x50'],'selector2_replays':[0],'steady_presence':False,
                    'owner_proof':'IFEBHistStats16Titan680::Initialize stores 0xb208 in object +0x34; CreateCmdList loads +0x34 for 0x1000/0x50 selector1/2 writes',
                    'semantic_role':'stats configuration/resource priming (ROI/channel/uniform/segment configuration), not a steady IQ feedback LUT'},
  },
  'umd_instruction_proof':umd_inst,
  'linux_consequence':'Do not schedule four host-start packets again from this trace. Model a distinct four-program selector-2 priming replay phase whose templates equal startup main streams except newly supplied two-value period_cfg; keep Windows DMI IOVAs nonportable. Exact replay2/replay3 placement relative to MIPI_START and SENSOR_STREAM_ON remains unclosed.',
  'runtime_authorized':False,
 }
 a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('PASS: selector-2 batches 0..3 are startup-template priming replays with period_cfg-only refresh; LCAC111/BHistStats16 startup-only DMI ownership closed')
 print(sha_path(a.output),a.output)
if __name__=='__main__': main()
