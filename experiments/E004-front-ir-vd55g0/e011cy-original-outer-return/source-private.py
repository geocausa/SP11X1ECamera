#!/usr/bin/env python3
"""Independently bounded original publication callback and outer return; same-SP11 private source inputs."""
from pathlib import Path
import importlib.util,inspect,textwrap,hashlib,json,collections,struct
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
OUT=Path(__file__).resolve().parent
P=ROOT/'experiments/E004-front-ir-vd55g0/e011cx-original-output-publication/source-private.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='ca61b04cfe71ab0da454012f906c450520d5b8d8089408e634783f320b90fa05'
sp=importlib.util.spec_from_file_location('cy_cx',P);CX=importlib.util.module_from_spec(sp);sp.loader.exec_module(CX)
CW=CX.CW;CF=CX.CF;CP=CX.CP;CV=CW.CV
AUTH_PATH=OUT/'RETURN-CODE-AUTHORITY-SAFE.json'
assert hashlib.sha256(AUTH_PATH.read_bytes()).hexdigest()=='adfe54be02201e61b5cdd26e7329527077717ff1420a32db7cea104070a68ec2'
AUTH=json.loads(AUTH_PATH.read_text())
# Expose the existing root mutex closure without changing its modeled effects.
marker=' type(u).hook_add(u,UC_HOOK_CODE,mutex)'
assert CP.CO.CN.source.count(marker)==1
CP.CO.CN.source=CP.CO.CN.source.replace(marker,marker+"\n o.root_lock_snapshot=lambda: {'depth':lock_depth,'events':dict(lock_events)}")
# Keep exact original IAT fixture bindings for the post-publication parent lock handler.
source=textwrap.dedent(inspect.getsource(CW.Startup.invoke_entry))
assert source.count(' cleanup=Cleanup(self,join,adapters).run()')==1
source=source.replace(' cleanup=Cleanup(self,join,adapters).run()',' cleanup_owner=Cleanup(self,join,adapters);cleanup=cleanup_owner.run()')
assert source.count('super().invoke_entry()')==1 and source.count(' ROWS.append')==1
source=source.replace('super().invoke_entry()','CS.Startup.invoke_entry(self)').replace(' ROWS.append',' self.cw_join=join;self.cw_cleanup=cleanup_owner;self.cy_old_bindings=bindings\n ROWS.append')
scope={};exec(source,CW.__dict__,scope);CX.invoke=scope['invoke_entry']
# Execute only this outer frame's original cookie producer/checker. Nested legacy fixtures stay explicit.
cookie_owners=[]
for cls in CF.Production.__mro__:
 fn=cls.__dict__.get('hook')
 if fn:
  text=inspect.getsource(fn).lower()
  if '0x11d0' in text and '0x11f0' in text:cookie_owners.append((cls,fn))
assert len(cookie_owners)==1
cookie_class,legacy_cookie_hook=cookie_owners[0]
def outer_cookie_hook(self,u,pc,size,user):
 if (pc-self.n.base,u.reg_read(UC_ARM64_REG_LR)-self.n.base) in ((0x11d0,0x36cbd0),(0x11f0,0x36e36c)):return
 return legacy_cookie_hook(self,u,pc,size,user)
