#!/usr/bin/env python3
"""Original Windows conversion code in guarded Unicorn fixtures; no native DLL calls."""
from pathlib import Path
import importlib.util,hashlib,json,struct,collections,pefile
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ,UC_PROT_READ,UC_PROT_WRITE,UC_PROT_EXEC
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
BASE='0ba6f3ca5d4f2438ea5d9c260785325844ad2c42'
CQ_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011cq-original-conversion-query/source-private.py'
CQ_PIN='b3c69f5a2acc5c70ed83fa6270ae62c10349d2c71e3fa5e324dacf3a696af2c8'
assert hashlib.sha256(CQ_PATH.read_bytes()).hexdigest()==CQ_PIN
s=importlib.util.spec_from_file_location('cr_cq',CQ_PATH);CQ=importlib.util.module_from_spec(s);s.loader.exec_module(CQ)
CP=CQ.CP;CF=CQ.CF
NT_PIN='60ef561645b50dce71ad0919dbbef3ad334a0489432cde718e75b73b558c7997'
BLOCKS=[["dependency",291200,312,"b1311c903dd0e51929dc846290eca854cc97254131979d33a5ec6fc11c6d26ba"],["dependency",291524,28,"84dd4ca705bcc811356afe41a9982cbacc459cb558f570e5e9c8add91ac3ed08"],["dependency",291568,52,"455a3f472ebaedbae822802c923f04641b22ed0331f29427eb1485bde61a319f"],["dependency",294104,92,"19f52be7ef671f32c0bb21277268bc7f0225f49887d9279eb6658738910f97f7"],["dependency",294828,20,"421ed650d9ee2e505610050d9463b407033c41be054509896a0e2db4cfc16982"],["dependency",295240,16,"8a2a55c5b688fad388cb082806ef0229448f4dea965b5f87e48c66e0f5c792ea"],["dependency",1644656,32,"2b15ee9ef725e6b8d082d6524f3237a3f8a93e8a28574f349345ea7a0b5998ce"],["dependency",1721248,12,"e481c907a537113983f708817563f135705cbdc801d146b91598736a72dc7f87"],["dependency",3161472,24,"bc5378b38232278957e82381391dcf42880070a300199e81c11ccf88f0da3fa1"],["ntdll",451208,1024,"997bbe79017f5427eb62c079a7e48b87a364893c5f2d117e297f0097cf884ef5"],["ntdll",452736,1024,"4fb20a55aba52532b10e9788f15122e7b0379555a3b43236cf077fcd3e0632d0"]]
DATA=[[6524928,8,"8b6c58e749b9dc0ee6ec7b4b027fb1c3c486b484e1f0c143369fab5b454074d4"],[6530208,4,"a59d78e73652bbb0eac1c7cf2825921cdb91ef930d76a00c5e98d8c3b74851de"],[6530212,4,"a59d78e73652bbb0eac1c7cf2825921cdb91ef930d76a00c5e98d8c3b74851de"]]
NT=None;CASES=[]
def authority():
 global NT
 inherited,camera=CQ.authority()
 raw=(ROOT.parent/'private/E011CR-explore/ntdll.dll').read_bytes();assert len(raw)==4359168 and hashlib.sha256(raw).hexdigest()==NT_PIN
 NT=pefile.PE(data=raw);NT.parse_data_directories();assert NT.FILE_HEADER.Machine==0xaa64
 e=next(e for e in NT.DIRECTORY_ENTRY_EXPORT.symbols if e.name==b'RtlUTF8ToUnicodeN');assert e.address==0x6e880 and not e.forwarder
 imp=next(i for d in CP.DEP.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.address-CP.DEP.OPTIONAL_HEADER.ImageBase==0x3182b8)
 assert imp.name==b'RtlUTF8ToUnicodeN'
 for role,a,z,pin in BLOCKS:assert hashlib.sha256((CP.DEP if role=='dependency' else NT).get_data(a,z)).hexdigest()==pin
 for a,z,pin in DATA:assert len(CP.DEP.get_data(a,z))==z and hashlib.sha256(CP.DEP.get_data(a,z)).hexdigest()==pin
 assert all(int.from_bytes(CP.DEP.get_data(a,4),'little')==65001 for a in [0x63a4a0,0x63a4a4])
 for a in [0x640578,0x640588]:
  assert CP.DEP.get_data(a,8)==b''
  section=next(sec for sec in CP.DEP.sections if sec.VirtualAddress<=a and a+8<=sec.VirtualAddress+sec.Misc_VirtualSize)
  assert a-section.VirtualAddress>=section.SizeOfRawData
 return {'inherited_CQ_verifier_sha256':CQ_PIN,'NTDLL_sha256':NT_PIN,'NTDLL_bytes':4359168,'blocks':BLOCKS,'source_data':DATA,
  'file_image_ANSI_and_OEM_codepage_defaults':65001,'explicit_zero_virtual_cache_cells':['0x640578','0x640588'],
  'original_UTF8_conversion_export_RVA':'0x6e880','dependency_UTF8_import_RVA':'0x3182b8',
  'contract_reference':'https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-multibytetowidechar',
  'file_image_defaults_and_zero_caches_are_owned_fixture_not_live_Windows_state':True},camera
