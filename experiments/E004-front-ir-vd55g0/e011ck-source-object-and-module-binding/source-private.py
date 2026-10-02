#!/usr/bin/env python3
"""Original post-reset source objects/modules; independent guarded byte models."""
from pathlib import Path
import importlib.util,inspect,json,hashlib,struct,collections
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
CJ_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011cj-baseline-state-reset/source-private.py'
assert hashlib.sha256(CJ_PATH.read_bytes()).hexdigest()=='f00af2970d246001e21e815aad7f2f96c4a37e159f7e1aefc2a881b1254b3d26'
spec=importlib.util.spec_from_file_location('ck_cj',CJ_PATH);CJ=importlib.util.module_from_spec(spec);spec.loader.exec_module(CJ)
CI=CJ.CI;CF=CJ.CF;CG=CJ.CG;START=CJ.STOP;STOP=0x36dc58;POISON=False
ACCESSORS=[0x36d9d0,0x36dbac,0x36dbcc]
for site in ACCESSORS:CF.NUMERIC[site]={0x3a8730}
ALLOC_SIZES=[1088,48]+[488,32]*6+[120,240,880]
# Values are scalar IEEE bits or independently selected source-object relationships.
WRITES=[(0x36d7b0,16,8,'object1088'),(0x36d818,24,8,'object120'),
 (0x36d848,592,8,'face352'),(0x36d8e4,1192,8,'face408'),
 (0x36d978,1212,8,0),(0x36d988,1244,4,1025758986),
 (0x36d98c,1220,8,515396075530),(0x36d994,1228,4,130),
 (0x36d99c,1236,4,5),(0x36d9a4,1232,4,1008981770),
 (0x36d9a8,1240,4,1058642330),(0x36d9ac,91576,8,0),
 (0x36d9b4,91584,8,0),(0x36d9b8,605160,8,0),
 (0x36da70,1792,8,'meter392'),(0x36db0c,2392,8,'meter448'),
 (0x36dc0c,555728,4,0)]
MODULES={0x36d834:(26,440,'aecxface',0x1375ea0),0x36da5c:(31,624,'aecxmetering',0x1375e68)}
CALLS={0x36d7a4:0x394048,0x36d80c:0x39c1f8,0x36d9e4:0x370728,0x36d830:0x6f39f8,0x36da58:0x6f39f8,0x36dc54:0xf5df00}
def authority():
 facts,imports=CJ.authority();p,c=CF.p,CF.c
 for site,target in CALLS.items():
  i=next(c.disasm(p.get_data(site,4),site));assert i.mnemonic=='bl' and i.operands[0].imm==target
 for site in ACCESSORS:
  a,b=list(c.disasm(p.get_data(site,8),site));assert a.mnemonic==b.mnemonic=='blr'
  assert c.reg_name(a.operands[0].reg)=='x17' and c.reg_name(b.operands[0].reg)=='x15'
 for r,off,z,value in WRITES:
  i=next(c.disasm(p.get_data(r,4),r));assert i.mnemonic.startswith(('str','stp'))
 for index,size,name,key in MODULES.values():assert p.get_data(key,len(name)+1)==name.encode()+b'\0'
 facts.update({'stop_before_RVA':hex(STOP),'post_reset_start_RVA':hex(START),'post_reset_prefix_bytes':STOP-START,'inner_object_binding_offsets':[16,24],'new_primary_object_sizes':[1088,120],'additional_module_cache_indices':[26,31],'additional_module_binding_offsets':[592,1192,1792,2392],'independent_new_inner_store_chunks':len(WRITES),'source_compare_RVA':'0xf5df00','source_compare_is_strcmp_not_memcpy':True,'post_reset_range_sha256':hashlib.sha256(p.get_data(START,STOP-START)).hexdigest(),'inherited_CJ_verifier_sha256':hashlib.sha256(CJ_PATH.read_bytes()).hexdigest()})
 return facts,imports
