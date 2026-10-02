#!/usr/bin/env python3
"""Integrate original CRT producers into bounded original camera startup; SP11 private inputs."""
from pathlib import Path
import importlib.util,json,hashlib,inspect,textwrap,struct,collections
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
CM_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011cm-crt-object-producers/source-private.py'
assert hashlib.sha256(CM_PATH.read_bytes()).hexdigest()=='ced215f019ff73c93586f72cc68fe393544ee4a2bc052e331dff3880d0e37d7d'
sp=importlib.util.spec_from_file_location('cn_cm',CM_PATH);CM=importlib.util.module_from_spec(sp);sp.loader.exec_module(CM)
CL=CM.CL;CI=CL.CI;CF=CL.CF;START=CL.STOP;STOP=0xcb9c10
CRT_IMPORTS=None;CASE_FACTS=[]
def authority():
 global CRT_IMPORTS,CLAIM_BIT
 facts,CRT_IMPORTS=CM.authority();camera_imports=CL.authority()[1];p,c=CF.p,CF.c
 calls={0xcc6094:0xcb7300,0xcc609c:0xcc6108,0xcc60c4:0xcb7398,0xcc61b0:0xcb75e0,0xcc61e0:0xcba4b0,0xcc61f0:0x1360,0xcc61f8:0xcb3470,0xced14c:0xcc6078}
 for site,target in calls.items():
  i=next(c.disasm(p.get_data(site,4),site));assert i.mnemonic=='bl' and i.operands[0].imm==target
 constants=lambda a,z:[o.imm for i in c.disasm(p.get_data(a,z),a) for o in i.operands if o.type==2 and i.mnemonic in ['mov','movz','orr','lsl']]
 values=constants(0xcc61a0,100);assert all(v in values for v in [1,88,-1,4000,8192])
 CLAIM_BIT=next(v for v in constants(0xcc61e4,12) if v==8192)
 assert 2147483648 in constants(0x1310,288)
 imports={i.name.decode():i.address-p.OPTIONAL_HEADER.ImageBase for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
 assert imports['LoadLibraryExW']==0xf7e310
 assert next(c.disasm(p.get_data(STOP,4),STOP)).mnemonic=='blr'
 for site in [0xcc608c,0xcc60a4]:
  i=next(c.disasm(p.get_data(site,4),site));assert i.mnemonic=='str' and i.operands[-1].mem.disp==0 and c.reg_name(i.operands[-1].mem.base)=='x19'
 facts.update({'inherited_CM_verifier_sha256':hashlib.sha256(CM_PATH.read_bytes()).hexdigest(),
 'camera_entry_RVA':'0x36cba0','tail_start_RVA':hex(START),'stop_before_original_OS_call_RVA':hex(STOP),
 'unmodeled_next_OS_import':'LoadLibraryExW','unmodeled_import_IAT_RVA':'0xf7e310',
 'stream_allocator_entry_RVA':'0xcc6078','stream_allocation_count':1,'stream_allocation_bytes':88,
 'stream_claim_flag':CLAIM_BIT,'runtime_source_calls':{hex(k):hex(v) for k,v in calls.items()},
 'new_source_ranges_sha256':{hex(a):hashlib.sha256(p.get_data(a,z)).hexdigest() for a,z in [(0xcc6078,448),(0x1310,288),(0xcb9b28,288)]}})
 return facts,camera_imports
# Reuse the pinned CM initializer with the already-loaded Native instance.
init=textwrap.dedent(inspect.getsource(CM.Bootstrap.__init__))
assert init.count('self.n=N.Native()')==1
init=init.replace('self.n=N.Native()','self.n=EXISTING_NATIVE').replace('self.u.hook_add(','type(self.u).hook_add(self.u,')
ns={};exec(init,dict(CM.__dict__,EXISTING_NATIVE=None),ns)
class Bootstrap(CM.Bootstrap):
 runtime=False
 def code(self,u,pc,z,user):
  if not self.runtime:return super().code(u,pc,z,user)
  assert pc!=self.n.base+0xcfe600,'original TLS initializer remains unqualified'
  if pc not in self.sentinels:return
  name=self.sentinels[pc];args=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(3)]
  ret=u.reg_read(UC_ARM64_REG_LR)-self.n.base
  assert self.tail_active,'OS request outside qualified bounded tail'
  if name=='HeapAlloc':
   assert ret==0xcb7630 and args==[self.handle,8,88] and not self.new_stream and self.calloc_requested
   at=self.next_alloc;assert at%16==0 and at+120<self.own+self.extent
   self.next_alloc=(at+88+64+4095)&~4095
   self.u.mem_write(at,bytes(88));self.allocs.append((at,88));self.new_stream=at;value=at
  elif name=='InitializeCriticalSectionEx':
   assert ret==0xcc61e4 and self.new_stream and args==[self.new_stream+48,4000,0]
   assert args[0] not in self.lock_objects and bytes(u.mem_read(args[0],40))==bytes(40)
   self.lock_objects.add(args[0]);value=1
  else:raise AssertionError(('unqualified runtime OS contract',name,hex(ret)))
  self.api_events[name]+=1;u.reg_write(UC_ARM64_REG_X0,value);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
 def runtime_mutex(self,name,receiver,ret):
  assert self.tail_active and receiver in self.lock_objects
  expected={'EnterCriticalSection':{0xcc6098:self.global_mutex(8)},'LeaveCriticalSection':{0xcc60c8:self.global_mutex(8)}}
  if self.new_stream:expected['EnterCriticalSection'][0xcc61fc]=self.new_stream+48
  assert expected[name].get(ret)==receiver,('unqualified runtime mutex source',name,hex(ret))
  if name=='EnterCriticalSection':assert self.depths[receiver]==0;self.depths[receiver]+=1
  else:assert self.depths[receiver]==1;self.depths[receiver]-=1
  self.api_events[name]+=1
 def memory(self,u,access,at,z,value,user):
  if not self.runtime:return super().memory(u,access,at,z,value,user)
  if not self.tail_active:return
  r=u.reg_read(UC_ARM64_REG_PC)-self.n.base
  if self.n.stack<=at and at+z<=self.n.stack+0x10000:return
  if self.n.base<=at<self.n.base+CF.p.OPTIONAL_HEADER.SizeOfImage:
   assert (r,at-self.n.base,z,value) in [(0x13f8,0x1607b00,4,0x80000000),(0x1420,0x1607b00,4,0x80000000)]
   self.runtime_image_writes[(r,at-self.n.base,z)]+=1;return
  assert self.new_stream,'unowned tail write before allocation'
  vector=self.allocs[1][0];k=3+len(self.completed_streams)
  schema={(0xcc61b4,vector+8*k,8):self.new_stream,
   (0xcc61cc,self.new_stream+24,4):0xffffffff,(0x1380,self.new_stream+20,4):CLAIM_BIT,
   (0xcc60ac,self.new_stream+16,4):0,(0xcc60b0,self.new_stream+40,8):0,
   (0xcc60b4,self.new_stream,8):0,(0xcc60b4,self.new_stream+8,8):0,
   (0xcc60bc,self.new_stream+24,4):0xffffffff}
  key=(r,at,z);assert key in schema and value==schema[key],('unexpected bounded tail memory store',hex(r),z)
  self.runtime_owned_writes[key]+=1
 def begin_tail(self):
  assert not self.tail_active;self.tail_active=True;self.new_stream=None;self.calloc_requested=False
  self.runtime_image_writes=collections.Counter();self.runtime_owned_writes=collections.Counter();self.events_before=self.api_events.copy()
  self.flag_before=struct.unpack('<I',self.u.mem_read(self.n.base+0x1607b00,4))[0]
  assert self.flag_before in [0,0x80000000]
 def check_runtime(self):
  assert self.new_stream and self.calloc_requested and len(self.runtime_owned_writes)==8 and all(v==1 for v in self.runtime_owned_writes.values())
  expected_image_writes=collections.Counter({(r,0x1607b00,4):1 for r in [0x13f8,0x1420]}) if self.flag_before==0 else collections.Counter()
  assert self.runtime_image_writes==expected_image_writes
  delta=self.api_events-self.events_before
  assert dict(delta)=={'EnterCriticalSection':2,'HeapAlloc':1,'InitializeCriticalSectionEx':1,'LeaveCriticalSection':1}
  streams=self.completed_streams+[self.new_stream]
  expected_arena=bytearray(self.arena_baseline);vec=self.allocs[1][0]
  for k,at in enumerate(streams,3):
   struct.pack_into('<Q',expected_arena,vec-self.own+8*k,at)
   stream=bytearray(88);struct.pack_into('<II',stream,20,CLAIM_BIT,0xffffffff)
   expected_arena[at-self.own:at-self.own+88]=stream
   assert bytes(self.u.mem_read(at,88))==stream
  assert bytes(self.u.mem_read(self.own,self.extent))==expected_arena,'independent whole CRT arena including prior held streams'
  expected_image=bytearray(self.camera_image_baseline);struct.pack_into('<I',expected_image,0x1607b00,0x80000000)
  assert bytes(self.u.mem_read(self.n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))==expected_image,'independent whole original image delta'
  assert bytes(self.u.mem_read(self.n.heap,0x30000))==self.heap_before
  assert self.lock_objects==self.initial_locks|{at+48 for at in streams}
  assert all(self.depths[at]==(1 if at in {a+48 for a in streams} else 0) for at in self.lock_objects)
  assert all(self.u.mem_read(a-32,32)==b'\xa5'*32 and self.u.mem_read(a+size,32)==b'\xa5'*32 for a,size in self.allocs)
  self.completed_streams=streams;self.tail_active=False
  return bytes(expected_image)
