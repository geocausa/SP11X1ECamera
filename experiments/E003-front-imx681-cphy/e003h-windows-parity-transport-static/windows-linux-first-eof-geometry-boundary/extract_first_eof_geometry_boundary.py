#!/usr/bin/env python3
import hashlib,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
DRIVER=ROOT/'00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys'
WIN_START=STATIC/'windows-csid1-ipp-start-oracle.json'
WIN_GEOM=STATIC/'windows-csid1-first-ipp-geometry/E003H_FIRST_IPP_GEOMETRY_CHECKPOINT_20260831.txt'
LINUX=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-rupdone-no-regupdate-0051-candidate/runtime-0051-analysis.json'
LSRC=ROOT/'02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss-csid-680.c'
EXPECTED={
 'driver':'64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c',
 'win_start':'01960da41376809d694c6aa2336ecef6ff4c010abfa29e4674b1a68d303c3cda',
 'win_geom':'0276623cbf63290bad79afb5ce6ce3acf3f7981c6502bbcfcb629e092c545fe6',
 'linux':'2e1fbd740073b98e9e86ef477f1986d9b7e94a26a5e486f4386197b8e331f9d1',
 'linux_source':'683c0d5c042d3a8f24be211cda7dc02d06befe31e42aeb29fcd14f117397c81c',
}
MASK=0x3cbc601c
N={2:'ERROR_FIFO_OVERFLOW',3:'CAMIF_EOF',4:'CAMIF_SOF',5:'FRAME_DROP_EOF',6:'FRAME_DROP_EOL',7:'FRAME_DROP_SOL',8:'FRAME_DROP_SOF',9:'INFO_INPUT_EOF',10:'INFO_INPUT_EOL',11:'INFO_INPUT_SOL',12:'INFO_INPUT_SOF',13:'ERROR_PIX_COUNT',14:'ERROR_LINE_COUNT',15:'VCDT_GRP0_SEL',16:'VCDT_GRP1_SEL',17:'VCDT_GRP_CHANGE',18:'FRAME_DROP',19:'OVERFLOW_RECOVERY',20:'ERROR_REC_CCIF_VIOLATION',21:'CAMIF_EPOCH0',22:'CAMIF_EPOCH1',23:'RUP_DONE',24:'ILLEGAL_BATCH_ID',25:'BATCH_END_MISSING_VIOLATION',26:'HEIGHT_VIOLATION',27:'WIDTH_VIOLATION',28:'SENSOR_SWITCH_OUT_OF_SYNC_FRAME_DROP',29:'CCIF_VIOLATION'}
def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bits(v): return [N.get(i,str(i)) for i in range(32) if v&(1<<i)]
def chk(k,p):
 g=sha(p)
 if g!=EXPECTED[k]: die(f'{k} hash drift {g}')
def pe_sections(data):
 pe=struct.unpack_from('<I',data,0x3c)[0]; n=struct.unpack_from('<H',data,pe+6)[0]; opt=struct.unpack_from('<H',data,pe+20)[0]; sh=pe+24+opt
 return [(data[sh+i*40:sh+i*40+8].rstrip(b'\0').decode(errors='ignore'),)+struct.unpack_from('<IIII',data,sh+i*40+8) for i in range(n)]
def verify_driver():
 chk('driver',DRIVER); data=DRIVER.read_bytes(); secs=pe_sections(data); text=next(x for x in secs if x[0]=='.text'); _,vs,va,rs,raw=text
 # tuple order after name is virtual-size, virtual-address, raw-size, raw-pointer
 md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.skipdata=True; base=0x140000000
 ins={x.address-base:(x.mnemonic,x.op_str) for x in md.disasm(data[raw:raw+rs],base+va) if x.mnemonic!='.byte'}
 req={0x1b65c:('ldr','w8, [x8, #0xac]'),0x1b748:('ldr','w9, [x20, #0x10]'),0x1b750:('str','w9, [x8, #0xb4]')}
 for r,v in req.items():
  if ins.get(r)!=v: die(f'qccamisp IRQ read/clear anchor drift 0x{r:x}: {ins.get(r)}')
 return {f'0x{r:x}':f'{v[0]} {v[1]}' for r,v in req.items()}