class Startup(CJ.Startup):
 def __init__(self,f):
  super().__init__(f);self.extra=False
  type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.inner_write)
 def resolve(self,value):
  if not isinstance(value,str):return value
  return {'object1088':getattr(self,'object1088',None),'object120':getattr(self,'object120',None),
   'face352':self.face+352,'face408':self.face+408,'meter392':self.meter+392,'meter448':self.meter+448}[value]
 def inner_write(self,u,access,at,z,value,user):
  if not self.active or not self.extra or not self.inner<=at<self.inner+606264:return
  r=u.reg_read(UC_ARM64_REG_PC)-self.n.base;key=(r,at-self.inner,z)
  assert key in self.write_schema,('unmodelled inner store',hex(r),at-self.inner,z)
  assert value==self.resolve(self.write_schema[key]),('independent inner store mismatch',hex(r),at-self.inner)
  self.write_counts[key]+=1
 def verify_objects(self):
  new=self.f.allocs[self.new_count:];assert [z for at,z in new]==ALLOC_SIZES
  assert all(at not in self.f.released for at,z in new)
  assert new[0][0]==self.object1088 and new[14][0]==self.object120
  expected=bytearray(1088);struct.pack_into('<QQ',expected,0,self.n.base+0x13380e8,self.inner)
  for j in range(6):struct.pack_into('<Q',expected,56+8*j,new[2+2*j][0])
  struct.pack_into('<Q',expected,104,new[1][0]);struct.pack_into('<Q',expected,120,6)
  assert bytes(self.u.mem_read(self.object1088,1088))==expected,'independent whole1088-byte object'
  assert bytes(self.u.mem_read(new[1][0],48))==bytes(48),'independent entire48-byte child buffer'
  expected=bytearray(120)
  values={0:self.n.base+0x1338140,8:self.inner,48:new[16][0],56:15<<32,64:55,72:0xbf800000<<32,80:0xbf800000,104:new[15][0]}
  for off,value in values.items():struct.pack_into('<Q',expected,off,value)
  assert bytes(self.u.mem_read(self.object120,120))==expected,'independent whole120-byte object'
 def hook(self,u,pc,z,user):
  r=pc-self.n.base
  if self.active and self.extra:
   if r in [0x36d784,0x36d7b8]:assert u.reg_read(UC_ARM64_REG_X0)==(1088 if r==0x36d784 else 120)
   if r in [0x36d788,0x36d7bc]:
    value=u.reg_read(UC_ARM64_REG_X0);size=1088 if r==0x36d788 else 120
    assert (value,size) in self.f.allocs and value not in self.f.released
    setattr(self,'object1088' if size==1088 else 'object120',value)
   if r==0x394048:
    assert [u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1)]==[self.object1088,self.inner]
    self.ck_events['original1088_constructor_entry']+=1
   if r==0x39c1f8:
    assert u.reg_read(UC_ARM64_REG_X0)==self.object120;self.ck_events['original120_helper_entry']+=1
   if r==0x370728:
    assert [u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_W1),u.reg_read(UC_ARM64_REG_W2)]==[self.core+0xf00,7,2]
    self.ck_events['original_core_query_entry']+=1
   if r in [0x36d7a8,0x36d810,0x36d9e8]:self.ck_events['original_helper_return_'+hex(r)]+=1
   if r in ACCESSORS:
    receiver=u.reg_read(UC_ARM64_REG_X0);assert receiver==self.f.readq(self.inner+8)
    assert self.f.readq(receiver+312)==u.reg_read(UC_ARM64_REG_X15)==self.n.base+0x3a8730
    self.ck_events['additional_original_interface_accessors']+=1
   if r==0x6f39f8 and u.reg_read(UC_ARM64_REG_LR)-self.n.base in MODULES:
    ret=u.reg_read(UC_ARM64_REG_LR)-self.n.base;index,size,name,key=MODULES[ret]
    assert [u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2),u.reg_read(UC_ARM64_REG_W3)]==[self.f.manager,self.n.base+key,self.mode,0]
    self.ck_events['exact_additional_source_GetTag_entries']+=1
   if r in MODULES:
    index,size,name,key=MODULES[r];expected=self.face if index==26 else self.meter
    assert u.reg_read(UC_ARM64_REG_X0)==expected and (expected,size) in self.f.allocs and expected not in self.f.released
    assert self.f.sy[self.f.readi(expected+56)]['type']==name
    self.ck_events['independent_source_module_returns']+=1
   if r==0x36dc54:
    self.compare_ptrs=[u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1)]
    assert all((at,7) in self.f.allocs and at not in self.f.released for at in self.compare_ptrs)
    self.compare_before=[bytes(u.mem_read(at,7)) for at in self.compare_ptrs]
    assert all(v[-1:]==b'\0' for v in self.compare_before) and self.compare_before[0]==self.compare_before[1]
   if r==0xf5df00 and u.reg_read(UC_ARM64_REG_LR)-self.n.base==STOP:self.ck_events['original_strcmp_entry']+=1
   if r==STOP:
    assert u.reg_read(UC_ARM64_REG_W0)==0
    assert self.compare_before==[bytes(u.mem_read(at,7)) for at in self.compare_ptrs]
    self.ck_events['original_strcmp_equal_return']+=1
    assert self.write_counts==collections.Counter({k:1 for k in self.write_schema})
    expected=bytearray(self.before_inner)
    for r,off,width,value in WRITES:expected[off:off+width]=self.resolve(value).to_bytes(width,'little')
    assert bytes(u.mem_read(self.inner,606264))==expected,'independent entire post-reset inner delta'
    self.verify_objects()
    predicted_arena=bytearray(self.before_arena);off=self.inner-self.f.arena;predicted_arena[off:off+606264]=expected
    assert len(CG.exact_new_payloads(self.f,bytes(predicted_arena),self.new_count))==17
    assert bytes(u.mem_read(self.outer,72))==self.prefix_outer
    assert self.f.readq(self.inner+40)==self.manager and self.f.readq(self.inner+91952)==self.mode_configuration
    expected_events={'original1088_constructor_entry':1,'original120_helper_entry':1,'original_core_query_entry':1,**{'original_helper_return_'+hex(ret):1 for ret in [0x36d7a8,0x36d810,0x36d9e8]},'additional_original_interface_accessors':3,'exact_additional_source_GetTag_entries':2,'independent_source_module_returns':2,'original_strcmp_entry':1,'original_strcmp_equal_return':1}
    assert dict(self.ck_events)==expected_events,dict(self.ck_events)
    self.done=True;u.emu_stop();return
  return super().hook(u,pc,z,user)
 def invoke_entry(self):
  self.extra=False;super().invoke_entry();assert self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+START
  self.face=self.f.readq(self.core+0xf00+8*26)-288;self.meter=self.f.readq(self.core+0xf00+8*31)-288
  for at,size,name in [(self.face,440,'aecxface'),(self.meter,624,'aecxmetering')]:
   assert (at,size) in self.f.allocs and at not in self.f.released and self.f.sy[self.f.readi(at+56)]['type']==name
  self.before_inner=bytes(self.u.mem_read(self.inner,606264));self.new_count=len(self.f.allocs)
  self.ck_events=collections.Counter();self.write_counts=collections.Counter();self.write_schema={(r,off,z):value for r,off,z,value in WRITES}
  if POISON:
   poisoned=bytearray(self.before_inner)
   for r,off,z,value in WRITES:
    if isinstance(value,int):poisoned[off:off+z]=b'\xa5'*z
   self.u.mem_write(self.inner,bytes(poisoned))
  self.before_arena=bytes(self.u.mem_read(self.f.arena,self.f.arena_size));self.done=False;self.extra=True;self.active=True
  try:self.u.emu_start(self.n.base+START,self.n.end,count=1000000)
  except Exception:
   print(json.dumps({'excluded_fixture_stop_RVA':hex(self.u.reg_read(UC_ARM64_REG_PC)-self.n.base),'placement_bias':self.bias,'owned_scalar_poison':POISON}),flush=True);raise
  finally:self.active=False;self.extra=False
  assert self.done and self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+STOP
  self.before_arena=None
