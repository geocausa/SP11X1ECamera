#!/usr/bin/env python3
"""Private existing-camera join exploration; not acceptance evidence."""
from pathlib import Path
import importlib.util,inspect,textwrap,hashlib,json,struct,collections
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
OUT=Path(__file__).resolve().parent
def load(name,path,pin):
 assert hashlib.sha256(path.read_bytes()).hexdigest()==pin
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
CV=load('cw_cv',ROOT/'experiments/E004-front-ir-vd55g0/e011cv-original-slot-thread-producer/source-private.py','e979d0d4046f485f74cacbfa9403681da03edcb69751866e8715fd26a7b6e870')
CU=load('cw_cu',ROOT/'experiments/E004-front-ir-vd55g0/e011cu-original-file-error-boundary/source-private.py','7215b71c2b289e808f1addfb50b063aeb43cf7fb2c14a338f21ad5d1065c3310')
CS=CU.CS;CP=CS.CP;CF=CS.CF
CV.CO.authority();facts,camera=CS.CR.authority();CV.verify_catalog()
init=textwrap.dedent(inspect.getsource(CV.Case.__init__))
old='self.b=CO.StandaloneBootstrap(bias,0,CO.CN.CRT_IMPORTS);self.b.run();self.b.runtime=True'
assert old in init;init=init.replace(old,'self.b=EXISTING_BOOTSTRAP')
for kind in ('CODE','MEM_WRITE','MEM_READ'):
 old='u.hook_add(UC_HOOK_'+kind+',self.'+{'CODE':'code','MEM_WRITE':'memory','MEM_READ':'read'}[kind]+')'
 assert old in init;init=init.replace(old,'self.hooks.append(type(u).hook_add(u,UC_HOOK_'+kind+',self.'+{'CODE':'code','MEM_WRITE':'memory','MEM_READ':'read'}[kind]+'))')
init=init.replace('self.saved={','self.hooks=[];self.saved={')
ns=dict(CV.__dict__);exec(init,ns);join_init=ns['__init__']
class Join(CV.Case):
 def __init__(self,b):
  ns['EXISTING_BOOTSTRAP']=b;join_init(self,0,37,3,2)
 def run(self):
  # Entire inherited models remain active; this trace length differs because the earlier camera prefix initialized one CRT flag.
  source=textwrap.dedent(inspect.getsource(CV.Case.run))
  source=source.replace(' and len(self.trace)==421',' and len(self.trace)==401')
  local={};exec(source,dict(CV.__dict__),local)
  return local['run'](self)
