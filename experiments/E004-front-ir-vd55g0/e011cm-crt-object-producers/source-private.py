#!/usr/bin/env python3
"""Original CRT object producers under explicit owned single-thread OS contracts."""
from pathlib import Path
import importlib.util,struct,json,hashlib,collections
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
CL_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011cl-conditional-source-context/source-private.py'
assert hashlib.sha256(CL_PATH.read_bytes()).hexdigest()=='0f2f307d05d053ee86fde1c986074e39424f1185b71af1a99713682beba42274'
sp=importlib.util.spec_from_file_location('cm_cl',CL_PATH);CL=importlib.util.module_from_spec(sp);sp.loader.exec_module(CL)
CF=CL.CF;N=CF.CC.CA.BW.N
API_RETURNS={'GetProcessHeap':{0xcbae28},'HeapAlloc':{0xcb7630},
 'InitializeCriticalSectionEx':{0xcb72b8,0xcc061c,0xcb3328},
 'EnterCriticalSection':{0xcc074c},'LeaveCriticalSection':{0xcc0790}}
ENTRIES=[(0xcb7280,1),(0xcbae10,1),(0xcc06f0,0),(0xcb3260,0)]
def authority():
 facts,_=CL.authority();p,c=CF.p,CF.c;p.parse_data_directories()
 imports={i.name.decode():i.address-p.OPTIONAL_HEADER.ImageBase for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
 expected={'GetProcessHeap':0xf7e358,'HeapAlloc':0xf7e280,'InitializeCriticalSectionEx':0xf7e230,'EnterCriticalSection':0xf7e0b8,'LeaveCriticalSection':0xf7e0c0}
 assert all(imports[name]==rva for name,rva in expected.items())
 for site,target in [(0xcb72b4,0xcba4b0),(0xcb32a8,0xcb75e0),(0xcb3324,0xcba4b0),(0xcc0748,0xcb7300),(0xcc078c,0xcb7398),(0xcc0618,0xcba4b0)]:
  i=next(c.disasm(p.get_data(site,4),site));assert i.mnemonic=='bl' and i.operands[0].imm==target
 assert [p.get_dword_at_rva(0x1607060+88*k+20) for k in range(3)]==[8193,8194,8194]
 ranges=[(0xcb7280,128),(0xcbae10,64),(0xcc06f0,232),(0xcb3260,320),(0xcb75e0,208),(0xcba4b0,16),(0xcc0598,344)]
 return {'original_DLL_sha256':facts['original_DLL_sha256'],'inherited_CL_verifier_sha256':hashlib.sha256(CL_PATH.read_bytes()).hexdigest(),
  'original_entries':[hex(r) for r,v in ENTRIES],'OS_import_IAT_RVAs':{name:hex(rva) for name,rva in expected.items()},
  'source_ranges_sha256':{hex(r):hashlib.sha256(p.get_data(r,z)).hexdigest() for r,z in ranges},
  'global_count_field_RVA':'0x16a2a50','global_count_field_bytes':4,'global_pointer_vector_RVA':'0x16a2a58',
  'process_heap_handle_global_RVA':'0x16a3240','indexed_table_global_RVA':'0x16a2a90',
  'indexed_record_stride_bytes':72,'indexed_record_count':64,'global_mutex_count':15,'static_stream_object_stride':88},expected
class Bootstrap:
 def __init__(self,bias,preset,imports):
  self.n=N.Native();self.u=self.n.u;self.bias=bias;self.preset=preset;self.capacity=preset or 512
  self.own=0x92000000;self.extent=0x200000;self.u.mem_map(self.own,self.extent);self.u.mem_write(self.own,b'\xa5'*self.extent)
  self.handle=(self.own+0x100+bias+15)&~15;self.u.mem_write(self.handle,bytes(32))
  self.next_alloc=(self.own+0x10000+bias+15)&~15;self.allocs=[];self.lock_objects=set();self.depths=collections.Counter();self.api_events=collections.Counter()
  self.sentinels={self.own+0x1000+32*k:name for k,name in enumerate(API_RETURNS)}
  for at,name in self.sentinels.items():self.u.mem_write(self.n.base+imports[name],struct.pack('<Q',at))
  self.u.mem_write(self.n.base+0x16a2a50,struct.pack('<I',preset))
  self.image_before=bytes(self.u.mem_read(self.n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))
  self.arena_before=bytes(self.u.mem_read(self.own,self.extent));self.heap_before=bytes(self.u.mem_read(self.n.heap,0x30000))
  self.phase=None;self.source_image_stores=collections.Counter();self.counter_values=[]
  self.u.hook_add(UC_HOOK_CODE,self.code);self.u.hook_add(UC_HOOK_MEM_WRITE,self.memory)
 def global_mutex(self,k):return self.n.base+0x16a2ec0+40*k
 def stream(self,k):return self.n.base+0x1607060+88*k
 def invoke(self,rva):
  for k in range(29):self.u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0)
  self.u.mem_write(self.n.stack,bytes(0x10000));self.u.reg_write(UC_ARM64_REG_SP,self.n.stack+0xf000);self.u.reg_write(UC_ARM64_REG_LR,self.n.end)
  self.phase=rva;self.u.emu_start(self.n.base+rva,self.n.end,count=250000)
  assert self.u.reg_read(UC_ARM64_REG_PC)==self.n.end,'complete original entry did not return'
  return self.u.reg_read(UC_ARM64_REG_W0)
 def os_contract(self,name,args,ret):
  assert ret in API_RETURNS[name],('unqualified OS caller',name,hex(ret))
  if name=='GetProcessHeap':
   assert self.phase==0xcbae10;value=self.handle
  elif name=='HeapAlloc':
   assert args[0]==self.handle and args[1]==8
   expected_size=4608 if not self.allocs else 8*self.capacity
   assert len(self.allocs)<2 and args[2]==expected_size and self.phase in [0xcc06f0,0xcb3260]
   at=self.next_alloc;size=args[2];assert at%16==0 and at+size+32<self.own+self.extent
   self.next_alloc=((at+size+64+4095)&~4095)+((self.bias+15)&~15)
   self.u.mem_write(at,bytes(size));self.allocs.append((at,size));value=at
  elif name=='InitializeCriticalSectionEx':
   assert args[1:]==[4000,0] and args[0] not in self.lock_objects
   if self.phase==0xcb7280:expected=self.global_mutex(len(self.lock_objects))
   elif self.phase==0xcc06f0:
    assert len(self.allocs)==1;expected=self.allocs[0][0]+72*(len(self.lock_objects)-15)
   elif self.phase==0xcb3260:expected=self.stream(len(self.lock_objects)-79)+48
   else:raise AssertionError('unqualified mutex owner')
   assert args[0]==expected and bytes(self.u.mem_read(expected,40))==bytes(40)
   self.lock_objects.add(expected);value=1
  elif name in ['EnterCriticalSection','LeaveCriticalSection']:
   assert self.phase==0xcc06f0 and args[0]==self.global_mutex(7) and args[0] in self.lock_objects
   if name=='EnterCriticalSection':self.depths[args[0]]+=1
   else:assert self.depths[args[0]]>0;self.depths[args[0]]-=1
   value=args[0]
  else:raise AssertionError('unqualified OS contract')
  self.api_events[name]+=1;return value
 def code(self,u,pc,z,user):
  if pc in self.sentinels:
   args=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(3)]
   ret=u.reg_read(UC_ARM64_REG_LR)-self.n.base
   value=self.os_contract(self.sentinels[pc],args,ret)
   u.reg_write(UC_ARM64_REG_X0,value);u.reg_write(UC_ARM64_REG_PC,self.n.base+ret);return
  r=pc-self.n.base
  assert 0<=r<CF.p.OPTIONAL_HEADER.SizeOfImage,('unqualified original or OS target',hex(r))
  assert r!=0xcfe600,'original TLS initialization remains unqualified; no success substitute'
 def memory(self,u,access,at,z,value,user):
  if not self.n.base<=at<self.n.base+CF.p.OPTIONAL_HEADER.SizeOfImage:return
  r=u.reg_read(UC_ARM64_REG_PC)-self.n.base;off=at-self.n.base
  if r==0xcb72cc:
   assert off==0x16a3118 and z==4 and value==len(self.counter_values)+1<=15
   self.counter_values.append(value)
  elif r==0xcbae2c:assert (off,z,value)==(0x16a3240,8,self.handle)
  elif r==0xcc077c:assert self.allocs and (off,z,value)==(0x16a2a90,8,self.allocs[0][0])
  elif r==0xcc07a0:assert (off,z,value)==(0x16a2e90,4,64)
  elif r==0xcb329c:assert self.preset==0 and (off,z,value)==(0x16a2a50,4,512)
  elif r==0xcb32b0:assert len(self.allocs)==2 and (off,z,value)==(0x16a2a58,8,self.allocs[1][0])
  elif r==0xcb3350:assert off in [0x1607060+88*k+24 for k in range(3)] and z==4 and value==0xfffffffe
  else:raise AssertionError(('unexpected original image store',hex(r),hex(off),z))
  self.source_image_stores[(r,off,z)]+=1
 def check_memory(self,stage):
  expected_image=bytearray(self.image_before)
  if stage>=1:struct.pack_into('<I',expected_image,0x16a3118,15)
  if stage>=2:struct.pack_into('<Q',expected_image,0x16a3240,self.handle)
  arena=bytearray(self.arena_before)
  if stage>=3:
   assert self.allocs and self.allocs[0][1]==4608
   a=self.allocs[0][0];record=bytearray(72);struct.pack_into('<Q',record,40,2**64-1);record[58:61]=b'\n\n\n'
   payload=record*64;arena[a-self.own:a-self.own+4608]=payload
   struct.pack_into('<Q',expected_image,0x16a2a90,a);struct.pack_into('<I',expected_image,0x16a2e90,64)
  if stage>=4:
   assert len(self.allocs)==2 and self.allocs[1][1]==8*self.capacity
   a=self.allocs[1][0];vector=bytearray(8*self.capacity)
   for k in range(3):struct.pack_into('<Q',vector,8*k,self.stream(k))
   arena[a-self.own:a-self.own+len(vector)]=vector
   struct.pack_into('<I',expected_image,0x16a2a50,self.capacity);struct.pack_into('<Q',expected_image,0x16a2a58,a)
   for k in range(3):
    struct.pack_into('<I',expected_image,0x1607060+88*k+24,0xfffffffe)
    stream=bytearray(88);struct.pack_into('<II',stream,20,8193 if k==0 else 8194,0xfffffffe)
    assert bytes(self.u.mem_read(self.stream(k),88))==stream,'independent whole88byte static stream object'
  assert bytes(self.u.mem_read(self.n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))==expected_image,'independent complete mapped-image delta'
  assert bytes(self.u.mem_read(self.own,self.extent))==arena,'independent complete owned-arena delta'
  assert bytes(self.u.mem_read(self.n.heap,0x30000))==self.heap_before,'unexpected native heap change'
  assert all(self.u.mem_read(a-32,32)==b'\xa5'*32 and self.u.mem_read(a+size,32)==b'\xa5'*32 for a,size in self.allocs)
  expected_locks=set(self.global_mutex(k) for k in range(15)) if stage>=1 else set()
  if stage>=3:expected_locks.update(self.allocs[0][0]+72*k for k in range(64))
  if stage>=4:expected_locks.update(self.stream(k)+48 for k in range(3))
  assert self.lock_objects==expected_locks and not any(self.depths.values()),'owned lock set or balance'
 def run(self):
  returns=[]
  for stage,(entry,expected) in enumerate(ENTRIES,1):
   value=self.invoke(entry);assert value==expected,('original entry result',hex(entry),value)
   self.check_memory(stage);returns.append({'entry_RVA':hex(entry),'return_W0':value})
  before_allocs=self.allocs.copy();before_events=self.api_events.copy()
  assert self.invoke(0xcc06f0)==0;self.check_memory(4)
  assert self.allocs==before_allocs and self.api_events['HeapAlloc']==before_events['HeapAlloc']
  assert self.api_events['InitializeCriticalSectionEx']==before_events['InitializeCriticalSectionEx']
  assert dict(self.api_events)=={'InitializeCriticalSectionEx':82,'GetProcessHeap':1,'EnterCriticalSection':2,'HeapAlloc':2,'LeaveCriticalSection':2}
  expected={(0xcb72cc,0x16a3118,4):15,(0xcbae2c,0x16a3240,8):1,
   (0xcc077c,0x16a2a90,8):1,(0xcc07a0,0x16a2e90,4):1,(0xcb32b0,0x16a2a58,8):1,
   **{(0xcb3350,0x1607060+88*k+24,4):1 for k in range(3)}}
  if self.preset==0:expected[(0xcb329c,0x16a2a50,4)]=1
  assert self.source_image_stores==collections.Counter(expected)
  assert self.counter_values==list(range(1,16))
  # These invalid OS requests must be rejected before any memory/resource/event mutation.
  invalid=[('HeapAlloc',[self.handle+16,8,128],0xcb7630),
   ('InitializeCriticalSectionEx',[self.global_mutex(0),4000,0],0xcb72b8),
   ('LeaveCriticalSection',[self.global_mutex(7),0,0],0xcc0790)]
  rejected=0
  for name,args,ret in invalid:
   events=self.api_events.copy();locks=self.lock_objects.copy();allocs=self.allocs.copy()
   try:self.os_contract(name,args,ret)
   except AssertionError:rejected+=1
   else:raise AssertionError('invalid ownership request accepted')
   assert self.api_events==events and self.lock_objects==locks and self.allocs==allocs
   self.check_memory(4)
  return {'requested_placement_bias':self.bias,'actual_heap_handle_owned_offset':self.handle-self.own,
   'owned_preset_stream_capacity':self.preset,'actual_source_stream_capacity':self.capacity,
   'original_entry_returns':returns,'original_existing_index0_lookup_return':0,'new_allocations_bytes':[size for a,size in self.allocs],
   'independent_whole_mapped_image_and_arena_deltas':True,'independent_complete72byte_records':64,
   'independent_complete88byte_stream_objects':3,'independent_entire_pointer_vector':True,
   'original_initialized_mutexes':82,'original_source_image_store_chunks':sum(self.source_image_stores.values()),
   'OS_contract_events':dict(self.api_events),'balanced_existing_index0_lookup':True,
   'rejected_invalid_OS_ownership_requests':rejected,'opaque_OS_mutex_bytes_and_Windows_concurrency_proven':False}