cookie_class.hook=outer_cookie_hook
MASK=(1<<64)-1
class ReturnProof:
 def __init__(self,o):
  self.o=o;self.u=o.u;self.n=o.n;self.f=o.f;self.b=o.crt;self.j=o.cw_join
  self.regions=o.publication.regions.copy();self.before=self.snapshot()
  self.models={k:bytearray(v) for k,v in self.before.items() if k in ('stack','camera','caller')}
  n=self.n;f=self.f;inner=o.inner;outer=o.outer
  self.interface=f.readq(inner+8);self.core=f.readq(self.interface);self.component=f.readq(self.core+16)
  self.link=f.readq(self.component+464);self.head=f.readq(self.link)
  for at,z in [(inner,606264),(outer,72),(self.interface,320),(self.core,5152),(self.component,3120),(self.link,16),(self.head,448)]:assert (at,z) in f.allocs
  assert len({inner,outer,self.interface,self.core,self.component,self.link,self.head})==7
  self.fields={}
  self.expected_clear=(self.component+16,432)
  self.patch_model(self.component+16,bytes(432))
  rows=[(0x374094,o.tls+0x2000+304,4,0),(0x3ae358,o.tls+0x2000+304,4,0),
   (0x3801b4,inner+91608,4,0),(0x379b00,inner+91420,4,0),
   (0x3afb88,self.core+128,4,0),(0x3c8284,self.core+128,4,0),
   (0x3c8cc8,self.component+8,8,0),(0x3c8ce4,self.component+448,4,0),
   (0x3c8ce8,self.component+24,4,1),(0x3c8cec,self.component+456,8,0),
   (0x3c8cfc,self.head,8,0),(0x3c8d20,self.head,8,self.head),(0x3c8d28,self.head+8,8,self.head),(0x3c8d2c,self.link+8,8,0),
   (0x3c8d4c,self.core+552,4,0),(0x3c8d5c,self.core+2820,16,0),
   (0x3c8698,self.core+192,8,0),(0x3c86bc,self.core+192,8,2),
   (0x36e190,outer+64,4,1),(0x36e190,outer+68,4,0)]
  for r,at,z,value in rows:self.fields[r,at,z]=value;self.patch_model(at,value.to_bytes(z,'little'))
  self.guards={
   0x36e178:(outer,n.base+0x36e670,outer+16,0),
   0x36e770:(inner,n.base+0x374050,n.base+0x1337fd8+32,n.base+0x1337fd8),
   0x3740b4:(self.core,n.base+0x3ae320,n.base+0x1338428+296,n.base+0x1338428),
   0x36e794:(inner,n.base+0x370ec0,n.base+0x1337fd8+8,n.base+0x1337fd8),
   0x379968:(inner+93032,n.base+0x36ec00,n.base+0x1338028,n.base+0x1338028),
   0x379a6c:(self.interface,n.base+0x3a8730,self.interface+312,0),
   0x3a8754:(self.core,n.base+0x3af540,n.base+0x1338428+312,n.base+0x1338428),
   0x3af560:(self.core+8,n.base+0x3aebb0,n.base+0x13383b8+104,n.base+0x13383b8),
   0x379b1c:(inner+93032,n.base+0x36ec10,n.base+0x1338028+8,n.base+0x1338028),
   0x370f0c:(self.interface,n.base+0x3a7f90,self.interface+96,0),
   0x3a7fc0:(self.core,n.base+0x3afb60,n.base+0x1338428+16,n.base+0x1338428)}
  self.instructions={}
  for row in AUTH['source_authority']:
   r=int(row['RVA'],16);z=row['bytes'];raw=CF.p.get_data(r,z);assert hashlib.sha256(raw).hexdigest()==row['sha256']
   for i in CF.c.disasm(raw,n.base+r):self.instructions[i.address]=i
  self.visits=0;self.executed=0;self.writes=0;self.pending={};self.calls=collections.Counter();self.adapters=collections.Counter();self.negative_count=0
  self.clear_completed=False;self.leave_completed=False;self.cookie_trace=[]
  self.allocs=f.allocs.copy();self.released=f.released.copy();self.next=f.next
  self.crt_state=(self.b.allocs.copy(),self.b.next_alloc,self.b.depths.copy(),self.b.api_events.copy())
  self.pages=self.j.pages();self.root_before=o.root_lock_snapshot();assert self.root_before=={'depth':1,'events':{'EnterCriticalSection':1}}
  assert f.readq(o.output)==outer and f.readq(n.base+0x1798460)==outer and f.readq(outer+40)==inner
  self.diagnostics_before=o.new_diagnostic_sites.copy()
  self.hooks=[type(self.u).hook_add(self.u,UC_HOOK_CODE,self.code),type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.memory),type(self.u).hook_add(self.u,UC_HOOK_MEM_READ,self.read)]
 def snapshot(self):return {name:bytes(self.u.mem_read(at,z)) for name,at,z in self.regions}
 def patch_model(self,at,raw):
  name,base,z=next((name,base,z) for name,base,z in self.regions if name in self.models and name!='stack' and base<=at and at+len(raw)<=base+z)
  self.models[name][at-base:at-base+len(raw)]=raw
 def contract(self,site,args):
  o=self.o;n=self.n;u=self.u;f=self.f
  assert self.calls[site]==0
  if site in self.guards:
   receiver,target,cell,vt=self.guards[site]
   assert args==[receiver,target,cell]
   assert f.readq(cell)==target
   if vt:assert f.readq(receiver)==vt and CF.p.get_qword_at_rva(cell-n.base)==CF.p.OPTIONAL_HEADER.ImageBase+target-n.base
   elif receiver==o.outer:assert f.readq(o.output)==receiver and f.readq(receiver+40)==o.inner
   else:assert receiver==self.interface and f.readq(o.inner+8)==receiver
  elif site==0x3c51d0:
   assert args==[0,n.base+0x16a4230,0] and f.readq(n.base+0x16a4230)==0 and o.target_origins.get('x15')==(0x16a4230,n.base+0x16a4230)
  elif site==0x3c8cdc:
   assert args==[self.component+16,0,432] and f.readq(self.core+16)==self.component and not self.clear_completed
  elif site==0x36e2b0:
   assert args==[0x9006c008,n.base+0x36e2b4,0x90070020] and o.root_lock_snapshot()==self.root_before and not self.leave_completed
   assert f.readq(n.base+CV.CO.IMPORTS['LeaveCriticalSection'])==args[2]
  elif site==0x36e368:
   sp=u.reg_read(UC_ARM64_REG_SP);encoded=f.readq(sp+8);cookie=f.readq(n.base+0x1607000)
   assert args==[sp,encoded,cookie] and sp==o.cookie_frame_SP and encoded==o.cookie_encoded
   assert (sp-encoded)&MASK==cookie==o.cookie_value and not self.cookie_trace
  else:raise AssertionError('unqualified return contract')
 def negatives(self,site,args):
  requests=[(site+1,args),(site,args+[0])]
  for k in range(len(args)):
   bad=args.copy();bad[k]+=1;requests.append((site,bad))
  before=self.snapshot();state=(self.calls.copy(),self.o.root_lock_snapshot(),self.j.pages(),self.f.allocs.copy(),self.b.depths.copy())
  for req in requests:
   try:self.contract(*req)
   except AssertionError:pass
   else:raise AssertionError('invalid return scope admitted')
  assert self.snapshot()==before and state==(self.calls.copy(),self.o.root_lock_snapshot(),self.j.pages(),self.f.allocs.copy(),self.b.depths.copy())
  self.negative_count+=len(requests)
 def before_hook(self,pc):
  n=self.n;u=self.u;r=pc-n.base
  if r in self.guards:
   expected=self.guards[r];args=[u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X15),expected[2]]
  elif r==0x3c51d0:args=[u.reg_read(UC_ARM64_REG_X15),n.base+0x16a4230,0]
  elif r==0x3c8cdc:args=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(3)]
  elif r==0x36e2b0:args=[u.reg_read(UC_ARM64_REG_X0),n.base+0x36e2b4,self.f.readq(n.base+CV.CO.IMPORTS['LeaveCriticalSection'])]
  elif r==0x36e368:
   sp=u.reg_read(UC_ARM64_REG_SP);args=[sp,self.f.readq(sp+8),self.f.readq(n.base+0x1607000)]
  else:return
  self.contract(r,args);self.negatives(r,args);self.calls[r]+=1
  if r in self.guards:CF.NUMERIC[r]={args[1]-n.base}
 def code(self,u,pc,size,user):
  assert not self.pending
  n=self.n;o=self.o;r=pc-n.base
  if pc==0x90070020:
   assert self.calls[0x36e2b0]==1 and u.reg_read(UC_ARM64_REG_PC)==n.base+0x36e2b4 and u.reg_read(UC_ARM64_REG_LR)==n.base+0x36e2b4
   assert o.root_lock_snapshot()=={'depth':0,'events':{'EnterCriticalSection':1,'LeaveCriticalSection':1}}
   self.leave_completed=True;return
  if r==0x3c8ce0:
   assert self.calls[0x3c8cdc]==1 and bytes(u.mem_read(self.component+16,432))==bytes(432)
   assert u.reg_read(UC_ARM64_REG_X0)==self.component+16;self.clear_completed=True
  if r==0x36e36c:
   assert self.cookie_trace==list(range(0x11f0,0x1210,4))
   assert u.reg_read(UC_ARM64_REG_SP)==o.cookie_frame_SP+16 and u.reg_read(UC_ARM64_REG_X16)==o.cookie_value
  assert pc in self.instructions,('unqualified return instruction',hex(r))
  i=self.instructions[pc];assert bytes(u.mem_read(pc,4))==CF.p.get_data(r,4)
  self.visits+=1
  if u.reg_read(UC_ARM64_REG_PC)!=pc:
   assert r in {*self.guards,0x3c51d0,0xce7c98,0x1a8c0,0xf5e600}
   if r==0xf5e600:assert self.calls[0x3c8cdc]==1 and u.reg_read(UC_ARM64_REG_LR)==n.base+0x3c8ce0
   self.adapters[r]+=1;return
  self.executed+=1
  if 0x11f0<=r<0x1210:
   assert self.calls[0x36e368]==1;self.cookie_trace.append(r)
  self.pending_pc=pc
  if i.mnemonic.startswith(('stp','str','stur','stlxr')):
   operand=next(op for op in i.operands if op.type==3);mem=operand.mem;assert not mem.index
   at=CV.reg(u,CF.c.reg_name(mem.base))+mem.disp;first=1 if i.mnemonic=='stlxr' else 0;name=CF.c.reg_name(i.operands[first].reg)
   width=2 if i.mnemonic.endswith('h') or name.startswith('h') else 1 if i.mnemonic.endswith('b') or name.startswith('b') else 16 if name.startswith('q') else 8 if name in ('fp','lr') or name.startswith(('x','d')) else 4
   ops=i.operands[:2] if i.mnemonic=='stp' else i.operands[first:first+1]
   for k,op in enumerate(ops):
    address=at+k*width;value=CV.reg(u,CF.c.reg_name(op.reg))&((1<<(8*width))-1)
    if n.stack<=address and address+width<=n.stack+65536:
     off=address-n.stack;self.models['stack'][off:off+width]=value.to_bytes(width,'little')
    else:assert (r,address,width) in self.fields and self.fields[r,address,width]==value,('unowned return store',hex(r),width,address-self.core,value)
    for j in range(0,width,8):z=min(width-j,8);self.pending[address+j,z]=(value>>(8*j))&((1<<(8*z))-1)
 def memory(self,u,access,at,size,value,user):
  assert u.reg_read(UC_ARM64_REG_PC)==self.pending_pc and (at,size) in self.pending
  assert value&((1<<(8*size))-1)==self.pending.pop((at,size));self.writes+=1
 def read(self,u,access,at,size,value,user):
  assert at+size<=self.b.utf_output or at>=self.b.utf_output+74,'read of retired Unicode owner'
 def run(self):
  o=self.o;u=self.u;n=self.n;o.active=True;o.cy_active=True
  try:u.emu_start(n.base+0x36e178,n.end,count=200000)
  finally:
   o.active=False;o.cy_active=False
   for hook in self.hooks:u.hook_del(hook)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end and u.reg_read(UC_ARM64_REG_W0)==0 and not self.pending
  assert self.visits==575 and self.executed==560 and self.writes==111,(self.visits,self.executed,self.writes)
  assert self.clear_completed and self.leave_completed and self.cookie_trace==list(range(0x11f0,0x1210,4))
  assert dict(self.calls)==dict.fromkeys([*self.guards,0x3c51d0,0x3c8cdc,0x36e2b0,0x36e368],1)
  assert self.negative_count==75
  assert dict(self.adapters)==dict.fromkeys([*self.guards,0x3c51d0,0xce7c98,0x1a8c0,0xf5e600],1)
  after=self.snapshot();assert all(after[k]==self.models.get(k,v) for k,v in self.before.items()),'independent entire return memory model'
  assert self.f.allocs==self.allocs and self.f.released==self.released and self.f.next==self.next
  assert (self.b.allocs,self.b.next_alloc,self.b.depths,self.b.api_events)==self.crt_state and self.j.pages()==self.pages
  assert o.root_lock_snapshot()=={'depth':0,'events':{'EnterCriticalSection':1,'LeaveCriticalSection':1}}
  assert u.reg_read(UC_ARM64_REG_SP)==o.incoming_SP
  assert all(u.reg_read(globals()['UC_ARM64_REG_X'+str(k)])==v for k,v in o.incoming_caller.items())
  assert all(u.reg_read(globals()['UC_ARM64_REG_D'+str(k)])==v for k,v in o.incoming_float.items())
  assert self.f.readq(o.output)==o.outer and self.f.readq(o.outer+40)==o.inner and self.f.readq(n.base+0x1798460)==o.outer
  assert self.f.readq(self.link)==self.head and self.f.readq(self.head)==self.head and self.f.readq(self.head+8)==self.head and self.f.readq(self.link+8)==0
  assert {r:value for r,value in o.new_diagnostic_sites.items() if r not in self.diagnostics_before}=={0x3c51d0:0x16a4230}
  self.b.policy.check_pages()
  return {'source_guarded_OEM_visits':self.visits,'unchanged_executed_OEM_instructions':self.executed,'inherited_typed_adapter_entries':sum(self.adapters.values()),
   'exact_source_store_chunks':self.writes,'strict_owned_clear_bytes':432,'invalid_callback_clear_leave_cookie_requests_rejected':self.negative_count,
   'whole_original_outer_return_under_declared_ABI_fixtures':True,'status_W0':0,
   'actual_incoming_SP_X19_X29_D8_D15_restored':True,'independent_entire_stack_camera_caller_models':True,'all_other_entire_regions_immutable':True,
   'actual_permissions_and_allocation_CRT_state_unchanged':True,'same_logical_camera_root_lock_enter_and_leave_balanced':True,
   'original_outer_cookie_producer_instructions':6,'original_outer_cookie_checker_instructions':8,
   'original_interface_core_embedded_callbacks_execute_unchanged':True,'original_output_and_global_publication_retained':True,
   'clear_helper_is_strict_owned_library_adapter':True,'retired_UTF16_no_reads':True,'native_rear_runtime_allowed':False}
