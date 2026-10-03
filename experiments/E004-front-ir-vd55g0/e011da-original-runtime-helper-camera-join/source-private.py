#!/usr/bin/env python3
"""Bounded shared-camera original runtime helpers with independent whole-memory and caller checks."""
from pathlib import Path
import importlib.util,inspect,textwrap,hashlib,json,collections,copy
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
OUT=Path(__file__).resolve().parent
P=ROOT/'experiments/E004-front-ir-vd55g0/e011cz-original-runtime-helpers/source-private.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='5baea38164f6f59bd0d90e456cc1cea12fe111bf16771693c8a8a52084ba1a37'
s=importlib.util.spec_from_file_location('da_cz',P);CZ=importlib.util.module_from_spec(s);s.loader.exec_module(CZ)
CY=CZ.CY;CX=CY.CX;CW=CY.CW;CF=CY.CF;CP=CY.CP;AUTH=CZ.AUTH
# Retain the legacy counter for inherited reports, but remove only its result fixture.
source=textwrap.dedent(inspect.getsource(CF.Observer.hook))
old="if r==0xce7c98:self.events['owned_diagnostic_context']+=1;self.ret(self.tls+0x3000);return"
assert source.count(old)==1
source=source.replace(old,"if r==0xce7c98:self.events['owned_diagnostic_context']+=1;return")
scope={};exec(source,CF.__dict__,scope);CF.Observer.hook=scope['hook']
row=next(r for r in AUTH['source_authority'] if int(r['RVA'],16)==0xce7c98)
raw=CF.p.get_data(0xce7c98,row['bytes']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
HELPER_INSTRUCTIONS={i.address:i for i in CF.c.disasm(raw,CF.p.OPTIONAL_HEADER.ImageBase+0xce7c98)}
old_pub_init=CX.Publication.__init__
def publication_init(self,o):
 old_pub_init(self,o)
 self.instructions.update({pc:(i,CF.p,self.n.base,'OEM') for pc,i in HELPER_INSTRUCTIONS.items()})
CX.Publication.__init__=publication_init
old_ret_init=CY.ReturnProof.__init__
def return_init(self,o):
 old_ret_init(self,o);self.instructions.update(HELPER_INSTRUCTIONS)
CY.ReturnProof.__init__=return_init
for cls,module,changes in [
 (CX.Publication,CX,[('self.visits==394 and self.executed==386','self.visits==904 and self.executed==898'),('{0xce7c98:2,0x1a8c0:2','{0x1a8c0:2')]),
 (CY.ReturnProof,CY,[('self.visits==575 and self.executed==560','self.visits==826 and self.executed==812'),('[*self.guards,0x3c51d0,0xce7c98,0x1a8c0,0xf5e600]','[*self.guards,0x3c51d0,0x1a8c0,0xf5e600]')])]:
 source=textwrap.dedent(inspect.getsource(cls.run))
 for old,new in changes:assert source.count(old)==1;source=source.replace(old,new)
 scope={};exec(source,module.__dict__,scope);cls.run=scope['run']
EXPECTED_COUNTS={0x13a9fc0:256,0x13b42f0:266,0x13b5380:266,0x13b6c30:266,0x13b9e20:262,0x13bc310:252,0x13bd0a0:266,0x13c07b0:252}
class HelperJoin:
 def __init__(self,o):
  self.o=o;self.u=o.u;self.n=o.n;self.active=False;self.rows=[];self.negatives_count=0;self.calls=collections.Counter()
  self.literals={int(r['input_RVA'],16):r for r in AUTH['private_source_literals']}
  self.callers={int(r['return_RVA'],16):r for r in AUTH['actual_original_caller_sites']}
  for r in self.callers:
   i=next(CF.c.disasm(CF.p.get_data(r-4,4),r-4));assert i.mnemonic=='bl' and i.operands[0].imm==0xce7c98
  self.hooks=[type(self.u).hook_add(self.u,UC_HOOK_CODE,self.code),type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.memory),type(self.u).hook_add(self.u,UC_HOOK_MEM_READ,self.read)]
 def snapshot(self):
  return {(a,b,p):bytes(self.u.mem_read(a,b-a+1)) for a,b,p in self.u.mem_regions()}
 def preserved(self):
  return {r:self.u.reg_read(r) for r in [UC_ARM64_REG_SP,*[globals()['UC_ARM64_REG_X'+str(k)] for k in range(19,30)],*[globals()['UC_ARM64_REG_D'+str(k)] for k in range(8,16)]]}
 def resources(self):
  o=self.o;f=o.f
  return copy.deepcopy((f.allocs,f.released,f.next,o.root_lock_snapshot() if hasattr(o,'root_lock_snapshot') else None,
   (o.crt.allocs,o.crt.next_alloc,o.crt.depths,o.crt.api_events) if hasattr(o,'crt') else None))
 def contract(self,entry,args):
  assert entry==0xce7c98 and len(args)==3
  source,value,ret=args;assert ret in self.callers
  row=self.callers[ret];assert source==int(row['input_RVA'],16) and value==row['search_byte']==92
  lit=self.literals[source];raw=bytes(self.u.mem_read(self.n.base+source,lit['bytes_with_NUL']))
  assert hashlib.sha256(raw).hexdigest()==lit['sha256'] and raw[-1:]==bytes(1)
  assert raw[:-1].rfind(bytes([92]))==lit['last_backslash_offset']
 def begin(self):
  assert not self.active
  u=self.u;n=self.n
  self.request=[u.reg_read(UC_ARM64_REG_X0)-n.base,u.reg_read(UC_ARM64_REG_W1),u.reg_read(UC_ARM64_REG_LR)-n.base]
  self.contract(0xce7c98,self.request)
  before=self.snapshot()
  regs={r:u.reg_read(r) for r in [UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_LR,UC_ARM64_REG_SP,*self.preserved()]}
  requests=[(0xce7c9c,self.request),(0xce7c98,self.request+[0])]
  for k in range(3):
   bad=self.request.copy();bad[k]+=1;requests.append((0xce7c98,bad))
  for entry,args in requests:
   try:self.contract(entry,args)
   except AssertionError:pass
   else:raise AssertionError('invalid reverse search camera request admitted')
  assert before==self.snapshot() and all(u.reg_read(r)==v for r,v in regs.items())
  self.negatives_count+=len(requests);self.before=before;self.incoming=self.preserved();self.resource_before=self.resources()
  source,value,ret=self.request;lit=self.literals[source]
  self.read_start=(n.base+source)&~15;self.read_end=(n.base+source+lit['bytes_with_NUL']+15)&~15
  self.expected=n.base+source+lit['last_backslash_offset'];self.count=0;self.active=True
 def finish(self):
  assert self.active and self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+self.request[2]
  assert self.u.reg_read(UC_ARM64_REG_X0)==self.expected and self.preserved()==self.incoming
  assert self.snapshot()==self.before and self.resources()==self.resource_before
  assert self.count==EXPECTED_COUNTS[self.request[0]]
  self.calls[self.request[2]]+=1
  self.rows.append({'input_RVA':hex(self.request[0]),'return_RVA':hex(self.request[2]),'original_instructions':self.count,'all_mapped_memory_permissions_and_resources_unchanged':True,'actual_callee_saved_registers_restored':True})
  self.active=False;self.before=None
 def code(self,u,pc,size,user):
  if not self.active:return
  assert pc in HELPER_INSTRUCTIONS and u.reg_read(UC_ARM64_REG_PC)==pc
  assert bytes(u.mem_read(pc,4))==CF.p.get_data(pc-self.n.base,4)
  self.count+=1
 def memory(self,u,access,at,size,value,user):
  assert not self.active,'original reverse search must not store'
 def read(self,u,access,at,size,value,user):
  if self.active:assert self.read_start<=at and at+size<=self.read_end,'original reverse search read outside aligned source window'
 def result(self):
  assert not self.active and self.rows
  assert self.o.events['owned_diagnostic_context']==len(self.rows)
  return {'original_reverse_search_calls':len(self.rows),'original_reverse_search_instructions':sum(r['original_instructions'] for r in self.rows),
   'invalid_scope_requests_rejected':self.negatives_count,'exact_source_callers':{hex(k):v for k,v in self.calls.items()},
   'whole_mapped_memory_permissions_resources_and_caller_checks':True,'CE7C98_result_fixture_removed':True,'legacy_counter_semantics_corrected':True,'calls':self.rows}

