#!/usr/bin/env python3
"""Bounded unchanged CRT slot/thread producer with original OS getters/setter and owned OS adapters."""
from pathlib import Path
import importlib.util,json,hashlib,struct,collections,pefile
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ,UC_PROT_READ,UC_PROT_WRITE,UC_PROT_EXEC
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
OUT=Path(__file__).resolve().parent
PRIVATE=ROOT.parent/'private/E011CV-explore'
CO_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011co-original-api-resolver/source-private.py'
CO_PIN='e5f06f34b4701d9a9344959f6417290941116cf2d8e77ea527702be0de3e45a5'
assert hashlib.sha256(CO_PATH.read_bytes()).hexdigest()==CO_PIN
spec=importlib.util.spec_from_file_location('cv_co',CO_PATH);CO=importlib.util.module_from_spec(spec);spec.loader.exec_module(CO)
AUTH_PATH=PRIVATE/'CODE-AUTHORITY-SAFE.json'
assert hashlib.sha256(AUTH_PATH.read_bytes()).hexdigest()=='594dff35131664dd54b2b630677930c92486fad34c9b5ab83679f6955794c62b'
AUTH=json.loads(AUTH_PATH.read_text())
SCHEDULE=[('LoadLibraryExW',0xcb9c14),('GetProcAddress',0xcb9d58),('EnterCriticalSection',0xcb9c94),('VirtualProtect',0xcb9cbc),('VirtualProtect',0xcb9cf0),('LeaveCriticalSection',0xcb9cfc),('FlsAlloc',0xcb4334),('FlsGetValue2',0xcb4210),('GetLastError',0xcb3fa8),('FlsSetValue',0xcb3fbc),('HeapAlloc',0xcb7630),('FlsSetValue',0xcb400c),('EnterCriticalSection',0xcb3c24),('LeaveCriticalSection',0xcb3c3c),('EnterCriticalSection',0xcb3cfc),('LeaveCriticalSection',0xcb3d18),('SetLastError',0xcb404c)]
def digest(x):return hashlib.sha256(x).hexdigest()
def pinned(path,pin):
 raw=path.read_bytes();assert digest(raw)==pin;return pefile.PE(data=raw)
def reg(u,name):
 if name in ('xzr','wzr'):return 0
 name={'fp':'x29','lr':'x30'}.get(name,name)
 return u.reg_read(globals()['UC_ARM64_REG_'+name.upper()])
def verify_catalog():
 p=CO.CF.p
 schema=pinned(PRIVATE/'API-set-schema.dll',AUTH['APIset_schema_sha256'])
 section=next(s for s in schema.sections if s.Name.rstrip(b'\0')==b'.apiset')
 blob=schema.get_data(section.VirtualAddress,section.Misc_VirtualSize)
 assert len(blob)>=28
 version,size,flags,count,offset,hashoffset,factor=struct.unpack_from('<7I',blob)
 assert version==6 and 28<=size<=len(blob) and count==984 and offset+24*count<=size
 def text(at,z):
  assert z%2==0 and at+z<=size;return blob[at:at+z].decode('utf-16-le')
 requested=p.get_data(0xf8c610,60)
 assert digest(requested)==AUTH['module_UTF16_SHA256'] and requested[-2:]==bytes(2)
 contract=requested[:-2].decode('utf-16-le').lower().removesuffix('.dll')
 matches=[]
 for k in range(count):
  flags,at,z,hashed,valoffset,valcount=struct.unpack_from('<6I',blob,offset+24*k)
  assert hashed<=z and valcount<100 and valoffset+20*valcount<=size
  if text(at,z).lower()!=contract:continue
  defaults=[]
  for j in range(valcount):
   vf,alias,aliaslen,host,hostlen=struct.unpack_from('<5I',blob,valoffset+20*j)
   text(alias,aliaslen);name=text(host,hostlen)
   if aliaslen==0:defaults.append(name)
  assert len(defaults)==1;matches.extend(defaults)
 assert len(matches)==1
 host=pinned(PRIVATE/'API-set-host-module.dll',AUTH['host_SHA256'])
 assert host.get_string_at_rva(host.DIRECTORY_ENTRY_EXPORT.struct.Name).decode('ascii').lower()==matches[0].lower()
 requested_api=p.get_data(0xf8cbc0,13)
 assert digest(requested_api)==AUTH['API_name_SHA256'] and requested_api[-1:]==b'\0'
 exports=[e for e in host.DIRECTORY_ENTRY_EXPORT.symbols if e.name==requested_api[:-1]]
 assert len(exports)==1 and exports[0].address==0x624562 and exports[0].forwarder
 module,name=exports[0].forwarder.split(b'.',1)
 nt=pinned(ROOT.parent/'private/E011CR-explore/ntdll.dll',AUTH['NTDLL_SHA256'])
 assert nt.get_string_at_rva(nt.DIRECTORY_ENTRY_EXPORT.struct.Name).lower()==module.lower()+b'.dll'
 resolved=[e for e in nt.DIRECTORY_ENTRY_EXPORT.symbols if e.name==name]
 assert len(resolved)==1 and not resolved[0].forwarder and resolved[0].address==0x185670
 return {'schema_version':version,'namespace_entry_count':count,'exact_contract_default_host_matches':1,'exact_requested_export_matches':1,'catalog_forward_to_NTDLL_RVA':'0x185670','actual_Windows_loader_execution':False}