ROWS=[]
class Startup(CX.Startup):
 def hook(self,u,pc,size,user):
  r=pc-self.n.base
  if r==0x36cba0:
   self.incoming_caller={k:u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(19,30)}
   self.incoming_float={k:u.reg_read(globals()['UC_ARM64_REG_D'+str(k)]) for k in range(8,16)}
   self.incoming_SP=u.reg_read(UC_ARM64_REG_SP);self.cookie_producer_trace=[]
  if r==0x11d0 and u.reg_read(UC_ARM64_REG_LR)==self.n.base+0x36cbd0:
   self.cookie_input_SP=u.reg_read(UC_ARM64_REG_SP);self.cookie_frame_SP=self.cookie_input_SP-16
   self.cookie_value=self.f.readq(self.n.base+0x1607000);assert self.cookie_value==CF.p.get_qword_at_rva(0x1607000)
   self.cookie_encoded=(self.cookie_frame_SP-self.cookie_value)&MASK
   self.cookie_stack_before=bytes(u.mem_read(self.n.stack,65536))
   self.cookie_registers={k:u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(31) if k!=17}
  if 0x11d0<=r<0x11e8 and u.reg_read(UC_ARM64_REG_LR)==self.n.base+0x36cbd0:
   assert bytes(u.mem_read(pc,4))==CF.p.get_data(r,4);self.cookie_producer_trace.append(r)
  if r==0x36cbd0:
   assert self.cookie_producer_trace==list(range(0x11d0,0x11e8,4))
   assert u.reg_read(UC_ARM64_REG_SP)==self.cookie_frame_SP and self.f.readq(self.cookie_frame_SP+8)==self.cookie_encoded
   expected=bytearray(self.cookie_stack_before);off=self.cookie_frame_SP+8-self.n.stack;expected[off:off+8]=self.cookie_encoded.to_bytes(8,'little')
   assert bytes(u.mem_read(self.n.stack,65536))==expected
   assert all(u.reg_read(globals()['UC_ARM64_REG_X'+str(k)])==v for k,v in self.cookie_registers.items())
  if getattr(self,'cy_active',False):self.return_proof.before_hook(pc)
  return super().hook(u,pc,size,user)
 def invoke_entry(self):
  try:CX.Startup.invoke_entry(self)
  except CW.BoundedStop:pass
  u=self.u;n=self.n;j=self.cw_join
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x36e178
  assert self.cookie_producer_trace==list(range(0x11d0,0x11e8,4))
  # Explicit extended owned TEB/TLS-array ABI fixture; no claim of an actual Windows loader producer.
  assert self.f.readq(j.teb+88)==0 and self.f.readq(self.tls+88)==self.tls+0x1000
  u.mem_write(j.teb+88,struct.pack('<Q',self.tls+0x1000))
  leave=CV.CO.IMPORTS['LeaveCriticalSection'];original=self.cy_old_bindings[leave];assert int.from_bytes(original,'little')==0x90070020
  u.mem_write(n.base+leave,original)
  self.return_proof=ReturnProof(self);detail=self.return_proof.run()
  ROWS.append({'inherited_publication':CX.ROWS[-1],'outer_return':detail})
  raise CW.BoundedStop()
