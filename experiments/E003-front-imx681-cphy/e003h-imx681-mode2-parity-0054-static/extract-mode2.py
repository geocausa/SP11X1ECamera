#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, importlib.util, json, struct
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
SRC=ROOT/'00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.sensormodule.ffc_imx681.bin'
CAP=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-imx681-mode-selection-capture-20260831/windows-imx681-mode-selection-oracle.json'
OUT=REPO/'experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-static'
EXPECTED_BLOB='f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c'
EXPECTED_CAP='4520699c754e131af6126587da87086c973201a9c273df252c279b93ad5916c4'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def raw(e): return bytes.fromhex(e['raw_hex'])
def scalar(e):
 b=raw(e); return int.from_bytes(b,'little') if b else None
def u32s(e):
 b=raw(e); assert len(b)%4==0; return list(struct.unpack('<'+'I'*(len(b)//4),b))
def decode_regsetting(e,ids,expected_count=None):
 b=raw(e); assert len(b)%40==0
 if expected_count is not None: assert len(b)==expected_count*40
 out=[]
 for idx,off in enumerate(range(0,len(b),40)):
  z=struct.unpack('<10I',b[off:off+40]); out.append(dict(index=idx,address=z[2],data=scalar(ids[z[4]]),addr_type=z[5],data_type=z[6],operation=z[7],delay_us=scalar(ids[z[9]]) or 0,slave_override=z[0] or None))
 return out
def regs_from_res_settings(e,ids):
 w=u32s(e); assert len(w)==2; count,ref=w; assert ids[ref]['name']=='regSetting'; return decode_regsetting(ids[ref],ids,count),ref
def emit_c(path,init,mode):
 def arr(name,rs):
  q=[f'static const struct cci_reg_sequence {name}[] = {{']
  q += [f'\t{{ CCI_REG8(0x{r["address"]:04x}), 0x{r["data"]:02x} }},' for r in rs]
  q += ['};','']; return q
 text=['/* SPDX-License-Identifier: GPL-2.0 */','/* Machine-derived SP11 IMX681 init + Windows-selected mode2 tables. */','/* Safety invariant: neither generated table contains MODE_SELECT. */','']
 text += arr('imx681_sp11_init_regs',init); text += arr('imx681_sp11_mode2_regs',mode)
 path.write_text('\n'.join(text))
def main():
 assert sha(SRC)==EXPECTED_BLOB and sha(CAP)==EXPECTED_CAP
 cap=json.loads(CAP.read_text()); assert cap['accepted'] and cap['full_firmware_match']['matching_resolution_indices']==[2]
 sp=importlib.util.spec_from_file_location('qti',REPO/'tools/qti_parameter_bin.py'); q=importlib.util.module_from_spec(sp); sp.loader.exec_module(q)
 obj=q.parse(SRC); ids={e['id']:e for e in obj['entries']}
 init_desc=next(e for e in obj['entries'] if e['name']=='initSettings' and e['payload_size']); w=u32s(init_desc); assert len(w)==3 and w[1]==1
 inner=ids[w[2]]; assert inner['name']=='initSetting'; iw=u32s(inner); assert len(iw)==2; init_count,init_ref=iw; assert ids[init_ref]['name']=='regSetting'; init=decode_regsetting(ids[init_ref],ids,init_count)
 rd=next(e for e in obj['entries'] if e['name']=='resolutionData' and e['payload_size']); rb=raw(rd); assert len(rb)==6*252
 modes=[]
 for i in range(6):
  rec=rb[i*252:(i+1)*252]; rid=struct.unpack_from('<I',rec,0x70)[0]; rr,regid=regs_from_res_settings(ids[rid],ids); modes.append((rr,regid,rec))
 mode0,_,_=modes[0]; mode2,mode2_regid,rec2=modes[2]
 assert len(mode0)==len(mode2)==68
 assert [r['address'] for r in mode0]==[r['address'] for r in mode2]
 diffs=[(i,a['address'],a['data'],b['data']) for i,(a,b) in enumerate(zip(mode0,mode2)) if a['data']!=b['data']]
 expected=[(12,0x0347,0x00,0xf0),(15,0x034a,0x0b,0x0a),(16,0x034b,0x4f,0x5f),(31,0x040e,0x0a,0x08),(32,0x040f,0x50,0x70),(35,0x034e,0x0a,0x08),(36,0x034f,0x50,0x70)]
 assert diffs==expected
 for rs in (init,mode2):
  assert all(r['operation']==0 and r['addr_type']==2 and r['data_type']==1 and r['slave_override'] is None and r['address']!=0x0100 and 0<=r['data']<=0xff for r in rs)
 line=struct.unpack_from('<I',rec2,0x24)[0]; frame=struct.unpack_from('<I',rec2,0x28)[0]; pix=struct.unpack_from('<I',rec2,0x34)[0]; fps=struct.unpack_from('<d',rec2,0x40)[0]
 assert (line,frame,pix,fps)==(6752,3554,548570000,30.0)
 fm={r['address']:r['data'] for r in mode2}
 assert [fm[x] for x in range(0x034c,0x0350)]==[0x0f,0,0x08,0x70]
 assert [fm[x] for x in range(0x040c,0x0410)]==[0x0f,0,0x08,0x70]
 summary={'schema':'sp11-e003h-imx681-mode2-static-extraction-v1','accepted':True,'sensor_blob_sha256':EXPECTED_BLOB,'windows_mode_selection_oracle_sha256':EXPECTED_CAP,'selected_resolution_index':2,'geometry':'3840x2160','fps':30.0,'line_length':line,'frame_length':frame,'pixel_rate_hz':pix,'mode2_regsetting_id':mode2_regid,'init_records':len(init),'mode2_records':len(mode2),'mode_select_writes':0,'mode0_mode2_address_order_identical':True,'mode0_mode2_value_differences':[{'index':i,'address':f'0x{a:04x}','mode0':f'0x{x:02x}','mode2':f'0x{y:02x}'} for i,a,x,y in diffs],'changed_register_count':len(diffs),'runtime_authorized':False}
 emit_c(OUT/'imx681-sp11-mode2-regs.h',init,mode2)
 with (OUT/'mode2-registers.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['index','address','data'],lineterminator='\n'); w.writeheader()
  for r in mode2:w.writerow({'index':r['index'],'address':f'0x{r["address"]:04x}','data':f'0x{r["data"]:02x}'})
 blob=json.dumps(summary,indent=2,sort_keys=True)+'\n'; (OUT/'MODE2-SUMMARY.json').write_text(blob); (OUT/'EXTRACT.txt').write_text(blob); print(blob,end='')
if __name__=='__main__': main()
