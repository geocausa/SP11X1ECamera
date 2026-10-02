#!/usr/bin/env python3
"""Bounded original API resolution; private SP11 catalog, explicit owned OS contracts."""
from pathlib import Path
import importlib.util,json,hashlib,struct,collections,pefile
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_PROT_READ,UC_PROT_WRITE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
OUT=Path(__file__).resolve().parent
PRIVATE=ROOT.parent/'private/E011CO-explore'
CN_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011cn-crt-startup-integration/source-private.py'
CN_PIN='afd8c03466f2de1b8064b7bfa02e22789685568ebcea727fd7855f888e9c1966'
assert hashlib.sha256(CN_PATH.read_bytes()).hexdigest()==CN_PIN
spec=importlib.util.spec_from_file_location('co_cn',CN_PATH);CN=importlib.util.module_from_spec(spec);spec.loader.exec_module(CN)
CF=CN.CF;N=CN.CM.N
MODULE_RVA=0xf8caa8;NAME_RVA=0xf8cb70;CACHE_RVA=0x1b60000;MODULE_CACHE_RVA=0x16a3210
CATALOG_PIN='6a7bd4daff9c0c4cc8b9478ecd9828c3f19be257a4a18db9559cae929197fffa'
MODULE_PIN='f13bc601140315bf38eb1acc78fd1e70b10c343142db1ddadc9488f30cd1103f'
NAME_PIN='3b9feef1c63ed1907dddfd087ee57e5702fd263bcda0da6b89eeb128f38619a9'
IMPORTS=None;FACTS=None
def authority():
 global IMPORTS,FACTS,MODULE_BYTES,NAME_BYTES,CATALOG
 inherited,camera_imports=CN.authority();p=CF.p;c=CF.c
 MODULE_BYTES=p.get_data(MODULE_RVA,18);NAME_BYTES=p.get_data(NAME_RVA,16)
 assert hashlib.sha256(MODULE_BYTES).hexdigest()==MODULE_PIN and MODULE_BYTES[-2:]==bytes(2)
 assert hashlib.sha256(NAME_BYTES).hexdigest()==NAME_PIN and NAME_BYTES[-1:]==bytes(1)
 raw=(PRIVATE/'requested-module.dll').read_bytes();assert len(raw)==1472296 and hashlib.sha256(raw).hexdigest()==CATALOG_PIN
 CATALOG=pefile.PE(data=raw);CATALOG.parse_data_directories();assert CATALOG.FILE_HEADER.Machine==0xaa64
 exports={e.name:e for e in CATALOG.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
 assert len(exports)==1691 and NAME_BYTES[:-1] in exports
 entry=exports[NAME_BYTES[:-1]]
 assert entry.ordinal==38 and entry.address==0x70a90 and not entry.forwarder
 assert any(sec.VirtualAddress<=entry.address<sec.VirtualAddress+sec.Misc_VirtualSize and sec.Characteristics&0x20000000 for sec in CATALOG.sections)
 assert MODULE_BYTES[:-2].decode('utf-16-le').casefold().removesuffix('.dll')==CATALOG.DIRECTORY_ENTRY_EXPORT.name.decode().casefold().removesuffix('.dll')
 IMPORTS={i.name.decode():i.address-p.OPTIONAL_HEADER.ImageBase for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
 assert {k:IMPORTS[k] for k in ['LoadLibraryExW','GetProcAddress','VirtualProtect','EnterCriticalSection','LeaveCriticalSection']}=={
  'LoadLibraryExW':0xf7e310,'GetProcAddress':0xf7e270,'VirtualProtect':0xf7e308,'EnterCriticalSection':0xf7e0b8,'LeaveCriticalSection':0xf7e0c0}
 pins={0xcb9b88:(480,'458b7c049c564986bee3304bec76e749bb69aa4ff0a5f41610c2d565792bdb31'),
       0xcb9f68:(96,'bcccce70775ee06c49deff53f1ebd475a949e303992537b81bc6a0d5bf113a73')}
 for a,(z,pin) in pins.items():assert hashlib.sha256(p.get_data(a,z)).hexdigest()==pin
 assert next(c.disasm(p.get_data(0xcb9fa0,4),0xcb9fa0)).operands[0].imm==0xcb9b88
 assert next(c.disasm(p.get_data(0xcb9fb0,4),0xcb9fb0)).mnemonic=='blr'
 assert p.get_data(CACHE_RVA,256)==bytes(256)
 module_section=next(s for s in p.sections if s.VirtualAddress<=MODULE_CACHE_RVA<s.VirtualAddress+s.Misc_VirtualSize)
 assert MODULE_CACHE_RVA>=module_section.VirtualAddress+module_section.SizeOfRawData and MODULE_CACHE_RVA+8<=module_section.VirtualAddress+module_section.Misc_VirtualSize
 section=next(s for s in p.sections if s.VirtualAddress<=CACHE_RVA<s.VirtualAddress+s.Misc_VirtualSize)
 assert section.Characteristics&0x80000000
 FACTS={'inherited_CN_verifier_sha256':CN_PIN,'OEM_DLL_sha256':inherited['OEM_DLL_sha256'] if 'OEM_DLL_sha256' in inherited else 'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35',
  'source_module_name':{'RVA':hex(MODULE_RVA),'bytes':18,'sha256':MODULE_PIN},
  'source_API_name':{'RVA':hex(NAME_RVA),'bytes':16,'sha256':NAME_PIN,'role':'file_encoding_policy'},
  'same_SP11_OS_catalog':{'sha256':CATALOG_PIN,'bytes':len(raw),'machine':43620,'named_exports':1691,'selected_export_ordinal':38,'selected_export_RVA':'0x70a90','forwarded':False},
  'original_source_ranges':{hex(a):{'bytes':z,'sha256':pin} for a,(z,pin) in pins.items()},
  'module_cache_RVA':hex(MODULE_CACHE_RVA),'API_cache_RVA':hex(CACHE_RVA),'protection_request_bytes':256,'physical_page_bytes':4096,
  'initial_source_PE_cache_section_writable':True,'final_source_requested_protection':2,
  'resolver_global_lock_RVA':'0x16a30f0','resolver_global_lock_index':14}
 return FACTS,camera_imports
class Resolver:
 def __init__(self,n,b,bias=0,adapter_index=0,initial_protection=4,install_locks=True):
  self.n=n;self.u=n.u;self.b=b;self.own=0x94000000;self.extent=0x10000
  self.handle=self.own+0x100+bias;self.adapter=self.own+0x2000+adapter_index*64
  self.u.mem_map(self.own,self.extent);self.owned_expected=bytearray(b'\xa5'*self.extent)
  self.owned_expected[self.handle-self.own:self.handle-self.own+32]=bytes(32)
  self.u.mem_write(self.own,bytes(self.owned_expected))
  names=['LoadLibraryExW','GetProcAddress','VirtualProtect']
  if install_locks:names+=['EnterCriticalSection','LeaveCriticalSection']
  self.sentinels={self.own+0x1000+32*k:name for k,name in enumerate(names)}
  for at,name in self.sentinels.items():self.u.mem_write(n.base+IMPORTS[name],struct.pack('<Q',at))
  self.protection=initial_protection;assert initial_protection in [2,4]
  self.u.mem_protect(n.base+CACHE_RVA,4096,UC_PROT_READ|(UC_PROT_WRITE if initial_protection==4 else 0))
  self.active=False
  type(self.u).hook_add(self.u,UC_HOOK_CODE,self.code)
  type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.memory)
 def begin(self,warm=False):
  assert not self.active and self.b.depths[self.b.global_mutex(14)]==0
  self.warm=warm;self.before=bytes(self.u.mem_read(self.n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))
  self.heap_before=bytes(self.u.mem_read(self.n.heap,0x30000));self.crt_before=bytes(self.u.mem_read(self.b.own,self.b.extent))
  self.depths_before=self.b.depths.copy();self.events=collections.Counter();self.stores=collections.Counter();self.old_protections=[];self.returned=0;self.boundary=0
  self.flag_before=struct.unpack_from('<I',self.before,0x1607b00)[0];assert self.flag_before in [0,0x80000000]
  for at,val in [(MODULE_CACHE_RVA,self.handle),(CACHE_RVA,self.adapter)]:
   assert struct.unpack_from('<Q',self.before,at)[0]==(val if warm else 0)
  self.active=True
 def load_module(self,args,ret):
  assert not self.warm and ret==0xcb9c14 and args==[self.n.base+MODULE_RVA,0,2048]
  assert bytes(self.u.mem_read(args[0],18))==MODULE_BYTES
  return self.handle
 def resolve_export(self,args,ret):
  assert not self.warm and ret==0xcb9d58 and args[:2]==[self.handle,self.n.base+NAME_RVA]
  assert bytes(self.u.mem_read(args[1],16))==NAME_BYTES
  assert NAME_BYTES[:-1] in {e.name for e in CATALOG.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
  return self.adapter
 def protect(self,args,oldptr,ret):
  at,size,new=args
  assert not self.warm and at==self.n.base+CACHE_RVA and size==256
  assert (ret,new)==[(0xcb9cbc,4),(0xcb9cf0,2)][len(self.old_protections)]
  assert self.n.stack<=oldptr and oldptr+4<=self.n.stack+0x10000
  assert self.b.depths[self.b.global_mutex(14)]==1
  before=bytes(self.u.mem_read(self.n.stack,0x10000));old=self.protection
  self.u.mem_protect(at,4096,UC_PROT_READ|(UC_PROT_WRITE if new==4 else 0))
  self.u.mem_write(oldptr,struct.pack('<I',old));expected=bytearray(before);struct.pack_into('<I',expected,oldptr-self.n.stack,old)
  assert bytes(self.u.mem_read(self.n.stack,0x10000))==expected
  self.protection=new;self.old_protections.append(old)
  return 1
 def mutex(self,name,receiver,ret):
  assert not self.warm and receiver==self.b.global_mutex(14) and receiver in self.b.lock_objects
  assert (name,ret) in [('EnterCriticalSection',0xcb9c94),('LeaveCriticalSection',0xcb9cfc)]
  if name=='EnterCriticalSection':assert self.b.depths[receiver]==0;self.b.depths[receiver]=1
  else:assert self.b.depths[receiver]==1;self.b.depths[receiver]=0
  self.events[name]+=1
 def code(self,u,pc,z,user):
  if not self.active:return
  assert pc!=self.n.base+0xcfe600,'original TLS remains unqualified'
  if pc==self.n.base+0xcb9fa4:
   assert not self.warm and u.reg_read(UC_ARM64_REG_X0)==self.adapter
   self.returned+=1
  if pc==self.adapter:
   assert u.reg_read(UC_ARM64_REG_LR)-self.n.base==0xcb9fb4
   self.boundary+=1;u.emu_stop();return
  if pc not in self.sentinels:return
  name=self.sentinels[pc];ret=u.reg_read(UC_ARM64_REG_LR)-self.n.base
  args=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(3)]
  if name=='LoadLibraryExW':value=self.load_module(args,ret)
  elif name=='GetProcAddress':value=self.resolve_export(args,ret)
  elif name=='VirtualProtect':value=self.protect(args,u.reg_read(UC_ARM64_REG_X3),ret)
  else:self.mutex(name,args[0],ret);value=args[0]
  if name not in ['EnterCriticalSection','LeaveCriticalSection']:self.events[name]+=1
  u.reg_write(UC_ARM64_REG_X0,value);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
 def memory(self,u,access,at,z,value,user):
  if not self.active:return
  if self.n.stack<=at and at+z<=self.n.stack+0x10000:return
  r=u.reg_read(UC_ARM64_REG_PC)-self.n.base
  schema={(0x132c,self.n.base+MODULE_CACHE_RVA,8):self.handle,(0x132c,self.n.base+CACHE_RVA,8):self.adapter}
  if self.flag_before==0:
   schema.update({(site,self.n.base+0x1607b00,4):0x80000000 for site in [0x13f8,0x1420]})
  key=(r,at,z)
  assert not self.warm and key in schema and value==schema[key],('unexpected resolver store',hex(r),z)
  if at==self.n.base+CACHE_RVA:assert self.protection==4 and self.b.depths[self.b.global_mutex(14)]==1
  self.stores[key]+=1
 def expected_image(self,image):
  expected=bytearray(image);struct.pack_into('<I',expected,0x1607b00,0x80000000)
  struct.pack_into('<Q',expected,MODULE_CACHE_RVA,self.handle);struct.pack_into('<Q',expected,CACHE_RVA,self.adapter)
  return bytes(expected)
 def check(self):
  self.active=False
  assert self.u.reg_read(UC_ARM64_REG_PC)==self.adapter and self.boundary==1 and self.returned==(0 if self.warm else 1)
  assert self.events==(collections.Counter() if self.warm else collections.Counter({'LoadLibraryExW':1,'GetProcAddress':1,'VirtualProtect':2,'EnterCriticalSection':1,'LeaveCriticalSection':1}))
  expected_stores=collections.Counter()
  if not self.warm:
   expected_stores.update({(0x132c,self.n.base+MODULE_CACHE_RVA,8):1,(0x132c,self.n.base+CACHE_RVA,8):1})
   if self.flag_before==0:expected_stores.update({(site,self.n.base+0x1607b00,4):1 for site in [0x13f8,0x1420]})
  assert self.stores==expected_stores
  assert self.protection==2 and (not self.old_protections if self.warm else self.old_protections in [[2,4],[4,4]])
  perms=next(perms for low,high,perms in self.u.mem_regions() if low<=self.n.base+CACHE_RVA<=high)
  assert perms==UC_PROT_READ
  assert bytes(self.u.mem_read(self.n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))==self.expected_image(self.before)
  assert bytes(self.u.mem_read(self.own,self.extent))==self.owned_expected
  assert bytes(self.u.mem_read(self.n.heap,0x30000))==self.heap_before and bytes(self.u.mem_read(self.b.own,self.b.extent))==self.crt_before
  assert self.b.depths==self.depths_before
  return {'cold':not self.warm,'complete_original_resolver_returns':self.returned,'original_API_call_boundary_stops':self.boundary,
   'owned_OS_contract_calls':dict(self.events),'exact_image_store_chunks':sum(self.stores.values()),
   'old_protection_scalars':self.old_protections,'final_page_read_only':True,'complete_independent_image_and_owned_arenas':True,
   'CRT_lock_balanced':True,'resolved_API_executed':False,'whole_wrapper_return_qualified':False}
 def negatives(self):
  before=bytes(self.u.mem_read(self.n.base,CF.p.OPTIONAL_HEADER.SizeOfImage));own=bytes(self.u.mem_read(self.own,self.extent))
  depths=self.b.depths.copy();protection=self.protection;old=self.old_protections.copy();events=self.events.copy();warm=self.warm
  self.warm=False;self.old_protections=[]
  requests=[
   lambda:self.load_module([self.n.base+MODULE_RVA,0,0],0xcb9c14),
   lambda:self.resolve_export([self.handle+8,self.n.base+NAME_RVA,0],0xcb9d58),
   lambda:self.resolve_export([self.handle,self.n.base+NAME_RVA+1,0],0xcb9d58),
   lambda:self.protect([self.own,256,4],self.n.stack+0x100,0xcb9cbc),
   lambda:self.protect([self.n.base+CACHE_RVA,256,4],self.own,0xcb9cbc),
   lambda:self.mutex('EnterCriticalSection',self.b.global_mutex(8),0xcb9c94)]
  for request in requests:
   try:request()
   except (AssertionError,IndexError):pass
   else:raise AssertionError('invalid OS ownership admitted')
  assert bytes(self.u.mem_read(self.n.base,len(before)))==before and bytes(self.u.mem_read(self.own,self.extent))==own
  assert self.b.depths==depths and self.protection==protection and self.old_protections==[] and self.events==events
  self.warm=warm;self.old_protections=old
  return len(requests)
class StandaloneBootstrap(CN.CM.Bootstrap):
 runtime=False
 def code(self,u,pc,z,user):
  if not self.runtime:return super().code(u,pc,z,user)
  assert pc!=self.n.base+0xcfe600
 def memory(self,u,access,at,z,value,user):
  if not self.runtime:return super().memory(u,access,at,z,value,user)
def standalone(bias,index,initial):
 b=StandaloneBootstrap(bias,0,CN.CRT_IMPORTS);b.run();b.runtime=True
 r=Resolver(b.n,b,bias,index,initial)
 rows=[]
 for warm in [False,True]:
  r.begin(warm)
  for k in range(29):r.u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0)
  r.u.reg_write(UC_ARM64_REG_SP,b.n.stack+0xf000);r.u.reg_write(UC_ARM64_REG_LR,b.n.end)
  r.u.emu_start(b.n.base+0xcb9f68,b.n.end,count=250000)
  rows.append(r.check())
 print(json.dumps({'completed_resolver_cold_cached_bias':bias,'initial_protection':initial}),flush=True)
 return {'owned_handle_placement_bias':bias,'initial_protection_owned_fixture':initial,'cold_and_cached':rows,'rejected_OS_ownership_requests':r.negatives()}
