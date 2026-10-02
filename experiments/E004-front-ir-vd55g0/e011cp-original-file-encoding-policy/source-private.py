#!/usr/bin/env python3
from pathlib import Path
import subprocess,importlib.util,json,hashlib,struct,pefile,collections
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_PROT_READ,UC_PROT_WRITE,UC_PROT_EXEC
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
"""Execute pinned small OS policy routines only in owned Unicorn pages; never native."""
BASE='47b7301a26fe12609785ba8e65d7d550d2e7310a'
CO_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011co-original-api-resolver/source-private.py'
assert hashlib.sha256(CO_PATH.read_bytes()).hexdigest()=='e5f06f34b4701d9a9344959f6417290941116cf2d8e77ea527702be0de3e45a5'
s=importlib.util.spec_from_file_location('cp_co',CO_PATH);CO=importlib.util.module_from_spec(s);s.loader.exec_module(CO)
CN=CO.CN;CF=CO.CF
DEP_PIN='26be64c26bac33368a650372cb5fb1e3235f1bd7883471bd3291dbf6372ae274'
RANGES={('requested',0x70a90): (4,'f372e5e917383d81ceaa6232a613a4caf42aab8900460ab385e16218af2f481b'),('requested',0x6cc0c):(12,'1eca86da74e1770ff548898f9c21879fafbff4976198f9e9ba18cb1a4b00b138'),
 ('dependency',0x1e0910):(28,'c0c1b456d7fdcc1b7145cec97f60fdb93c5a0255e51d1d82b87a50e5aefd70d2'),
 ('dependency',0x185c50):(68,'79e44ee9dc5e1152caa22057154235695d424ffb0e82dc8acf6b080b93a46ed0'),
 ('dependency',0x185ca0):(68,'440adc724a1181188f23f39466c7b557952f26290f7f64aa09eec7891144adbe')}
SLOT=0x639880
SCHEMA={
 'ANSI':[(0x185c5c,0x6392b0,'import',0x317990),(0x185c6c,0x6392a8,'import',0x3182c8),(0x185c7c,SLOT,'address',0x2ce8b0),(0x185c8c,0x639878,'address',0x2cf3e0)],
 'OEM':[(0x185cac,0x6392b0,'import',0x317ff0),(0x185cbc,0x6392a8,'import',0x3182d8),(0x185ccc,SLOT,'address',0x2cf3d0),(0x185cdc,0x639878,'address',0x2cf3f0)]}