class BoundedStop(Exception):pass
AUTH_PATH=OUT/'CODE-AUTHORITY-SAFE.json'
assert hashlib.sha256(AUTH_PATH.read_bytes()).hexdigest()=='bdc6a3b56f0f119082c52a2626ab98b5d01cefaf8f184788fa08885b09d7f516'
AUTH=json.loads(AUTH_PATH.read_text())
SCHEDULE=[('CreateFileW',0xcfd65c),('GetLastError',0xcfd700),('FlsGetValue2',0xcb4210),('FlsGetValue2',0xcb4210),('FlsGetValue2',0xcb4210),('HeapFree',0xcb1680),('LeaveCriticalSection',0xcfcce4),('LeaveCriticalSection',0xced194)]
class Cleanup:
 def __init__(self,o,join,adapters):
  self.o=o;self.j=join;self.n=o.n;self.u=o.u;self.b=o.crt;self.adapters=adapters
  self.step=0;self.calls=[];self.native=False;self.pending={};self.count=0;self.os_count=0;self.writes=0;self.negatives_count=0;self.released=[];self.stopped=False
  self.records=next(at for at,size in self.b.allocs if size==4608);self.stream=self.b.new_stream
  self.regions=join.regions.copy()+[('cleanup_API_page',0x93020000,4096)]
  self.regions=[(name,self.n.stack if name=='stack' else at,z) for name,at,z in self.regions]
  self.regions+=[('initializer_scratch_stack',0x96300000,65536),('camera',o.f.arena,o.f.arena_size),('serialized',o.f.map,o.f.map_size)]
  for at,page in self.b.policy.pages.items():
   if not any(base<=at and at+4096<=base+size for name,base,size in self.regions):self.regions.append(('inherited_OS_page_'+hex(at),at,4096))
  self.before=self.snapshot();self.stack_model=bytearray(self.before['stack']);self.crt_model=bytearray(self.before['CRT'])
  self.fields={(self.records+56,1):0,(join.thread+32,4):2,(join.thread+36,4):3,(self.stream,8):0,(self.stream+8,8):0,(self.stream+16,4):0,(self.stream+20,4):0,(self.stream+24,8):0xffffffff,(self.stream+32,4):0,(self.stream+40,8):0}
  self.source_fields={(0xcfd6f0,self.records+56,1),(0xcfccd8,self.records+56,1),(0xcaec50,join.thread+36,4),(0xcaec74,join.thread+32,4),(0xcc60e0,self.stream,8),(0xcc60e0,self.stream+8,8),(0xcc60e8,self.stream+16,4),(0xcc60f0,self.stream+24,8),(0xcc60f4,self.stream+32,4),(0xcc60f8,self.stream+40,8),(0x12ec,self.stream+20,4)}
  for (at,z),value in self.fields.items():self.crt_model[at-self.b.own:at-self.b.own+z]=value.to_bytes(z,'little')
  self.depths=self.b.depths.copy();self.allocs=self.b.allocs.copy();self.next_alloc=self.b.next_alloc;self.events=self.b.api_events.copy();self.pages=join.pages()
  assert self.depths[self.records]==self.depths[self.stream+48]==1
  self.instructions={}
  for row in AUTH['source_authority']:
   at=int(row['RVA'],16);size=row['bytes'];raw=CF.p.get_data(at,size);assert hashlib.sha256(raw).hexdigest()==row['sha256']
   for i in CF.c.disasm(raw,self.n.base+at):self.instructions[i.address]=(i,CF.p,self.n.base,'OEM')
  for at,row in join.instructions.items():
   if row[3]=='FlsGetValue2':self.instructions[at]=row
  self.hooks=[type(self.u).hook_add(self.u,UC_HOOK_CODE,self.code),type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.memory),type(self.u).hook_add(self.u,CV.UC_HOOK_MEM_READ,self.read)]
 def snapshot(self):return {name:bytes(self.u.mem_read(at,z)) for name,at,z in self.regions}
 def contract(self,name,args,ret):
  n=self.n;b=self.b;u=self.u
  assert self.step<len(SCHEDULE) and (name,ret)==SCHEDULE[self.step]
  assert b.depths[self.records]==(1 if self.step<7 else 0) and b.depths[self.stream+48]==1
  if name=='CreateFileW':
   assert len(args)==7 and args[0]==b.utf_output and args[1:3]==[0x80000000,1] and args[4:]==[3,128,0]
   assert n.stack<=args[3] and args[3]+24<=n.stack+65536
   assert bytes(u.mem_read(args[3],24))==b'\x18'+bytes(15)+b'\x01'+bytes(7)
   assert b.utf_bytes==74 and hashlib.sha256(bytes(u.mem_read(b.utf_output,74))[:-2].decode('utf-16-le').encode('ascii')+b'\0').hexdigest()==CU.OBS['source_filename_sha256']
   return list(range(7))
  if name=='GetLastError':assert struct.unpack('<I',u.mem_read(self.j.teb+0x68,4))[0]==CU.OBS['Win32_last_error']==3;return []
  if name=='FlsGetValue2':
   assert args[0]==self.j.slot and self.j.registry[self.j.slot]==self.j.thread and u.reg_read(UC_ARM64_REG_X18)==self.j.teb
   assert struct.unpack('<I',u.mem_read(n.base+0x1607168,4))[0]==self.j.slot
   return [0]
  if name=='HeapFree':
   assert args[:3]==[b.handle,0,b.utf_output] and (b.utf_output,74) in b.allocs and self.released==[]
   assert b.depths[self.records]==b.depths[self.stream+48]==1;return [0,1,2]
  assert name=='LeaveCriticalSection'
  expected=self.records if self.step==6 else self.stream+48
  assert args[0]==expected and expected in b.lock_objects and b.depths[expected]==1 and self.released==[b.utf_output];return [0]
 def negatives(self,name,args,ret,indices):
  requests=[(name,args,ret+4),('UnknownCleanupAPI',args,ret)]
  for k in indices:
   a=args.copy();a[k]+=1;requests.append((name,a,ret))
  before=self.snapshot();state=(self.step,self.released.copy(),self.b.depths.copy(),self.b.allocs.copy(),self.b.next_alloc,self.j.pages())
  for request in requests:
   try:self.contract(*request)
   except AssertionError:pass
   else:raise AssertionError('invalid cleanup API admitted')
  assert self.snapshot()==before and state==(self.step,self.released.copy(),self.b.depths.copy(),self.b.allocs.copy(),self.b.next_alloc,self.j.pages())
  self.negatives_count+=len(requests)
 def code(self,u,pc,z,user):
  assert not self.pending
  if self.native and pc==self.n.base+0xcb4210:
   assert u.reg_read(UC_ARM64_REG_X0)==self.j.thread and struct.unpack('<I',u.mem_read(self.j.teb+0x68,4))[0]==3
   self.calls.append({'API':'FlsGetValue2','return_RVA':'0xcb4210','effect':'unchanged original Windows getter','returned_exact_owned_thread':True});self.step+=1;self.native=False
  if pc==self.n.base+0xced194:self.stopped=True;u.emu_stop();return
  if pc in [CU.API_BASE,CU.API_BASE+32] or pc in self.adapters or pc==self.j.getter:
   name='CreateFileW' if pc==CU.API_BASE else 'GetLastError' if pc==CU.API_BASE+32 else 'FlsGetValue2' if pc==self.j.getter else self.adapters[pc]
   args=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(7)];ret=u.reg_read(UC_ARM64_REG_LR)-self.n.base
   indices=self.contract(name,args,ret);self.negatives(name,args,ret,indices)
   if name=='FlsGetValue2':assert not self.native;self.native=True
   else:
    if name=='CreateFileW':value=0xffffffffffffffff
    elif name=='GetLastError':value=3
    elif name=='HeapFree':self.released.append(self.b.utf_output);value=1
    else:self.b.depths[args[0]]=0;value=args[0]
    self.calls.append({'API':name,'return_RVA':hex(ret),'effect':'measured external file/error contract' if name in ('CreateFileW','GetLastError') else 'strict owned resource adapter'})
    self.step+=1;u.reg_write(UC_ARM64_REG_X0,value);u.reg_write(UC_ARM64_REG_PC,self.n.base+ret);return
  assert pc in self.instructions,('unqualified cleanup instruction',hex(pc-self.n.base))
  i,pe,base,component=self.instructions[pc];assert bytes(u.mem_read(pc,4))==pe.get_data(pc-base,4)
  if component=='OEM':self.count+=1
  else:assert component=='FlsGetValue2' and self.native;self.os_count+=1
  self.pending_pc=pc
  if i.mnemonic.startswith(('stp','str','stur','stlxr')):
   mem=next(op.mem for op in i.operands if op.type==3);assert not mem.index
   at=CV.reg(u,CF.c.reg_name(mem.base))+mem.disp;first=1 if i.mnemonic=='stlxr' else 0;name=CF.c.reg_name(i.operands[first].reg)
   width=2 if i.mnemonic.endswith('h') else 1 if i.mnemonic.endswith('b') else 16 if name.startswith('q') else 8 if name in ('fp','lr') or name.startswith(('x','d')) else 4
   ops=i.operands[:2] if i.mnemonic=='stp' else i.operands[first:first+1]
   for k,op in enumerate(ops):
    address=at+k*width;value=CV.reg(u,CF.c.reg_name(op.reg))&((1<<(8*width))-1)
    if self.n.stack<=address and address+width<=self.n.stack+65536:
     off=address-self.n.stack;self.stack_model[off:off+width]=value.to_bytes(width,'little')
    else:assert (pc-self.n.base,address,width) in self.source_fields and (address,width) in self.fields and self.fields[address,width]==value, ('unowned cleanup store',hex(pc-self.n.base),hex(address),width,value,hex(self.stream),address-self.stream)
    for j in range(0,width,8):size=min(width-j,8);self.pending[address+j,size]=(value>>(8*j))&((1<<(8*size))-1)
 def memory(self,u,access,at,z,value,user):
  assert u.reg_read(UC_ARM64_REG_PC)==self.pending_pc and (at,z) in self.pending
  assert value&((1<<(8*z))-1)==self.pending.pop((at,z));self.writes+=1
 def read(self,u,access,at,z,value,user):
  if self.released:assert at+z<=self.b.utf_output or at>=self.b.utf_output+74,'read of retired Unicode allocation'
  if self.native:
   assert (at,z) in {(self.j.teb+0x17c8,8),(self.j.data+8*self.j.chunk,8),(self.j.slab+8*self.j.index,8)}
 def run(self):
  u=self.u;n=self.n;b=self.b
  try:u.emu_start(n.base+0xcfd658,n.end,count=10000)
  finally:
   for hook in self.hooks:u.hook_del(hook)
  assert self.stopped and u.reg_read(UC_ARM64_REG_PC)==n.base+0xced194 and not self.pending and not self.native
  assert self.step==8 and self.count==261 and self.os_count==57 and self.writes==39
  after=self.snapshot();assert after['stack']==self.stack_model and after['CRT']==self.crt_model
  assert all(after[k]==v for k,v in self.before.items() if k not in ('stack','CRT'))
  depths=self.depths.copy();depths[self.records]=0;depths[self.stream+48]=0
  assert b.depths==depths and b.allocs==self.allocs and b.next_alloc==self.next_alloc and b.api_events==self.events and self.j.pages()==self.pages
  assert self.released==[b.utf_output] and self.o.f.readq(self.o.output)==0;b.policy.check_pages()
  return {'original_cleanup_instructions':self.count,'original_OS_getter_instructions':self.os_count,'exact_cleanup_store_chunks':self.writes,'negative_cleanup_API_requests':self.negatives_count,'API_schedule':self.calls,'original_error3_mapped_to_thread_OS3_CRT2':True,'descriptor0_flag_cleared_and_lock_released':True,'stream_claim_cleared_and_lock_released':True,'UTF16_owned74byte_allocation_released':True,'no_original_reads_of_retired_UTF16_owner':True,'independent_entire_stack_and_CRT_models':True,'all_other_entire_regions_unchanged':True,'actual_permissions_unchanged':True,'only_record0_and_stream_locks_released':True,'public_output_zero':True,'stop_RVA':'0xced194','full_original_outer_return_qualified':False}