CI.Startup=Startup
def main():
 global POISON
 facts,imports=authority();rows=[]
 for poison in [False,True]:
  POISON=poison
  for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
   blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
   row=CI.source(blob,pin,imports);row['owned_post_reset_scalar_poison']=poison
   for v in row['cases']:v.update({'independent_entire_inner_post_reset_delta':True,'independent_whole1088byte_object':True,'independent_whole120byte_object':True,'independent_whole48byte_child_buffer':True,'new_original_allocations':17,'new_inner_store_chunks':17,'additional_original_GetTag_returns':2,'additional_original_interface_accessors':3,'original_strcmp_equal_return':True,'all_preexisting_objects_except_predicted_inner_immutable':True,'whole_new_child_payload_semantics_qualified':False})
   rows.append(row)
 cases=[v for row in rows for v in row['cases']]
 result={'status':'PASS_BOUNDED_ORIGINAL_SOURCE_OBJECT_AND_MODULE_BINDING','experiment':'E011CK','base_commit':'c4c9d4c2055160883d4bc1a0dbb864a886a15ae3','authority':facts,'sources':rows,'cases':len(cases),'unmodified_cases':12,'owned_scalar_poison_cases':12,'independent_entire_inner_delta_cases':len(cases),'independent_whole1088byte_object_cases':len(cases),'independent_whole120byte_object_cases':len(cases),'original_helper_returns':3*len(cases),'additional_source_GetTag_returns':2*len(cases),'additional_original_interface_accessors':3*len(cases),'original_strcmp_equal_returns':len(cases),'exact_post_reset_inner_store_chunks':17*len(cases),'new_guarded_allocations':17*len(cases),'independent_152byte_records':sum(v['independent_152byte_records'] for v in cases),'statistics_record_initializers':sum(v['original_48byte_stride_array_initializers'] for v in cases),'core_vector_initializers':sum(v['original_core_vector_initializers'] for v in cases),'core_cache_lookups':sum(v['source_cache_lookups'] for v in cases),'statistics_and_mode_links_retained_to_stop':True,'whole_new_child_payload_semantics_qualified':False,'whole_outer_return_qualified':False,'final_output_publication_qualified':False,'CRT_environment_qualified':False,'actual_live_Default_producers_qualified':False,'new_numeric_or_TLS_success_stub':False,'new_logger16A4228_classification_admitted':False,'native_rear_runtime_allowed':False,'new_camera_Starts':0,'new_reboots':0,'runtime_or_image_test':False,'next_experiment':'E011CL'}
 assert len(cases)==24 and result['independent_152byte_records']==360 and result['statistics_record_initializers']==2880 and result['core_vector_initializers']==584 and result['core_cache_lookups']==1032
 (OUT/'BINDING-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))}),flush=True)
if __name__=='__main__':main()
