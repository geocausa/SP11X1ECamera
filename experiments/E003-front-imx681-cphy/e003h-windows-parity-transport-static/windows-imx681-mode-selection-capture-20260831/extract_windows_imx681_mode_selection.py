#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, re, struct
from pathlib import Path

REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
OUT=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-imx681-mode-selection-capture-20260831'
RAW=OUT/'E003H_IMX681_MODE_SELECTION_20260831.log'
BLOB=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.sensormodule.ffc_imx681.bin')
SIX=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-imx681-six-mode-correction/imx681-six-mode-correction-oracle.json'
PARSER=REPO/'tools/qti_parameter_bin.py'
EXPECTED={
 'raw':'341df7c5cf0d80456d9d74242878bb4561911a37d76d288e74b2a489ae2ed0ec',
 'raw_bytes':16162,
 'blob':'f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c',
 'six':'82ba7144845e873dcb4f537e557bdde95383baf7078eb6c152be309912f56ac2',
 'sensor_driver':'80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03',
}

def sha(p:Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def raw_entry(e): return bytes.fromhex(e['raw_hex'])
def scalar(e):
 b=raw_entry(e); return int.from_bytes(b,'little') if b else None
def u32s(e):
 b=raw_entry(e)
 if len(b)%4: die('non-u32 qti payload')
 return list(struct.unpack('<'+'I'*(len(b)//4),b))
def firmware_regs(desc,ids):
 w=u32s(desc); count,ref=w[-2:]; target=ids[ref]; b=raw_entry(target)
 if len(b)!=count*40: die('firmware regSetting length mismatch')
 out=[]
 for off in range(0,len(b),40):
  z=struct.unpack('<10I',b[off:off+40])
  out.append((z[2],scalar(ids[z[4]])))
 return out

def parse_event_packet(text:str):
 lines=text.splitlines()
 labels=['E003H_RES_PACKET_A','E003H_RES_PACKET_B','E003H_SENSORCROP_A','E003H_SENSORCROP_B','E003H_SENSORCROP_C']
 counts={x:sum(1 for l in lines if l.strip()==f'==={x}===') for x in labels}
 if counts!={'E003H_RES_PACKET_A':1,'E003H_RES_PACKET_B':0,'E003H_SENSORCROP_A':0,'E003H_SENSORCROP_B':0,'E003H_SENSORCROP_C':0}:
  die('event-count drift '+repr(counts))
 idx=next(i for i,l in enumerate(lines) if l.strip()=='===E003H_RES_PACKET_A===')
 m=re.fullmatch(r'DESC=([0-9a-f]+) DATA=([0-9a-f]+) LEN=([0-9a-f]+)',lines[idx+1].strip(),re.I)
 if not m: die('descriptor line malformed')
 desc,data,length=m.group(1).lower(),m.group(2).lower(),int(m.group(3),16)
 if length!=0x228: die(f'packet length {length:#x} != 0x228')
 mem=[]
 mem_re=re.compile(r'^[0-9a-f]{8}`[0-9a-f]{8}\s{2}(.+)$',re.I)
 byte_re=re.compile(r'(?<![0-9a-f])([0-9a-f]{2})(?![0-9a-f])',re.I)
 for l in lines[idx+3:]:
  mm=mem_re.match(l)
  if not mm: break
  # The debugger renders 16 bytes before the ASCII column. Keep only the left byte field.
  field=mm.group(1)
  if '  ' in field: field=field.split('  ',1)[0]
  # Remove the visual 8-byte separator; parse exactly two-digit tokens.
  field=field.replace('-',' ')
  toks=re.findall(r'\b[0-9a-fA-F]{2}\b',field)
  if len(toks)<16: die('short memory-dump line: '+l)
  mem.extend(int(x,16) for x in toks[:16])
  if len(mem)>=length: break
 if len(mem)<length: die(f'only {len(mem)} packet bytes recovered')
 packet=bytes(mem[:length])
 count=struct.unpack_from('<H',packet,0)[0]
 if count!=68: die(f'pair count {count} != 68')
 if 8+count*8!=length: die('count/packet-length relation fails')
 pairs=[]
 for i in range(count):
  off=8+i*8
  addr=struct.unpack_from('<H',packet,off)[0]
  value=struct.unpack_from('<H',packet,off+4)[0]
  if value>0xff: die(f'non-8-bit value at pair {i}: {value:#x}')
  pairs.append((addr,value))
 return counts,desc,data,length,packet,pairs

def main():
 if sha(RAW)!=EXPECTED['raw'] or RAW.stat().st_size!=EXPECTED['raw_bytes']: die('raw KD identity drift')
 if sha(BLOB)!=EXPECTED['blob']: die('sensor blob drift')
 if sha(SIX)!=EXPECTED['six']: die('six-mode oracle drift')
 six=json.loads(SIX.read_text())
 if not six.get('accepted') or six['selection_proof']['windows_selected_resolution_index'] is not None: die('six-mode prerequisite drift')
 text=RAW.read_text(encoding='utf-16')
 if "Closing open log file C:\\Users\\SurfacePro7\\Documents\\KDNET\\Codex\\E003H_IMX681_MODE_SELECTION_20260831.log" not in text:
  die('KD log was not cleanly closed')
 counts,desc,data,length,packet,pairs=parse_event_packet(text)
 sp=importlib.util.spec_from_file_location('qti',PARSER); q=importlib.util.module_from_spec(sp); sp.loader.exec_module(q)
 obj=q.parse(BLOB); ids={e['id']:e for e in obj['entries']}; rd=next(e for e in obj['entries'] if e['name']=='resolutionData' and e['payload_size']); rb=raw_entry(rd)
 if len(rb)!=6*252: die('resolutionData size drift')
 mode_pairs=[]
 for i in range(6):
  rec=rb[i*252:(i+1)*252]; rid=struct.unpack_from('<I',rec,0x70)[0]
  mode_pairs.append(firmware_regs(ids[rid],ids))
 matches=[i for i,x in enumerate(mode_pairs) if x==pairs]
 if matches!=[2]: die('full captured pair sequence did not uniquely match mode2: '+repr(matches))
 fm=dict(pairs)
 required={
  0x0342:0x1a,0x0343:0x60,0x033d:0x00,0x033e:0x0d,0x033f:0xe2,
  0x0344:0x00,0x0345:0x68,0x0346:0x01,0x0347:0xf0,0x0348:0x0f,0x0349:0x67,0x034a:0x0a,0x034b:0x5f,
  0x040c:0x0f,0x040d:0x00,0x040e:0x08,0x040f:0x70,
  0x034c:0x0f,0x034d:0x00,0x034e:0x08,0x034f:0x70,
  0x0368:0x00,0x036a:0x08,0x036b:0x70,
 }
 bad={f'0x{k:04x}':[fm.get(k),v] for k,v in required.items() if fm.get(k)!=v}
 if bad: die('key captured register drift '+repr(bad))
 mode=six['modes'][2]
 if (mode['width'],mode['height'],mode['frame_rate'],mode['line_length'],mode['frame_length'],mode['pixel_rate_hz'])!=(3840,2160,30.0,6752,3554,548570000):
  die('mode2 metadata prerequisite drift')
 out={
  'schema':'sp11-e003h-windows-imx681-mode-selection-capture-v1','accepted':True,
  'raw_kd_log':{'name':RAW.name,'bytes':EXPECTED['raw_bytes'],'sha256':EXPECTED['raw'],'encoding':'UTF-16LE','clean_logclose':True},
  'same_machine_windows':{'sensor_driver_sha256':EXPECTED['sensor_driver'],'sensor_blob_sha256':EXPECTED['blob'],'camera_app':'Microsoft.WindowsCamera_2026.2605.7.0_arm64__8wekyb3d8bbwe'},
  'capture':{'event_counts':counts,'callsite':'surfacecamfrontsensor8380.sys +0x54c4','packet_descriptor':desc,'packet_data':data,'packet_length_bytes':length,'pair_count':len(pairs),'packet_sha256':hashlib.sha256(packet).hexdigest()},
  'full_firmware_match':{'matching_resolution_indices':matches,'selected_resolution_index':2,'all_68_address_value_pairs_exact':True},
  'selected_mode':{'geometry':'3840x2160','fps':30.0,'line_length':6752,'frame_length':3554,'pixel_rate_hz':548570000,'output_size_regs':'0x034c..0x034f = 0x0f 0x00 0x08 0x70','digital_crop_size_regs':'0x040c..0x040f = 0x0f 0x00 0x08 0x70'},
  'sensorcrop':{'breakpoints_armed':True,'actual_hits':0,'required_for_mode_selection_proof':False},
  'classification':{
   'windows_selected_resolution_index_2_proven':True,
   'windows_sensor_output_is_3840x2160_before_csid_proven':True,
   'prior_windows_mode0_3840x2640_selection_assumption':False,
   'prior_linux_csid_vertical_crop_failure_interpretation_superseded':True,
   'reason':'same-machine Windows stock Camera submits the exact 68-pair firmware resolution record 2, which programs IMX681 output and digital crop to 3840x2160; Linux test path used record 0 3840x2640'},
  'runtime_authorized':False,
  'next_gate':'derive an exact static Linux IMX681 mode2 parity delta from the same firmware record; do not add a CSID crop write. Package/authorize a bounded one-shot only after static inspection.'
 }
 blob=json.dumps(out,indent=2,sort_keys=True)+'\n'
 (OUT/'windows-imx681-mode-selection-oracle.json').write_text(blob)
 (OUT/'EXTRACT.txt').write_text(blob)
 (OUT/'captured-resolution-pairs.csv').write_text('index,address,value\n'+''.join(f'{i},0x{a:04x},0x{v:02x}\n' for i,(a,v) in enumerate(pairs)))
 (OUT/'captured-resolution-packet.bin').write_bytes(packet)
 print(blob,end='')

if __name__=='__main__': main()