DEP=None;FACTS=None
def authority():
 global DEP,FACTS
 inherited,camera=CO.authority()
 raw=(CO.PRIVATE/'forwarder-module.dll').read_bytes();assert len(raw)==7185240 and hashlib.sha256(raw).hexdigest()==DEP_PIN
 DEP=pefile.PE(data=raw);DEP.parse_data_directories()
 imports={i.address-DEP.OPTIONAL_HEADER.ImageBase:(d,i) for d in DEP.DIRECTORY_ENTRY_IMPORT for i in d.imports}
 for role,schema in SCHEMA.items():
  for site,slot,kind,value in schema:
   if kind=='import':assert value in imports and imports[value][1].name
 names=[('query',CO.NAME_BYTES[:-1],0x1e0910),('ANSI',CO.NAME_BYTES[:-1].replace(b'AreFileApis',b'SetFileApisTo',1),0x185c50),('OEM',CO.NAME_BYTES[:-1].replace(b'AreFileApis',b'SetFileApisTo',1).replace(b'ANSI',b'OEM'),0x185ca0)]
 exports={e.name:e for e in DEP.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
 assert all(exports[name].address==a and not exports[name].forwarder for role,name,a in names)
 assert next(CF.c.disasm(CO.CATALOG.get_data(0x70a90,4),0x70a90)).operands[0].imm==0x6cc0c
 request_import=next((d,i) for d in CO.CATALOG.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.address-CO.CATALOG.OPTIONAL_HEADER.ImageBase==0xf8038)
 assert request_import[1].name==CO.NAME_BYTES[:-1] and request_import[0].dll.lower()==DEP.DIRECTORY_ENTRY_EXPORT.name.lower()
 consumer=CF.p.get_data(0xcfd49c,8)
 assert hashlib.sha256(consumer).hexdigest()=='ab4f4bb93cf6fb33af73e4c0d5cdad55ec0e101fcdb11fec2047a96003be5f55'
 first,branch=list(CF.c.disasm(consumer,0xcfd49c))
 assert first.mnemonic=='ldrb' and CF.c.reg_name(first.operands[0].reg)=='w8' and CF.c.reg_name(first.operands[-1].mem.base)=='sp' and first.operands[-1].mem.disp==48
 assert branch.mnemonic=='cbnz' and CF.c.reg_name(branch.operands[0].reg)=='w0' and branch.operands[-1].imm==0xcfd4c0
 hashes={}
 for (alias,a),(z,pin) in RANGES.items():
  q=CO.CATALOG if alias=='requested' else DEP
  actual=hashlib.sha256(q.get_data(a,z)).hexdigest();assert pin is None or pin==actual
  hashes[alias+':'+hex(a)]={'bytes':z,'sha256':actual}
 query=list(CF.c.disasm(DEP.get_data(0x1e0910,28),0x1e0910))
 assert [i.mnemonic for i in query]==['adrp','add','adrp','ldr','cmp','cset','ret'] and query[5].cc==1
 FACTS={'requested_module_sha256':CO.CATALOG_PIN,'dependency_module_sha256':DEP_PIN,'dependency_bytes':len(raw),
  'source_ranges':hashes,'selected_dependency_export_ordinal':82,'selected_dependency_export_RVA':'0x1e0910',
  'requested_module_query_IAT_RVA':'0xf8038','policy_qword_RVA':hex(SLOT),'query_ANSI_identity_RVA':'0x2ce8b0',
  'consumer_8byte_sha256':'ab4f4bb93cf6fb33af73e4c0d5cdad55ec0e101fcdb11fec2047a96003be5f55','ANSI_consumer_stop_RVA':'0xcfd4c0','OEM_consumer_stop_RVA':'0xcfd4a4',
  'setter_export_ordinals':{'ANSI':1633,'OEM':1634},'setter_store_schema':{mode:[{'site_RVA':hex(a),'slot_RVA':hex(slot),'value_kind':kind,'value_RVA':hex(value)} for a,slot,kind,value in schema] for mode,schema in SCHEMA.items()},
  'conversion_identity_imports':[{'IAT_RVA':hex(a),'name_sha256':hashlib.sha256(imports[a][1].name).hexdigest(),'name_bytes':len(imports[a][1].name)} for a in [0x317990,0x3182c8,0x317ff0,0x3182d8]]}
 return FACTS,camera
class Policy:
 def __init__(self,n,b,placement=0):
  self.n=n;self.b=b;self.u=n.u
  self.rb=0x98000000+placement*0x1000000;self.db=0xa0000000+placement*0x1000000;self.tb=0xa8000000+placement*0x10000
  self.entry=self.rb+0x70a90;self.pages={};self.permissions={};self.active=False;self.mode=None;self.wrapper_return=None;self.wrapper_entries=0
  for alias,base,page_offsets in [('requested',self.rb,[0x70000,0x6c000,0xf8000]),('dependency',self.db,[0x1e0000,0x185000,0x317000,0x318000,0x639000,0x2ce000,0x2cf000]),('tokens',self.tb,[0])]:
   for off in page_offsets:
    at=base+off;self.u.mem_map(at,4096);self.pages[at]=bytearray(b'\xa5'*4096);self.u.mem_write(at,bytes(self.pages[at]))
  for (alias,a),(z,pin) in RANGES.items():
   q=CO.CATALOG if alias=='requested' else DEP;base=self.rb if alias=='requested' else self.db
   self.put(base+a,q.get_data(a,z))
  self.tokens={a:self.tb+0x100+32*k for k,a in enumerate([0x317990,0x3182c8,0x317ff0,0x3182d8])}
  for cell,pointer in self.tokens.items():self.put(self.db+cell,struct.pack('<Q',pointer));self.put(pointer,bytes(32))
  self.put(self.rb+0xf8038,struct.pack('<Q',self.db+0x1e0910))
  for at in self.pages:
   perm=UC_PROT_READ|UC_PROT_WRITE if at==self.db+0x639000 else UC_PROT_READ
   if at in [self.rb+0x70000,self.rb+0x6c000,self.db+0x1e0000,self.db+0x185000,self.db+0x2ce000,self.db+0x2cf000]:perm=UC_PROT_READ|UC_PROT_EXEC
   self.u.mem_protect(at,4096,perm);self.permissions[at]=perm
  type(self.u).hook_add(self.u,UC_HOOK_CODE,self.code)
  type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.memory)
 def put(self,at,data):
  page=at&~4095;off=at-page;assert off+len(data)<=4096 and page in self.pages
  self.u.mem_write(at,data);self.pages[page][off:off+len(data)]=data
 def value(self,kind,a):return self.tokens[a] if kind=='import' else self.db+a
 def code(self,u,pc,z,user):
  if pc==self.n.base+0xcb9f68:
   self.wrapper_return=u.reg_read(UC_ARM64_REG_LR);self.wrapper_entries+=1
  if not self.active:return
  if self.phase in ['query','consumer'] and pc==self.return_to:u.emu_stop();return
  if self.phase=='consumer':
   assert pc in [self.n.base+0xcfd49c,self.n.base+0xcfd4a0]
   if pc==self.n.base+0xcfd4a0:assert u.reg_read(UC_ARM64_REG_W0)==self.expected_bool and u.reg_read(UC_ARM64_REG_W8)==self.consumer_input
   self.instructions[pc]+=1;return
  if self.phase=='producer':
   a,z=({'ANSI':(0x185c50,68),'OEM':(0x185ca0,68)})[self.target_mode]
   assert self.db+a<=pc<self.db+a+z and pc%4==0
  else:
   allowed={self.rb+0x70a90}|{self.rb+a for a in range(0x6cc0c,0x6cc18,4)}|{self.db+a for a in range(0x1e0910,0x1e092c,4)}|{self.n.base+a for a in range(0xcb9fb4,0xcb9fc8,4)}
   assert pc in allowed,('unqualified policy continuation',hex(pc-self.n.base))
   if pc==self.db+0x1e0928:
    assert u.reg_read(UC_ARM64_REG_W0)==self.expected_bool
    self.query_returns+=1
  self.instructions[pc]+=1
 def memory(self,u,access,at,z,value,user):
  if not self.active:return
  if self.phase!='producer':raise AssertionError('query/wrapper continuation wrote memory')
  pc=u.reg_read(UC_ARM64_REG_PC)-self.db
  expected={(site,self.db+slot,8):self.value(kind,v) for site,slot,kind,v in SCHEMA[self.target_mode]}
  key=(pc,at,z);assert key in expected and value==expected[key]
  self.stores[key]+=1
 def check_pages(self):
  assert all(bytes(self.u.mem_read(at,4096))==expected for at,expected in self.pages.items())
  for at,perm in self.permissions.items():assert next(p for low,high,p in self.u.mem_regions() if low<=at<=high)==perm
 def produce(self,mode):
  assert not self.active and mode in SCHEMA;self.phase='producer';self.target_mode=mode;self.active=True;self.stores=collections.Counter();self.instructions=collections.Counter()
  image=bytes(self.u.mem_read(self.n.base,CF.p.OPTIONAL_HEADER.SizeOfImage));heap=bytes(self.u.mem_read(self.n.heap,0x30000));crt=bytes(self.u.mem_read(self.b.own,self.b.extent));stack=bytes(self.u.mem_read(self.n.stack,0x10000))
  for k in range(29):self.u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0)
  self.u.reg_write(UC_ARM64_REG_SP,self.n.stack+0xf000);self.u.reg_write(UC_ARM64_REG_LR,self.n.end)
  a={'ANSI':0x185c50,'OEM':0x185ca0}[mode]
  try:self.u.emu_start(self.db+a,self.n.end,count=100)
  finally:self.active=False
  assert self.u.reg_read(UC_ARM64_REG_PC)==self.n.end and len(self.instructions)==17 and all(v==1 for v in self.instructions.values())
  assert self.stores==collections.Counter({(site,self.db+slot,8):1 for site,slot,kind,v in SCHEMA[mode]})
  for site,slot,kind,v in SCHEMA[mode]:
   data=struct.pack('<Q',self.value(kind,v));page=(self.db+slot)&~4095;off=self.db+slot-page;self.pages[page][off:off+8]=data
  self.check_pages();self.mode=mode
  assert bytes(self.u.mem_read(self.n.base,len(image)))==image and bytes(self.u.mem_read(self.n.heap,0x30000))==heap and bytes(self.u.mem_read(self.b.own,self.b.extent))==crt and bytes(self.u.mem_read(self.n.stack,0x10000))==stack
 def query_wrapper(self,return_to):
  assert not self.active and self.u.reg_read(UC_ARM64_REG_PC)==self.entry and self.mode
  self.expected_bool=int(self.mode=='ANSI');self.return_to=return_to;self.phase='query';self.instructions=collections.Counter();self.query_returns=0;self.active=True
  image=bytes(self.u.mem_read(self.n.base,CF.p.OPTIONAL_HEADER.SizeOfImage));crt=bytes(self.u.mem_read(self.b.own,self.b.extent));heap=bytes(self.u.mem_read(self.n.heap,0x30000));stack=bytes(self.u.mem_read(self.n.stack,0x10000))
  try:self.u.emu_start(self.entry,self.n.end,count=100)
  finally:self.active=False
  assert self.u.reg_read(UC_ARM64_REG_PC)==return_to and self.u.reg_read(UC_ARM64_REG_W0)==self.expected_bool and self.query_returns==1
  self.check_pages()
  assert bytes(self.u.mem_read(self.n.base,len(image)))==image and bytes(self.u.mem_read(self.b.own,self.b.extent))==crt and bytes(self.u.mem_read(self.n.heap,0x30000))==heap and bytes(self.u.mem_read(self.n.stack,0x10000))==stack
  return {'policy_fixture':self.mode,'source_produced_BOOL':self.expected_bool,'original_dependency_query_returns':1,'original_OEM_wrapper_returns':1,'original_OS_instruction_count':sum(v for pc,v in self.instructions.items() if self.rb<=pc<self.db+0x700000),'original_OEM_return_RVA':hex(return_to-self.n.base) if return_to!=self.n.end else 'owned_caller_end','query_writes':0,'complete_owned_pages_unchanged':True}

 def consumer(self):
  assert self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+0xcfd49c
  sp=self.u.reg_read(UC_ARM64_REG_SP);assert self.n.stack<=sp and sp+49<=self.n.stack+0x10000
  self.consumer_input=self.u.mem_read(sp+48,1)[0]
  before=bytes(self.u.mem_read(self.n.stack,0x10000));image=bytes(self.u.mem_read(self.n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))
  self.phase='consumer';self.return_to=self.n.base+(0xcfd4c0 if self.expected_bool else 0xcfd4a4);self.instructions=collections.Counter();self.active=True
  try:self.u.emu_start(self.n.base+0xcfd49c,self.n.end,count=10)
  finally:self.active=False
  assert self.u.reg_read(UC_ARM64_REG_PC)==self.return_to and self.u.reg_read(UC_ARM64_REG_W0)==self.expected_bool
  assert self.instructions==collections.Counter({self.n.base+0xcfd49c:1,self.n.base+0xcfd4a0:1})
  assert bytes(self.u.mem_read(self.n.stack,0x10000))==before and bytes(self.u.mem_read(self.n.base,len(image)))==image
  self.check_pages()
  return {'source_policy_consumer_instructions':2,'consumer_caller_byte_at_SP48':self.consumer_input,'consumer_nonzero_branch_selected':bool(self.expected_bool),'consumer_stop_RVA':hex(self.return_to-self.n.base)}
 def reject_unqualified(self):
  assert not self.active
  phase=self.phase;target=getattr(self,'target_mode',None);counts=self.instructions.copy();stores=self.stores.copy()
  image=bytes(self.u.mem_read(self.n.base,CF.p.OPTIONAL_HEADER.SizeOfImage));regs=[self.u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(31)]
  self.active=True;self.target_mode='ANSI'
  initial_pc=self.u.reg_read(UC_ARM64_REG_PC)
  def wrong_producer_store():
   self.u.reg_write(UC_ARM64_REG_PC,self.db+0x185c7c)
   try:self.memory(self.u,0,self.db+SLOT+8,8,self.db+0x2ce8b0,None)
   finally:self.u.reg_write(UC_ARM64_REG_PC,initial_pc)
  requests=[('query',lambda:self.code(self.u,self.db+0x2ce8b0,4,None)),
            ('query',lambda:self.memory(self.u,0,self.db+SLOT,8,self.db+0x2ce8b0,None)),
            ('producer',wrong_producer_store)]
  try:
   for context,request in requests:
    self.phase=context
    try:request()
    except AssertionError:pass
    else:raise AssertionError('unqualified policy operation admitted')
  finally:self.active=False;self.phase=phase;self.target_mode=target
  self.check_pages()
  assert self.instructions==counts and self.stores==stores and bytes(self.u.mem_read(self.n.base,len(image)))==image
  assert [self.u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(31)]==regs and self.u.reg_read(UC_ARM64_REG_PC)==initial_pc
  return 3

