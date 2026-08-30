#!/usr/bin/env python3
import argparse,csv,hashlib,json,re,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN

DRIVER_SHA='64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
DRIVER_BYTES=376560
CSV_SHA='95e26dd7d116fdc48b7281a153222a7b4edd11294703b555d81e25c2251b1238'
LINUX_SHA='70d0dad027d266026bde7b2c81cc8d9e4d73a477f12fcb3e831f9d10a9a98866'
QCOM_COMMIT='0f16924ff6a7f9bb56a7e958016da2ed8a174f2f'
QCOM_HASHES={
 'cam_ife_csid680.h':'a0eb6dca54ea3dfa11a72b9e649b350390d26e613b8d27d7640f8544c0c24882',
 'cam_ife_csid_hw_ver2.h':'d0dbaaa1ed7b98a4e160434ac40cf3d0293c27b0507ca19cb1fbb70db5729ad7',
 'cam_ife_csid_hw_ver2.c':'a1079bfb5166d9936227099781a195471069a91f0f3b5f3e1b993325909d1266',
}
BASE=0x140000000
WINDOWS_ERROR_MASK=0x3c1c6004
WINDOWS_LIVE_IPP=0x00e11ff8
LINUX_HISTORY=0x00e15ff8
BIT14=1<<14

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pe_sections(data):
 pe=struct.unpack_from('<I',data,0x3c)[0]; n=struct.unpack_from('<H',data,pe+6)[0]; opt=struct.unpack_from('<H',data,pe+20)[0]; sh=pe+24+opt
 out=[]
 for i in range(n):
  o=sh+i*40; name=data[o:o+8].rstrip(b'\0').decode('ascii',errors='ignore'); vs,va,rs,raw=struct.unpack_from('<IIII',data,o+8); out.append((name,va,vs,raw,rs))
 return out
def rva_off(secs,rva):
 for name,va,vs,raw,rs in secs:
  if va<=rva<va+max(vs,rs): return raw+rva-va
 die(f'RVA 0x{rva:x} unmapped')
def verify_driver(path):
 data=Path(path).read_bytes()
 if len(data)!=DRIVER_BYTES or hashlib.sha256(data).hexdigest()!=DRIVER_SHA: die('qccamisp identity drift')
 secs=pe_sections(data); text=next(s for s in secs if s[0]=='.text'); _,va,vs,raw,rs=text
 md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.skipdata=True
 ins={x.address-BASE:(x.mnemonic,x.op_str) for x in md.disasm(data[raw:raw+rs],BASE+va) if x.mnemonic!='.byte'}
 anchors={
  0x1b65c:('ldr','w8, [x8, #0xac]'),
  0x1b660:('and','w8, w8, #0x3fffffff'),
  0x1b664:('str','w8, [x20, #0x10]'),
  0x1b8b0:('ldp','w25, w24, [x1, #0xc]'),
  0x1b9f8:('ldr','w27, #0x14001bdd8'),
  0x1b9fc:('tst','w24, w27'),
  0x1ba00:('b.eq','#0x14001ba1c'),
  0x1ba0c:('mov','w3, w24'),
  0x1ba10:('add','x1, x8, #0x148'),
  0x1ba18:('bl','#0x140029ad8'),
 }
 rendered={}
 for r,(mn,ops) in anchors.items():
  got=ins.get(r)
  if got!=(mn,ops): die(f'driver anchor drift at 0x{r:x}: {got!r}')
  rendered[f'0x{r:x}']=f'{got[0]} {got[1]}'
 lit=struct.unpack_from('<I',data,rva_off(secs,0x1bdd8))[0]
 if lit!=WINDOWS_ERROR_MASK: die(f'IPP error mask literal drift 0x{lit:08x}')
 s=b'CSID%d: CSID Received error IRQs on IPP Path, ippIrqStatus = 0x%x.\0'
 if data[rva_off(secs,0x36148):rva_off(secs,0x36148)+len(s)]!=s: die('IPP error string drift')
 return rendered,lit