def main():
 for k,p in [('win_start',WIN_START),('win_geom',WIN_GEOM),('linux',LINUX),('linux_source',LSRC)]: chk(k,p)
 anchors=verify_driver()
 start=WIN_START.read_text(); wg=WIN_GEOM.read_text(); lx=json.loads(LINUX.read_text()); src=LSRC.read_text()
 if '0x3cbc601c' not in start or '0x00130013' not in start: die('Windows mask/epoch oracle drift')
 if '#define SP11_CSID_IPP_IRQ_MASK_MODE0\t\t\t\t0x3cbc601c' not in src: die('Linux final IPP mask drift')
 if 'status 0x00811dd0' not in wg or 'status 0x00600228' not in wg or 'actual=0x08700f00 = 3840x2160' not in wg: die('Windows geometry checkpoint drift')
 if 'raw KD log file was not found' not in wg: die('Windows raw-log fail-closed warning lost')
 seq=[(int(x['status_hex'],16),int(x['actual_hex'],16)) for x in lx['linux_sequence']]
 expected=[(0x00811dd0,0x00000f00),(0x00600cc0,0x00000f00),(0x00000cc0,0x00000f00),(0x00004ee8,0x0a500f00)]
 if seq!=expected: die('Linux 0051 sequence drift')
 wpre=0x00811dd0; weof=0x00600228; lepoch=0x00600cc0; leof=0x00004ee8
 if weof & (1<<3)==0 or lepoch & (1<<3): die('EOF classification drift')
 if leof & (1<<3)==0 or leof & (1<<14)==0: die('Linux EOF/error classification drift')
 if (weof&MASK)!=0x00200008 or (lepoch&MASK)!=0x00200000 or (leof&MASK)!=0x00004008: die('masked-cause decode drift')
 out={
  'schema':'sp11-e003h-first-eof-geometry-boundary-v1','accepted':True,
  'source_sha256':EXPECTED,
  'final_ipp_irq_mask':f'0x{MASK:08x}',
  'qccamisp_irq_snapshot_clear':{'anchors':anchors,'reads_ipp_status_then_clears_full_snapshot':True},
  'windows':{
   'pre_complete':{'status':'0x00811dd0','status_bits':bits(wpre),'masked_bits':bits(wpre&MASK),'actual':'0x00000f00','geometry':'3840 x incomplete-height'},
   'first_complete_checkpoint':{'status':'0x00600228','status_bits':bits(weof),'masked_bits':bits(weof&MASK),'contains_camif_eof':True,'contains_epoch0':True,'actual':'0x08700f00','geometry':'3840x2160'},
   'raw_kd_bytes_local_present':False,'checkpoint_provenance_fail_closed':True,
  },
  'linux_0051':{
   'first_epoch_sample':{'status':'0x00600cc0','status_bits':bits(lepoch),'masked_bits':bits(lepoch&MASK),'contains_camif_eof':False,'actual':'0x00000f00','geometry':'3840 x incomplete-height'},
   'first_complete_eof_sample':{'status':'0x00004ee8','status_bits':bits(leof),'masked_bits':bits(leof&MASK),'contains_camif_eof':True,'contains_error_line_count':True,'actual':'0x0a500f00','geometry':'3840x2640'},
  },
  'classification':{
   'height_is_incomplete_in_both_os_before_eof':True,
   'windows_first_complete_sample_is_eof_bearing':True,
   'linux_first_epoch_sample_is_pre_eof':True,
   'prior_first_epoch_geometry_divergence_boundary_superseded':True,
   'geometry_divergence_boundary':'first completed EOF/frame-size measurement: Windows 3840x2160 versus Linux 3840x2640 + ERROR_LINE_COUNT',
   'epoch_side_bit_difference_is_proven_causal':False,
   'irq_status_side_bits_may_coalesce_between_full-status clears':True,
   'vertical_crop_failure_at_completed_frame_remains_proven':True,
   'speculative_crop_register_write_justified':False,
  },
  'next_gate':'Audit completed-frame timing/active-crop semantics rather than pre-EOF Epoch sampling. The strongest remaining same-machine delta is completed-frame timing telemetry: Windows HBI=0x03b203ad versus Linux error-time HBI=0x02c502c0 despite identical 3840 input width and sensor mode. First statically decode FORMAT_MEASURE1/HBI semantics and determine whether that delta identifies a clock/timing or path-latch mismatch; no runtime yet.'
 }
 blob=json.dumps(out,indent=2,sort_keys=True)+'\n'
 (Path(__file__).parent/'first-eof-geometry-boundary-oracle.json').write_text(blob)
 (Path(__file__).parent/'EXTRACT.txt').write_text(blob)
 print(blob,end='')
if __name__=='__main__': main()