CP_MODE='ANSI';CP_CASES=[]
def attach(n):
 b=CO.attach(n);p=Policy(n,b);b.policy=p;b.co.adapter=p.entry;p.produce(CP_MODE)
 return b
class Startup(CO.Startup):
 def invoke_entry(self):
  super().invoke_entry();p=self.crt.policy
  assert p.wrapper_entries==1 and self.n.base<=p.wrapper_return<self.n.base+CF.p.OPTIONAL_HEADER.SizeOfImage
  site=p.wrapper_return-self.n.base-4
  instruction=next(CF.c.disasm(CF.p.get_data(site,4),site))
  assert instruction.mnemonic=='bl' and instruction.operands[0].imm==0xcb9f68
  arena=bytes(self.u.mem_read(self.f.arena,self.f.arena_size));inner=bytes(self.u.mem_read(self.inner,606264));outer=bytes(self.u.mem_read(self.outer,72))
  detail=p.query_wrapper(p.wrapper_return);detail.update(p.consumer());detail['rejected_policy_scope_requests']=p.reject_unqualified()
  assert bytes(self.u.mem_read(self.f.arena,self.f.arena_size))==arena and bytes(self.u.mem_read(self.inner,606264))==inner and bytes(self.u.mem_read(self.outer,72))==outer
  assert self.f.readq(self.output)==0 and self.crt.depths[self.crt.new_stream+48]==1
  detail.update({'camera_objects_unchanged':True,'public_output_zero':True,'source_policy_setter_returns':1,'source_policy_store_chunks':4})
  CP_CASES.append(detail)