class Case:
 def __init__(self,bias,slot,error,initial):
  assert slot in (1,16,37,63) and error in (0,3) and initial in (2,4)
  self.bias=bias;self.slot=slot;self.error=error;self.initial=initial
  self.b=CO.StandaloneBootstrap(bias,0,CO.CN.CRT_IMPORTS);self.b.run();self.b.runtime=True
  self.n=self.b.n;self.u=self.n.u;self.p=CO.CF.p;self.c=CO.CF.c;u=self.u;n=self.n;b=self.b
  self.kb=pinned(PRIVATE/'API-set-host-module.dll',AUTH['host_SHA256'])
  self.nt=pinned(ROOT.parent/'private/E011CR-explore/ntdll.dll',AUTH['NTDLL_SHA256'])
  assert digest((PRIVATE/'API-set-schema.dll').read_bytes())==AUTH['APIset_schema_sha256']
  assert self.p.get_dword_at_rva(0x1607168)==0xffffffff
  self.api=0x93010000;self.nb=0xb0000000;self.db=0xa0000000
  self.teb=0x96000000;self.data=0x96100000;self.slab=0x96200000
  self.handle=self.api+0x800+((bias+15)&~15)
  assert self.handle+16<self.api+4096
  self.thread=b.next_alloc
  self.chunk=(slot+16).bit_length()-3;self.index=slot+17-(1<<(self.chunk+2))
  assert 0<self.chunk<8 and 0<self.index<64
  self.registry={};self.protection=initial;self.pending={};self.calls=[];self.trace=[];self.os_trace=[]
  self.write_count=0;self.negative_count=0;self.native=None;self.exclusive_status=None;self.step=0;self.phase='initializer'
  self.instructions={}
  for row in AUTH['source_authority']:
   at=int(row['RVA'],16);size=row['bytes'];raw=self.p.get_data(at,size);assert digest(raw)==row['sha256']
   for i in self.c.disasm(raw,n.base+at):self.instructions[i.address]=(i,self.p,n.base,'OEM')
  u.mem_map(self.api,4096,UC_PROT_READ|UC_PROT_EXEC)
  names=['LoadLibraryExW','GetProcAddress','VirtualProtect','EnterCriticalSection','LeaveCriticalSection','FlsAlloc','FlsSetValue','HeapAlloc']
  self.adapters={self.api+32*k:name for k,name in enumerate(names)}
  for at,name in self.adapters.items():u.mem_write(n.base+CO.IMPORTS[name],struct.pack('<Q',at))
  for at in (self.teb,self.data,self.slab):u.mem_map(at,8192)
  u.mem_write(self.teb+0x68,struct.pack('<I',error))
  u.mem_map(self.nb+0x38d000,4096,UC_PROT_READ);u.mem_write(self.nb+0x38ddd8,bytes(4))
  self.entries={};self.native_pages=[]
  for name,pe,base,rva,length in [('FlsGetValue2',self.nt,self.nb,0x185670,128),('GetLastError',self.kb,self.db,0x1c7150,8),('SetLastError',self.nt,self.nb,0x166fc0,128)]:
   first=(base+rva)&~4095;last=(base+rva+length+4095)&~4095
   u.mem_map(first,last-first,UC_PROT_READ|UC_PROT_EXEC);u.mem_write(base+rva,pe.get_data(rva,length))
   self.native_pages.append((name,first,last-first))
   self.entries[base+rva]=name
   for i in self.c.disasm(pe.get_data(rva,length),base+rva):self.instructions[i.address]=(i,pe,base,name)
  for name in ['GetLastError','SetLastError']:u.mem_write(n.base+CO.IMPORTS[name],struct.pack('<Q',next(at for at,v in self.entries.items() if v==name)))
  self.getter=next(at for at,v in self.entries.items() if v=='FlsGetValue2')
  u.mem_protect(n.base+CO.CACHE_RVA,4096,UC_PROT_READ|(UC_PROT_WRITE if initial==4 else 0))
  self.regions=[('image',n.base,self.p.OPTIONAL_HEADER.SizeOfImage),('CRT',b.own,b.extent),('stack',n.stack,65536),('native_heap',n.heap,0x30000),('API',self.api,4096),('TEB',self.teb,8192),('FLS_data',self.data,8192),('FLS_slab',self.slab,8192),('NT_diagnostic',self.nb+0x38d000,4096)]+[(name+'_code',at,z) for name,at,z in self.native_pages]
  for k in range(30):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0x1100+k if k>=19 else 0)
  u.reg_write(UC_ARM64_REG_X18,self.teb);u.mem_write(n.stack,bytes(65536))
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  self.saved={k:u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(19,30)}
  self.saved[18]=self.teb
  self.before=self.snapshot();self.stack_model=bytearray(self.before['stack'])
  self.image_model=bytearray(self.before['image']);self.crt_model=bytearray(self.before['CRT'])
  self.image_stores={(n.base+0x1607b00,4):0x80000000,(n.base+0x16a3188,8):self.handle,(n.base+0x1b60018,8):self.getter,(n.base+0x16a2a80,1):1,(n.base+0x1607168,4):slot,(n.base+0x1607650,4):1}
  assert struct.unpack('<I',self.before['image'][0x1607650:0x1607654])[0]==0
  for (at,z),v in self.image_stores.items():self.image_model[at-n.base:at-n.base+z]=v.to_bytes(z,'little')
  thread=bytearray(968)
  self.fields={0:(8,n.base+0xf8b860),40:(4,1),136:(8,n.base+0x1607650),144:(8,0),188:(2,67),450:(2,67),928:(8,0),936:(4,1)}
  for off,(z,v) in self.fields.items():thread[off:off+z]=v.to_bytes(z,'little')
  self.crt_model[self.thread-b.own:self.thread-b.own+968]=thread
  self.depths=b.depths.copy();self.allocs=b.allocs.copy();self.events=b.api_events.copy()
  self.permissions=self.pages()
  u.hook_add(UC_HOOK_CODE,self.code);u.hook_add(UC_HOOK_MEM_WRITE,self.memory);u.hook_add(UC_HOOK_MEM_READ,self.read)
 def snapshot(self):return {name:bytes(self.u.mem_read(at,z)) for name,at,z in self.regions}
 def pages(self):return {at:perm for first,last,perm in self.u.mem_regions() for at in range(first,last+1,4096)}
 def current_args(self):return [self.u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(4)]
 def contract(self,name,args,ret):
  u=self.u;n=self.n;b=self.b;step=self.step
  if self.phase=='published_getter':assert name=='FlsGetValue2' and ret==n.end-n.base and args[0]==self.slot and self.registry[self.slot]==self.thread;return [0]
  assert step<len(SCHEDULE) and (name,ret)==SCHEDULE[step]
  if name=='LoadLibraryExW':
   assert args[:3]==[n.base+0xf8c610,0,2048] and digest(bytes(u.mem_read(args[0],60)))==AUTH['module_UTF16_SHA256'];return [0,1,2]
  if name=='GetProcAddress':
   assert args[:2]==[self.handle,n.base+0xf8cbc0] and digest(bytes(u.mem_read(args[1],13)))==AUTH['API_name_SHA256'];return [0,1]
  if name=='VirtualProtect':
   assert args[:3]==[n.base+CO.CACHE_RVA,256,4 if step==3 else 2]
   assert args[3]%4==0 and n.stack<=args[3] and args[3]+4<=n.stack+65536 and b.depths[b.global_mutex(14)]==1
   assert args[3]==u.reg_read(UC_ARM64_REG_SP)+16
   assert self.protection==(self.initial if step==3 else 4);return [0,1,2,3]
  if name in ('EnterCriticalSection','LeaveCriticalSection'):
   k=14 if step in (2,5) else 5 if step in (12,13) else 4
   assert args[0]==b.global_mutex(k) and args[0] in b.lock_objects
   assert b.depths[args[0]]==(0 if name=='EnterCriticalSection' else 1);return [0]
  if name=='FlsAlloc':assert args[0]==n.base+0xcb3e60 and not self.registry;return [0]
  if name=='FlsGetValue2':assert args[0]==self.slot and self.registry[self.slot] is None and bytes(u.mem_read(self.teb+0x17c8,8))==bytes(8);return [0]
  if name=='GetLastError':assert struct.unpack('<I',u.mem_read(self.teb+0x68,4))[0]==self.error;return []
  if name=='FlsSetValue':
   expect=0xffffffffffffffff if step==9 else self.thread
   prior=None if step==9 else 0xffffffffffffffff
   assert args[:2]==[self.slot,expect] and self.registry[self.slot]==prior
   assert step==9 or b.allocs==self.allocs+[(self.thread,968)];return [0,1]
  if name=='HeapAlloc':
   assert args[:3]==[b.handle,8,968] and self.registry[self.slot]==0xffffffffffffffff and b.next_alloc==self.thread
   assert bytes(u.mem_read(self.thread-32,1032))==b'\xa5'*1032;return [0,1,2]
  assert name=='SetLastError' and args[0]==self.error and self.registry[self.slot]==self.thread
  assert struct.unpack('<I',u.mem_read(self.teb+0x68,4))[0]==0;return [0]
 def negatives(self,name,args,ret,indices):
  requests=[(name,args,ret+4),('UnknownAPI',args,ret)]
  for k in indices:
   a=args.copy();a[k]+=1;requests.append((name,a,ret))
  before=self.snapshot();state=(self.step,self.registry.copy(),self.b.depths.copy(),self.b.allocs.copy(),self.b.next_alloc,self.protection,self.pages())
  for request in requests:
   try:self.contract(*request)
   except AssertionError:pass
   else:raise AssertionError(('invalid ownership admitted',name))
  assert self.snapshot()==before
  assert state==(self.step,self.registry.copy(),self.b.depths.copy(),self.b.allocs.copy(),self.b.next_alloc,self.protection,self.pages())
  self.negative_count+=len(requests)
 def adapter(self,name,args,ret):
  u=self.u;n=self.n;b=self.b
  if name=='LoadLibraryExW':value=self.handle
  elif name=='GetProcAddress':value=self.getter
  elif name=='VirtualProtect':
   at=args[3]-n.stack;self.stack_model[at:at+4]=struct.pack('<I',self.protection)
   u.mem_write(args[3],struct.pack('<I',self.protection));self.protection=args[2]
   u.mem_protect(args[0],4096,UC_PROT_READ|(UC_PROT_WRITE if args[2]==4 else 0));value=1
  elif name in ('EnterCriticalSection','LeaveCriticalSection'):
   b.depths[args[0]]=1 if name=='EnterCriticalSection' else 0;value=args[0]
  elif name=='FlsAlloc':self.registry[self.slot]=None;value=self.slot
  elif name=='HeapAlloc':
   u.mem_write(self.thread,bytes(968));b.allocs.append((self.thread,968));b.next_alloc=(self.thread+968+64+4095)&~4095;value=self.thread
  else:
   assert name=='FlsSetValue';self.registry[self.slot]=args[1]
   u.mem_write(self.teb+0x17c8,struct.pack('<Q',self.data));u.mem_write(self.data+8*self.chunk,struct.pack('<Q',self.slab))
   u.mem_write(self.slab+8*self.index,struct.pack('<Q',args[1]));u.mem_write(self.teb+0x68,bytes(4));value=1
  self.calls.append({'API':name,'return_RVA':hex(ret),'effect':'strict owned OS adapter'});self.step+=1
  u.reg_write(UC_ARM64_REG_X0,value);u.reg_write(UC_ARM64_REG_PC,n.base+ret)
 def code(self,u,pc,z,user):
  assert not self.pending
  if self.exclusive_status:
   assert reg(u,self.exclusive_status)==0;self.exclusive_status=None
  if self.native and pc==self.native['return']:
   name=self.native['API'];value=u.reg_read(UC_ARM64_REG_X0)
   if name=='FlsGetValue2':assert value==0
   if name=='GetLastError':assert value==self.error
   assert struct.unpack('<I',u.mem_read(self.teb+0x68,4))[0]==self.error
   self.calls.append({'API':name,'return_RVA':hex(pc-self.n.base),'effect':'unchanged original OS instructions','actual_return_X0':value})
   self.native=None;self.step+=1
  if pc in self.adapters or pc in self.entries:
   name=self.adapters.get(pc,self.entries.get(pc));args=self.current_args();ret=u.reg_read(UC_ARM64_REG_LR)-self.n.base
   indices=self.contract(name,args,ret);self.negatives(name,args,ret,indices)
   if pc in self.adapters:self.adapter(name,args,ret);return
   assert self.native is None;self.native={'API':name,'return':self.n.base+ret}
  assert pc in self.instructions,('unqualified instruction',hex(pc))
  i,pe,base,component=self.instructions[pc]
  assert bytes(u.mem_read(pc,4))==pe.get_data(pc-base,4)
  if component=='OEM':self.trace.append(pc-base)
  else:assert self.native and self.native['API']==component;self.os_trace.append((component,pc-base))
  self.pending_pc=pc
  if i.mnemonic.startswith(('stp','str','stur','stlxr')):
   mem=next(op.mem for op in i.operands if op.type==3);assert not mem.index
   at=reg(u,self.c.reg_name(mem.base))+mem.disp;name=self.c.reg_name(i.operands[1 if i.mnemonic=='stlxr' else 0].reg)
   width=2 if i.mnemonic.endswith('h') else 1 if i.mnemonic.endswith('b') else 16 if name.startswith('q') else 8 if name in ('fp','lr') or name.startswith(('x','d')) else 4
   operands=i.operands[:2] if i.mnemonic=='stp' else i.operands[1:2] if i.mnemonic=='stlxr' else i.operands[:1]
   if i.mnemonic=='stlxr':self.exclusive_status=self.c.reg_name(i.operands[0].reg)
   for k,op in enumerate(operands):
    address=at+k*width;value=reg(u,self.c.reg_name(op.reg))&((1<<(8*width))-1)
    if self.n.stack<=address and address+width<=self.n.stack+65536:
     off=address-self.n.stack;self.stack_model[off:off+width]=value.to_bytes(width,'little')
    elif self.n.base<=address<self.n.base+self.p.OPTIONAL_HEADER.SizeOfImage:
     assert (address,width) in self.image_stores and value==self.image_stores[address,width]
    elif self.thread<=address<self.thread+968:
     off=address-self.thread;assert off in self.fields and self.fields[off]==(width,value)
    else:assert component=='SetLastError' and (address,width,value)==(self.teb+0x68,4,self.error)
    for j in range(0,width,8):size=min(width-j,8);self.pending[address+j,size]=(value>>(8*j))&((1<<(8*size))-1)
 def memory(self,u,access,at,z,value,user):
  assert u.reg_read(UC_ARM64_REG_PC)==self.pending_pc and (at,z) in self.pending, ('unexpected store',hex(u.reg_read(UC_ARM64_REG_PC)-self.n.base),hex(at),z,list(self.pending))
  assert value&((1<<(8*z))-1)==self.pending.pop((at,z));self.write_count+=1
 def read(self,u,access,at,z,value,user):
  if self.native is None:return
  name=self.native['API']
  if name=='GetLastError':allowed={(self.teb+0x68,4)}
  elif name=='SetLastError':allowed={(self.nb+0x38ddd8,4),(self.nb+0x38dddc,1),(self.teb+0x68,4)}
  else:allowed={(self.teb+0x17c8,8),(self.data+8*self.chunk,8),(self.slab+8*self.index,8)}
  assert (at,z) in allowed,('unowned native OS read',name,hex(at),z)
 def run(self):
  u=self.u;n=self.n;b=self.b
  u.emu_start(n.base+0xcb4310,n.end,count=10000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end and u.reg_read(UC_ARM64_REG_W0)==1 and not self.native and self.step==17
  assert not self.pending and u.reg_read(UC_ARM64_REG_SP)==n.stack+0xf000
  assert all(u.reg_read(globals()['UC_ARM64_REG_X'+str(k)])==v for k,v in self.saved.items())
  self.phase='published_getter';u.reg_write(UC_ARM64_REG_W0,self.slot);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(self.getter,n.end,count=100)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end and u.reg_read(UC_ARM64_REG_X0)==self.thread
  assert self.native and self.native['API']=='FlsGetValue2';self.native=None
  after=self.snapshot()
  assert after['stack']==self.stack_model and after['image']==self.image_model and after['CRT']==self.crt_model
  teb=bytearray(self.before['TEB']);teb[0x17c8:0x17d0]=struct.pack('<Q',self.data)
  data=bytearray(8192);data[8*self.chunk:8*self.chunk+8]=struct.pack('<Q',self.slab)
  slab=bytearray(8192);slab[8*self.index:8*self.index+8]=struct.pack('<Q',self.thread)
  assert after['TEB']==teb and after['FLS_data']==data and after['FLS_slab']==slab
  assert all(after[k]==v for k,v in self.before.items() if k not in ('stack','image','CRT','TEB','FLS_data','FLS_slab'))
  assert b.depths==self.depths and b.allocs==self.allocs+[(self.thread,968)] and b.api_events==self.events
  assert b.next_alloc==(self.thread+968+64+4095)&~4095
  pages=self.permissions.copy();pages[n.base+CO.CACHE_RVA]=UC_PROT_READ;assert self.pages()==pages
  assert self.protection==2 and self.registry=={self.slot:self.thread} and len(self.trace)==421
  counts=dict(collections.Counter(name for name,rva in self.os_trace))
  assert counts['FlsGetValue2']==27 and counts['GetLastError']==2
  assert struct.unpack('<I',after['TEB'][0x68:0x6c])[0]==self.error
  return {'placement_bias':self.bias,'fresh_slot_owned_fixture':self.slot,'initial_thread_error_fixture':self.error,'initial_cache_page_protection':self.initial,'original_initializer_return_W0':1,'original_OEM_instructions':len(self.trace),'original_OS_instruction_counts':counts,'original_exact_store_chunks':self.write_count,'invalid_API_requests_rejected_before_effect':self.negative_count,'API_schedule':self.calls,'whole_stack_image_CRT_TEB_FLS_models_match':True,'all_other_entire_regions_unchanged':True,'actual_permissions_match':True,'original_callback_registered_RVA':'0xcb3e60','thread_allocation_bytes':968,'callee_saved_registers_and_SP_restored':True,'all_locks_balanced':True,'original_published_getter_returns_exact_968_byte_owner':True,'original_error_restore_preserves_input':True}
def main():
 CO.authority();catalog=verify_catalog()
 cases=[]
 for args in [(0,1,0,2),(1,16,3,4),(40,37,3,2),(1230,63,3,4)]:
  row=Case(*args).run();cases.append(row);print(json.dumps({k:v for k,v in row.items() if k!='API_schedule'}),flush=True)
 result={'experiment':'E011CV','status':'PASS_BOUNDED_ORIGINAL_SLOT_AND_THREAD_PRODUCER','base_commit':'7beff0ccd479aea0e1b978b6c8123a32d721b909','evidence_class':'UNCHANGED_ORIGINAL_OEM_AND_OS_SOURCE_IN_EXPLICIT_OWNED_SINGLE_THREAD_FIXTURES','catalog_authority':catalog,'cases':cases,'original_OEM_instructions':sum(c['original_OEM_instructions'] for c in cases),'original_exact_store_chunks':sum(c['original_exact_store_chunks'] for c in cases),'invalid_API_requests_rejected_before_effect':sum(c['invalid_API_requests_rejected_before_effect'] for c in cases),'source_authority':AUTH['source_authority'],'original_CFE600_qualified':False,'live_Windows_loader_startup_TLS_locale_concurrency_qualified':False,'original_Windows_FlsAlloc_or_FlsSetValue_executed':False,'FLS_byte_layout_producer':'explicit minimal owned representation for original getter, not full OS structures','diagnostic_global':'NTDLL38DDD8 DWORD and38DDDC BYTE virtual-zero fixtures, actual Windows value unobserved','callback_invoked_or_qualified':False,'original_cleanup_and_outer_return_qualified':False,'native_rear_runtime_allowed':False,'new_camera_Starts':0,'new_reboots':0,'new_Linux_image_tests':0,'next_experiment':'E011CW'}
 (OUT/'SLOT-THREAD-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(list,dict))}),flush=True)
if __name__=='__main__':main()
