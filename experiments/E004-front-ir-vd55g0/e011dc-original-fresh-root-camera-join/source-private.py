#!/usr/bin/env python3
"""Fresh source-created root, strict success path and registered camera join under typed dependencies."""
from pathlib import Path
import importlib.util,hashlib,json,struct,collections,inspect
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
P=ROOT/'experiments/E004-front-ir-vd55g0/e011db-original-callback-registration-join/source-private.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='0ed454910404748f60451bd64527d0fa5c2a0894f1bf97e7d2c923d54d473f3d'
s=importlib.util.spec_from_file_location('dc_db',P);DB=importlib.util.module_from_spec(s);s.loader.exec_module(DB)
DA=DB.DA;CF=DB.CF;CP=DB.CP;CW=DB.CW;CV=DB.CV
NAME_RVA=0x13a80a8;raw=CF.p.get_data(NAME_RVA,128);NAME=raw[:raw.index(0)+1]
assert len(NAME)==12 and hashlib.sha256(NAME).hexdigest()=='1610d60ddb99fd7c26d9fc1ceaa75be05479d683c86008e2ce84e3c0415d4bcd'
HELPER=CF.p.get_data(0xcae7c0,248)
assert hashlib.sha256(HELPER).hexdigest()=='26f2545508e02bd0e83ce12d799f65e906966eeff43e44aae1ab4653a8adc5cf'
TRACE=(list(range(0x36e9c8,0x36ea0c,4))+list(range(0x36ea44,0x36ea90,4))+
 [0x36ea90,0x36ea94,0x36ea98]*5+list(range(0x36ea9c,0x36eabc,4))+
 [0xcae7c0,0xcae7c4,0xcae7c8,0xcae7cc,0xcae7e0,0xcae7e4,0xcae7e8,0xcae7f4,0xcae81c,0xcae820,0xcae824,0xcae828,0xcae82c,0xcae830]+
 [0xcae834,0xcae838,0xcae83c,0xcae840,0xcae844]*(len(NAME)-1)+[0xcae834,0xcae838,0xcae83c]+
 [0xcae7d8,0xcae7dc,0xcae810,0xcae814,0xcae818]+list(range(0x36eabc,0x36ead4,4))+list(range(0x36eb5c,0x36eb88,4)))
assert len(TRACE)==153
REGS=[*[globals()['UC_ARM64_REG_X'+str(k)] for k in range(31)],*[globals()['UC_ARM64_REG_Q'+str(k)] for k in range(32)],UC_ARM64_REG_SP,UC_ARM64_REG_PC,UC_ARM64_REG_NZCV,UC_ARM64_REG_FPCR,UC_ARM64_REG_FPSR]
# Replace only the inherited owned malloc adapter for this exact fresh-root source call.
# All other caller/profile adapters and observers remain enabled.
ACTIVE_FRESH={}
# CY's already-installed cookie wrapper delegates through this exact saved loader hook.
legacy_allocator_hook=DA.CY.legacy_cookie_hook
assert '0xcae740' in inspect.getsource(legacy_allocator_hook).lower()
assert DA.CY.cookie_class.hook is DA.CY.outer_cookie_hook
def fresh_allocator_hook(self,u,pc,z,user):
 proof=ACTIVE_FRESH.get(id(u))
 if proof and pc==proof.n.base+0xcae740 and u.reg_read(UC_ARM64_REG_LR)==proof.n.base+0x36ea80:
  proof.dependency('allocator',u.reg_read(UC_ARM64_REG_LR),[u.reg_read(UC_ARM64_REG_X0)])
  assert u.reg_read(UC_ARM64_REG_PC)==pc
  return
 return legacy_allocator_hook(self,u,pc,z,user)
DA.CY.legacy_cookie_hook=fresh_allocator_hook