def integrated(blob,pin,camera):
 source=CN.source
 old='enumerate(zip([0,1,40,1230],[1,2,5,8]))';assert source.count(old)==1;source=source.replace(old,'enumerate(zip([0],[1]))')
 old="assert bytes(u.mem_read(n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))==expected_image,'unexpected integrated CRT image delta'"
 new="assert bytes(u.mem_read(n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))==b.co.expected_image(expected_image),'unexpected integrated policy image delta'"
 assert source.count(old)==1;source=source.replace(old,new)
 namespace={};exec(source,dict(CN.ns2['source'].__globals__,Startup=Startup,attach=attach),namespace)
 CP_CASES.clear();CN.CASE_FACTS.clear();CO.CO_CASES.clear()
 row=namespace['source'](blob,pin,camera)
 assert len(row['cases'])==len(CP_CASES)==len(CN.CASE_FACTS)==len(CO.CO_CASES)==1
 row['cases'][0].update(CN.CASE_FACTS[0]);row['cases'][0].update(CO.CO_CASES[0]);row['cases'][0].update(CP_CASES[0])
 row['cases'][0]['original_resolved_API_executed']=True
 row['cases'][0]['resolved_API_executed']=True
 row['cases'][0]['whole_wrapper_return_qualified']=True
 row['cases'][0]['unmodeled_LoadLibraryExW_not_executed']=False
 print(json.dumps(CP_CASES[0]),flush=True)
 return row