class API:
 def __init__(self,n,b):
  self.n=n;self.b=b;self.u=n.u;self.p=b.policy;self.db=self.p.db;self.nb=0xb0000000;self.active=False
  self.bases={'dependency':self.db,'ntdll':self.nb};self.instructions={}
  for role,a,z,pin in BLOCKS:
   base=self.bases[role]
   for page in range((base+a)&~4095,((base+a+z-1)&~4095)+4096,4096):self.page(page,UC_PROT_READ|UC_PROT_EXEC)
   self.put(base+a,(CP.DEP if role=='dependency' else NT).get_data(a,z))
   for i in CF.c.disasm((CP.DEP if role=='dependency' else NT).get_data(a,z),base+a):self.instructions[i.address]=i
  for a,z,pin in DATA:
   self.page((self.db+a)&~4095,UC_PROT_READ);self.put(self.db+a,CP.DEP.get_data(a,z))
  for a in [0x640578,0x640588]:self.page((self.db+a)&~4095,UC_PROT_READ);self.put(self.db+a,bytes(8))
  self.put(self.db+0x3182b8,struct.pack('<Q',self.nb+0x6e880))
  self.u.mem_write(n.base+0xf7e2e8,struct.pack('<Q',self.db+0x47180))
  self.p.check_pages()
  type(self.u).hook_add(self.u,UC_HOOK_CODE,self.code)
  type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.memory)
  type(self.u).hook_add(self.u,UC_HOOK_MEM_READ,self.read)
 def page(self,at,perm):
  if at in self.p.pages:return
  self.u.mem_map(at,4096);self.u.mem_write(at,b'\xa5'*4096);self.p.pages[at]=bytearray(b'\xa5'*4096)
  self.u.mem_protect(at,4096,perm);self.p.permissions[at]=perm
 def put(self,at,data):
  page=at&~4095;perm=self.p.permissions[page]
  self.u.mem_protect(page,4096,UC_PROT_READ|UC_PROT_WRITE)
  try:self.p.put(at,data)
  finally:self.u.mem_protect(page,4096,perm)
 def reg(self,name):
  name={'fp':'x29','lr':'x30','wzr':'zero','xzr':'zero'}.get(name,name)
  if name=='zero':return 0
  return self.u.reg_read(globals()['UC_ARM64_REG_'+name.upper()])
 def code(self,u,pc,z,user):
  if not self.active:return
  if pc==self.return_to:u.emu_stop();return
  if pc==self.n.base+0xcb8dd4:
   assert self.from_tail and not self.tail_seen and u.reg_read(UC_ARM64_REG_X8)==self.db+0x47180
   self.tail_seen=True;return
  assert pc in self.instructions,('unqualified original API code',hex(pc-self.db))
  assert not self.pending,'unobserved original API store'
  i=self.instructions[pc];self.counts[pc]+=1;self.pending={};self.pending_pc=pc
  if i.mnemonic.startswith(('stp','str','stur')):
   mem=next(op.mem for op in i.operands if op.type==3);at=self.reg(CF.c.reg_name(mem.base))+mem.disp
   assert not mem.index,'unqualified indexed store'
   width=2 if i.mnemonic.endswith('h') else 1 if i.mnemonic.endswith('b') else 8 if CF.c.reg_name(i.operands[0].reg) in ['fp','lr'] or CF.c.reg_name(i.operands[0].reg).startswith('x') else 4
   operands=i.operands[:2] if i.mnemonic=='stp' else i.operands[:1]
   for j,op in enumerate(operands):
    address=at+j*width;value=self.reg(CF.c.reg_name(op.reg))&((1<<(width*8))-1)
    assert self.n.stack<=address and address+width<=self.n.stack+0x10000 or getattr(self.b,'utf_output',0)<=address and address+width<=getattr(self.b,'utf_output',0)+getattr(self.b,'utf_bytes',0),'unowned API write'
    self.pending[(address,width)]=value
    if self.n.stack<=address<self.n.stack+0x10000:
     off=address-self.n.stack;self.stack_model[off:off+width]=value.to_bytes(width,'little')
    else:
     off=address-self.b.own;self.crt_model[off:off+width]=value.to_bytes(width,'little')
 def memory(self,u,access,at,z,value,user):
  if not self.active:return
  assert u.reg_read(UC_ARM64_REG_PC)==self.pending_pc and self.pending.get((at,z))==(value&((1<<(8*z))-1)) and (at,z) in self.pending,'unexpected original API write'
  self.writes[(u.reg_read(UC_ARM64_REG_PC),at,z)]+=1;del self.pending[(at,z)]
 def read(self,u,access,at,z,value,user):
  if not self.active:return
  allowed=[(self.n.stack,0x10000)]+[(self.db+a,z0) for a,z0 in [(0x639000,8),(0x63a4a0,4),(0x63a4a4,4),(0x640578,8),(0x640588,8),(0x3182b8,8)]]
  assert any(low<=at and at+z<=low+extent for low,extent in allowed),'unowned original API read'
  self.reads[(u.reg_read(UC_ARM64_REG_PC),at,z)]+=1
 def run(self,start,return_to,from_tail=False):
  u=self.u;n=self.n
  args=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(6)]
  assert args[0] in [0,1] and args[1]==9 and args[3]==0xffffffff
  assert n.stack<=args[2]<n.stack+0x10000
  data=bytes(u.mem_read(args[2],min(4096,n.stack+0x10000-args[2])));assert 0 in data;data=data[:data.index(0)+1]
  assert all(c<128 for c in data),'only independently qualified ASCII source path admitted'
  utf16=data.decode('utf-8').encode('utf-16-le');chars=len(utf16)//2
  if args[5]:
   assert args[5]>=chars,'insufficient qualified Unicode capacity'
   assert (n.stack<=args[4] and args[4]+2*args[5]<=n.stack+0x10000 or args[4]==getattr(self.b,'utf_output',None) and 2*args[5]==getattr(self.b,'utf_bytes',None)),'unowned Unicode output'
  else:assert args[4]==0
  before=bytes(u.mem_read(n.stack,0x10000));image=bytes(u.mem_read(n.base,CF.p.OPTIONAL_HEADER.SizeOfImage));crt=bytes(u.mem_read(self.b.own,self.b.extent));heap=bytes(u.mem_read(n.heap,0x30000))
  saved=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(19,30)];sp=u.reg_read(UC_ARM64_REG_SP)
  self.stack_model=bytearray(before);self.crt_model=bytearray(crt);self.return_to=return_to;self.from_tail=from_tail;self.tail_seen=False;self.pending={};self.counts=collections.Counter();self.writes=collections.Counter();self.reads=collections.Counter();self.active=True
  try:u.emu_start(start,n.end,count=100000)
  finally:self.active=False
  assert u.reg_read(UC_ARM64_REG_PC)==return_to and u.reg_read(UC_ARM64_REG_W0)==chars and u.reg_read(UC_ARM64_REG_SP)==sp
  assert [u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(19,30)]==saved
  assert bytes(u.mem_read(n.stack,0x10000))==self.stack_model,'independent original API entire stack mismatch'
  if args[5]:assert bytes(u.mem_read(args[4],len(utf16)))==utf16
  assert bytes(u.mem_read(args[2],len(data)))==data
  assert bytes(u.mem_read(n.base,len(image)))==image and bytes(u.mem_read(self.b.own,self.b.extent))==self.crt_model and bytes(u.mem_read(n.heap,0x30000))==heap
  self.p.check_pages()
  return {'source_codepage':args[0],'original_API_size_query':not bool(args[5]),'original_API_return_characters':chars,
   'input_bytes_including_NUL':len(data),'input_sha256':hashlib.sha256(data).hexdigest(),'UTF16_bytes':len(utf16),
   'original_API_instruction_count':sum(self.counts.values()),'original_API_write_chunks':sum(self.writes.values()),
   'original_NTDLL_entry_executed':self.counts[self.nb+0x6e880]==1,'independent_entire_stack_model':True,
   'independent_UTF8_UTF16_outcome':True,'callee_saved_registers_and_SP_restored':True,'entire_owned_pages_and_permissions_match':True,
   'original_size_or_conversion_result_stub':False}