ROWS=[]
class Startup(CS.Startup):
 def invoke_entry(self):
  super().invoke_entry();u=self.u;n=self.n;b=self.crt;assert u.reg_read(UC_ARM64_REG_PC)==n.base+0xcfd658
  saved={k:u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(31)}
  extra={k:u.reg_read(globals()['UC_ARM64_REG_'+k]) for k in ('SP','PC','NZCV','FPCR','FPSR')}
  oldstack=n.stack;original_stack=bytes(u.mem_read(oldstack,65536))
  camera_before=bytes(u.mem_read(self.f.arena,self.f.arena_size));serialized_before=bytes(u.mem_read(self.f.map,self.f.map_size))
  bindings={rva:bytes(u.mem_read(n.base+rva,8)) for rva in CV.CO.IMPORTS.values()}
  self.active=False;n.stack=0x96300000;u.mem_map(n.stack,65536)
  join=None
  try:
   join=Join(b);detail=join.run()
  finally:
   if join:
    for hook in join.hooks:u.hook_del(hook)
   n.stack=oldstack
  assert bytes(u.mem_read(oldstack,65536))==original_stack and bytes(u.mem_read(self.f.arena,self.f.arena_size))==camera_before and bytes(u.mem_read(self.f.map,self.f.map_size))==serialized_before
  for rva,raw in bindings.items():u.mem_write(n.base+rva,raw)
  for k,value in saved.items():u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],value)
  for k,value in extra.items():u.reg_write(globals()['UC_ARM64_REG_'+k],value)
  u.reg_write(UC_ARM64_REG_X18,join.teb)
  b.policy.check_pages()
  api=0x93020000;u.mem_map(api,4096,CV.UC_PROT_READ|CV.UC_PROT_EXEC)
  adapters={api:'LeaveCriticalSection',api+32:'HeapFree'}
  for at,name in adapters.items():u.mem_write(n.base+CV.CO.IMPORTS[name],struct.pack('<Q',at))
  cleanup=Cleanup(self,join,adapters).run()
  ROWS.append({'slot_thread_source':detail,'cleanup':cleanup,'whole_original_paused_stack_camera_and_serialized_unchanged_during_initializer':True,'original_initializer_ran_in_same_Native_and_CRT_owner':True,'owned_separate_initializer_stack_and_saved_caller_registers':True,'platform_X18_is_explicit_owned_TEB_fixture':True})
  raise BoundedStop()
