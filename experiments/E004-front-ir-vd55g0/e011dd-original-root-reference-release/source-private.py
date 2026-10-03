#!/usr/bin/env python3
"""Original fresh-root construction followed by an isolated reference-release component.
No parent destructor execution, camera object cleanup, hardware retirement, or native OS.
"""
from pathlib import Path
import importlib.util,json,hashlib,struct
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
P=ROOT/'experiments/E004-front-ir-vd55g0/e011dc-original-fresh-root-camera-join/source-private.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='8e04c3221839f40d3d21f2598d8978003b48799f78dabdf21e7b60ee27244096'
s=importlib.util.spec_from_file_location('dd_dc_life',P);DC=importlib.util.module_from_spec(s);s.loader.exec_module(DC)
CF=DC.CF;CV=DC.CV
ENTRY=0x290988;END=0x2909d4;GLOBAL=0x1798458;DELETE_IAT=0xf7e0d0;SIZED_DELETE=0xca2830
PARENT_RAW=CF.p.get_data(0x290780,1940)
assert hashlib.sha256(PARENT_RAW).hexdigest()=='512a6ed5b113cd0d2def8f794250f65a71d04e40b1cd687184bc1c91182a1539'
SOURCE=CF.p.get_data(ENTRY,END-ENTRY)
REGS=DC.REGS
class Release:
 def __init__(self,n,root,api,ref):
  self.n=n;self.u=n.u;self.root=root;self.api=api;self.ref=ref
  self.allocated={root} if ref is not None else set()
  self.initialized=ref is not None
  self.held=0;self.other_live_owned_users=0  # explicit isolated caller fixture
  self.delete_count=self.free_count=0;self.trace=[];self.pending={};self.write_count=0
  self.ins={i.address:i for i in CF.c.disasm(SOURCE,n.base+ENTRY)}
  assert len(self.ins)==19
 def q(self,at):return int.from_bytes(self.u.mem_read(at,8),'little')
 def snapshot(self):return {(a,b,p):bytes(self.u.mem_read(a,b-a+1)) for a,b,p in self.u.mem_regions()}
 def state(self):return (tuple(sorted(self.allocated)),self.initialized,self.held,self.other_live_owned_users,self.delete_count,self.free_count)
 def patch(self,at,data):
  k=next(k for k in self.before if k[0]<=at and at+len(data)<=k[1]+1)
  if k not in self.models:self.models[k]=bytearray(self.before[k])
  self.models[k][at-k[0]:at-k[0]+len(data)]=data
 def contract(self,entry,args):
  assert entry==ENTRY and args==[self.root,self.ref,self.api,0,0]
  assert self.root%8==0 and self.held==self.other_live_owned_users==0
  assert self.q(self.n.base+GLOBAL)==(0 if self.ref is None else self.root)
  assert self.q(self.n.base+DELETE_IAT)==self.api
  if self.ref is None:assert not self.allocated and not self.initialized
  else:
   assert self.ref in (1,2,41) and self.allocated=={self.root} and self.initialized
   assert int.from_bytes(self.u.mem_read(self.root,4),'little')==self.ref
  for at,z in ((self.root,176),(self.api,4)):
   assert any(a<=at and at+z<=b+1 for a,b,p in self.u.mem_regions())
 def dep(self,kind,ret,args):
  assert self.ref==1 and self.held==self.other_live_owned_users==0
  assert self.q(self.n.base+GLOBAL)==self.root and int.from_bytes(self.u.mem_read(self.root,4),'little')==0
  if kind=='delete':
   assert ret==self.n.base+0x2909c4 and args==[self.root+8] and self.initialized and self.allocated=={self.root} and self.delete_count==self.free_count==0
  elif kind=='free':
   assert ret==self.n.base+0x2909d0 and args==[self.root,176] and not self.initialized and self.allocated=={self.root} and self.delete_count==1 and self.free_count==0
  else:raise AssertionError('unknown dependency')
 def reject(self,fn,tests):
  before=self.snapshot();regs={r:self.u.reg_read(r) for r in REGS};state=self.state()
  for args in tests:
   try:fn(*args)
   except AssertionError:pass
   else:raise AssertionError('invalid release request admitted')
  assert self.snapshot()==before and state==self.state() and all(self.u.reg_read(r)==v for r,v in regs.items())
  self.negatives+=len(tests)
 def run(self):
  u=self.u;n=self.n;self.paused={r:u.reg_read(r) for r in REGS};self.negatives=0
  args=[self.root,self.ref,self.api,0,0];self.contract(ENTRY,args)
  tests=[(ENTRY+4,args),(ENTRY,args+[0])]
  for k in (0,2,3,4):
   bad=args.copy();bad[k]+=1;tests.append((ENTRY,bad))
  bad=args.copy();bad[1]=0 if self.ref is not None else 1;tests.append((ENTRY,bad))
  self.reject(self.contract,tests)
  # Test the actual logical owner state, beyond malformed request tuples.
  states=[('held',1),('other_live_owned_users',1),('allocated',{self.root} if self.ref is None else set()),('initialized',self.ref is None)]
  for field,bad in states:
   old=getattr(self,field);setattr(self,field,bad)
   try:self.reject(self.contract,[(ENTRY,args)])
   finally:setattr(self,field,old)
  fixtures=[(n.base+GLOBAL,struct.pack('<Q',self.root if self.ref is None else self.root+8))]
  if self.ref is not None:fixtures.extend([(self.root,bytes(4)),(n.base+DELETE_IAT,struct.pack('<Q',self.api+4))])
  for address,bad in fixtures:
   old=bytes(u.mem_read(address,len(bad)));u.mem_write(address,bad)
   try:self.reject(self.contract,[(ENTRY,args)])
   finally:u.mem_write(address,old)
  self.before=self.snapshot();self.models={};self.initial_state=self.state()
  if self.ref is not None:self.patch(self.root,struct.pack('<I',self.ref-1))
  if self.ref==1:self.patch(n.base+GLOBAL,bytes(8))
  self.expected=list(range(ENTRY,0x290994,4)) if self.ref is None else list(range(ENTRY,0x2909b0,4)) if self.ref>1 else list(range(ENTRY,END,4))
  # Only this parent-destructor component runs, to its next source boundary.
  # Source-generated register effects are allowed; no claim of parent ABI return.
  self.allowed_regs=set()
  for i in self.ins.values():
   _,writes=i.regs_access()
   for r in writes:
    name=CF.c.reg_name(r)
    if name=='nzcv':self.allowed_regs.add(UC_ARM64_REG_NZCV)
    elif name in ('fp','lr'):self.allowed_regs.add(UC_ARM64_REG_FP if name=='fp' else UC_ARM64_REG_LR)
    elif name.startswith(('x','w')) and name[1:].isdigit():self.allowed_regs.add(globals()['UC_ARM64_REG_X'+name[1:]])
  self.allowed_regs.update((UC_ARM64_REG_PC,UC_ARM64_REG_X0,UC_ARM64_REG_LR))
  self.hooks=[u.hook_add(UC_HOOK_CODE,self.code),u.hook_add(UC_HOOK_MEM_WRITE,self.memory),u.hook_add(UC_HOOK_MEM_READ,self.read)]
  try:u.emu_start(n.base+ENTRY,n.base+END,count=100)
  finally:
   for h in self.hooks:u.hook_del(h)
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+END and self.trace==self.expected and not self.pending
  assert self.write_count==(2 if self.ref==1 else 0 if self.ref is None else 1)
  assert self.delete_count==self.free_count==(1 if self.ref==1 else 0)
  assert self.q(n.base+GLOBAL)==(0 if self.ref in (None,1) else self.root)
  assert self.state()==((),False,0,0,1,1) if self.ref==1 else self.state()==self.initial_state
  after=self.snapshot();assert after.keys()==self.before.keys() and all(after[k]==self.models.get(k,v) for k,v in self.before.items())
  assert all(u.reg_read(r)==v for r,v in self.paused.items() if r not in self.allowed_regs)
  for r,v in self.paused.items():u.reg_write(r,v)
  assert all(u.reg_read(r)==v for r,v in self.paused.items())
  return {'owned_initial_reference':self.ref,'original_release_component_instructions':len(self.trace),'source_store_chunks':self.write_count,'invalid_requests_rejected_before_effects':self.negatives,
   'owned_OS_delete_calls':self.delete_count,'owned_sized_allocator_release_calls':self.free_count,
   'whole_memory_permissions_and_logical_resources_checked':True,'source_parent_register_effects_declared_and_paused_state_restored':True,
   'full_parent_destructor_and_caller_return_qualified':False,'concurrent_atomic_retry_native_OS_and_DMA_retirement_qualified':False}
 def code(self,u,pc,z,user):
  assert not self.pending;n=self.n;r=pc-n.base
  if pc==self.api:
   self.dep('delete',u.reg_read(UC_ARM64_REG_LR),[u.reg_read(UC_ARM64_REG_X0)])
   self.reject(lambda ret,args:self.dep('delete',ret,args),[(n.base+0x2909c8,[self.root+8]),(n.base+0x2909c4,[self.root+16]),(n.base+0x2909c4,[self.root+8,0])])
   for field in ('held','other_live_owned_users'):
    old=getattr(self,field);setattr(self,field,1)
    try:self.reject(lambda ret,args:self.dep('delete',ret,args),[(u.reg_read(UC_ARM64_REG_LR),[self.root+8])])
    finally:setattr(self,field,old)
   self.initialized=False;self.delete_count=1
   # void standard OS dependency; caller does not depend on its X0 residue.
   u.reg_write(UC_ARM64_REG_X0,0xdead0001);u.reg_write(UC_ARM64_REG_PC,n.base+0x2909c4);return
  if r==SIZED_DELETE:
   self.dep('free',u.reg_read(UC_ARM64_REG_LR),[u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1)])
   self.reject(lambda ret,args:self.dep('free',ret,args),[(n.base+0x2909d4,[self.root,176]),(n.base+0x2909d0,[self.root+8,176]),(n.base+0x2909d0,[self.root,160]),(n.base+0x2909d0,[self.root,176,0])])
   for field in ('held','other_live_owned_users'):
    old=getattr(self,field);setattr(self,field,1)
    try:self.reject(lambda ret,args:self.dep('free',ret,args),[(u.reg_read(UC_ARM64_REG_LR),[self.root,176])])
    finally:setattr(self,field,old)
   self.allocated.remove(self.root);self.free_count=1
   u.reg_write(UC_ARM64_REG_X0,0xdead0002);u.reg_write(UC_ARM64_REG_PC,n.base+0x2909d0);return
  assert pc in self.ins and bytes(u.mem_read(pc,4))==CF.p.get_data(r,4)
  assert len(self.trace)<len(self.expected) and r==self.expected[len(self.trace)],('trace',hex(r))
  self.trace.append(r);i=self.ins[pc]
  if i.mnemonic.startswith(('str','stp','stur','stlxr')):
   op=next(o for o in i.operands if o.type==3);at=CV.reg(u,CF.c.reg_name(op.mem.base))+op.mem.disp
   assert not op.mem.index
   first=1 if i.mnemonic=='stlxr' else 0;name=CF.c.reg_name(i.operands[first].reg)
   width=8 if name.startswith('x') else 4
   value=CV.reg(u,name)&((1<<(8*width))-1)
   expected=(self.root,4,self.ref-1) if r==0x2909a0 else (n.base+GLOBAL,8,0) if r==0x2909d0 else None
   assert expected==(at,width,value),('unowned store',hex(r),width)
   if r==0x2909d0:assert not self.allocated and not self.initialized and self.free_count==self.delete_count==1
   self.pending[at,width]=value
 def memory(self,u,access,at,z,value,user):
  assert self.pending.pop((at,z),None)==value;self.write_count+=1
 def read(self,u,access,at,z,value,user):
  assert (at,z) in {(self.n.base+GLOBAL,8),(self.root,4),(self.n.base+DELETE_IAT,8)}