def attach(n):
 b=CN.attach(n);r=Resolver(n,b,install_locks=False);b.co=r
 original=b.runtime_mutex
 def mutex(name,receiver,ret):
  if r.active:r.mutex(name,receiver,ret)
  else:original(name,receiver,ret)
 b.runtime_mutex=mutex
 return b
class Startup(CN.Startup):
 def invoke_entry(self):
  super().invoke_entry()
  assert self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+CN.STOP
  arena=bytes(self.u.mem_read(self.f.arena,self.f.arena_size));inner=bytes(self.u.mem_read(self.inner,606264));outer=bytes(self.u.mem_read(self.outer,72))
  allocs=self.f.allocs.copy();released=self.f.released.copy()
  r=self.crt.co;r.begin()
  try:self.u.emu_start(self.n.base+CN.STOP,self.n.end,count=500000)
  finally:r.active=False
  detail=r.check()
  assert bytes(self.u.mem_read(self.f.arena,self.f.arena_size))==arena and bytes(self.u.mem_read(self.inner,606264))==inner and bytes(self.u.mem_read(self.outer,72))==outer
  assert self.f.allocs==allocs and self.f.released==released and self.f.readq(self.output)==0
  assert self.f.readq(self.inner+40)==self.manager and self.f.readq(self.inner+91952)==self.mode_configuration
  assert self.crt.depths[self.crt.new_stream+48]==1
  detail.update({'camera_arena_inner_outer_unchanged_after_CN':True,'public_output_zero':True,'camera_and_stream_locks_still_held':True,
   'rejected_OS_ownership_requests':r.negatives()})
  self.co_detail=detail
  CO_CASES.append(detail)
