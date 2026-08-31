#!/usr/bin/env python3
import hashlib,importlib.util,json,struct
from pathlib import Path
REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
SRC=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.sensormodule.ffc_imx681.bin')
OUT=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-imx681-six-mode-correction'
EXPECTED='f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c'
sp=importlib.util.spec_from_file_location('qti',REPO/'tools/qti_parameter_bin.py'); q=importlib.util.module_from_spec(sp); sp.loader.exec_module(q)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def raw(e):return bytes.fromhex(e['raw_hex'])
def scalar(e):
 b=raw(e); return int.from_bytes(b,'little') if b else None
def u32s(e):
 b=raw(e); return list(struct.unpack('<'+'I'*(len(b)//4),b))
def regs(desc,ids):
 w=u32s(desc); count,ref=w[-2:]; t=ids[ref]; b=raw(t); assert len(b)==count*40
 out=[]
 for off in range(0,len(b),40):
  z=struct.unpack('<10I',b[off:off+40]); out.append((z[2],scalar(ids[z[4]])))
 return out,t['id']
def main():
 assert sha(SRC)==EXPECTED
 o=q.parse(SRC); ids={e['id']:e for e in o['entries']}; rd=next(e for e in o['entries'] if e['name']=='resolutionData' and e['payload_size']); b=raw(rd)
 assert len(b)==1512 and len(b)%252==0
 streams=[e for e in o['entries'] if e['name']=='streamConfiguration' and e['payload_size']]; assert len(streams)==6
 modes=[]
 for i in range(6):
  m=b[i*252:(i+1)*252]; sw=u32s(streams[i]); vc=scalar(ids[sw[1]]); rid=struct.unpack_from('<I',m,0x70)[0]; rr,rset=regs(ids[rid],ids); fm=dict(rr)
  mode={'index':i,'vc':vc,'data_type':sw[2],'x_start':sw[3],'y_start':sw[4],'width':sw[5],'height':sw[6],'bit_width':sw[7],
   'line_length':struct.unpack_from('<I',m,0x24)[0],'frame_length':struct.unpack_from('<I',m,0x28)[0],'pixel_rate_hz':struct.unpack_from('<I',m,0x34)[0],
   'frame_rate':struct.unpack_from('<d',m,0x40)[0],'resSettings_id':rid,'regSetting_id':rset,'register_count':len(rr),
   'output_size_regs':{f'0x{a:04x}':fm.get(a) for a in range(0x34c,0x350)},'digital_crop_size_regs':{f'0x{a:04x}':fm.get(a) for a in range(0x40c,0x410)}}
  modes.append(mode)
 exp=[(3840,2640,30.0,6752,3554,548570000),(3840,2160,60.0,5408,2218,548570000),(3840,2160,30.0,6752,3554,548570000),(3520,2640,30.0,6752,3554,548570000),(3660,2440,30.0,6752,3554,548570000),(504,378,3.0,3096,77518,655710000)]
 assert [(x['width'],x['height'],x['frame_rate'],x['line_length'],x['frame_length'],x['pixel_rate_hz']) for x in modes]==exp
 assert modes[2]['output_size_regs']=={'0x034c':15,'0x034d':0,'0x034e':8,'0x034f':112}
 assert modes[2]['digital_crop_size_regs']=={'0x040c':15,'0x040d':0,'0x040e':8,'0x040f':112}
 out={'schema':'sp11-e003h-windows-imx681-six-mode-correction-v1','accepted':True,'sensor_blob_sha256':EXPECTED,'resolution_count':6,'modes':modes,
  'corrections':{
   'prior_mode0_only_assumption_valid':False,
   'prior_timing_parity_proves_mode0_selected':False,
   'reason':'resolution index 2 is 3840x2160@30 and has the same line length 6752, frame length 3554 and pixel rate 548.57MHz as index 0 3840x2640@30',
   'mode2_exact_same_timing_as_mode0':True,
   'mode2_sensor_output_geometry':'3840x2160',
   'mode2_output_registers':'0x034c..0x034f = 0x0f000870'},
  'selection_proof':{'windows_selected_resolution_index':None,'mode2_selected_proven':False,'sensor_crop_packet_bytes_captured':False},
  'runtime_authorized':False,
  'next_gate':'Capture same-machine Windows SensorCrop packet/register pairs or live IMX681 output-size registers before any Linux sensor-mode change.'}
 blob=json.dumps(out,indent=2,sort_keys=True)+'\n'; (OUT/'imx681-six-mode-correction-oracle.json').write_text(blob); (OUT/'EXTRACT.txt').write_text(blob); print(blob,end='')
if __name__=='__main__':main()