OLD_BOOT_CODE=CP.CO.CN.Bootstrap.code
def boot_code(b,u,pc,z,user):
 if getattr(b,'conversion_active',False) and pc in b.sentinels and b.sentinels[pc]=='HeapAlloc':
  args=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(3)]
  assert u.reg_read(UC_ARM64_REG_LR)==b.n.base+0xcb1700 and args==[b.handle,0,b.utf_bytes] and not b.utf_output
  at=b.next_alloc;assert at%16==0 and at+b.utf_bytes+32<b.own+b.extent
  assert bytes(u.mem_read(at-32,b.utf_bytes+64))==b'\xa5'*(b.utf_bytes+64)
  b.utf_output=at;b.allocs.append((at,b.utf_bytes));b.next_alloc=(at+b.utf_bytes+64+4095)&~4095
  b.api_events['HeapAlloc']+=1;u.reg_write(UC_ARM64_REG_X0,at);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR));return
 return OLD_BOOT_CODE(b,u,pc,z,user)
CP.CO.CN.Bootstrap.code=boot_code
OLD_ATTACH=CP.attach
def attach(n):
 b=OLD_ATTACH(n);b.api=API(n,b);return b
CP.attach=attach
CRT_RANGES=[[13334408,200,"2e468b618fe52e29ec5fa9a6d97f76101bcb66e72b3e40b22e587ffdc5de948a"],[13309632,160,"09f99d3304aa9c5c7eabc84fcfa8a7beac0c893d9e7f17999a2da8e0ecf83b22"]]
CRT_EXTRA=["0xcb8d88","0xcb8d8c","0xcb8d90","0xcb8d94","0xcb8d98","0xcb8d9c","0xcb8da0","0xcb8da4","0xcb8da8","0xcb8dac","0xcb8db0","0xcb8dc0","0xcb8dc4","0xcb8dcc","0xcb8dd0","0xcb8dd4"]
class Tail:
 def __init__(self,o,first):
  self.o=o;self.b=o.crt;self.n=o.n;self.u=o.u;self.api=self.b.api;self.first=first;self.active=False;self.pending={};self.instructions={}
  for a,z,pin in CRT_RANGES:
   assert hashlib.sha256(CF.p.get_data(a,z)).hexdigest()==pin
   for i in CF.c.disasm(CF.p.get_data(a,z),self.n.base+a):self.instructions[i.address]=i
  for rva in CRT_EXTRA:
   a=int(rva,16);i=next(CF.c.disasm(CF.p.get_data(a,4),self.n.base+a));self.instructions[i.address]=i
  type(self.u).hook_add(self.u,UC_HOOK_CODE,self.code);type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.memory)
 def code(self,u,pc,z,user):
  if not self.active:return
  if pc in [self.n.base+0xcb8dd4,self.n.base+0xcfd4e8]:
   assert not self.pending;u.emu_stop();return
  if pc in self.b.sentinels:
   assert self.b.sentinels[pc]=='HeapAlloc' and self.b.utf_output and u.reg_read(UC_ARM64_REG_PC)==self.n.base+0xcb1700
   self.heap_calls+=1;return
  assert pc in self.instructions,('unqualified original CRT converter continuation',hex(pc-self.n.base))
  assert not self.pending
  i=self.instructions[pc];self.counts[pc]+=1;self.pending_pc=pc
  if i.mnemonic.startswith(('stp','str','stur')):
   mem=next(op.mem for op in i.operands if op.type==3);assert not mem.index
   at=self.api.reg(CF.c.reg_name(mem.base))+mem.disp
   width=2 if i.mnemonic.endswith('h') else 1 if i.mnemonic.endswith('b') else 8 if CF.c.reg_name(i.operands[0].reg) in ['fp','lr'] or CF.c.reg_name(i.operands[0].reg).startswith('x') else 4
   operands=i.operands[:2] if i.mnemonic=='stp' else i.operands[:1]
   for j,op in enumerate(operands):
    address=at+j*width;value=self.api.reg(CF.c.reg_name(op.reg))&((1<<(8*width))-1)
    assert self.n.stack<=address and address+width<=self.n.stack+0x10000
    self.pending[(address,width)]=value;off=address-self.n.stack;self.model[off:off+width]=value.to_bytes(width,'little')
    for role,base in [('caller_result',self.result_record),('caller_context',self.context)]:
     if base<=address<base+32:
      kind='owned_UTF16_pointer' if value==self.b.utf_output and value else 'zero' if value==0 else 'character_count' if value==self.first['original_API_return_characters'] else 'other_scalar_or_owned_pointer'
      self.receiver_stores.append({'site_RVA':hex(pc-self.n.base),'receiver':role,'offset':address-base,'bytes':width,'value_kind':kind})
 def memory(self,u,access,at,z,value,user):
  if not self.active:return
  assert u.reg_read(UC_ARM64_REG_PC)==self.pending_pc and (at,z) in self.pending and (value&((1<<(8*z))-1))==self.pending[(at,z)]
  self.writes[(u.reg_read(UC_ARM64_REG_PC),at,z)]+=1;del self.pending[(at,z)]
 def run(self):
  n=self.n;u=self.u;b=self.b;f=self.o.f
  cq=CQ.CASES[-1];self.result_record=n.stack+cq['converter_result_record_stack_offset'];self.context=n.stack+cq['converter_context_pointer_stack_offset']
  self.model=bytearray(self.api.stack_model);assert bytes(u.mem_read(n.stack,0x10000))==self.model
  original_crt=bytes(u.mem_read(b.own,b.extent));image=bytes(u.mem_read(n.base,CF.p.OPTIONAL_HEADER.SizeOfImage));heap=bytes(u.mem_read(n.heap,0x30000));arena=bytes(u.mem_read(f.arena,f.arena_size));serialized=bytes(u.mem_read(f.map,f.map_size))
  allocations=b.allocs.copy();depths=b.depths.copy();saved_registers={k:struct.unpack_from('<Q',self.model,n.stack+cq['source_converter_entry_SP_offset']+off-n.stack)[0] for k,off in [(19,-48),(20,-40),(21,-32),(22,-24),(23,-16),(24,-8),(29,-64),(30,-56)]};result_before=bytes(u.mem_read(self.result_record,32));self.receiver_stores=[];self.counts=collections.Counter();self.writes=collections.Counter();self.heap_calls=0
  b.conversion_active=True;b.utf_output=0;b.utf_bytes=2*self.first['original_API_return_characters']
  self.active=True
  try:u.emu_start(n.base+0xcb7788,n.end,count=10000)
  finally:self.active=False
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0xcb8dd4 and self.heap_calls==1 and b.allocs==allocations+[(b.utf_output,b.utf_bytes)]
  assert bytes(u.mem_read(n.stack,0x10000))==self.model and bytes(u.mem_read(b.own,b.extent))==original_crt
  args=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(6)]
  assert args==[int(CP.CP_MODE=='OEM'),9,n.stack+cq['source_filename_stack_offset'],0xffffffff,b.utf_output,self.first['original_API_return_characters']]
  assert u.reg_read(UC_ARM64_REG_LR)==n.base+0xcb7824
  second=self.api.run(n.base+0xcb8dd4,n.base+0xcb7824,True);self.model=bytearray(self.api.stack_model)
  self.active=True
  try:u.emu_start(n.base+0xcb7824,n.end,count=10000)
  finally:self.active=False;b.conversion_active=False
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0xcfd4e8 and u.reg_read(UC_ARM64_REG_W0)==0
  assert u.reg_read(UC_ARM64_REG_SP)==n.stack+cq['source_converter_entry_SP_offset']
  assert bytes(u.mem_read(n.stack,0x10000))==self.model
  assert all(u.reg_read(globals()['UC_ARM64_REG_X'+str(k)])==v for k,v in saved_registers.items())
  expected_record=bytearray(result_before);struct.pack_into('<QQ',expected_record,16,b.utf_output,self.first['original_API_return_characters'])
  assert bytes(u.mem_read(self.result_record,32))==expected_record,'independent entire caller result record'
  filename=bytes(u.mem_read(args[2],self.first['input_bytes_including_NUL']))
  wide=filename.decode('utf-8').encode('utf-16-le');expected=bytearray(original_crt);off=b.utf_output-b.own;expected[off:off+len(wide)]=wide
  assert len(wide)==b.utf_bytes and bytes(u.mem_read(b.own,b.extent))==expected
  assert bytes(u.mem_read(b.utf_output-32,32))==b'\xa5'*32 and bytes(u.mem_read(b.utf_output+b.utf_bytes,32))==b'\xa5'*32
  assert bytes(u.mem_read(n.base,len(image)))==image and bytes(u.mem_read(n.heap,0x30000))==heap and bytes(u.mem_read(f.arena,f.arena_size))==arena and bytes(u.mem_read(f.map,f.map_size))==serialized
  assert b.depths==depths and f.readq(self.o.output)==0;b.policy.check_pages()
  assert any(r['value_kind']=='owned_UTF16_pointer' for r in self.receiver_stores)
  return {'original_query':self.first,'original_conversion':second,'complete_original_converter_return_RVA':'0xcfd4e8',
   'original_converter_return_status_W0':0,'owned_UTF16_allocation_bytes':b.utf_bytes,'owned_HeapAlloc_flags':0,'original_malloc_heap_return_RVA':'0xcb1700',
   'qualified_owned_heap_allocations':1,'original_CRT_continuation_instruction_count':sum(self.counts.values()),
   'exact_original_CRT_continuation_store_chunks':sum(self.writes.values()),'derived_caller_receiver_stores':self.receiver_stores,
   'independent_entire_stack_and_CRT_output_models':True,'independent_entire32byte_caller_result_record':True,'original_converter_saved_registers_restored':True,'whole_other_regions_unchanged':True,
   'no_lock_depth_change':True,'public_output_zero':True,'full_CRT_file_open_or_outer_return_qualified':False,'rejected_heap_contract_requests':heap_negatives(b)}

