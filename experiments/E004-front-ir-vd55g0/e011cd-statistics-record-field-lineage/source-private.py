#!/usr/bin/env python3
"""Same-SP11 independent ordinary statistics record and attachment byte model."""
from pathlib import Path
import importlib.util,struct,json,hashlib,collections
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cd_cc',ROOT/'experiments/E004-front-ir-vd55g0/e011cc-coherent-source-statistics-setup/source-private.py');CC=importlib.util.module_from_spec(spec);spec.loader.exec_module(CC)
NORMAL={0:0,1:2,2:1,4:4,5:5,6:6}
def enum(value):return NORMAL.get(value,3)
def expected_record(source,final=False):
 assert len(source)==72;b=bytearray(152)
 b[8:12]=source[0:4];b[16:24]=source[40:48];struct.pack_into('<I',b,24,enum(struct.unpack_from('<I',source,8)[0]));b[48:52]=source[36:40]
 b[52:68]=source[20:36];struct.pack_into('<If',b,68,1,1.0);b[76:80]=source[16:20];struct.pack_into('<I',b,80,0xffffffff if struct.unpack_from('<I',source,12)[0] else 0)
 b[96:100]=source[4:8];b[100:104]=b[24:28];b[124:140]=source[20:36]
 if final:b[116:124]=source[64:72]
 return bytes(b)
class Model(CC.Setup):
 totals=collections.Counter()
 def __init__(self,p,c):super().__init__(p,c);self.pending=None;self.setter=None
 def hook(self,u,pc,size,user):
  r=pc-self.n.base
  if r==0x3a0564:
   assert self.pending is None;source=u.reg_read(UC_ARM64_REG_X19);obj=u.reg_read(UC_ARM64_REG_X21)
   payload=struct.unpack('<Q',u.mem_read(self.core+0xf20,8))[0];array=struct.unpack('<Q',u.mem_read(payload+56,8))[0];count=struct.unpack('<I',u.mem_read(payload+44,4))[0]
   assert array<=source<array+72*count and (source-array)%72==0
   assert dict(self.allocs)[obj] in [648,504,488]
   self.pending={'source_pointer':source,'source':bytes(u.mem_read(source,72)),'object':obj,'source_index':(source-array)//72}
  if r==0x3a0568:
   at=u.reg_read(UC_ARM64_REG_X0);assert dict(self.allocs)[at]==152;self.pending['record']=at
  if r==0x3a0610:
   assert u.reg_read(UC_ARM64_REG_X22)==self.pending['record'];assert bytes(u.mem_read(self.pending['record'],152))==expected_record(self.pending['source'])
   self.totals['exact_pre_attachment_records']+=1
  if r in [0x39d8c0,0x39da00]:
   a=self.pending;obj=a['object'];record=a['record'];assert u.reg_read(UC_ARM64_REG_X0)==obj and u.reg_read(UC_ARM64_REG_X1)==a['source_pointer']
   index=struct.unpack_from('<I',a['source'],16)[0];off=(216 if r==0x39d8c0 else 40)+48*index
   z=dict(self.allocs)[obj];assert off+28<=z;ptr=struct.unpack('<Q',u.mem_read(obj+off,8))[0];head,used,cap=struct.unpack('<3I',u.mem_read(obj+off+8,12));counter=struct.unpack('<I',u.mem_read(obj+off+24,4))[0]
   assert dict(self.allocs)[ptr]==160 and cap==20 and used<cap and head<cap
   baseptr=struct.unpack('<Q',u.mem_read(obj+8,8))[0];bh,bu,bc=struct.unpack('<3I',u.mem_read(obj+16,12));assert struct.unpack('<Q',u.mem_read(baseptr+8*((bh+bu-1)%bc),8))[0]==record
   expected=bytearray(u.mem_read(obj,z));struct.pack_into('<I',expected,off+12,used+1);struct.pack_into('<I',expected,off+24,counter+1)
   ring=bytearray(u.mem_read(ptr,160));struct.pack_into('<Q',ring,8*((head+used)%cap),record)
   self.setter=(obj,z,bytes(expected),ptr,bytes(ring));self.totals['original_attachment_setter_entries']+=1
  if r==0x3a0668:
   obj,z,expected,ptr,ring=self.setter;assert bytes(u.mem_read(obj,z))==expected and bytes(u.mem_read(ptr,160))==ring
   assert bytes(u.mem_read(self.pending['record'],152))==expected_record(self.pending['source']);self.setter=None;self.pending['setter_returned']=True;self.totals['exact_attachment_setter_returns']+=1
  if r==0x3a0670 and self.pending is not None:
   assert self.pending.get('setter_returned');assert bytes(u.mem_read(self.pending['record'],152))==expected_record(self.pending['source'],True)
   self.totals['exact_final_152_byte_records']+=1;self.pending=None
  return super().hook(u,pc,size,user)
def authority():
 p,c,facts=CC.authority();table=0x388764;expected={0:0,1:2,2:1,3:3,4:4,5:5,6:6,7:3}
 for key,value in expected.items():
  offset=struct.unpack('<b',p.get_data(table+key,1))[0];target=table+4*offset
  i=next(c.disasm(p.get_data(target,4),target));assert i.mnemonic=='mov' and c.reg_name(i.operands[0].reg)=='w0' and i.operands[1].imm==value
 for r in [0x39d8c0,0x39da00]:
  ins=list(c.disasm(p.get_data(r,132),r));m=next(i for i in ins if i.mnemonic=='umaddl');assert c.reg_name(m.operands[3].reg)=='x0'
  assert any(i.mnemonic=='mov' and i.operands[-1].type==2 and i.operands[-1].imm==48 for i in ins)
  assert next(o.mem.disp for i in ins if i.mnemonic=='ldr' for o in i.operands if o.type==3 and c.reg_name(o.mem.base)=='x1')==16
 return p,c,facts
def main():
 p,c,facts=authority();CC.Setup=Model;rows=[]
 for name,pin in CC.CA.BB.AZ.AV.FILES:
  blob=(CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  rows.append(CC.run(blob,pin,p,c));print(json.dumps({'source_sha256':pin,'passed_placements':4}),flush=True)
 counts=dict(Model.totals);assert all(v==180 for v in counts.values()) and len(counts)==4
 result={'status':'PASS_BOUNDED_INDEPENDENT_STATISTICS_RECORD_AND_ATTACHMENT_MODEL','authority':{'original_DLL_sha256':facts['original_DLL_sha256'],'native_record_bytes':152,'source_record_bytes':72,'normalizer_RVA':'0x388630','normalizer_model':NORMAL,'normalizer_default':3,'attachment_setter_RVAs':['0x39d8c0','0x39da00'],'embedded_ring_stride_bytes':48,'embedded_ring_header_bases_by_setter':[216,40]},'counts':counts,'sources':rows,'full_setup_returns':12,'post_setup_full_query_returns':72,'numeric_callbacks_unmodified':True,'source_input_immutable':True,'actual_live_normal_request_qualified':False,'whole_core_outer_constructor_qualified':False,'runtime_or_image_test':False}
 (OUT/'FIELDS-SAFE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'counts':counts}),flush=True)
if __name__=='__main__':main()
