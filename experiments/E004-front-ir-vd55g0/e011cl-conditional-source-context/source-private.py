#!/usr/bin/env python3
"""Independently model original conditional source context; private input only."""
from pathlib import Path
import importlib.util,json,hashlib,struct,collections
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
CK_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ck-source-object-and-module-binding/source-private.py'
assert hashlib.sha256(CK_PATH.read_bytes()).hexdigest()=='7ae4b9601bd7b45bad2425fc5ad32e72c6fae5758ea36322d40b072d38c87e01'
sp=importlib.util.spec_from_file_location('cl_ck',CK_PATH);CK=importlib.util.module_from_spec(sp);sp.loader.exec_module(CK)
CI=CK.CI;CF=CK.CF;START=CK.STOP;STOP=0x36de04;POISON=False;CASE_FACTS=[]
STORES=[(0x36dc78,555728,4,'match'),(0x36dc84,555752,4,'context'),
 (0x36dc8c,555760,8,'meter_fields'),(0x36dd24,555768,4,'meter_id'),
 (0x36dd30,555772,4,'scene_id'),(0x36ddd8,555776,8,'sentinel')]
def authority():
 facts,imports=CK.authority();p,c=CF.p,CF.c
 for r,off,z,key in STORES:
  i=next(c.disasm(p.get_data(r,4),r));assert i.mnemonic=='str'
 for r,disp in [(0x36dc7c,8),(0x36dd1c,0),(0x36dd28,0)]:
  i=next(c.disasm(p.get_data(r,4),r));assert i.mnemonic=='ldr' and i.operands[-1].mem.disp==disp
 i=next(c.disasm(p.get_data(0x36dc48,4),0x36dc48));assert i.mnemonic=='ldr' and c.reg_name(i.operands[0].reg)=='x1' and i.operands[-1].mem.disp==16
 i=next(c.disasm(p.get_data(STOP,4),STOP));assert i.mnemonic=='bl' and i.operands[0].imm==0x7ac38
 facts.update({'conditional_start_RVA':hex(START),'stop_before_RVA':hex(STOP),
  'conditional_prefix_bytes':STOP-START,'conditional_prefix_sha256':hashlib.sha256(p.get_data(START,STOP-START)).hexdigest(),
  'scene_module_core_cache_index':37,'scene_bank_wire_stride':144,'scene_bank_owned_stride':176,
  'new_context_inner_store_offsets':[off for r,off,z,k in STORES],
  'inherited_CK_verifier_sha256':hashlib.sha256(CK_PATH.read_bytes()).hexdigest()})
 return facts,imports