CP.Startup=Startup
def authority():
 p=CF.p;c=CF.c
 i=next(c.disasm(p.get_data(0x11d0,4),0x11d0));assert i.mnemonic=='sub' and [c.reg_name(o.reg) for o in i.operands[:2]]==['sp','sp'] and i.operands[2].imm==16
 i=next(c.disasm(p.get_data(0x11dc,4),0x11dc));assert i.mnemonic=='sub' and [c.reg_name(o.reg) for o in i.operands]==['x17','sp','x17']
 i=next(c.disasm(p.get_data(0x11e0,4),0x11e0));assert i.mnemonic=='str' and c.reg_name(i.operands[0].reg)=='x17' and c.reg_name(i.operands[1].mem.base)=='sp' and i.operands[1].mem.disp==8
 i=next(c.disasm(p.get_data(0x11fc,4),0x11fc));assert i.mnemonic=='sub' and [c.reg_name(o.reg) for o in i.operands]==['x16','sp','x16']
 i=next(c.disasm(p.get_data(0x1208,4),0x1208));assert i.mnemonic=='add' and i.operands[2].imm==16
 for site,target in [(0x36cbcc,0x11d0),(0x36e368,0x11f0),(0x3c8cdc,0xf5e600)]:
  i=next(c.disasm(p.get_data(site,4),site));assert i.mnemonic=='bl' and i.operands[0].imm==target