class Startup(CQ.Startup):
 def invoke_entry(self):
  super().invoke_entry();u=self.u;n=self.n
  first=self.crt.api.run(n.base+0xcb8dd4,n.base+0xcb7788,True);CASES.append(Tail(self,first).run())
CQ.CP.Startup=Startup
def heap_negatives(b):
 u=b.u;n=b.n
 regs=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(31)];pc=u.reg_read(UC_ARM64_REG_PC);sp=u.reg_read(UC_ARM64_REG_SP)
 allocs=b.allocs.copy();events=b.api_events.copy();next_alloc=b.next_alloc;crt=bytes(u.mem_read(b.own,b.extent));stack=bytes(u.mem_read(n.stack,0x10000))
 sentinel=next(at for at,name in b.sentinels.items() if name=='HeapAlloc')
 b.conversion_active=True
 try:
  requests=[([b.handle+1,0,b.utf_bytes],n.base+0xcb1700),([b.handle,8,b.utf_bytes],n.base+0xcb1700),
   ([b.handle,0,b.utf_bytes+2],n.base+0xcb1700),([b.handle,0,b.utf_bytes],n.base+0xcb7630)]
  for args,ret in requests:
   for k,v in enumerate(args):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],v)
   u.reg_write(UC_ARM64_REG_LR,ret)
   try:boot_code(b,u,sentinel,4,None)
   except AssertionError:pass
   else:raise AssertionError('out-of-scope UTF16 allocation admitted')
 finally:
  b.conversion_active=False
  for k,v in enumerate(regs):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],v)
  u.reg_write(UC_ARM64_REG_PC,pc);u.reg_write(UC_ARM64_REG_SP,sp)
 assert b.allocs==allocs and b.api_events==events and b.next_alloc==next_alloc
 assert bytes(u.mem_read(b.own,b.extent))==crt and bytes(u.mem_read(n.stack,0x10000))==stack;b.policy.check_pages()
 return 4