class Startup(CK.Startup):
 def __init__(self,f):
  super().__init__(f);self.context_phase=False;self.selection_ready=False
  type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.context_write)
 def wire(self,sid):
  row=self.f.sy[sid];return self.f.blob[row['data_abs_offset']:row['data_abs_offset']+row['data_bytes']]
 def owned(self,at,z):
  assert (at,z) in self.f.allocs and at not in self.f.released
 def prepare_selection(self):
  assert not self.selection_ready
  self.scene=self.f.readq(self.core+0xf00+8*37)-288;self.owned(self.scene,352)
  scene_id=self.f.readi(self.scene+56);meter_id=self.f.readi(self.meter+56)
  assert self.f.sy[scene_id]['type']=='aecxscenechangedetector' and self.f.sy[meter_id]['type']=='aecxmetering'
  assert self.f.readi(self.scene+288)==scene_id and self.f.readi(self.meter+288)==meter_id
  sw=self.wire(scene_id);assert len(sw)==32
  count,bank_id=struct.unpack_from('<II',sw,24);assert count>0 and self.f.sy[bank_id]['type']=='scdBank'
  self.bank_count=count
  bw=self.wire(bank_id);assert len(bw)==144*count and self.f.readi(self.scene+332)==count
  self.banks=self.f.readq(self.scene+344);self.owned(self.banks,176*count)
  self.meter_name=self.f.readq(self.meter+368);self.owned(self.meter_name,7)
  name=bytes(self.u.mem_read(self.meter_name,7));assert name[-1:]==b'\0'
  assert self.f.readi(self.meter+360)==1
  selected=[]
  for k in range(count):
   raw=bw[144*k:144*(k+1)];at=self.banks+176*k
   assert bytes(self.u.mem_read(at,12))==raw[:12],'source-derived bank scalar prefix'
   length,nsid=struct.unpack_from('<II',raw,12);nw=self.wire(nsid)
   assert self.f.sy[nsid]['type']=='SCDName' and len(nw)==length,('bank name source type',self.f.sy[nsid]['type'],len(nw),length)
   ptr=self.f.readq(at+16);self.owned(ptr,length)
   assert bytes(self.u.mem_read(ptr,length))==nw,'source-derived bank name'
   if struct.unpack_from('<I',raw)[0]==1 and nw==name:selected.append(k)
  assert selected and selected[0]==1
  self.selected_bank=self.banks+176*selected[0]
  raw=bw[144*selected[0]:144*(selected[0]+1)]
  self.expected_values={'match':1,'context':struct.unpack_from('<I',raw,8)[0],
   'meter_fields':self.meter+360,'meter_id':meter_id,'scene_id':scene_id,'sentinel':2**64-1}
  self.selection_ready=True;self.selection_visits=[];self.context_reads=collections.Counter()
 def context_write(self,u,access,at,z,value,user):
  if not self.active or not self.context_phase or not self.inner<=at<self.inner+606264:return
  key=(u.reg_read(UC_ARM64_REG_PC)-self.n.base,at-self.inner,z)
  assert key in self.context_schema,('unmodelled context store',hex(key[0]),key[1:])
  assert value%(1<<(z*8))==self.expected_values[self.context_schema[key]],('context store mismatch',hex(key[0]))
  self.context_counts[key]+=1
 def hook(self,u,pc,z,user):
  r=pc-self.n.base
  if self.active and self.extra:
   if r==0x36dc10:self.prepare_selection()
   if r==0x36dc3c:
    assert self.selection_ready
    at=u.reg_read(UC_ARM64_REG_X24);k=(at-self.banks)//176
    assert at==self.banks+176*k and 0<=k<self.bank_count;self.selection_visits.append(k)
   if r==0x36dc54:
    assert self.selection_visits==[0,1]
    assert u.reg_read(UC_ARM64_REG_X24)==self.selected_bank
    assert [u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1)]==[self.meter_name,self.f.readq(self.selected_bank+16)]
  if self.active and self.context_phase:
   reads={0x36dc7c:(UC_ARM64_REG_X24,self.selected_bank),
    0x36dd1c:(UC_ARM64_REG_X19,self.meter+288),
    0x36dd28:(UC_ARM64_REG_X22,self.scene+288)}
   if r in reads:
    reg,expected=reads[r];assert u.reg_read(reg)==expected;self.context_reads[r]+=1
   if r==0x36dde8:
    assert self.f.readi(self.inner+91908)==0;self.context_reads[r]+=1
   if r==STOP:
    assert self.context_counts==collections.Counter({k:1 for k in self.context_schema})
    assert dict(self.context_reads)=={r:1 for r in [0x36dc7c,0x36dd1c,0x36dd28,0x36dde8]}
    expected=bytearray(self.before_context_inner)
    for r,off,z,key in STORES:expected[off:off+z]=self.expected_values[key].to_bytes(z,'little')
    assert bytes(u.mem_read(self.inner,606264))==expected,'independent entire conditional inner delta'
    arena=bytearray(self.before_context_arena);off=self.inner-self.f.arena;arena[off:off+606264]=expected
    assert bytes(u.mem_read(self.f.arena,self.f.arena_size))==arena,'unexpected other arena object/gap delta'
    assert len(self.f.allocs)==self.context_allocation_count and self.f.released==self.context_released
    assert bytes(u.mem_read(self.outer,72))==self.prefix_outer and self.f.readq(self.output)==0
    assert self.f.readq(self.inner+40)==self.manager and self.f.readq(self.inner+91952)==self.mode_configuration
    self.f.bounds();self.done=True;u.emu_stop();return
  return super().hook(u,pc,z,user)
 def invoke_entry(self):
  self.selection_ready=False;self.context_phase=False;super().invoke_entry()
  assert self.selection_ready and self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+START
  assert self.u.reg_read(UC_ARM64_REG_X24)==self.selected_bank
  self.context_schema={(r,off,z):key for r,off,z,key in STORES};self.context_counts=collections.Counter()
  if POISON:
   for r,off,z,key in STORES:self.u.mem_write(self.inner+off,b'\xa5'*z)
  self.before_context_inner=bytes(self.u.mem_read(self.inner,606264))
  self.before_context_arena=bytes(self.u.mem_read(self.f.arena,self.f.arena_size))
  self.context_allocation_count=len(self.f.allocs);self.context_released=self.f.released.copy()
  self.active=True;self.context_phase=True;self.done=False
  try:self.u.emu_start(self.n.base+START,self.n.end,count=100000)
  except Exception:
   print(json.dumps({'excluded_stop_RVA':hex(self.u.reg_read(UC_ARM64_REG_PC)-self.n.base),'placement_bias':self.bias,'owned_context_destination_poison':POISON}),flush=True);raise
  finally:self.active=False;self.context_phase=False
  assert self.done and self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+STOP
  CASE_FACTS.append({'scene_bank_count':self.bank_count,'owned_scene_bank_array_bytes':176*self.bank_count})
