#!/usr/bin/env python3
"""Bounded original factory cold-prefix proof under explicit owned loader/SRW models."""
from pathlib import Path
import importlib.util,hashlib,json
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
P=ROOT/'experiments/E004-front-ir-vd55g0/e011de-original-startup-guard-sequence/source-private.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='948969eebad0a326f5525e8e1a834768586e1db4f3b5957aa0ef4aa9378749c6'
s=importlib.util.spec_from_file_location('df_de',P);DE=importlib.util.module_from_spec(s);s.loader.exec_module(DE)
DC=DE.DC;CV=DE.CV;p=DE.p;c=DE.c;REGS=DC.REGS
FACTORY_PIN='5231dea192141b25677216b06fce4906a0a55af1a7cca139ce177dde2d432653'
assert hashlib.sha256(p.get_data(0x5bde08,4008)).hexdigest()==FACTORY_PIN
PRESERVED=[UC_ARM64_REG_SP,*[globals()['UC_ARM64_REG_X'+str(k)] for k in range(19,30)],*[globals()['UC_ARM64_REG_D'+str(k)] for k in range(8,16)]]
class Prefix(DE.GuardSequence):
 def __init__(self,bias,index,epoch):
  super().__init__(bias,index,epoch)
  n=self.n;u=self.u;self.guard=n.base+0x1b302d0
  assert self.rd(self.guard)==0 and epoch in (0x80000000,0xffffff00)
  self.sp=n.stack+0xf000-bias
  self.source_ranges=[(0x5bde08,4008),(0x11d0,24),(0x11f0,32),(0xce7ad8,188)]
  self.instructions={i.address:i for r,z in self.source_ranges for i in c.disasm(p.get_data(r,z),n.base+r)}
  self.expected_apis=['AcquireSRWLockExclusive','ReleaseSRWLockExclusive'];self.phase='fresh'
  self.negatives=0;self.entry=0x5bde08;self.header_saved=None;self.header_count=0;self.header_done=False;self.stopped=False
  for k in range(19,30):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0x123000+k+bias)
  for k in range(8,16):u.reg_write(globals()['UC_ARM64_REG_D'+str(k)],0x456000+k+bias)
  u.reg_write(UC_ARM64_REG_SP,self.sp);u.reg_write(UC_ARM64_REG_LR,n.end)
  self.field_plan={(0xce7b14,self.guard,4):0xffffffff,(0x5be68c,n.base+0x18a296c,4):0,
   (0x5be694,n.base+0x1b302a0,8):0,(0x5be694,n.base+0x1b302a8,8):0}
 def layout(self):
  n=self.n
  assert self.lock_ready and self.cv_ready
  assert self.u.reg_read(UC_ARM64_REG_X18)==self.teb
  assert self.rd(n.base+0x16a3740)==self.index and self.rd(self.teb+88,8)==self.array
  assert self.rd(self.array+self.index*8,8)==self.block
  assert self.rd(self.block+16)==self.initial_epoch and self.rd(n.base+0x1607b04)==self.initial_epoch
  assert all(self.rd(cell,8)==target for cell,target in self.bindings.items())
 def contract(self,entry,args):
  self.layout();n=self.n;u=self.u
  assert entry==0x5bde08 and args==[self.sp,n.end,self.teb]
  assert u.reg_read(UC_ARM64_REG_SP)==self.sp and u.reg_read(UC_ARM64_REG_LR)==n.end
  assert not self.held and self.rd(self.guard)==0
 def header_contract(self,entry,args):
  self.layout();n=self.n;u=self.u
  assert entry==0xce7ad8 and args==[self.guard,n.base+0x5be680]
  assert u.reg_read(UC_ARM64_REG_X0)==self.guard and u.reg_read(UC_ARM64_REG_LR)==n.base+0x5be680
  assert self.header_saved is None and not self.held and self.rd(self.guard)==0
 def stop_contract(self,site,target,args):
  self.layout();n=self.n;u=self.u
  assert site==0x5be698 and target==0xcae740 and args==[48]
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+site and u.reg_read(UC_ARM64_REG_X0)==48
  assert self.header_done and not self.held and self.next_api==2 and self.rd(self.guard)==0xffffffff
  assert all(self.rd(a,z)==v for (r,a,z),v in self.field_plan.items())
 def expect_invalid(self,fn,tests):self.reject(fn,tests)
 def actual_invalid(self,fn,args,fixtures):
  for cell,value,size in fixtures:
   old=bytes(self.u.mem_read(cell,size));self.wr(cell,value,size)
   try:self.reject(fn,[args])
   finally:self.u.mem_write(cell,old)
 def flags_invalid(self,fn,args,fixtures):
  for field,value in fixtures:
   old=getattr(self,field);setattr(self,field,value)
   try:self.reject(fn,[args])
   finally:setattr(self,field,old)
 def code(self,u,pc,z,user):
  assert not self.pending;n=self.n
  if pc in self.reverse:
   name=self.reverse[pc];ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_X0)]
   self.dependency(name,ret,args)
   self.reject(lambda ret,args:self.dependency(name,ret,args),[(ret+4,args),(ret,[args[0]+8]),(ret,args+[0])])
   self.flags_invalid(lambda ret,args:self.dependency(name,ret,args),(ret,args),[('held',not self.held),('lock_ready',False)])
   if name=='AcquireSRWLockExclusive':self.held=True
   elif name=='ReleaseSRWLockExclusive':self.held=False
   else:raise AssertionError('unsupported factory dependency')
   self.next_api+=1;u.reg_write(UC_ARM64_REG_X0,0xdead0101+self.bias);u.reg_write(UC_ARM64_REG_PC,ret);return
  r=pc-n.base;assert pc in self.instructions and bytes(u.mem_read(pc,4))==p.get_data(r,4)
  if r==0x5be698:
   i=self.instructions[pc];assert i.mnemonic=='bl' and i.operands[0].type==2 and i.operands[0].imm==n.base+0xcae740
   self.stop_contract(r,0xcae740,[u.reg_read(UC_ARM64_REG_X0)])
   self.reject(self.stop_contract,[(r+4,0xcae740,[48]),(r,0xcae744,[48]),(r,0xcae740,[49]),(r,0xcae740,[48,0])])
   self.flags_invalid(self.stop_contract,(r,0xcae740,[48]),[('held',True),('header_done',False)])
   self.actual_invalid(self.stop_contract,(r,0xcae740,[48]),[(self.guard,0,4),(n.base+0x1b302a0,1,8)])
   self.stopped=True;u.emu_stop();return
  assert len(self.trace)<200;self.trace.append(r)
  if r==0xce7ad8:
   args=[u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_LR)];self.header_contract(r,args)
   self.reject(self.header_contract,[(r+4,args),(r,[args[0]+4,args[1]]),(r,[args[0],args[1]+4]),(r,args+[0])])
   self.flags_invalid(self.header_contract,(r,args),[('held',True)])
   self.header_saved={k:u.reg_read(k) for k in PRESERVED}
  if 0xce7ad8<=r<0xce7b94:self.header_count+=1
  if r==0x5be680:
   assert self.header_saved and all(u.reg_read(k)==v for k,v in self.header_saved.items())
   assert self.header_count==26 and self.rd(self.guard)==0xffffffff and not self.held
   self.header_done=True
  i=self.instructions[pc]
  if i.mnemonic.startswith(('str','stp','stur')):
   op=next(o for o in i.operands if o.type==3);assert not op.mem.index
   at=CV.reg(u,c.reg_name(op.mem.base))+op.mem.disp
   first=c.reg_name(i.operands[0].reg);width=8 if first.startswith(('x','d')) or first in ('fp','lr') else 4
   dataops=i.operands[:2] if i.mnemonic=='stp' else i.operands[:1]
   for k,o in enumerate(dataops):
    address=at+k*width;value=CV.reg(u,c.reg_name(o.reg))&((1<<(8*width))-1)
    if n.stack<=address and address+width<=n.stack+65536:self.patch(address,value.to_bytes(width,'little'))
    else:assert self.field_plan.get((r,address,width))==value,('unowned factory write',hex(r),width)
    self.pending[address,width]=value
 def memory(self,u,access,at,z,value,user):
  planned=self.pending.pop((at,z),None)
  assert planned is not None and planned==(value&((1<<(8*z))-1)),('source-store mismatch',hex(u.reg_read(UC_ARM64_REG_PC)-self.n.base),z)
  self.stores+=1
 def read(self,u,access,at,z,value,user):
  n=self.n
  if n.stack<=at and at+z<=n.stack+65536:return
  allowed={(n.base+0x1607000,8),(self.guard,4),(n.base+0x16a3740,4),(self.teb+88,8),
   (self.array+self.index*8,8),(self.block+16,4)}|{(cell,8) for cell in self.bindings}
  assert (at,z) in allowed,('unowned prefix read',hex(at-n.base),z)
 def run(self):
  n=self.n;u=self.u;args=[self.sp,n.end,self.teb];self.contract(self.entry,args)
  bad=[(self.entry+4,args),(self.entry,args+[0])]
  for k in range(3):
   a=args.copy();a[k]+=1;bad.append((self.entry,a))
  self.reject(self.contract,bad)
  self.flags_invalid(self.contract,(self.entry,args),[('held',True),('lock_ready',False),('cv_ready',False)])
  fixtures=[(self.guard,1,4),(n.base+0x16a3740,self.index+1,4),(self.teb+88,self.array+8,8),
   (self.array+self.index*8,self.block+8,8),(self.block+16,41,4),(n.base+0x1607b04,41,4)]
  fixtures +=[(cell,target+4,8) for cell,target in self.bindings.items()]
  self.actual_invalid(self.contract,(self.entry,args),fixtures)
  self.before=self.snapshot();self.models={};self.pending={};self.trace=[];self.stores=0
  for (r,at,z),value in self.field_plan.items():self.patch(at,value.to_bytes(z,'little'))
  hooks=[u.hook_add(UC_HOOK_CODE,self.code),u.hook_add(UC_HOOK_MEM_WRITE,self.memory),u.hook_add(UC_HOOK_MEM_READ,self.read)]
  try:u.emu_start(n.base+self.entry,n.end,count=300)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.stopped and self.header_done and not self.pending and not self.held and self.next_api==2 and self.wake==0
  assert len(self.trace)==84 and self.header_count==26 and self.stores==22 and self.negatives==40
  after=self.snapshot();assert after.keys()==self.before.keys()
  assert all(after[k]==self.models.get(k,v) for k,v in self.before.items()),'entire prefix memory model'
  assert self.layout() is None
  return {'placement_bias':self.bias,'owned_loader_index':self.index,'owned_cold_epoch':self.initial_epoch,
   'executed_original_instructions':len(self.trace),'executed_original_header_instructions':self.header_count,
   'exact_source_store_chunks':self.stores,'invalid_requests_rejected_before_effects':self.negatives,
   'whole_memory_actual_permissions_and_ordered_logical_SRW_checks':True,
   'actual_guard_caller_SP_and_nonvolatile_preserved':True,'allocator_call_executed':False}