CO_CASES=[]
def integrated(blob,pin,camera_imports):
 source=CN.source
 old='enumerate(zip([0,1,40,1230],[1,2,5,8]))';assert source.count(old)==1;source=source.replace(old,'enumerate(zip([0],[1]))')
 old="assert bytes(u.mem_read(n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))==expected_image,'unexpected integrated CRT image delta'"
 new="assert bytes(u.mem_read(n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))==b.co.expected_image(expected_image),'unexpected integrated resolver image delta'"
 assert source.count(old)==1;source=source.replace(old,new)
 namespace={};exec(source,dict(CN.ns2['source'].__globals__,Startup=Startup,attach=attach),namespace)
 CO_CASES.clear();CN.CASE_FACTS.clear()
 row=namespace['source'](blob,pin,camera_imports)
 assert len(row['cases'])==len(CO_CASES)==len(CN.CASE_FACTS)==1
 row['cases'][0].update(CN.CASE_FACTS[0]);row['cases'][0].update(CO_CASES[0])
 row['cases'][0]['unmodeled_LoadLibraryExW_not_executed']=False
 return row
def main():
 facts,camera_imports=authority()
 isolated=[standalone(bias,k,initial) for k,(bias,initial) in enumerate([(0,4),(1,2),(40,4),(1230,2)])]
 sources=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  sources.append(integrated(blob,pin,camera_imports))
 cold=[x['cold_and_cached'][0] for x in isolated]+[x['cases'][0] for x in sources]
 cached=[x['cold_and_cached'][1] for x in isolated]
 result={'experiment':'E011CO','status':'PASS_BOUNDED_ORIGINAL_API_RESOLUTION','base_commit':'dd6467aaa2c2e3c28953192e716f08560eddd133',
  'authority':facts,'isolated_cases':isolated,'sources':sources,
  'isolated_cold_cases':4,'isolated_cached_cases':4,'integrated_cold_camera_cases':3,'integrated_camera_placements_per_source':1,
  'complete_original_resolver_returns':sum(x['complete_original_resolver_returns'] for x in cold),
  'original_resolved_API_boundary_stops':sum(x['original_API_call_boundary_stops'] for x in cold+cached),
  'exact_resolver_image_store_chunks':sum(x['exact_image_store_chunks'] for x in cold+cached),
  'rejected_OS_ownership_requests':sum(x['rejected_OS_ownership_requests'] for x in isolated)+sum(x['cases'][0]['rejected_OS_ownership_requests'] for x in sources),
  'owned_module_loads':7,'owned_export_lookups':7,'owned_protection_changes':14,'balanced_CRT_lock_pairs':7,
  'integrated_statistics_records':sum(x['cases'][0]['independent_152byte_records'] for x in sources),
  'original_resolved_API_executed':False,'native_Windows_loader_or_API_qualified':False,
  'source_PE_writable_and_explicit_owned_readonly_initial_states_covered':True,
  'whole_original_wrapper_return_qualified':False,'whole_outer_return_qualified':False,'final_output_publication_qualified':False,
  'native_rear_runtime_allowed':False,'new_numeric_or_TLS_success_stub':False,'new_logger16A4228_admitted':False,
  'new_camera_Starts':0,'new_reboots':0,'runtime_or_image_test':False,'next_experiment':'E011CP'}
 assert result['complete_original_resolver_returns']==7 and result['original_resolved_API_boundary_stops']==11 and result['exact_resolver_image_store_chunks']==22
 assert result['rejected_OS_ownership_requests']==42 and result['integrated_statistics_records']==45
 (OUT/'RESOLVER-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))}),flush=True)
if __name__=='__main__':main()