def main():
 authority();rows=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  for mode in ('ANSI','OEM'):
   CP.CP_MODE=mode;ROWS.clear();CX.ROWS.clear();CW.ROWS.clear();CW.CS.CASES.clear();CW.CS.CR.CASES.clear();CW.CS.CR.CQ.CASES.clear()
   try:CP.integrated(blob,pin,CW.camera)
   except CW.BoundedStop:assert len(ROWS)==1
   else:raise AssertionError('strict outer return not captured')
   row={'policy':mode,'source_sha256':pin,**ROWS[0]};rows.append(row);print(json.dumps({'policy':mode,'source_sha256':pin,**row['outer_return']}),flush=True)
 result={'experiment':'E011CY','status':'PASS_BOUNDED_ORIGINAL_PUBLICATION_CALLBACK_AND_OUTER_RETURN','base_commit':'3a26bff9d332c9f2e8c95fa29b510e109e7bbc96',
  'sources':rows,'source_authority':AUTH['source_authority'],'integrated_camera_cases':len(rows),'distinct_tuning_sources':3,
  'source_guarded_OEM_visits':sum(r['outer_return']['source_guarded_OEM_visits'] for r in rows),
  'unchanged_executed_OEM_instructions':sum(r['outer_return']['unchanged_executed_OEM_instructions'] for r in rows),
  'inherited_typed_adapter_entries':sum(r['outer_return']['inherited_typed_adapter_entries'] for r in rows),
  'exact_source_store_chunks':sum(r['outer_return']['exact_source_store_chunks'] for r in rows),
  'strict_owned_clear_bytes':sum(r['outer_return']['strict_owned_clear_bytes'] for r in rows),
  'invalid_scope_requests_rejected':sum(r['outer_return']['invalid_callback_clear_leave_cookie_requests_rejected'] for r in rows),
  'original_outer_cookie_producer_instructions':36,'original_outer_cookie_checker_instructions':48,
  'whole_memory_permissions_resources_and_actual_caller_checks':True,'same_logical_camera_root_locks_balanced':True,
  'original_publication_callback_and_whole_outer_return_under_explicit_ABI_fixtures':True,
  'actual_windows_loader_Default_CRT_TLS_locale_concurrency_qualified':False,'original_CFE600_qualified':False,
  'original_F5E600_implementation_qualified':False,'all_nested_cookie_helpers_qualified':False,
  'hardware_WM16_IRQ_IOVA_DMA_IOMMU_retirement_qualified':False,'native_rear_runtime_allowed':False,
  'new_camera_Starts':0,'new_reboots':0,'new_Linux_image_tests':0,'next_experiment':'E011CZ'}
 assert len(rows)==6
 (OUT/'OUTER-RETURN-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(list,dict))}),flush=True)
if __name__=='__main__':main()