def attach(n):
 ns['__init__'].__globals__['EXISTING_NATIVE']=n
 b=Bootstrap.__new__(Bootstrap);ns['__init__'](b,0,0,CRT_IMPORTS)
 b.run();b.arena_baseline=bytes(b.u.mem_read(b.own,b.extent));b.initial_locks=b.lock_objects.copy()
 b.completed_streams=[];b.runtime=True;b.tail_active=False
 return b
class Startup(CL.Startup):
 def __init__(self,f):
  super().__init__(f);self.cn_tail=False
  type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.result_record_write)
 def result_record_write(self,u,access,at,z,value,user):
  if not self.active or not self.cn_tail or self.allocator_output is None:return
  if at>=self.allocator_output+8 or at+z<=self.allocator_output:return
  r=u.reg_read(UC_ARM64_REG_PC)-self.n.base
  assert at==self.allocator_output and z==8
  assert (r==0xcc608c and value==0) or (r==0xcc60a4 and value==self.crt.new_stream)
  self.result_writes[r]+=1
 def hook(self,u,pc,z,user):
  r=pc-self.n.base
  if self.active and getattr(self,'cn_tail',False):
   if r==0xcc6078:
    assert self.allocator_return is None;self.allocator_return=u.reg_read(UC_ARM64_REG_LR)-self.n.base
    assert self.allocator_return==0xced150
    self.allocator_output=u.reg_read(UC_ARM64_REG_X0)
    assert self.n.stack<=self.allocator_output and self.allocator_output+32<=self.n.stack+0x10000
    self.result_before=bytes(u.mem_read(self.allocator_output,32))
    self.cn_events['original_stream_allocator_entry']+=1
   if r==0xcb75e0:
    assert [u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1)]==[1,88]
    assert u.reg_read(UC_ARM64_REG_LR)-self.n.base==0xcc61b4 and not self.crt.calloc_requested
    self.crt.calloc_requested=True;self.cn_events['original_calloc_request']+=1
   if r==self.allocator_return:
    assert u.reg_read(UC_ARM64_REG_X0)==self.allocator_output
    assert bytes(u.mem_read(self.allocator_output,32))==struct.pack('<Q',self.crt.new_stream)+self.result_before[8:]
    assert self.result_writes==collections.Counter({0xcc608c:1,0xcc60a4:1})
    assert self.crt.depths[self.crt.global_mutex(8)]==0 and self.crt.depths[self.crt.new_stream+48]==1
    self.cn_events['complete_original_stream_allocator_return']+=1
   if r==STOP:
    assert all(self.cn_events[k]==1 for k in ['original_stream_allocator_entry','original_calloc_request','complete_original_stream_allocator_return'])
    ins=next(CF.c.disasm(CF.p.get_data(r,4),r));reg=CF.c.reg_name(ins.operands[0].reg)
    assert u.reg_read(globals()['UC_ARM64_REG_X'+reg[1:]])==self.f.readq(self.n.base+0xf7e310)
    assert bytes(u.mem_read(self.f.arena,self.f.arena_size))==self.tail_arena_before,'unexpected camera object delta'
    assert bytes(u.mem_read(self.inner,606264))==self.tail_inner_before and bytes(u.mem_read(self.outer,72))==self.prefix_outer
    assert len(self.f.allocs)==self.tail_alloc_count and self.f.released==self.tail_released
    assert self.f.readq(self.output)==0 and self.f.readq(self.inner+40)==self.manager and self.f.readq(self.inner+91952)==self.mode_configuration
    self.crt.check_runtime();self.done=True;u.emu_stop();return
  return super().hook(u,pc,z,user)
 def invoke_entry(self):
  self.cn_tail=False;super().invoke_entry();assert self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+START
  self.extra=False;self.context_phase=False;self.active=True;self.cn_tail=True;self.done=False
  self.tail_arena_before=bytes(self.u.mem_read(self.f.arena,self.f.arena_size));self.tail_inner_before=bytes(self.u.mem_read(self.inner,606264))
  self.tail_alloc_count=len(self.f.allocs);self.tail_released=self.f.released.copy()
  self.allocator_return=None;self.allocator_output=None;self.result_writes=collections.Counter();self.cn_events=collections.Counter();self.crt.begin_tail()
  try:self.u.emu_start(self.n.base+START,self.n.end,count=500000)
  except Exception:
   print(json.dumps({'excluded_tail_stop_RVA':hex(self.u.reg_read(UC_ARM64_REG_PC)-self.n.base),'placement_bias':self.bias}),flush=True);raise
  finally:self.active=False;self.cn_tail=False
  assert self.done and self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+STOP
  CASE_FACTS.append({'integrated_CRT_stream_allocator_returns':1,'original_argument0_result_record_bytes':8,'original_return_points_to_argument0_record':True,'independent_entire_new88byte_stream':True,
   'exact_runtime_owned_store_chunks':8,'exact_runtime_image_store_chunks':sum(self.crt.runtime_image_writes.values()),
   'CRT_global_lock_released_stream_lock_held':True,'public_output_zero':True,
   'unmodeled_LoadLibraryExW_not_executed':True})
