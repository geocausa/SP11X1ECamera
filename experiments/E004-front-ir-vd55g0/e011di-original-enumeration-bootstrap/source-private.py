#!/usr/bin/env python3
"""Original enumeration bootstrap in the retained factory VM, stopping before callback registration."""
from pathlib import Path
import importlib.util,json,hashlib
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
P=ROOT/'experiments/E004-front-ir-vd55g0/e011dh-original-factory-initialization-clear/source-private.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='cb8f6ef1de49b4ddcac4c26a45305c55b63e83599dead95ea75f907ac27649c2'
s=importlib.util.spec_from_file_location('di_parent_dh',P);DH=importlib.util.module_from_spec(s);s.loader.exec_module(DH)
DE=DH.DE;DC=DH.DC;CV=DH.CV;p=DH.p;c=DH.c;REGS=DH.REGS;PRESERVED=DH.PRESERVED
SOURCES={0x5f8dc0:(1820,'31ceee61563302682fdb6f8a3f98cb92f0bcc29cf7a5b2bc4ca89385f0fa7a5b'),0x1440:(48,'f63f52748e3065341e8e73a6fb2abab1f5af2e25a17f3b0d627034c7341c9b5b'),0xce7ad8:(188,'d310e3f40e9666c9e47bb67e2bef87de0f68142b0413af59613ad85d362f6efc'),0x11d0:(24,'45f51b8d001d6377ce1ebc2559aed1c500722293cf84a7f8040a9e9bfa1570d4')}
for r,(z,pin) in SOURCES.items():assert hashlib.sha256(p.get_data(r,z)).hexdigest()==pin
class Enumeration(DE.GuardSequence):
 def __init__(self,parent):
  self.parent=parent;self.n=parent.n;self.u=parent.u;n=self.n;u=self.u
  self.bias=parent.bias;self.index=parent.index;self.initial_epoch=parent.initial_epoch;self.poison=parent.poison
  self.teb=parent.teb;self.array=parent.array;self.block=parent.block;self.api_page=parent.api_page
  self.apis=parent.apis;self.reverse=parent.reverse;self.bindings=parent.bindings
  self.guard=n.base+0x1b30320;self.original_guard=parent.guard;self.static=n.base+0x169fe00
  self.entry=0x5be9fc;self.stop=0x5f94a0;self.start_sp=u.reg_read(UC_ARM64_REG_SP)
  self.receiver=parent.clear_dest;self.held=False;self.lock_ready=parent.lock_ready;self.cv_ready=parent.cv_ready
  self.wake=0;self.phase='fresh';self.next_api=0;self.expected_apis=['AcquireSRWLockExclusive','ReleaseSRWLockExclusive']
  self.negatives=0;self.header_saved=None;self.header_done=False;self.header_count=0
  self.probe_saved=None;self.probe_done=False;self.probe_count=0;self.constructor_entered=False;self.stopped=False
  assert parent.stopped and parent.clear_done and not parent.held and parent.next_api==2
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+self.entry and u.reg_read(UC_ARM64_REG_X0)==self.receiver
  # Explicit owned already-committed stack bounds, prepared before the component baseline.
  self.wr(self.teb+8,n.stack+65536,8);self.wr(self.teb+16,n.stack,8)
  if self.poison:u.mem_write(self.static,bytes([self.poison])*56)
  self.instructions={i.address:i for r,(z,pin) in SOURCES.items() for off in range(0,z,4) for i in c.disasm(p.get_data(r+off,4),n.base+r+off)}
  i=next(c.disasm(p.get_data(self.entry,4),n.base+self.entry));self.instructions[i.address]=i
  self.fields={(0xce7b14,self.guard,4):0xffffffff}
  for off in range(0,32,8):self.fields[(0x5f9488,self.static+off,8)]=0
  for off in (32,40):self.fields[(0x5f9490,self.static+off,8)]=0
  self.fields[(0x5f9494,self.static+48,8)]=0
 def state(self):
  return super().state()+(tuple(self.parent.allocations),tuple(sorted(self.parent.owners.items())),self.parent.alloc_ready,self.parent.held)
 def layout(self):
  n=self.n;u=self.u;assert self.lock_ready and self.cv_ready and self.parent.alloc_ready and not self.parent.held
  assert u.reg_read(UC_ARM64_REG_X18)==self.teb and self.rd(n.base+0x16a3740)==self.index
  assert self.rd(self.teb+88,8)==self.array and self.rd(self.array+self.index*8,8)==self.block
  assert self.rd(self.block+16)==self.initial_epoch and self.rd(n.base+0x1607b04)==self.initial_epoch
  assert self.rd(self.teb+8,8)==n.stack+65536 and self.rd(self.teb+16,8)==n.stack
  assert all(self.rd(a,8)==v for a,v in self.bindings.items())
  assert self.rd(self.original_guard)==0xffffffff
  assert self.parent.allocations==self.parent.nodes and self.parent.owners=={a:48 for a in self.parent.nodes}
 def contract(self,entry,args):
  self.layout();u=self.u;n=self.n
  assert entry==self.entry and args==[self.receiver,self.start_sp,self.teb]
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+entry and u.reg_read(UC_ARM64_REG_X0)==self.receiver
  assert u.reg_read(UC_ARM64_REG_SP)==self.start_sp and self.rd(self.guard)==0 and not self.held
  assert bytes(u.mem_read(self.receiver,1040))==bytes(1040)
 def header_contract(self,entry,ret,args):
  self.layout();n=self.n;u=self.u
  assert entry==0xce7ad8 and ret==n.base+0x5f9464 and args==[self.guard]
  assert self.header_saved is None and self.probe_done and not self.held and self.rd(self.guard)==0
  assert u.reg_read(UC_ARM64_REG_X0)==self.guard and u.reg_read(UC_ARM64_REG_LR)==ret
  assert u.reg_read(UC_ARM64_REG_SP)==self.start_sp-6032
 def probe_contract(self,entry,ret,args):
  self.layout();n=self.n;u=self.u
  assert entry==0x1440 and ret==n.base+0x5f8dec and args==[self.start_sp-112,370,self.teb]
  assert self.constructor_entered and self.probe_saved is None and not self.held
  assert u.reg_read(UC_ARM64_REG_SP)==args[0] and u.reg_read(UC_ARM64_REG_X15)==370 and u.reg_read(UC_ARM64_REG_LR)==ret
  assert args[0]-370*16>=self.rd(self.teb+16,8) and args[0]<=self.rd(self.teb+8,8)
 def final_contract(self,site,args):
  self.layout();n=self.n;u=self.u
  assert site==self.stop and args==[n.base+0xf7b5e0]
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+site and u.reg_read(UC_ARM64_REG_X0)==args[0]
  assert self.header_done and self.probe_done and not self.held and self.next_api==2
  assert self.rd(self.guard)==0xffffffff and bytes(u.mem_read(self.static,56))==bytes(56)
  assert bytes(u.mem_read(self.receiver,1040))==bytes(1040) and u.reg_read(UC_ARM64_REG_SP)==self.start_sp-6032
 def flags_invalid(self,fn,args,tests):
  for field,value in tests:
   old=getattr(self,field);setattr(self,field,value)
   try:self.reject(fn,[args])
   finally:setattr(self,field,old)
 def actual_invalid(self,fn,args,tests):
  for cell,value,z in tests:
   old=bytes(self.u.mem_read(cell,z));self.wr(cell,value,z)
   try:self.reject(fn,[args])
   finally:self.u.mem_write(cell,old)
 def code(self,u,pc,z,user):
  assert not self.pending;n=self.n
  if pc in self.reverse:
   name=self.reverse[pc];ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_X0)]
   self.dependency(name,ret,args)
   self.reject(lambda ret,args:self.dependency(name,ret,args),[(ret+4,args),(ret,[args[0]+8]),(ret,args+[0])])
   self.flags_invalid(lambda ret,args:self.dependency(name,ret,args),(ret,args),[('held',not self.held),('lock_ready',False)])
   self.held=name=='AcquireSRWLockExclusive';self.next_api+=1
   u.reg_write(UC_ARM64_REG_X0,0xdead0101+self.bias);u.reg_write(UC_ARM64_REG_PC,ret);return
  r=pc-n.base;assert pc in self.instructions and bytes(u.mem_read(pc,4))==p.get_data(r,4)
  if r==self.stop:
   i=self.instructions[pc];assert i.mnemonic=='bl' and i.operands[0].imm==n.base+0xca34a0
   args=[u.reg_read(UC_ARM64_REG_X0)];self.final_contract(r,args)
   self.reject(self.final_contract,[(r+4,args),(r,[args[0]+4]),(r,args+[0])])
   self.flags_invalid(self.final_contract,(r,args),[('held',True),('header_done',False)])
   self.actual_invalid(self.final_contract,(r,args),[(self.guard,0,4),(self.static+48,1,8),(self.receiver,1,8)])
   self.stopped=True;u.emu_stop();return
  assert len(self.trace)<200;self.trace.append(r)
  if r==self.entry:
   i=self.instructions[pc];assert i.mnemonic=='bl' and i.operands[0].imm==n.base+0x5f8dc0
  if r==0x5f8dc0:
   assert not self.constructor_entered and u.reg_read(UC_ARM64_REG_X0)==self.receiver and u.reg_read(UC_ARM64_REG_LR)==n.base+0x5bea00
   self.constructor_entered=True
  if r==0x1440:
   ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_SP),u.reg_read(UC_ARM64_REG_X15),u.reg_read(UC_ARM64_REG_X18)]
   self.probe_contract(r,ret,args)
   self.reject(self.probe_contract,[(r+4,ret,args),(r,ret+4,args),(r,ret,[args[0]+16,370,args[2]]),(r,ret,[args[0],371,args[2]]),(r,ret,args+[0])])
   self.actual_invalid(self.probe_contract,(r,ret,args),[(self.teb+16,0,8),(self.teb+8,n.stack+65520,8)])
   self.probe_saved={k:u.reg_read(k) for k in PRESERVED}
  if 0x1440<=r<0x1470:self.probe_count+=1
  if r==0x5f8dec:
   assert self.probe_saved and all(u.reg_read(k)==v for k,v in self.probe_saved.items())
   assert self.probe_count==6 and u.reg_read(UC_ARM64_REG_X15)==370;self.probe_done=True
  if r==0xce7ad8:
   ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_X0)];self.header_contract(r,ret,args)
   self.reject(self.header_contract,[(r+4,ret,args),(r,ret+4,args),(r,ret,[args[0]+4]),(r,ret,args+[0])])
   self.flags_invalid(self.header_contract,(r,ret,args),[('held',True)])
   self.header_saved={k:u.reg_read(k) for k in PRESERVED}
  if 0xce7ad8<=r<0xce7b94:self.header_count+=1
  if r==0x5f9464:
   assert self.header_saved and all(u.reg_read(k)==v for k,v in self.header_saved.items())
   assert self.header_count==26 and self.rd(self.guard)==0xffffffff and not self.held;self.header_done=True
  i=self.instructions[pc]
  if i.mnemonic.startswith(('str','stp','stur','st1')):
   op=next(o for o in i.operands if o.type==3);assert not op.mem.index
   at=CV.reg(u,c.reg_name(op.mem.base))+op.mem.disp;first=c.reg_name(i.operands[0].reg)
   width=16 if first.startswith(('q','v')) else 8 if first.startswith(('x','d')) or first in ('fp','lr') else 2 if first.startswith('h') else 1 if first.startswith('b') else 4
   if i.mnemonic.endswith('h'):width=2
   elif i.mnemonic.endswith('b'):width=1
   ops=[o for o in i.operands if o.type==1] if i.mnemonic=='st1' else i.operands[:2] if i.mnemonic=='stp' else i.operands[:1]
   for k,o in enumerate(ops):
    rn=c.reg_name(o.reg);value=u.reg_read(globals()['UC_ARM64_REG_Q'+rn[1:]]) if rn.startswith('v') else CV.reg(u,rn)
    data=(value&((1<<(8*width))-1)).to_bytes(width,'little')
    for off in range(0,width,8):
     address=at+k*width+off;size=min(8,width-off);chunk=int.from_bytes(data[off:off+size],'little')
     if n.stack<=address and address+size<=n.stack+65536:self.patch(address,chunk.to_bytes(size,'little'))
     else:assert self.fields.get((r,address,size))==chunk,('unowned enumeration write',hex(r),size)
     self.pending[address,size]=chunk
 def memory(self,u,access,at,z,value,user):
  planned=self.pending.pop((at,z),None);assert planned is not None and planned==(value&((1<<(8*z))-1))
  self.stores+=1
 def read(self,u,access,at,z,value,user):
  n=self.n
  if n.stack<=at and at+z<=n.stack+65536:return
  allowed={(n.base+0x1607000,8),(n.base+0x16a3740,4),(self.guard,4),(self.block+16,4),
   (self.teb+16,8),(self.teb+88,8),(self.array+self.index*8,8)}|{(a,8) for a in self.bindings}
  assert (at,z) in allowed,('unowned enumeration read',hex(at-n.base),z)
 def run(self):
  u=self.u;n=self.n;args=[self.receiver,self.start_sp,self.teb];self.contract(self.entry,args)
  self.reject(self.contract,[(self.entry+4,args),(self.entry,args+[0]),(self.entry,[args[0]+1,args[1],args[2]]),(self.entry,[args[0],args[1]+16,args[2]]),(self.entry,[args[0],args[1],args[2]+8])])
  self.flags_invalid(self.contract,(self.entry,args),[('held',True),('lock_ready',False),('cv_ready',False)])
  tests=[(self.guard,1,4),(n.base+0x16a3740,self.index+1,4),(self.teb+88,self.array+8,8),
   (self.array+self.index*8,self.block+8,8),(self.block+16,41,4),(self.teb+16,0,8),(self.receiver,1,8)]
  tests +=[(a,v+4,8) for a,v in self.bindings.items()]
  self.actual_invalid(self.contract,(self.entry,args),tests)
  self.before=self.snapshot();self.models={};self.pending={};self.trace=[];self.stores=0
  for (r,at,z),value in self.fields.items():self.patch(at,value.to_bytes(z,'little'))
  hooks=[u.hook_add(UC_HOOK_CODE,self.code),u.hook_add(UC_HOOK_MEM_WRITE,self.memory),u.hook_add(UC_HOOK_MEM_READ,self.read)]
  try:u.emu_start(n.base+self.entry,n.end,count=250)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.stopped and self.constructor_entered and self.probe_done and self.header_done and not self.pending and not self.held
  assert len(self.trace)==80 and self.stores==32 and self.next_api==2 and self.negatives==48
  after=self.snapshot();assert after.keys()==self.before.keys() and all(after[k]==self.models.get(k,v) for k,v in self.before.items())
  self.layout()
  for k,node in enumerate(self.parent.nodes):
   assert self.rd(n.base+[0x1b302a0,0x1b302c0][k],8)==node
   assert all(self.rd(node+off,8)==node for off in (0,8,16)) and self.rd(node+24,2)==257 and bytes(u.mem_read(node+26,22))==bytes(22)
  return {'executed_original_instructions':len(self.trace),'exact_source_store_chunks':self.stores,'invalid_requests_rejected':self.negatives,
   'original_stack_probe_instructions':self.probe_count,'original_second_guard_instructions':self.header_count,
   'whole_memory_actual_permissions_logical_resources_and_actual_helper_callers_checked':True}