def main():
 facts,imports=authority();cases=[]
 for preset in [0,128]:
  for bias in [0,1,40,1230]:
   b=Bootstrap(bias,preset,imports);row=b.run();cases.append(row)
   print(json.dumps({'completed_owned_CRT_bootstrap_bias':bias,'preset_capacity_fixture':preset,'source_capacity':row['actual_source_stream_capacity'],'owned_locks':82}),flush=True)
 result={'status':'PASS_BOUNDED_ORIGINAL_CRT_OBJECT_PRODUCERS','experiment':'E011CM',
  'base_commit':'4ffe0b6185e19ad7b0cab319cfb728d3d37085ab','authority':facts,'cases':cases,
  'case_count':len(cases),'default_capacity_cases':4,'owned_nondefault_capacity_cases':4,
  'complete_original_entry_returns':4*len(cases),'original_existing_table_lookup_returns':len(cases),
  'independent_complete72byte_records':64*len(cases),'independent_complete88byte_static_stream_objects':3*len(cases),
  'original_OS_mutex_initializer_calls':82*len(cases),'original_guarded_heap_allocations':2*len(cases),
  'original_OS_lock_enters':2*len(cases),'original_OS_lock_leaves':2*len(cases),
  'rejected_invalid_OS_ownership_requests':3*len(cases),'CRT_global16A2A50_is_32bit_count_not_pointer':True,
  'CRT_count_pointer_and_indexed_object_producers_qualified':True,'source_CRT_lock16A3000_initializer_included':True,
  'complete_CRT_environment_qualified':False,'CRT_bootstrap_integrated_with_outer_entry':False,
  'whole_outer_return_qualified':False,'final_output_publication_qualified':False,
  'actual_live_Default_producers_qualified':False,'actual_OS_locale_or_standard_handle_producers_qualified':False,
  'opaque_singlethread_OS_contracts_not_live_Windows_proof':True,'new_numeric_or_TLS_success_stub':False,
  'new_logger16A4228_classification_admitted':False,'native_rear_runtime_allowed':False,
  'new_camera_Starts':0,'new_reboots':0,'runtime_or_image_test':False,'next_experiment':'E011CN'}
 assert len(cases)==8 and sum(row['original_source_image_store_chunks'] for row in cases)==180
 (OUT/'BOOTSTRAP-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))}),flush=True)
if __name__=='__main__':main()