def main():
 rows=[]
 for bias in (0,16,128,512):
  for ref in (None,1,2,41):
   n=DC.DA.CZ.N.Native();u=n.u;root=n.heap+0x5000+bias;table=n.heap+0x1000+bias;api=n.heap+0x2f000
   u.mem_write(n.heap,bytes([0xa5])*0x30000);u.mem_write(n.stack,bytes([0xd5])*65536)
   u.mem_write(api,bytes.fromhex('c0035fd6'));u.mem_write(api+0x100,bytes.fromhex('c0035fd6'))
   for k in range(31):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0x111000+k)
   for k in range(8,16):u.reg_write(globals()['UC_ARM64_REG_D'+str(k)],0x222000+k)
   fresh=None
   if ref is not None:
    old=DC.prepare(n,table,root,n.stack,api)
    f=DC.FreshRoot(n,table,root,n.stack,api);fresh=f.run();f.final()
    u.mem_write(n.base+0xf7e0c8,old);u.mem_write(root,struct.pack('<I',ref)) # additional owned refs are explicit fixtures
   else:u.mem_write(n.base+GLOBAL,bytes(8))
   u.mem_write(n.base+DELETE_IAT,struct.pack('<Q',api+0x100))
   proof=Release(n,root,api+0x100,ref);release=proof.run()
   row={'placement_bias':bias,'fresh_construction':fresh,'isolated_release':release};rows.append(row)
   print(json.dumps({'placement_bias':bias,'reference':ref,'status':'PASS_BOUNDED_RELEASE_COMPONENT','instructions':release['original_release_component_instructions']}),flush=True)
 result={'experiment':'E011DD-private-verifier','status':'PASS_BOUNDED_FRESH_ROOT_REFERENCE_RELEASE_COMPONENT','cases':rows,
  'release_original_instructions':sum(x['isolated_release']['original_release_component_instructions'] for x in rows),
  'release_store_chunks':sum(x['isolated_release']['source_store_chunks'] for x in rows),
  'release_negative_requests':sum(x['isolated_release']['invalid_requests_rejected_before_effects'] for x in rows),
  'fresh_original_instructions':sum((x['fresh_construction'] or {}).get('original_fresh_root_instructions',0) for x in rows),
  'full_parent_destructor_actual_Default_full_startup_and_hardware_qualified':False,
  'new_camera_Starts':0,'new_reboots':0}
 assert len(rows)==16 and result['release_original_instructions']==168 and result['release_store_chunks']==16 and result['release_negative_requests']==260 and result['fresh_original_instructions']==1836
 (OUT/'FRESH-ROOT-REFERENCE-RELEASE-V2-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='cases'}),flush=True)
if __name__=='__main__':main()