def main():
 rows=[]
 for bias in (0,16,128,512):
  for index in (0,37):
   for epoch in (0x80000000,0xffffff00):
    for poison in (0,0xd7):
     parent=DH.Prefix(bias,index,epoch,poison);prior=parent.run();new=Enumeration(parent).run()
     rows.append({'placement_bias':bias,'owned_loader_index':index,'owned_cold_epoch':epoch,'zero_field_poison_fixture':poison,'factory':prior,'enumeration':new})
     print(json.dumps({'case':len(rows),'status':'PASS_BOUNDED_ORIGINAL_ENUMERATION_BOOTSTRAP'}),flush=True)
 result={'experiment':'E011DI-private-verifier','status':'PASS_BOUNDED_ORIGINAL_FACTORY_AND_ENUMERATION_BOOTSTRAP','cases':rows,
  'executed_original_instructions':sum(r['factory']['executed_original_instructions']+r['enumeration']['executed_original_instructions'] for r in rows),
  'exact_source_store_chunks':sum(r['factory']['exact_source_store_chunks']+r['enumeration']['exact_source_store_chunks'] for r in rows),
  'invalid_requests_rejected':sum(r['factory']['invalid_requests_rejected_before_effects']+r['enumeration']['invalid_requests_rejected'] for r in rows),
  'stop_before_source_call_RVA':'0x5f94a0','unexecuted_next_target_RVA':'0xca34a0','source_callback_argument_RVA':'0xf7b5e0',
  'original_second_guard_RVA':'0x1b30320','owned_committed_stack_bounds_fixture':True,
  'OS_guard_page_growth_and_full_parent_return_registry_completion_file_enumeration_Default_hardware_qualified':False,
  'new_camera_Starts':0,'new_reboots':0,'native_rear_runtime_allowed':False}
 assert len(rows)==32 and result['executed_original_instructions']==15936 and result['exact_source_store_chunks']==12832 and result['invalid_requests_rejected']==3488
 (OUT/'ORIGINAL-ENUMERATION-BOOTSTRAP-V6-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='cases'}),flush=True)
if __name__=='__main__':main()