def scope_negatives(a):
 u=a.u;n=a.n;p=a.p;b=a.b
 registers=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(31)];pc=u.reg_read(UC_ARM64_REG_PC);sp=u.reg_read(UC_ARM64_REG_SP)
 stack=bytes(u.mem_read(n.stack,0x10000));crt=bytes(u.mem_read(b.own,b.extent));image=bytes(u.mem_read(n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))
 counts=a.counts.copy();writes=a.writes.copy();reads=a.reads.copy();pending=a.pending.copy();pending_pc=a.pending_pc
 a.active=True;a.pending={(n.stack+0x4000,8):0x1234};a.pending_pc=a.db+0x47184;u.reg_write(UC_ARM64_REG_PC,a.pending_pc)
 try:
  requests=[lambda:a.memory(u,0,n.stack+0x4001,8,0x1234,None),
   lambda:a.memory(u,0,n.stack+0x4000,4,0x1234,None),
   lambda:a.memory(u,0,n.stack+0x4000,8,0x1235,None),
   lambda:a.read(u,0,n.heap,8,0,None),
   lambda:a.code(u,n.base+0xcfe600,4,None)]
  for request in requests:
   try:request()
   except AssertionError:pass
   else:raise AssertionError('out-of-scope Unicode operation admitted')
 finally:a.active=False;a.pending=pending;a.pending_pc=pending_pc;u.reg_write(UC_ARM64_REG_PC,pc)
 # Reject an unowned output before entering the original API.
 for k,v in enumerate([0,9,n.stack+0x1001,0xffffffff,n.heap,4096]):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],v)
 try:
  try:a.run(a.db+0x47180,n.end)
  except AssertionError as error:assert error.args==('unowned Unicode output',)
  else:raise AssertionError('unowned Unicode output admitted')
 finally:
  for k,v in enumerate(registers):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],v)
  u.reg_write(UC_ARM64_REG_PC,pc);u.reg_write(UC_ARM64_REG_SP,sp)
 assert a.counts==counts and a.writes==writes and a.reads==reads
 assert bytes(u.mem_read(n.stack,0x10000))==stack and bytes(u.mem_read(b.own,b.extent))==crt and bytes(u.mem_read(n.base,len(image)))==image;p.check_pages()
 return 6