def verify_csv(path):
 path=Path(path)
 if sha(path)!=CSV_SHA: die('Windows live CSV identity drift')
 rows={int(r['offset'],16):r for r in csv.DictReader(path.open())}
 req={0xac:WINDOWS_LIVE_IPP,0x388:0x08700f00,0x38c:0x08700f00,0x390:0x03b203ad}
 for off,val in req.items():
  if off not in rows or int(rows[off]['live1'],16)!=val: die(f'Windows live +0x{off:x} drift')
 if rows[0x38c]['stable']!='1' or rows[0x388]['stable']!='1': die('Windows expected/actual frame-size stability drift')
 return {f'+0x{k:x}':{'live1':rows[k]['live1'],'live2':rows[k]['live2'],'stable':bool(int(rows[k]['stable']))} for k in (0xac,0x388,0x38c,0x390,0x394)}
def verify_linux(path):
 path=Path(path)
 if sha(path)!=LINUX_SHA: die('0048 runtime analysis identity drift')
 x=json.loads(path.read_text())
 if not x.get('accepted'): die('0048 runtime analysis not accepted')
 c=x['csid1']; w=x['windows_live_comparison']; cl=x['classification']
 if int(c['irq_history_or'],16)!=LINUX_HISTORY or c['irq_history_count']!=4: die('Linux IRQ history drift')
 if not all(c[k] for k in ('camif_sof_seen','camif_eof_seen','camif_epoch0_seen','camif_epoch1_seen','rup_done_seen','line_count_error_seen')): die('Linux CSID progression/history drift')
 if int(w['linux_history_extra_vs_windows_live'],16)!=BIT14 or w['linux_history_extra_bits']!=['ERROR_LINE_COUNT']: die('Linux-vs-Windows bit14 delta drift')
 if cl['vfe1_epoch0_seen'] is not False: die('VFE Epoch0 classification drift')
 return x