CI.Startup=Startup
def main():
 global POISON
 facts,imports=authority();rows=[]
 for poison in [False,True]:
  POISON=poison
  for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
   blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
   CASE_FACTS.clear();row=CI.source(blob,pin,imports);row['owned_context_destination_poison']=poison
   assert len(CASE_FACTS)==len(row['cases'])==4
   for case,detail in zip(row['cases'],CASE_FACTS):case.update(detail);case.update({'source_derived_scene_bank_selection':True,'selection_record_index':1,
    'independent_entire_conditional_inner_delta':True,'exact_conditional_store_chunks':6,
    'conditional_new_allocations':0,'other_arena_bytes_immutable':True})
   rows.append(row)
 cases=[v for row in rows for v in row['cases']]
 result={'status':'PASS_BOUNDED_ORIGINAL_CONDITIONAL_SOURCE_CONTEXT','experiment':'E011CL',
  'base_commit':'1ccf55cf404d893473bcfa98f81f6ce5c4664637','authority':facts,'sources':rows,
  'cases':len(cases),'unmodified_cases':12,'owned_destination_poison_cases':12,
  'independent_scene_bank_selection_cases':len(cases),'independent_entire_inner_delta_cases':len(cases),
  'scene_bank_counts_by_source':[row['cases'][0]['scene_bank_count'] for row in rows[:3]],
  'exact_conditional_inner_store_chunks':6*len(cases),'conditional_new_allocations':0,
  'independent_152byte_records':sum(v['independent_152byte_records'] for v in cases),
  'statistics_record_initializers':sum(v['original_48byte_stride_array_initializers'] for v in cases),
  'core_vector_initializers':sum(v['original_core_vector_initializers'] for v in cases),
  'core_cache_lookups':sum(v['source_cache_lookups'] for v in cases),'inherited_additional_GetTag_returns':2*len(cases),
  'statistics_and_mode_links_retained_to_stop':True,'outer_output_zero_and_lock_held':True,
  'alternate_nonmatching_context_branches_qualified':False,'whole_scene_bank_payload_qualified':False,
  'CRT_environment_qualified':False,'whole_outer_return_qualified':False,'final_output_publication_qualified':False,
  'actual_live_Default_producers_qualified':False,'new_numeric_or_TLS_success_stub':False,
  'new_logger16A4228_classification_admitted':False,'native_rear_runtime_allowed':False,
  'new_camera_Starts':0,'new_reboots':0,'runtime_or_image_test':False,'next_experiment':'E011CM'}
 assert len(cases)==24 and result['independent_152byte_records']==360
 assert result['statistics_record_initializers']==2880 and result['core_vector_initializers']==584 and result['core_cache_lookups']==1032
 (OUT/'CONTEXT-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))}),flush=True)
if __name__=='__main__':main()