class FreshRoot(DB.Registration):
 def __init__(self,n,table,root,stack,api,o=None):
  super().__init__(n,table,root,stack,o);self.api=api
  self.instructions.update({i.address:i for i in CF.c.disasm(HELPER,n.base+0xcae7c0)})
  self.void_x0=0 if o else {0:root+8,16:0,128:0x12340001,512:0xffffffff}[(table-n.heap-0x1000)]
  self.owned_initialized=False;self.allocator_count=0;self.os_count=0;self.name_count=0
 def contract(self,entry,args):
  assert entry==0x36e9c8 and args==self.request
  assert self.u.reg_read(UC_ARM64_REG_X0)==self.table and self.q(self.n.base+0x1798458)==0
  assert self.table%8==self.root%8==0 and self.table!=self.root
  for at,size in ((self.table,48),(self.root,176),(self.stack,65536),(self.api,4)):
   assert any(a<=at and at+size<=b+1 for a,b,p in self.u.mem_regions())
  for (r,z),v in DB.CONTROL.items():assert int.from_bytes(self.u.mem_read(self.n.base+r,z),'little')==v
  assert self.q(self.n.base+0xf7e0c8)==self.api and not self.owned_initialized and self.allocator_count==self.os_count==0
 def dependency(self,kind,ret,args):
  if kind=='allocator':assert ret==self.n.base+0x36ea80 and args==[176] and self.allocator_count==0 and self.os_count==0
  elif kind=='critical_section':
   assert ret==self.n.base+0x36eacc and args==[self.root+8] and self.allocator_count==1 and not self.owned_initialized and self.os_count==0 and self.name_count==1
   assert self.q(self.n.base+0x1798458)==0 and bytes(self.u.mem_read(self.root,176))==bytes(48)+NAME+bytes(128-len(NAME))
  elif kind=='name_copy':assert ret==self.n.base+0x36eabc and args==[self.root+48,128,self.n.base+NAME_RVA,(1<<64)-1] and self.allocator_count==1 and self.name_count==self.os_count==0
  else:raise AssertionError('unknown dependency')
 def run(self):
  u=self.u;n=self.n;self.paused={r:u.reg_read(r) for r in REGS}
  u.reg_write(UC_ARM64_REG_X0,self.table);u.reg_write(UC_ARM64_REG_SP,self.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  self.request=[self.table,self.root,self.stack+0xf000,n.end,self.api]
  self.contract(0x36e9c8,self.request);self.before=self.snapshot();self.resources=self.o.helper_join.resources() if self.o else None
  self.incoming={r:u.reg_read(r) for r in [UC_ARM64_REG_SP,*[globals()['UC_ARM64_REG_X'+str(k)] for k in range(19,30)],*[globals()['UC_ARM64_REG_D'+str(k)] for k in range(8,16)]]}
  tests=[(0x36e9cc,self.request),(0x36e9c8,self.request+[0])]
  for k in range(5):
   bad=self.request.copy();bad[k]+=1;tests.append((0x36e9c8,bad))
  for entry,args in tests:
   try:self.contract(entry,args)
   except AssertionError:pass
   else:raise AssertionError('invalid fresh registration admitted')
  for kind,ret,args in [('allocator',n.base+0x36ea80,[176]),('name_copy',n.base+0x36eabc,[self.root+48,128,n.base+NAME_RVA,(1<<64)-1])]:
   if kind=='name_copy':self.allocator_count=1
   invalid=[(ret+4,args)]
   for k in range(len(args)):
    bad=args.copy();bad[k]+=1;invalid.append((ret,bad))
   for r,a in invalid:
    try:self.dependency(kind,r,a)
    except AssertionError:pass
    else:raise AssertionError('invalid dependency admitted')
   tests.extend(invalid)
  self.allocator_count=0
  assert self.snapshot()==self.before
  self.models={};self.pending={};self.trace=[];self.writes=0;self.reads=collections.Counter();self.adapter_events=[]
  self.fields={(0x36ea48,self.table,4):48,(0x36ea54,self.table+16,8):n.base+0x36e870,
   (0x36ea68,self.table+32,8):n.base+0x36cba0,(0x36ea68,self.table+40,8):n.base+0x36e900,
   (0x36eacc,n.base+0x1798458,8):self.root,(0x36eb64,self.root,4):1}
  self.patch(self.root,bytes(48)+NAME+bytes(128-len(NAME)))
  self.patch(self.root,struct.pack('<I',1))
  for (site,at,z),value in self.fields.items():self.patch(at,value.to_bytes(z,'little'))
  self.hooks=[type(u).hook_add(u,UC_HOOK_CODE,self.code),type(u).hook_add(u,UC_HOOK_MEM_WRITE,self.memory),type(u).hook_add(u,UC_HOOK_MEM_READ,self.read)]
  assert id(u) not in ACTIVE_FRESH;ACTIVE_FRESH[id(u)]=self
  try:u.emu_start(n.base+0x36e9c8,n.end,count=3000)
  finally:
   assert ACTIVE_FRESH.pop(id(u)) is self
   for hook in self.hooks:u.hook_del(hook)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end and u.reg_read(UC_ARM64_REG_X0)==self.void_x0 and not self.pending, ('return boundary',hex(u.reg_read(UC_ARM64_REG_PC)),hex(n.end),hex(u.reg_read(UC_ARM64_REG_X0)),hex(self.table),len(self.trace),len(self.pending))
  assert self.trace==TRACE and self.writes==50 and self.allocator_count==self.os_count==self.name_count==1 and self.owned_initialized
  after=self.snapshot();assert after.keys()==self.before.keys() and all(after[k]==self.models.get(k,v) for k,v in self.before.items()),'independent whole fresh-root memory'
  assert all(u.reg_read(r)==v for r,v in self.incoming.items())
  if self.o:assert self.o.helper_join.resources()==self.resources
  self.ref=0;self.root_extent=176;self.table_bytes=bytes(u.mem_read(self.table,48));self.frozen_stack=bytes(u.mem_read(self.stack,65536))
  self.table_region=next(k for k in after if k[0]<=self.table and self.table+48<=k[1]+1);self.frozen_table_region=after[self.table_region]
  self.frozen_root=bytes(u.mem_read(self.root,176));self.stack_region=next(k for k in after if k[0]<=self.stack and self.stack+65536<=k[1]+1)
  self.api_region=next(k for k in after if k[0]<=self.api<k[1]+1);self.frozen_api=after[self.api_region]
  self.root_entry=self.q(self.table+32);assert self.root_entry==n.base+0x36cba0
  for r,v in self.paused.items():u.reg_write(r,v)
  assert all(u.reg_read(r)==v for r,v in self.paused.items())
  self.qualified=True;self.negative_count=len(tests)+self.negative_count_extra
  self.detail={'original_fresh_root_instructions':len(self.trace),'exact_source_store_chunks':self.writes,'invalid_scope_requests_rejected':self.negative_count,
   'source_root_bytes':176,'source_root_name_NUL_bytes':len(NAME),'source_root_name_sha256':hashlib.sha256(NAME).hexdigest(),
   'source_created_root_global_publication_and_reference1':True,'source_created_callback_record_used':True,'registration_X0_is_residual_void_OS_fixture_not_status':True,'owned_void_OS_return_register':self.void_x0,
   'original_name_copy_helper_executed':True,'owned_allocator_calls':1,'owned_standard_OS_initialize_calls':1,
   'allocator_and_critical_section_are_typed_dependency_models':True,'whole_memory_permissions_resources_and_actual_caller_checked':True,
   'source_allocation_failure_and_root_cleanup_qualified':False,'actual_Default_provider_and_full_Windows_startup_qualified':False}
  self.before=None;self.models=None;return self.detail
 def code(self,u,pc,z,user):
  assert not self.pending
  n=self.n;r=pc-n.base
  if pc==n.base+0xcae740:
   self.dependency('allocator',u.reg_read(UC_ARM64_REG_LR),[u.reg_read(UC_ARM64_REG_X0)]);self.allocator_count+=1
   self.adapter_events.append('owned_176byte_allocation');u.reg_write(UC_ARM64_REG_X0,self.root);u.reg_write(UC_ARM64_REG_PC,n.base+0x36ea80);return
  if pc==self.api:
   self.dependency('critical_section',u.reg_read(UC_ARM64_REG_LR),[u.reg_read(UC_ARM64_REG_X0)])
   before=self.snapshot();regs={reg:u.reg_read(reg) for reg in REGS};invalid=[(n.base+0x36ead0,[self.root+8]),(n.base+0x36eacc,[self.root+16]),(n.base+0x36eacc,[self.root+8,0])]
   for ret,args in invalid:
    try:self.dependency('critical_section',ret,args)
    except AssertionError:pass
    else:raise AssertionError('invalid critical-section owner admitted')
   assert before==self.snapshot() and all(u.reg_read(reg)==v for reg,v in regs.items())
   self.owned_initialized=True;self.os_count+=1;self.negative_count_extra=len(invalid)
   self.adapter_events.append('owned_critical_section_initialization');u.reg_write(UC_ARM64_REG_X0,self.void_x0);u.reg_write(UC_ARM64_REG_PC,n.base+0x36eacc);return
  if r==0xcae7c0:
   self.dependency('name_copy',u.reg_read(UC_ARM64_REG_LR),[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(4)]);self.name_count+=1
  if r==0x36eabc:assert u.reg_read(UC_ARM64_REG_W0)==0
  if r==0x36eacc:assert self.owned_initialized and self.os_count==1
  assert pc in self.instructions and u.reg_read(UC_ARM64_REG_PC)==pc and bytes(u.mem_read(pc,4))==CF.p.get_data(r,4)
  assert len(self.trace)<len(TRACE) and r==TRACE[len(self.trace)];self.trace.append(r);self.pending_pc=pc
  i=self.instructions[pc]
  if i.mnemonic.startswith(('str','stp','stur','stlxr')):
   op=next(o for o in i.operands if o.type==3)
   at=CV.reg(u,CF.c.reg_name(op.mem.base))+op.mem.disp
   if op.mem.index:at+=CV.reg(u,CF.c.reg_name(op.mem.index))
   first=1 if i.mnemonic=='stlxr' else 0;name=CF.c.reg_name(i.operands[first].reg)
   width=1 if i.mnemonic.endswith('b') else 2 if i.mnemonic.endswith('h') else 16 if name.startswith('q') else 8 if name.startswith(('x','d')) or name in ('fp','lr') else 4
   for k,o in enumerate(i.operands[:2] if i.mnemonic=='stp' else i.operands[first:first+1]):
    address=at+k*width;value=CV.reg(u,CF.c.reg_name(o.reg))&((1<<(8*width))-1)
    if self.stack<=address and address+width<=self.stack+65536:self.patch(address,value.to_bytes(width,'little'))
    elif r==0x36ea90:assert width==16 and self.root<=address<self.root+160 and (address-self.root)%16==0 and value==0
    elif r==0x36ea9c:assert width==16 and address==self.root+160 and value==0
    elif r==0xcae838:assert width==1 and self.root+48<=address<self.root+48+len(NAME) and value==NAME[address-self.root-48]
    else:assert self.fields.get((r,address,width))==value,('unowned fresh-root store',hex(r),width)
    for j in range(0,width,8):q=min(width-j,8);self.pending[address+j,q]=(value>>(8*j))&((1<<(8*q))-1)
 def read(self,u,access,at,z,value,user):
  if self.stack<=at and at+z<=self.stack+65536:return
  allowed={(self.n.base+r,s) for r,s in DB.CONTROL}|{(self.n.base+0x1798458,8),(self.n.base+0xf7e0c8,8),(self.root,4)}
  assert (at,z) in allowed or z==1 and self.n.base+NAME_RVA<=at<self.n.base+NAME_RVA+len(NAME)
  self.reads['private_source_name' if self.n.base+NAME_RVA<=at<self.n.base+NAME_RVA+len(NAME) else 'declared_control_or_reference']+=1
 def final(self):
  super().final();assert self.owned_initialized and self.os_count==1 and self.api_region in list(self.u.mem_regions())
  a,b,p=self.api_region;assert bytes(self.u.mem_read(a,b-a+1))==self.frozen_api
def prepare(n,table,root,stack,api):
 u=n.u
 u.mem_write(n.base+0x1798458,bytes(8));u.mem_write(root,bytes([0xa5])*176)
 old=bytes(u.mem_read(n.base+0xf7e0c8,8));u.mem_write(n.base+0xf7e0c8,struct.pack('<Q',api));return old
ROWS=[]
class Startup(DA.Startup):
 def invoke_entry(self):
  u=self.u;n=self.n;assert not self.active
  for address in (0x97600000,0x97610000,0x97620000):u.mem_map(address,65536);u.mem_write(address,bytes([0xa5])*65536)
  api=0x97620100;u.mem_write(api,bytes.fromhex('c0035fd6'))
  root=self.f.readq(n.base+0x1798458);assert root==0x9006c000
  old=prepare(n,0x97611000,root,0x97600000,api)
  self.registration=FreshRoot(n,0x97611000,root,0x97600000,api,self);detail=self.registration.run()
  u.mem_write(n.base+0xf7e0c8,old)
  try:DA.Startup.invoke_entry(self)
  except CW.BoundedStop:pass
  self.registration.final();ROWS.append({'fresh_root':detail,'inherited_camera_join':DA.ROWS[-1],
   'source_created_176byte_root_retained_through_camera_return':True,'same_initialized_owned_root_lock_enter_leave_balanced':True})
  raise CW.BoundedStop()
CP.Startup=Startup
def isolated():
 rows=[]
 for bias in [0,16,128,512]:
  n=DA.CZ.N.Native();u=n.u;table=n.heap+0x1000+bias;root=n.heap+0x5000+bias;api=n.heap+0x2f000
  u.mem_write(n.heap,bytes([0xa5])*0x30000);u.mem_write(n.stack,bytes([0xd5])*65536);u.mem_write(api,bytes.fromhex('c0035fd6'))
  prepare(n,table,root,n.stack,api)
  for k in range(31):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0x111000+k)
  for k in range(8,16):u.reg_write(globals()['UC_ARM64_REG_D'+str(k)],0x222000+k)
  proof=FreshRoot(n,table,root,n.stack,api);detail=proof.run();proof.final();rows.append({'placement_bias':bias,**detail})
 print(json.dumps({'isolated_fresh_root_cases':len(rows),'original_instructions':sum(r['original_fresh_root_instructions'] for r in rows),'status':'PASS_BOUNDED_FRESH_ROOT'}),flush=True)
 return rows