def isolated():
 from types import SimpleNamespace
 from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);n=SimpleNamespace(u=u,base=0x180000000,stack=0x71000000,heap=0x70000000,end=0x71000100)
 u.mem_map(n.base,(CF.p.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);u.mem_write(n.base,CF.p.get_memory_mapped_image())
 for at,z in [(n.stack,0x10000),(n.heap,0x30000),(0x92000000,0x200000)]:u.mem_map(at,z);u.mem_write(at,b'\xa5'*z)
 b=SimpleNamespace(n=n,u=u,own=0x92000000,extent=0x200000)
 b.policy=CP.Policy(n,b);b.policy.produce('ANSI');a=API(n,b);rows=[]
 for cp in [0,1]:
  b.policy.produce('OEM' if cp else 'ANSI')
  for alignment in [0,1]:
   for length in [0,1,7,8,15,16,36,255]:
    data=bytes(33+k%90 for k in range(length))+b'\0'
    for output in [False,True]:
     u.mem_write(n.stack,b'\xa5'*0x10000);inp=n.stack+0x1000+alignment;out=n.stack+0x2000+alignment*2;u.mem_write(inp,data)
     for k in range(29):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0xa5a5000000000000+k)
     for k,v in enumerate([cp,9,inp,0xffffffff,out if output else 0,len(data) if output else 0]):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],v)
     u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
     row=a.run(a.db+0x47180,n.end);row.update({'synthetic_ASCII_bytes_excluding_NUL':length,'input_alignment_offset':alignment,'caller_input_fixture':True});rows.append(row)
 print(json.dumps({'isolated_original_API_returns':len(rows)}),flush=True)
 return rows,scope_negatives(a)