CI.Startup=Startup
# Retain all pinned CI source checks, changing only exact CRT initialization/ownership/image scope.
source=inspect.getsource(CI.source)
patches={
 'f=CG.load_source(blob);u=f.n.u;n=f.n;o=Startup(f);own=0x90000000':
 'f=CG.load_source(blob);u=f.n.u;n=f.n;b=attach(n);o=Startup(f);o.crt=b;own=0x90000000',
 "name=sentinels[pc];assert u.reg_read(UC_ARM64_REG_X0)==lock+8":
 "name=sentinels[pc]\n  if u.reg_read(UC_ARM64_REG_X0)!=lock+8:\n   b.runtime_mutex(name,u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_LR)-n.base)\n   u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR));return",
 'native=bytes(u.mem_read(n.heap,0x30000));serialized=':
 'b.camera_image_baseline=bytes(u.mem_read(n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))\n native=bytes(u.mem_read(n.heap,0x30000));serialized=',
 "assert bytes(u.mem_read(n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))==image,'unexpected mapped-image/OS-fixture delta'":
 "expected_image=bytearray(image);struct.pack_into('<I',expected_image,0x1607b00,0x80000000)\n  assert bytes(u.mem_read(n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))==expected_image,'unexpected integrated CRT image delta'"}
for old,new in patches.items():assert source.count(old)==1;source=source.replace(old,new)
ns2={};exec(source,dict(CI.__dict__,Startup=Startup,attach=attach),ns2)
def main():
 facts,camera_imports=authority();rows=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  CASE_FACTS.clear();row=ns2['source'](blob,pin,camera_imports);assert len(CASE_FACTS)==len(row['cases'])==4
  for case,detail in zip(row['cases'],CASE_FACTS):case.update(detail)
  rows.append(row)
 cases=[v for row in rows for v in row['cases']]
 result={'experiment':'E011CN','status':'PASS_BOUNDED_ORIGINAL_CRT_INTEGRATION','base_commit':'26424022418adb9ecb934cc2d92db92153616a06',
  'authority':facts,'sources':rows,'case_count':len(cases),'source_files':3,'placement_cases_per_source':4,
  'complete_original_CRT_bootstrap_entry_returns':12,'original_existing_table_lookup_returns':3,
  'complete_original_runtime_stream_allocator_returns':12,'complete_argument0_pointer_result_records':12,'independent_entire_new88byte_streams':12,
  'independent_bootstrap72byte_records':192,'independent_bootstrap88byte_static_streams':9,
  'original_bootstrap_logical_OS_initializations':246,'original_runtime_logical_OS_initializations':12,
  'bootstrap_guarded_heap_allocations':6,'runtime_guarded_heap_allocations':12,
  'exact_runtime_owned_store_chunks':96,'exact_runtime_image_store_chunks':sum(v['exact_runtime_image_store_chunks'] for v in cases),
  'runtime_CRT_lock_enters':24,'runtime_CRT_global_lock_leaves':12,
  'CRT_stream_locks_held_at_stop':12,'camera_outer_locks_held_at_stop':12,
  'statistics_records':sum(v['independent_152byte_records'] for v in cases),
  'statistics_initializers':sum(v['original_48byte_stride_array_initializers'] for v in cases),
  'core_initializers':sum(v['original_core_vector_initializers'] for v in cases),
  'core_cache_lookups':sum(v['source_cache_lookups'] for v in cases),
  'camera_objects_unchanged_after_CL':True,'new_numeric_or_TLS_success_stub':False,'new_logger16A4228_admitted':False,
  'unmodeled_LoadLibraryExW_executed':False,'whole_outer_return_qualified':False,'final_output_publication_qualified':False,
  'complete_CRT_environment_qualified':False,'actual_live_Default_producers_qualified':False,
  'native_Windows_mutex_bytes_or_concurrency_qualified':False,'native_rear_runtime_allowed':False,
  'new_camera_Starts':0,'new_reboots':0,'runtime_or_image_test':False,'next_experiment':'E011CO'}
 assert result['exact_runtime_image_store_chunks']==6 and all([v['exact_runtime_image_store_chunks'] for v in row['cases']]==[2,0,0,0] for row in rows)
 assert len(cases)==12 and result['statistics_records']==180 and result['statistics_initializers']==1440 and result['core_initializers']==292
 (OUT/'INTEGRATION-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))}),flush=True)
if __name__=='__main__':main()