def verify_qcom(root):
 root=Path(root)
 base=root/'camera/drivers/cam_isp/isp_hw_mgr/isp_hw/ife_csid_hw'
 ps={n:base/n for n in QCOM_HASHES}
 for n,p in ps.items():
  if not p.is_file() or sha(p)!=QCOM_HASHES[n]: die('Qualcomm source identity drift: '+n)
 h=ps['cam_ife_csid680.h'].read_text(); vh=ps['cam_ife_csid_hw_ver2.h'].read_text(); c=ps['cam_ife_csid_hw_ver2.c'].read_text()
 anchors=[
  '.bitmask = BIT(14),', '.err_type = CAM_ISP_HW_ERROR_CSID_FRAME_SIZE,', '.desc = "ERROR_LINE_COUNT",',
  '.err_handler = cam_ife_csid_ver2_print_format_measure_info,', '.fatal_err_mask                   = 0x186004,',
  '.format_measure_cfg1_addr         = 0x388,', '.format_measure0_addr             = 0x38C,',
  '.format_measure_height_mask_val          = 0xFFFF,', '.format_measure_height_shift_val         = 0x10,',
  '.format_measure_width_mask_val           = 0xFFFF,',
 ]
 for a in anchors:
  if a not in h: die('Qualcomm CSID680 anchor missing: '+a)
 if '#define IFE_CSID_VER2_PATH_ERROR_LINE_COUNT                      BIT(14)' not in vh: die('Qualcomm ver2 bit14 macro drift')
 for a in ('actual_frame = cam_io_r_mb(base + path_reg->format_measure0_addr);','expected_frame = cam_io_r_mb(base + path_reg->format_measure_cfg1_addr);','cam_ife_csid_ver2_parse_path_irq_status('):
  if a not in c: die('Qualcomm handler anchor missing: '+a)
 return {'commit':QCOM_COMMIT,'file_sha256':QCOM_HASHES}
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--driver',type=Path,required=True)
 ap.add_argument('--windows-csv',type=Path,required=True)
 ap.add_argument('--linux-analysis',type=Path,required=True)
 ap.add_argument('--qcom-root',type=Path,required=True)
 ap.add_argument('-o','--output',type=Path)
 a=ap.parse_args()
 anchors,mask=verify_driver(a.driver); live=verify_csv(a.windows_csv); lx=verify_linux(a.linux_analysis); q=verify_qcom(a.qcom_root)
 bits=lambda v:[i for i in range(32) if v&(1<<i)]
 exp=0x08700f00
 out={
  'schema':'sp11-e003h-windows-csid1-line-count-error-oracle-v1','accepted':True,'date':'2026-08-30',
  'source_evidence':{
   'qccamisp':{'bytes':DRIVER_BYTES,'sha256':DRIVER_SHA},'windows_live_csv_sha256':CSV_SHA,'linux_0048_analysis_sha256':LINUX_SHA,
   'qualcomm_public':q,
  },
  'windows_qccamisp':{
   'csid_irq_reader_rva':'0x1b630','ipp_mmio_read_rva':'0x1b65c','ipp_mmio_offset':'0xac','payload_store_offset':'0x10',
   'error_handler_rva':'0x1b840','payload_load_rva':'0x1b8b0','ipp_payload_register':'w24',
   'ipp_error_mask_literal_rva':'0x1bdd8','ipp_error_mask':f'0x{mask:08x}','ipp_error_mask_bits':bits(mask),
   'bit14_in_error_mask':bool(mask&BIT14),'ipp_error_log_string_rva':'0x36148','instruction_anchors':anchors,
  },
  'same_machine_windows_live':{
   'ipp_status':f'0x{WINDOWS_LIVE_IPP:08x}','ipp_bit14_set':bool(WINDOWS_LIVE_IPP&BIT14),'registers':live,
   'expected_frame_size_register':'0x08700f00','actual_frame_size_register':'0x08700f00','expected_equals_actual':True,
   'decoded_expected_actual':{'height':(exp>>16)&0xffff,'width':exp&0xffff},
  },
  'linux_0048':{
   'ipp_history_or':f'0x{LINUX_HISTORY:08x}','history_bit14_set':True,'history_extra_vs_windows_live':'0x00004000',
   'camif_rup_epoch_seen':True,'vfe1_raw_epoch0_seen':False,
  },
  'qualcomm_csid680_reference':{
   'bit14_name':'ERROR_LINE_COUNT','bit14_error_type':'CAM_ISP_HW_ERROR_CSID_FRAME_SIZE','bit14_fatal_for_ipp':True,
   'ipp_fatal_error_mask':'0x00186004','format_measure_expected_offset':'0x388','format_measure_actual_offset':'0x38c',
   'format_measure_encoding':'height bits31:16, width bits15:0','error_handler_reads_actual_and_expected':True,
  },
  'classification':{
   'windows_treats_ipp_bit14_as_error':True,
   'same_machine_windows_live_bit14_absent':True,
   'same_machine_windows_expected_actual_frame_size_match':True,
   'linux_transient_bit14_is_real_parity_mismatch':True,
   'causal_link_to_missing_vfe_epoch0_proven':False,
  },
  'next_gate':'Read-only Linux CSID1 format-measure result telemetry (+0x38c/+0x390/+0x394) is justified to determine the actual frame-size/HBI/VBI state when bit14 asserts; do not alter CSID/VFE programming from this oracle alone.',
  'runtime_authorized':False,
 }
 txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
 if a.output:a.output.write_text(txt)
 else: print(txt,end='')
 print('PASS: Windows qccamisp IPP error path includes bit14; Windows actual=expected 2160x3840; Linux 0048 uniquely adds bit14')
if __name__=='__main__': main()