def main():
 DA.CY.authority();standalone=isolated();rows=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  for mode in ('ANSI','OEM'):
   CP.CP_MODE=mode;ROWS.clear();DA.ROWS.clear();DA.CY.ROWS.clear();DA.CX.ROWS.clear();CW.ROWS.clear();CW.CS.CASES.clear();CW.CS.CR.CASES.clear();CW.CS.CR.CQ.CASES.clear()
   try:CP.integrated(blob,pin,CW.camera)
   except CW.BoundedStop:assert len(ROWS)==1
   else:raise AssertionError('fresh-root camera return not reached')
   rows.append({'source_sha256':pin,'policy':mode,**ROWS[0]});print(json.dumps({'policy':mode,'source_sha256':pin,**ROWS[0]['fresh_root'],'registered_camera_join':'PASS'}),flush=True)
 result={'experiment':'E011DC','status':'PASS_BOUNDED_ORIGINAL_FRESH_ROOT_AND_REGISTERED_CAMERA_JOIN',
  'base_commit':'e2b4cecabad3f8f7314040ca2694b3133dcb0e96','isolated_cases':standalone,'camera_cases':rows,
  'original_fresh_root_instructions':sum(r['original_fresh_root_instructions'] for r in standalone)+sum(r['fresh_root']['original_fresh_root_instructions'] for r in rows),
  'exact_source_store_chunks':sum(r['exact_source_store_chunks'] for r in standalone)+sum(r['fresh_root']['exact_source_store_chunks'] for r in rows),
  'allocator_and_standard_OS_critical_section_remain_typed_models':True,
  'actual_Default_provider_full_Windows_startup_preflight_RS_qualified':False,
  'fresh_root_failure_and_cleanup_qualified':False,'native_rear_runtime_allowed':False,'new_camera_Starts':0,'new_reboots':0,
  'production_C_or_kernel_changed':False,'next_experiment':'E011DD'}
 assert len(standalone)==4 and len(rows)==6 and result['original_fresh_root_instructions']==1530 and result['exact_source_store_chunks']==500
 (OUT/'FRESH-ROOT-CAMERA-JOIN-V5-SAFE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))}),flush=True)
if __name__=='__main__':main()
