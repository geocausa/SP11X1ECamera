#!/usr/bin/env python3
"""Original isolated startup-guard sequence under declared loader/SRW dependency models."""
from pathlib import Path
import importlib.util,json,hashlib,struct,collections
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
P=ROOT/'experiments/E004-front-ir-vd55g0/e011dc-original-fresh-root-camera-join/source-private.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='8e04c3221839f40d3d21f2598d8978003b48799f78dabdf21e7b60ee27244096'
s=importlib.util.spec_from_file_location('de_strict_dc',P);DC=importlib.util.module_from_spec(s);s.loader.exec_module(DC)
CF=DC.CF;CV=DC.CV;p=CF.p;c=CF.c
SOURCES={0xce7ad8:(188,'d310e3f40e9666c9e47bb67e2bef87de0f68142b0413af59613ad85d362f6efc'),0xce7a48:(140,'6f84e7a29bab93d10f7570516c2e5be4717e748b87314a6c75857f05ce4455d2')}
for r,(size,pin) in SOURCES.items():assert hashlib.sha256(p.get_data(r,size)).hexdigest()==pin
REGS=DC.REGS
class GuardSequence:
 def __init__(self,bias,index,epoch):
  self.n=DC.DA.CZ.N.Native();self.u=self.n.u;n=self.n;u=self.u
  self.bias=bias;self.index=index;self.initial_epoch=epoch;self.guard=n.heap+0x5000+bias
  self.teb=0x97700000;self.array=0x97710000;self.block=0x97720000+bias;self.api_page=0x97730000
  for address in (self.teb,self.array,0x97720000,self.api_page):
   u.mem_map(address,65536);u.mem_write(address,bytes([0xa5])*65536)
  u.mem_write(n.heap,bytes([0xa5])*0x30000);u.mem_write(n.stack,bytes([0xd5])*65536)
  self.wr(n.base+0x16a3740,index);self.wr(self.teb+88,self.array,8);self.wr(self.array+index*8,self.block,8)
  self.wr(n.base+0x1607b04,epoch);self.wr(self.block+16,epoch);self.wr(self.guard,0)
  u.reg_write(UC_ARM64_REG_X18,self.teb)
  self.apis={'AcquireSRWLockExclusive':self.api_page+0x100,'ReleaseSRWLockExclusive':self.api_page+0x110,'WakeAllConditionVariable':self.api_page+0x120}
  self.bindings={}
  for dll in p.DIRECTORY_ENTRY_IMPORT:
   for x in dll.imports:
    name=x.name.decode('ascii') if x.name else ''
    if name in self.apis:
     cell=n.base+x.address-p.OPTIONAL_HEADER.ImageBase;self.wr(cell,self.apis[name],8);self.bindings[cell]=self.apis[name]
     u.mem_write(self.apis[name],bytes.fromhex('c0035fd6'))
  assert len(self.bindings)==3
  self.reverse={v:k for k,v in self.apis.items()}
  self.instructions={i.address:i for r,(size,pin) in SOURCES.items() for i in c.disasm(p.get_data(r,size),n.base+r)}
  self.held=False;self.lock_ready=self.cv_ready=True;self.wake=0;self.phase='';self.next_api=0
 def wr(self,a,v,z=4):self.u.mem_write(a,v.to_bytes(z,'little'))
 def rd(self,a,z=4):return int.from_bytes(self.u.mem_read(a,z),'little')
 def snapshot(self):return {(a,b,p):bytes(self.u.mem_read(a,b-a+1)) for a,b,p in self.u.mem_regions()}
 def state(self):return (self.held,self.lock_ready,self.cv_ready,self.wake,self.next_api)
 def patch(self,at,data):
  k=next(k for k in self.before if k[0]<=at and at+len(data)<=k[1]+1)
  if k not in self.models:self.models[k]=bytearray(self.before[k])
  self.models[k][at-k[0]:at-k[0]+len(data)]=data
 def contract(self,entry,args):
  n=self.n;assert entry==self.entry and args==[self.guard,n.stack+0xf000,n.end,self.teb]
  assert self.guard%4==0 and not self.held and self.lock_ready and self.cv_ready
  assert self.u.reg_read(UC_ARM64_REG_X0)==self.guard and self.u.reg_read(UC_ARM64_REG_X18)==self.teb
  assert self.u.reg_read(UC_ARM64_REG_SP)==n.stack+0xf000 and self.u.reg_read(UC_ARM64_REG_LR)==n.end
  assert self.rd(n.base+0x16a3740)==self.index and self.rd(self.teb+88,8)==self.array and self.rd(self.array+self.index*8,8)==self.block
  assert all(self.rd(cell,8)==target for cell,target in self.bindings.items())
  epoch=self.initial_epoch if self.phase in ('fresh','completion') else self.initial_epoch+1
  guard=0 if self.phase=='fresh' else 0xffffffff if self.phase=='completion' else self.initial_epoch+1
  assert self.rd(n.base+0x1607b04)==epoch and self.rd(self.guard)==guard and self.rd(self.block+16)==self.initial_epoch
 def reject(self,fn,tests):
  before=self.snapshot();regs={r:self.u.reg_read(r) for r in REGS};state=self.state()
  for args in tests:
   try:fn(*args)
   except AssertionError:pass
   else:raise AssertionError('invalid guard request admitted')
  assert before==self.snapshot() and self.state()==state and all(self.u.reg_read(r)==v for r,v in regs.items())
  self.negatives+=len(tests)
 def dependency(self,name,ret,args):
  n=self.n;assert name==self.expected_apis[self.next_api] and args==[n.base+(0x16a3730 if name=='WakeAllConditionVariable' else 0x16a3738)]
  expected={'AcquireSRWLockExclusive':0xce7a74 if self.phase=='completion' else 0xce7b08,
   'ReleaseSRWLockExclusive':0xce7ab4 if self.phase=='completion' else 0xce7b80,'WakeAllConditionVariable':0xce7ac4}
  assert ret==n.base+expected[name] and self.lock_ready and self.cv_ready
  assert self.held==(name=='ReleaseSRWLockExclusive')
 def code(self,u,pc,z,user):
  assert not self.pending;n=self.n
  if pc in self.reverse:
   name=self.reverse[pc];ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_X0)]
   self.dependency(name,ret,args)
   self.reject(lambda ret,args:self.dependency(name,ret,args),[(ret+4,args),(ret,[args[0]+8]),(ret,args+[0])])
   old=self.held;self.held=not old
   try:self.reject(lambda ret,args:self.dependency(name,ret,args),[(ret,args)])
   finally:self.held=old
   if name=='AcquireSRWLockExclusive':self.held=True
   elif name=='ReleaseSRWLockExclusive':self.held=False
   else:self.wake+=1
   self.next_api+=1
   u.reg_write(UC_ARM64_REG_X0,0xdead0101+self.bias);u.reg_write(UC_ARM64_REG_PC,ret);return
  r=pc-n.base;assert pc in self.instructions and bytes(u.mem_read(pc,4))==p.get_data(r,4)
  assert len(self.trace)<100;self.trace.append(r);i=self.instructions[pc]
  if i.mnemonic.startswith(('str','stp','stur')):
   op=next(o for o in i.operands if o.type==3);assert not op.mem.index
   at=CV.reg(u,c.reg_name(op.mem.base))+op.mem.disp
   first=c.reg_name(i.operands[0].reg);width=8 if first.startswith(('x','d')) or first in ('fp','lr') else 4
   dataops=i.operands[:2] if i.mnemonic=='stp' else i.operands[:1]
   for k,o in enumerate(dataops):
    address=at+k*width;value=CV.reg(u,c.reg_name(o.reg))&((1<<(8*width))-1)
    if n.stack<=address and address+width<=n.stack+65536:self.patch(address,value.to_bytes(width,'little'))
    else:assert self.fields.get((r,address,width))==value,('unowned guard store',hex(r),width)
    self.pending[address,width]=value
 def memory(self,u,access,at,z,value,user):
  assert self.pending.pop((at,z),None)==value;self.stores+=1
 def read(self,u,access,at,z,value,user):
  n=self.n
  if n.stack<=at and at+z<=n.stack+65536:return
  allowed={(self.guard,4),(n.base+0x1607b04,4),(n.base+0x16a3740,4),(self.teb+88,8),(self.array+self.index*8,8)}
  allowed|={(cell,8) for cell in self.bindings}
  assert (at,z) in allowed,('unowned guard read',z)
 def run_phase(self,phase,entry):
  n=self.n;u=self.u;self.phase=phase;self.entry=entry;self.next_api=0;self.negatives=0
  if phase=='cache':self.wr(self.block+16,self.initial_epoch)
  for k in range(19,30):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0x112000+k)
  for k in range(8,16):u.reg_write(globals()['UC_ARM64_REG_D'+str(k)],0x223000+k)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_X0,self.guard);u.reg_write(UC_ARM64_REG_LR,n.end)
  args=[self.guard,n.stack+0xf000,n.end,self.teb];self.contract(entry,args)
  bad=[(entry+4,args),(entry,args+[0])]
  for k in range(4):
   a=args.copy();a[k]+=1;bad.append((entry,a))
  self.reject(self.contract,bad)
  for field,value in [('held',True),('lock_ready',False),('cv_ready',False)]:
   old=getattr(self,field);setattr(self,field,value)
   try:self.reject(self.contract,[(entry,args)])
   finally:setattr(self,field,old)
  fixtures=[(n.base+0x16a3740,self.index+1,4),(self.teb+88,self.array+8,8),(self.array+self.index*8,self.block+8,8)]
  for cell,target in self.bindings.items():fixtures.append((cell,target+4,8))
  for cell,value,size in fixtures:
   old=bytes(u.mem_read(cell,size));self.wr(cell,value,size)
   try:self.reject(self.contract,[(entry,args)])
   finally:u.mem_write(cell,old)
  self.before=self.snapshot();self.models={};self.pending={};self.trace=[];self.stores=0
  self.fields={(0xce7b14,self.guard,4):0xffffffff} if phase=='fresh' else {(0xce7a84,n.base+0x1607b04,4):self.initial_epoch+1,(0xce7a88,self.guard,4):self.initial_epoch+1,(0xce7aa4,self.block+16,4):self.initial_epoch+1} if phase=='completion' else {(0xce7b6c,self.block+16,4):self.initial_epoch+1}
  for (site,at,size),value in self.fields.items():self.patch(at,value.to_bytes(size,'little'))
  self.expected_apis=['AcquireSRWLockExclusive','ReleaseSRWLockExclusive']+(['WakeAllConditionVariable'] if phase=='completion' else [])
  saved={r:u.reg_read(r) for r in [UC_ARM64_REG_SP,*[globals()['UC_ARM64_REG_X'+str(k)] for k in range(19,30)],*[globals()['UC_ARM64_REG_D'+str(k)] for k in range(8,16)]]}
  hooks=[u.hook_add(UC_HOOK_CODE,self.code),u.hook_add(UC_HOOK_MEM_WRITE,self.memory),u.hook_add(UC_HOOK_MEM_READ,self.read)]
  try:u.emu_start(n.base+entry,n.end,count=200)
  finally:
   for h in hooks:u.hook_del(h)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end and not self.pending and not self.held
  assert self.next_api==len(self.expected_apis) and self.lock_ready and self.cv_ready and self.wake==(0 if phase=='fresh' else 1)
  assert len(self.trace)=={'fresh':26,'completion':35,'cache':33}[phase]
  assert self.stores=={'fresh':6,'completion':7,'cache':6}[phase]
  assert self.negatives=={'fresh':23,'completion':27,'cache':23}[phase]
  after=self.snapshot();assert after.keys()==self.before.keys() and all(after[k]==self.models.get(k,v) for k,v in self.before.items()),'whole guard memory model'
  assert all(u.reg_read(r)==v for r,v in saved.items())
  self.before=None;self.models=None
  return {'phase':phase,'original_instructions':len(self.trace),'exact_source_store_chunks':self.stores,'invalid_requests_rejected_before_effects':self.negatives,
   'owned_standard_API_calls':self.next_api,'whole_memory_actual_permissions_logical_SRW_resources_and_actual_caller_preserved':True}