# Isolate one explicitly modeled emulator component. Parent observers remain fully active outside this phase.
TLS_PHASE_UC=None
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM
UC_CLASS=type(Uc(UC_ARCH_ARM64,UC_MODE_ARM))
original_hook_add=UC_CLASS.hook_add
def phased_hook_add(self,hook_type,callback,*args,**kwargs):
 def checked(u,*values):
  if TLS_PHASE_UC is u and getattr(callback,'__module__',None)!=__name__:return
  return callback(u,*values)
 return original_hook_add(self,hook_type,checked,*args,**kwargs)
UC_CLASS.hook_add=phased_hook_add
old='u.mem_write(o.tls+0x2000+20,struct.pack(\'<I\',1))'
assert CP.CO.CN.source.count(old)==1
CP.CO.CN.source=CP.CO.CN.source.replace(old,'u.mem_write(o.tls+0x2000+20,struct.pack(\'<I\',0))')
class TLSJoin:
 def __init__(self,o):
  self.o=o;self.n=o.n;self.u=o.u;self.stack=0x96310000;self.stack_size=65536
  self.u.mem_map(self.stack,self.stack_size);self.u.mem_write(self.stack,bytes([0xa5])*self.stack_size)
  self.teb=o.tls;self.array=o.tls+0x1000;self.block=o.tls+0x2000;self.slot=0;self.flag=0
  self.instructions={}
  for row in AUTH['source_authority']:
   r=int(row['RVA'],16)
   if r==0xce7c98:continue
   raw=CF.p.get_data(r,row['bytes']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
   self.instructions.update({i.address:i for i in CF.c.disasm(raw,self.n.base+r)})
  assert CF.p.DIRECTORY_ENTRY_TLS.struct.AddressOfIndex-self.n.base==0x16a3740
  assert CF.p.get_qword_at_rva(0xf7f438)==0
  self.pending={};self.count=0;self.writes=0;self.seen=collections.Counter();self.negative_count=0
 def q(self,at):return int.from_bytes(self.u.mem_read(at,8),'little')
 def snapshot(self):return {(a,b,p):bytes(self.u.mem_read(a,b-a+1)) for a,b,p in self.u.mem_regions()}
 def contract(self,entry,args):
  assert entry==0xcfe600 and args==[self.teb,self.array,self.block,self.slot,self.flag]
  assert self.u.reg_read(UC_ARM64_REG_X18)==self.teb
  assert self.q(self.teb+88)==self.array and self.q(self.array+8*self.slot)==self.block
  assert int.from_bytes(self.u.mem_read(self.n.base+0x16a3740,4),'little')==self.slot
  assert self.u.mem_read(self.block+20,4)==bytes(4) and self.q(self.n.base+0xf7f438)==0
 def run(self):
  global TLS_PHASE_UC
  o=self.o;u=self.u;n=self.n
  assert TLS_PHASE_UC is None and not o.helper_join.active
  registers=[*[globals()['UC_ARM64_REG_X'+str(k)] for k in range(31)],*[globals()['UC_ARM64_REG_Q'+str(k)] for k in range(32)],UC_ARM64_REG_SP,UC_ARM64_REG_PC,UC_ARM64_REG_NZCV,UC_ARM64_REG_FPCR,UC_ARM64_REG_FPSR]
  paused={r:u.reg_read(r) for r in registers}
  u.reg_write(UC_ARM64_REG_X18,self.teb);u.reg_write(UC_ARM64_REG_SP,self.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  self.incoming={r:u.reg_read(r) for r in [UC_ARM64_REG_SP,*[globals()['UC_ARM64_REG_X'+str(k)] for k in range(19,30)],*[globals()['UC_ARM64_REG_D'+str(k)] for k in range(8,16)]]}
  req=[self.teb,self.array,self.block,self.slot,self.flag];self.contract(0xcfe600,req)
  before=self.snapshot();before_regs={r:u.reg_read(r) for r in registers};resources=o.helper_join.resources()
  tests=[(0xcfe604,req),(0xcfe600,req+[0])]
  for k in range(5):
   bad=req.copy();bad[k]+=1;tests.append((0xcfe600,bad))
  for entry,args in tests:
   try:self.contract(entry,args)
   except AssertionError:pass
   else:raise AssertionError('invalid TLS component request admitted')
  assert before==self.snapshot() and all(u.reg_read(r)==v for r,v in before_regs.items())
  self.negative_count=len(tests);self.before=before
  self.models={k:bytearray(v) for k,v in before.items() if k[0] in (self.stack,0x90000000)}
  owner=next(k for k in self.models if k[0]<=self.block+20<=k[1])
  self.models[owner][self.block+20-owner[0]]=1
  self.hooks=[type(u).hook_add(u,UC_HOOK_CODE,self.code),type(u).hook_add(u,UC_HOOK_MEM_WRITE,self.memory),type(u).hook_add(u,UC_HOOK_MEM_READ,self.read)]
  TLS_PHASE_UC=u
  try:u.emu_start(n.base+0xcfe600,n.end,count=2000)
  finally:
   TLS_PHASE_UC=None
   for hook in self.hooks:u.hook_del(hook)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end and u.reg_read(UC_ARM64_REG_W0)==0 and not self.pending
  assert self.count==34 and self.writes==6 and self.seen[0xcfe5a4]==1
  after=self.snapshot();assert all(after[k]==self.models.get(k,v) for k,v in before.items()),'entire TLS preinitialization model'
  assert all(u.reg_read(r)==v for r,v in self.incoming.items()) and o.helper_join.resources()==resources
  self.frozen_stack=bytes(u.mem_read(self.stack,self.stack_size))
  self.stack_pages=[r for r in u.mem_regions() if r[0]<=self.stack and self.stack+self.stack_size-1<=r[1]];assert len(self.stack_pages)==1
  for r,v in paused.items():u.reg_write(r,v)
  assert all(u.reg_read(r)==v for r,v in paused.items())
  self.before=None;self.models=None
  self.result={'original_TLS_initializer_instructions':self.count,'exact_TLS_initializer_store_chunks':self.writes,'invalid_scope_requests_rejected':self.negative_count,
   'source_produced_flag20':True,'whole_mapped_memory_permissions_and_resources_checked':True,'original_callee_restored_and_paused_caller_fully_restored':True,
   'declared_loader_index_and_TEB_array_and_empty_initializer_table':True,'parent_observers_paused_only_for_independently_modeled_component':True,
   'actual_Windows_loader_or_full_runtime_bootstrap_qualified':False}
  return self.result
 def code(self,u,pc,size,user):
  assert TLS_PHASE_UC is u and not self.pending and pc in self.instructions and u.reg_read(UC_ARM64_REG_PC)==pc
  assert bytes(u.mem_read(pc,4))==CF.p.get_data(pc-self.n.base,4)
  self.count+=1;r=pc-self.n.base;self.seen[r]+=1;i=self.instructions[pc];self.pending_pc=pc
  if i.mnemonic.startswith(('str','stp','stur')):
   op=next(x for x in i.operands if x.type==3);assert not op.mem.index
   at=CZ.CV.reg(u,CF.c.reg_name(op.mem.base))+op.mem.disp;name=CF.c.reg_name(i.operands[0].reg)
   width=1 if i.mnemonic.endswith('b') else 2 if i.mnemonic.endswith('h') else 16 if name.startswith('q') else 8 if name.startswith(('x','d')) or name in ('fp','lr') else 4
   for k,operand in enumerate(i.operands[:2] if i.mnemonic=='stp' else i.operands[:1]):
    address=at+k*width;value=CZ.CV.reg(u,CF.c.reg_name(operand.reg))&((1<<(8*width))-1)
    if self.stack<=address and address+width<=self.stack+self.stack_size:
     region=next(k for k in self.models if k[0]==self.stack);off=address-self.stack;self.models[region][off:off+width]=value.to_bytes(width,'little')
    else:assert (r,address,width,value)==(0xcfe5a4,self.block+20,1,1)
    for j in range(0,width,8):z=min(width-j,8);self.pending[address+j,z]=(value>>(8*j))&((1<<(8*z))-1)
 def memory(self,u,access,at,size,value,user):
  assert TLS_PHASE_UC is u and u.reg_read(UC_ARM64_REG_PC)==self.pending_pc and (at,size) in self.pending
  assert value&((1<<(8*size))-1)==self.pending.pop((at,size));self.writes+=1
 def read(self,u,access,at,size,value,user):
  assert TLS_PHASE_UC is u
  if self.stack<=at and at+size<=self.stack+self.stack_size:return
  assert (at,size) in {(self.n.base+0x16a3740,4),(self.teb+88,8),(self.array,8),(self.block+20,1),(self.n.base+0xf7f438,8)}
 def final(self):
  assert TLS_PHASE_UC is None and bytes(self.u.mem_read(self.stack,self.stack_size))==self.frozen_stack
  assert [r for r in self.u.mem_regions() if r[0]<=self.stack and self.stack+self.stack_size-1<=r[1]]==self.stack_pages
  assert self.u.mem_read(self.block+20,4)==bytes([1,0,0,0])

ROWS=[]
class Startup(CY.Startup):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.helper_join=HelperJoin(self)
 def hook(self,u,pc,size,user):
  join=getattr(self,'helper_join',None)
  if join is not None:
   if join.active and pc==self.n.base+join.request[2]:join.finish()
   if pc==self.n.base+0xce7c98:join.begin()
  return super().hook(u,pc,size,user)
 def invoke_entry(self):
  self.tls_join=TLSJoin(self);tls_detail=self.tls_join.run()
  try:CY.Startup.invoke_entry(self)
  except CW.BoundedStop:pass
  self.tls_join.final();detail=self.helper_join.result();ROWS.append({'inherited_outer_return':CY.ROWS[-1],'reverse_search_join':detail,'TLS_initialization_join':tls_detail})
  raise CW.BoundedStop()
CP.Startup=Startup
def main():
 CY.authority();rows=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  for mode in ('ANSI','OEM'):
   CP.CP_MODE=mode;ROWS.clear();CY.ROWS.clear();CX.ROWS.clear();CW.ROWS.clear();CW.CS.CASES.clear();CW.CS.CR.CASES.clear();CW.CS.CR.CQ.CASES.clear()
   try:CP.integrated(blob,pin,CW.camera)
   except CW.BoundedStop:assert len(ROWS)==1
   else:raise AssertionError('shared original helper return not captured')
   row={'policy':mode,'source_sha256':pin,**ROWS[0]};rows.append(row)
   print(json.dumps({'policy':mode,'source_sha256':pin,**{k:v for k,v in row['reverse_search_join'].items() if k not in ('calls','exact_source_callers')}}),flush=True)
 assert len(rows)==6 and len({r['source_sha256'] for r in rows})==3
 result={'experiment':'E011DA','status':'PASS_BOUNDED_ORIGINAL_RUNTIME_HELPER_CAMERA_JOIN','base_commit':'001314aa22b4d69b1ac69d7529d3f5aefaa42ddf',
  'sources':rows,'source_authority':AUTH['source_authority'],'private_source_literal_authority':AUTH['private_source_literals'],'source_caller_authority':AUTH['actual_original_caller_sites'],
  'integrated_camera_cases':len(rows),'distinct_tuning_sources':3,
  'original_reverse_search_calls':sum(r['reverse_search_join']['original_reverse_search_calls'] for r in rows),
  'original_reverse_search_instructions':sum(r['reverse_search_join']['original_reverse_search_instructions'] for r in rows),
  'original_TLS_initializer_instructions':sum(r['TLS_initialization_join']['original_TLS_initializer_instructions'] for r in rows),
  'exact_TLS_initializer_store_chunks':sum(r['TLS_initialization_join']['exact_TLS_initializer_store_chunks'] for r in rows),
  'invalid_helper_scope_requests_rejected':sum(r['reverse_search_join']['invalid_scope_requests_rejected']+r['TLS_initialization_join']['invalid_scope_requests_rejected'] for r in rows),
  'publication_guarded_visits':sum(r['inherited_outer_return']['inherited_publication']['publication']['source_guarded_OEM_visits'] for r in rows),
  'publication_executed_OEM_instructions':sum(r['inherited_outer_return']['inherited_publication']['publication']['unchanged_executed_OEM_instructions'] for r in rows),
  'publication_inherited_adapter_entries':sum(r['inherited_outer_return']['inherited_publication']['publication']['inherited_typed_adapter_entries'] for r in rows),
  'outer_return_guarded_visits':sum(r['inherited_outer_return']['outer_return']['source_guarded_OEM_visits'] for r in rows),
  'outer_return_executed_OEM_instructions':sum(r['inherited_outer_return']['outer_return']['unchanged_executed_OEM_instructions'] for r in rows),
  'outer_return_inherited_adapter_entries':sum(r['inherited_outer_return']['outer_return']['inherited_typed_adapter_entries'] for r in rows),
  'CE7C98_reverse_search_result_fixture_removed':True,'source_produced_TLS_flag_replaces_seed1':True,
  'whole_mapped_memory_permissions_resources_and_original_caller_checks':True,
  'original_output_global_and_inner_link_retained_and_same_root_locks_balanced':True,
  'TLS_initializer_integrated_under_explicit_owned_component_ordering':True,
  'PE_TLS_index_TEB_array_null_callback_table_and_owned_stack_are_declared_fixtures':True,
  'parent_observers_paused_only_during_strict_independent_original_TLS_component':True,
  'original_CFE600_qualified_for_null_file_initializer_table_component_only':True,
  'full_original_CFE600_runtime_bootstrap_qualified':False,'actual_Windows_loader_Default_CRT_TLS_locale_concurrency_qualified':False,
  'hardware_WM16_IRQ_consumed_IOVA_DMA_IOMMU_retirement_optical_qualified':False,'native_rear_runtime_allowed':False,
  'new_camera_Starts':0,'new_reboots':0,'new_Linux_image_tests':0,'production_C_or_kernel_changed':False,'next_experiment':'E011DB'}
 assert result['original_TLS_initializer_instructions']==204 and result['exact_TLS_initializer_store_chunks']==36
 assert (result['publication_guarded_visits'],result['publication_executed_OEM_instructions'],result['publication_inherited_adapter_entries'])==(5424,5388,36)
 assert (result['outer_return_guarded_visits'],result['outer_return_executed_OEM_instructions'],result['outer_return_inherited_adapter_entries'])==(4956,4872,84)
 assert all(r['TLS_initialization_join']['source_produced_flag20'] for r in rows)
 (OUT/'RUNTIME-HELPER-CAMERA-JOIN-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))}),flush=True)
if __name__=='__main__':main()