def isolated(bias,index,first):
 b=CO.StandaloneBootstrap(bias,0,CN.CRT_IMPORTS);b.run();b.runtime=True
 r=CO.Resolver(b.n,b,bias,index,4 if index%2==0 else 2);p=Policy(b.n,b,index);r.adapter=p.entry;rows=[]
 for warm,mode in [(False,first),(True,'OEM' if first=='ANSI' else 'ANSI')]:
  p.produce(mode);r.begin(warm)
  for k in range(29):r.u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0)
  r.u.reg_write(UC_ARM64_REG_SP,b.n.stack+0xf000);r.u.reg_write(UC_ARM64_REG_LR,b.n.end)
  r.u.emu_start(b.n.base+0xcb9f68,b.n.end,count=250000);detail=r.check()
  detail.update(p.query_wrapper(b.n.end));detail['resolved_API_executed']=True;detail['whole_wrapper_return_qualified']=True
  detail.update({'source_policy_setter_returns':1,'source_policy_store_chunks':4})
  rows.append(detail)
 assert [row['source_produced_BOOL'] for row in rows]==([1,0] if first=='ANSI' else [0,1])
 print(json.dumps({'isolated_policy_flip_bias':bias,'returned_BOOLs':[x['source_produced_BOOL'] for x in rows]}),flush=True)
 return {'placement_bias':bias,'relocated_module_placement':index,'cold_and_cached_policy_flip':rows,
  'rejected_OS_ownership_requests':r.negatives(),'rejected_policy_scope_requests':p.reject_unqualified()}