def main():
 rows=[]
 for bias in (0,16,128,512):
  for index in (0,37):
   for epoch in (0x80000000,41):
    proof=GuardSequence(bias,index,epoch)
    phases=[proof.run_phase(phase,entry) for phase,entry in [('fresh',0xce7ad8),('completion',0xce7a48),('cache',0xce7ad8)]]
    row={'placement_bias':bias,'owned_loader_index':index,'owned_initial_epoch':epoch,'phases':phases};rows.append(row)
    print(json.dumps({'scenario':len(rows),'phases':3,'status':'PASS_BOUNDED_ORIGINAL_GUARD_SEQUENCE'}),flush=True)
 result={'experiment':'E011DE-private-verifier','status':'PASS_BOUNDED_ORIGINAL_STARTUP_GUARD_SEQUENCE','scenarios':rows,'phase_cases':48,
  'original_instructions':sum(x['original_instructions'] for r in rows for x in r['phases']),
  'exact_source_store_chunks':sum(x['exact_source_store_chunks'] for r in rows for x in r['phases']),
  'invalid_requests_rejected':sum(x['invalid_requests_rejected_before_effects'] for r in rows for x in r['phases']),
  'original_OS_SRW_concurrency_wait_path_loader_and_full_factory_Default_qualified':False,
  'new_camera_Starts':0,'new_reboots':0,'native_rear_runtime_allowed':False}
 assert len(rows)==16 and result['original_instructions']==1504 and result['exact_source_store_chunks']==304 and result['invalid_requests_rejected']==1168
 (OUT/'ORIGINAL-FACTORY-GUARD-SEQUENCE-V5-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='scenarios'}),flush=True)
if __name__=='__main__':main()