def main():
 facts,camera=authority();isolated_rows,isolated_negatives=isolated();sources=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  for mode in ['ANSI','OEM']:
   CP.CP_MODE=mode;CASES.clear();CQ.CASES.clear();row=CP.integrated(blob,pin,camera);assert len(CASES)==1
   row['cases'][0].update(CASES[0]);sources.append(row)
   print(json.dumps({'source_sha256':pin,'policy':mode,'original_converter_return':'0xcfd4e8','owned_UTF16_bytes':CASES[0]['owned_UTF16_allocation_bytes']}),flush=True)
 cases=[row['cases'][0] for row in sources]
 calls=isolated_rows+[c[role] for c in cases for role in ['original_query','original_conversion']]
 result={'experiment':'E011CR','status':'PASS_BOUNDED_ORIGINAL_UNICODE_CONVERSION','base_commit':BASE,'authority':facts,
  'isolated_API_calls':isolated_rows,'sources':sources,'isolated_original_API_returns':64,'integrated_camera_cases':6,'distinct_tuning_sources':3,
  'original_Windows_conversion_API_returns':len(calls),'original_NTDLL_conversion_entries':sum(c['original_NTDLL_entry_executed'] for c in calls),
  'complete_original_converter_returns':6,'qualified_owned_UTF16_heap_allocations':6,'qualified_UTF16_allocation_bytes_each':74,
  'integrated_original_API_instruction_count':sum(c[role]['original_API_instruction_count'] for c in cases for role in ['original_query','original_conversion']),
  'integrated_original_API_store_chunks':sum(c[role]['original_API_write_chunks'] for c in cases for role in ['original_query','original_conversion']),
  'integrated_original_CRT_continuation_instructions':sum(c['original_CRT_continuation_instruction_count'] for c in cases),
  'integrated_original_CRT_continuation_store_chunks':sum(c['exact_original_CRT_continuation_store_chunks'] for c in cases),
  'API_scope_rejections':isolated_negatives,'heap_contract_rejections':sum(c['rejected_heap_contract_requests'] for c in cases),'actual_Windows_default_codepage_locale_cookie_or_loader_qualified':False,
  'ASCII_conversion_in_file_image_UTF8_default_fixture_only':True,'original_size_or_conversion_result_stub':False,
  'explicit_owned_OS_heap_allocator_contract':True,'source_created_UTF16_owner_retained_at_stop':True,
  'native_Windows_DLL_execution':False,'whole_outer_return_qualified':False,'final_output_publication_qualified':False,
  'native_rear_runtime_allowed':False,'new_camera_Starts':0,'new_reboots':0,'runtime_or_image_test':False,'next_experiment':'E011CS'}
 assert len(isolated_rows)==64 and len(cases)==6 and len(calls)==76 and result['original_NTDLL_conversion_entries']==76
 assert all(c['owned_UTF16_allocation_bytes']==74 and c['original_converter_return_status_W0']==0 and c['independent_entire32byte_caller_result_record'] for c in cases)
 (OUT/'UNICODE-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))}),flush=True)
if __name__=='__main__':main()