def main():
 global CP_MODE
 facts,camera=authority()
 isolated_rows=[isolated(bias,k,'ANSI' if k%2==0 else 'OEM') for k,bias in enumerate([0,1,40,1230])]
 sources=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  for CP_MODE in ['ANSI','OEM']:sources.append(integrated(blob,pin,camera))
 cases=[x for row in isolated_rows for x in row['cold_and_cached_policy_flip']]+[row['cases'][0] for row in sources]
 result={'experiment':'E011CP','status':'PASS_BOUNDED_ORIGINAL_FILE_ENCODING_POLICY','base_commit':BASE,
  'authority':facts,'isolated_cases':isolated_rows,'sources':sources,'isolated_cold_cached_cases':8,'integrated_camera_cases':6,
  'distinct_tuning_sources':3,'camera_placements_per_source_per_policy':1,'original_policy_setter_returns':14,
  'original_dependency_query_returns':sum(x['original_dependency_query_returns'] for x in cases),
  'original_OEM_wrapper_returns':sum(x['original_OEM_wrapper_returns'] for x in cases),
  'source_policy_store_chunks':sum(x['source_policy_store_chunks'] for x in cases),
  'original_policy_OS_instruction_count':14*17+sum(x['original_OS_instruction_count'] for x in cases),
  'original_policy_consumer_instructions':sum(row['cases'][0]['source_policy_consumer_instructions'] for row in sources),
  'complete_original_resolver_returns':sum(x['complete_original_resolver_returns'] for x in cases),
  'exact_resolver_image_store_chunks':sum(x['exact_image_store_chunks'] for x in cases),
  'rejected_OS_ownership_requests':sum(row['rejected_OS_ownership_requests'] for row in isolated_rows)+sum(row['cases'][0]['rejected_OS_ownership_requests'] for row in sources),
  'rejected_policy_scope_requests':sum(row['rejected_policy_scope_requests'] for row in isolated_rows)+sum(row['cases'][0]['rejected_policy_scope_requests'] for row in sources),
  'returned_ANSI_BOOL1_cases':sum(x['source_produced_BOOL']==1 for x in cases),'returned_OEM_BOOL0_cases':sum(x['source_produced_BOOL']==0 for x in cases),
  'integrated_statistics_records':sum(row['cases'][0]['independent_152byte_records'] for row in sources),
  'original_OS_policy_code_emulated_only_in_owned_pages':True,'native_Windows_DLL_execution':False,
  'actual_Windows_default_policy_qualified':False,'actual_NTDLL_conversion_or_loader_environment_qualified':False,
  'policy_query_or_wrapper_write_chunks':0,'original_numeric_or_TLS_or_policy_success_stub':False,
  'new_logger16A4228_admitted':False,'whole_outer_return_qualified':False,'final_output_publication_qualified':False,
  'native_rear_runtime_allowed':False,'new_camera_Starts':0,'new_reboots':0,'runtime_or_image_test':False,
  'next_experiment':'E011CQ'}
 assert result['original_OEM_wrapper_returns']==result['original_dependency_query_returns']==14
 assert result['source_policy_store_chunks']==56 and result['original_policy_OS_instruction_count']==392
 assert result['complete_original_resolver_returns']==10 and result['exact_resolver_image_store_chunks']==28
 assert result['rejected_OS_ownership_requests']==60 and result['rejected_policy_scope_requests']==30
 assert result['original_policy_consumer_instructions']==12 and result['returned_ANSI_BOOL1_cases']==result['returned_OEM_BOOL0_cases']==7
 assert result['integrated_statistics_records']==90 and all(row['cases'][0]['consumer_stop_RVA']==('0xcfd4c0' if row['cases'][0]['source_produced_BOOL'] else '0xcfd4a4') for row in sources)
 (OUT/'POLICY-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))}),flush=True)
if __name__=='__main__':main()