CP.Startup=Startup
def main():
 sources=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  for mode in ('ANSI','OEM'):
   CP.CP_MODE=mode;ROWS.clear();CS.CASES.clear();CS.CR.CASES.clear();CS.CR.CQ.CASES.clear()
   try:CP.integrated(blob,pin,camera)
   except BoundedStop:assert len(ROWS)==1
   else:raise AssertionError('cleanup boundary not reached')
   row={'source_sha256':pin,'policy':mode,**ROWS[0]};sources.append(row)
   print(json.dumps({'policy':mode,'source_sha256':pin,'slot_producer_OEM_instructions':row['slot_thread_source']['original_OEM_instructions'],**{k:v for k,v in row['cleanup'].items() if k!='API_schedule'}}),flush=True)
 result={'experiment':'E011CW','status':'PASS_BOUNDED_ORIGINAL_FILE_ERROR_THREAD_JOIN_AND_CLEANUP','base_commit':'eada16e6648013c96d62f919b9372b3220642a04','evidence_class':'UNCHANGED_ORIGINAL_CAMERA_AND_CRT_OS_SOURCE_WITH_MEASURED_FILE_FAILURE_AND_OWNED_RESOURCE_CONTRACTS','sources':sources,'source_authority':AUTH['source_authority'],'integrated_camera_cases':len(sources),'distinct_tuning_sources':3,'original_slot_thread_OEM_instructions':sum(row['slot_thread_source']['original_OEM_instructions'] for row in sources),'original_slot_thread_OS_instructions':sum(sum(row['slot_thread_source']['original_OS_instruction_counts'].values()) for row in sources),'original_cleanup_instructions':sum(row['cleanup']['original_cleanup_instructions'] for row in sources),'original_cleanup_OS_getter_instructions':sum(row['cleanup']['original_OS_getter_instructions'] for row in sources),'exact_cleanup_store_chunks':sum(row['cleanup']['exact_cleanup_store_chunks'] for row in sources),'negative_cleanup_API_requests':sum(row['cleanup']['negative_cleanup_API_requests'] for row in sources),'negative_slot_thread_API_requests':sum(row['slot_thread_source']['invalid_API_requests_rejected_before_effect'] for row in sources),'original_error3_maps_to_OS3_CRT2':True,'descriptor0_and_stream_locks_released':True,'UTF16_owned74byte_owner_released':True,'full_whole_memory_and_permissions_checks':True,'separate_owned_initializer_stack_and_thread_ordering_are_fixtures':True,'actual_live_windows_loader_full_CRT_TLS_locale_concurrency_qualified':False,'original_Windows_HeapFree_FLS_implementations_executed':False,'original_CFE600_qualified':False,'full_original_outer_return_qualified':False,'later_unqualified_callback_RVA':'0x36df50','public_output_zero':True,'native_rear_runtime_allowed':False,'new_camera_Starts':0,'new_reboots':0,'new_Linux_image_tests':0,'next_experiment':'E011CX'}
 assert len(sources)==6 and result['original_cleanup_instructions']==1566 and result['original_cleanup_OS_getter_instructions']==342 and result['exact_cleanup_store_chunks']==234
 (OUT/'FILE-THREAD-CLEANUP-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(list,dict))}),flush=True)
if __name__=='__main__':main()