def main():
 rows=[]
 for bias in (0,16,128,512):
  for index in (0,37):
   for epoch in (0x80000000,0xffffff00):
    row=Prefix(bias,index,epoch).run();rows.append(row)
    print(json.dumps({'case':len(rows),'status':'PASS_BOUNDED_FACTORY_GUARD_PREFIX'}),flush=True)
 result={'experiment':'E011DF-private-verifier','status':'PASS_BOUNDED_ORIGINAL_FACTORY_GUARD_PREFIX','cases':rows,
  'executed_original_instructions':sum(r['executed_original_instructions'] for r in rows),
  'exact_source_store_chunks':sum(r['exact_source_store_chunks'] for r in rows),
  'invalid_requests_rejected':sum(r['invalid_requests_rejected_before_effects'] for r in rows),
  'stop_before_source_call_RVA':'0x5be698','unexecuted_allocator_target_RVA':'0xcae740','requested_bytes':48,
  'source_factory_guard_RVA':'0x1b302d0','guard_to_FFFFFFFF':True,
  'full_factory_parent_ABI_return_Default_native_OS_allocator_and_hardware_qualified':False,
  'new_camera_Starts':0,'new_reboots':0,'native_rear_runtime_allowed':False}
 assert len(rows)==16 and result['executed_original_instructions']==1344 and result['exact_source_store_chunks']==352 and result['invalid_requests_rejected']==640
 (OUT/'ORIGINAL-FACTORY-GUARD-PREFIX-V4-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='cases'}),flush=True)
if __name__=='__main__':main()
