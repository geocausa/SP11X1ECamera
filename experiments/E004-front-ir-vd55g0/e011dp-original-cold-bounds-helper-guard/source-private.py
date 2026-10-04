#!/usr/bin/env python3
"""Same-SP11 cold literal bounds and first-helper guard acquisition; stop before allocator."""
from pathlib import Path
import collections,hashlib,importlib.util,json,struct
import capstone,pefile
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
OUT=Path(__file__).resolve().parent
PRIVATE=R.parent/"private"
P=R/"experiments/E004-front-ir-vd55g0/e011ai-rear-neutral-scalar-full-integration/native-private.py"
s=importlib.util.spec_from_file_location("do_original_image",P);M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
blob=M.DLL.read_bytes();assert hashlib.sha256(blob).hexdigest()==M.DLL_SHA
PE=pefile.PE(data=blob)
RANGES={
 0x5b80a8:[(0x5b80a8,0x5b90af)],0xce7ad8:[(0xce7ad8,0xce7b93)],
 0x5de700:[(0x5de700,0x5df75b)],0x1df30:[(0x1df30,0x1df8b)],0x1df90:[(0x1df90,0x1dfeb)],
 0x1a8c0:[(0x1a8c0,0x1a8c3)],0x11d0:[(0x11d0,0x11e7)],
 0x11f0:[(0x11f0,0x120f),(0x1214,0x121b),(0x1220,0x1233)]}
PINS={hex(entry):{"body_bytes":sum(hi-lo+1 for lo,hi in ranges),"ranges":[[hex(lo),hex(hi)] for lo,hi in ranges],
"sha256":hashlib.sha256(b"".join(PE.get_data(lo,hi-lo+1) for lo,hi in ranges)).hexdigest()} for entry,ranges in RANGES.items()}
assert PINS["0x5de700"]["sha256"]=="776092eab939986d2258713b25723c3ad4c1ddcdc8231881da140e25a9960533"
assert PINS["0x5b80a8"]["sha256"]=="26c3514bda9b9c1e8e91c5988c51fd336d0b77465699675d4935ab2219a0ca9b"
assert PINS["0xce7ad8"]["sha256"]=="d310e3f40e9666c9e47bb67e2bef87de0f68142b0413af59613ad85d362f6efc"
C=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);C.detail=True
INS={i.address:i for ranges in RANGES.values() for lo,hi in ranges for i in C.disasm(PE.get_data(lo,hi-lo+1),lo)}
BINDINGS={}
for e in PE.DIRECTORY_ENTRY_IMPORT:
 for x in e.imports:
  name=(x.name or b"").decode()
  if name in ("EnterCriticalSection","LeaveCriticalSection","AcquireSRWLockExclusive","ReleaseSRWLockExclusive"):BINDINGS[name]=x.address-PE.OPTIONAL_HEADER.ImageBase
assert BINDINGS=={"EnterCriticalSection":0xf7e0b8,"LeaveCriticalSection":0xf7e0c0,"AcquireSRWLockExclusive":0xf7e520,"ReleaseSRWLockExclusive":0xf7e518}
LITERALS=[(0x5de82c,239),(0x5de834,282),(0xce7b10,-1)]
for site,value in LITERALS:
 i=INS[site];assert i.mnemonic in ("mov","movz") and i.operands[1].type==capstone.arm64.ARM64_OP_IMM and i.operands[1].imm==value
FIELDS={(0x5de830,0x17350ec,4):239,(0x5de838,0x17350e4,4):282,(0xce7b14,0x17a4220,4):0xffffffff}

NONVOL=[UC_ARM64_REG_SP,*[globals()["UC_ARM64_REG_X"+str(k)] for k in range(19,30)],*[globals()["UC_ARM64_REG_D"+str(k)] for k in range(8,16)]]
ALLREG=[UC_ARM64_REG_PC,UC_ARM64_REG_LR,*[globals()["UC_ARM64_REG_X"+str(k)] for k in range(29)],UC_ARM64_REG_SP]
def reg(u,name):
 if name in ("xzr","wzr"):return 0
 name={"fp":"x29","lr":"x30"}.get(name,name)
 if name.startswith("w"):return u.reg_read(globals()["UC_ARM64_REG_X"+name[1:]])&0xffffffff
 return u.reg_read(globals()["UC_ARM64_REG_"+name.upper()])
class Case:
 def __init__(self,bias,index,epoch,sentinel,diag_clobber,api_clobber):
  bound=0
  self.n=M.Native();self.u=self.n.u;u=self.u;n=self.n
  self.bias=bias;self.bound=bound;self.diag_clobber=diag_clobber;self.api_clobber=api_clobber
  self.obj=n.base+0x1626898;self.resource=self.obj+8;self.stacktop=n.stack+0xf000-bias
  self.api_page=0x76000000;u.mem_map(self.api_page,4096);u.mem_write(self.api_page,bytes([0xa5])*4096)
  self.apis={name:self.api_page+0x100+16*i for i,name in enumerate(BINDINGS)}
  self.reverse={v:k for k,v in self.apis.items()}
  for name,cell in BINDINGS.items():self.wr(n.base+cell,self.apis[name],8)
  u.mem_write(n.stack,bytes([0xd5])*65536)
  # Pre-existing scalar bound is an explicit owned fixture; no descriptor contents are supplied.
  self.wr(n.base+0x17350e0,bound,4)
  for k in range(31):u.reg_write(globals()["UC_ARM64_REG_X"+str(k)],0x123000+k*32+bias)
  for k in range(8,16):u.reg_write(globals()["UC_ARM64_REG_D"+str(k)],0x456000+k*32+bias)
  u.reg_write(UC_ARM64_REG_SP,self.stacktop);u.reg_write(UC_ARM64_REG_LR,n.end)
  self.ready=True;self.held=False;self.next_dep=0;self.callback=None
  self.pending={};self.stores=0;self.negatives=0;self.trace=[];self.callbacks=0;self.cfg_visits=0;self.dep_names=[];self.stopped=False
  self.expected_deps=["diagnostic_enter","EnterCriticalSection","AcquireSRWLockExclusive","ReleaseSRWLockExclusive"]
  self.index=index;self.epoch=epoch;self.sentinel=sentinel
  self.teb=0x97700000;self.array=0x97710000;self.block=0x97720000+bias
  for a in (self.teb,self.array,0x97720000):u.mem_map(a,65536);u.mem_write(a,bytes([0xa5])*65536)
  self.wr(n.base+0x16a3740,index,4);self.wr(self.teb+88,self.array,8);self.wr(self.array+index*8,self.block,8);self.wr(self.block+16,epoch,4)
  self.wr(n.base+0x17a4220,0,4)
  for field in (0x17350ec,0x17350e4):self.wr(n.base+field,sentinel,4)
  u.reg_write(UC_ARM64_REG_X18,self.teb)
  self.srw_ready=True;self.srw_held=False;self.guard_callback=None;self.guard_returns=0;self.field_stores=0;self.field_order=[]
  self.models={}

 def wr(self,a,v,z):self.u.mem_write(a,(v&((1<<(z*8))-1)).to_bytes(z,"little"))
 def rd(self,a,z):return int.from_bytes(self.u.mem_read(a,z),"little")
 def regs(self):return {r:self.u.reg_read(r) for r in ALLREG}
 def snapshot(self):return {(lo,hi,p):bytes(self.u.mem_read(lo,hi-lo+1)) for lo,hi,p in self.u.mem_regions()}
 def logical(self):return self.ready,self.held,self.srw_ready,self.srw_held,self.next_dep,self.callbacks,self.stores,self.field_stores,self.guard_returns
 def reject(self,fn,tests):
  regs=self.regs();state=self.logical()
  for args in tests:
   try:fn(*args)
   except AssertionError:pass
   else:raise AssertionError("invalid owned dependency contract admitted")
  assert self.regs()==regs and self.logical()==state
  self.negatives+=len(tests)
 def entry(self,rva,sp,ret,obj,ready,held):
  n=self.n;assert rva==0x5de700 and sp==self.stacktop and sp%16==0 and ret==n.end
  assert obj==self.obj and ready and not held
  assert self.rd(self.obj,8)==n.base+0x1330a68
  assert self.rd(n.base+0x1330a70,8)==n.base+0x1df30 and self.rd(n.base+0x1330a78,8)==n.base+0x1df90
  assert self.rd(n.base+0xf7e7b8,8)==n.base+0x1a8c0 and self.rd(n.base+0x17350e0,4)==self.bound
  assert all(self.rd(n.base+cell,8)==self.apis[name] for name,cell in BINDINGS.items())
  assert self.srw_ready and not self.srw_held and self.index in (0,37) and self.epoch in (0x80000000,0xfffffffe)
  assert self.u.reg_read(UC_ARM64_REG_X18)==self.teb and self.rd(n.base+0x16a3740,4)==self.index
  assert self.rd(self.teb+88,8)==self.array and self.rd(self.array+self.index*8,8)==self.block and self.rd(self.block+16,4)==self.epoch
  assert self.rd(n.base+0x17a4220,4)==0 and all(self.rd(n.base+field,4)==self.sentinel for field in (0x17350ec,0x17350e4))

 def dependency(self,name,ret,args,ready,held):
  n=self.n;assert ready and name==self.expected_deps[self.next_dep]
  if name.startswith("diagnostic"):
   enter=name=="diagnostic_enter"
   assert ret==n.base+(0x1df68 if enter else 0x1dfc8)
   assert args==[5,65535,n.base+(0x1352650 if enter else 0x1352688),n.base+0x1352590,41 if enter else 50,self.resource]
   assert held==(not enter)
  elif name in ("AcquireSRWLockExclusive","ReleaseSRWLockExclusive"):
   assert held and self.held and self.srw_ready and self.srw_held==(name=="ReleaseSRWLockExclusive")
   assert ret==n.base+(0xce7b08 if name=="AcquireSRWLockExclusive" else 0xce7b80) and args==[n.base+0x16a3738]
  else:
   assert ret==n.base+(0x1df78 if name=="EnterCriticalSection" else 0x1dfd8)
   assert args==[self.resource] and held==(name=="LeaveCriticalSection")
 def patch_stack(self,a,data):
  if self.n.stack<=a and a+len(data)<=self.n.stack+65536:
   self.expected_stack[a-self.n.stack:a-self.n.stack+len(data)]=data
  else:
   site=self.u.reg_read(UC_ARM64_REG_PC)-self.n.base;field=a-self.n.base;value=int.from_bytes(data,"little")
   assert FIELDS.get((site,field,len(data)))==value,("unowned source store",hex(site),hex(field),len(data))
   assert (site,field,len(data)) not in self.field_order
   self.field_order.append((site,field,len(data)));self.field_stores+=1
   key=next(k for k in self.before if k[0]<=a and a+len(data)<=k[1]+1)
   if key not in self.models:self.models[key]=bytearray(self.before[key])
   self.models[key][a-key[0]:a-key[0]+len(data)]=data

 def code(self,u,pc,z,_):
  n=self.n;assert not self.pending
  if self.callback and pc==self.callback["ret"]:
   assert all(u.reg_read(r)==v for r,v in self.callback["saved"].items()),"callback callee ABI did not restore"
   self.callback=None;self.callbacks+=1
  r=pc-n.base
  if self.guard_callback and pc==self.guard_callback["ret"]:
   assert all(u.reg_read(k)==v for k,v in self.guard_callback["saved"].items()),"guard callee ABI did not restore"
   self.guard_callback=None;self.guard_returns+=1
  if r==0x2ee1a0:
   assert self.held and not self.srw_held and self.callback is None and self.guard_callback is None and self.next_dep==4
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+0x5b9094
   self.stopped=True;self.next_args=[u.reg_read(UC_ARM64_REG_X0)-n.base,u.reg_read(UC_ARM64_REG_X1)]
   assert self.next_args==[0x17a7088,0xffff]
   u.emu_stop();return
  if r==0x5b80a8:
   assert u.reg_read(UC_ARM64_REG_X0)==0 and u.reg_read(UC_ARM64_REG_LR)==n.base+0x5de844
  if r==0xce7ad8:
   assert self.guard_callback is None and u.reg_read(UC_ARM64_REG_X0)==n.base+0x17a4220 and u.reg_read(UC_ARM64_REG_LR)==n.base+0x5b9074
   self.guard_callback={"ret":u.reg_read(UC_ARM64_REG_LR),"saved":{k:u.reg_read(k) for k in NONVOL}}

  if r==0x1aca8 or pc in self.reverse:
   if r==0x1aca8:
    name="diagnostic_enter" if self.next_dep==0 else "diagnostic_leave"
    args=[u.reg_read(globals()["UC_ARM64_REG_X"+str(k)]) for k in range(6)]
   else:name=self.reverse[pc];args=[u.reg_read(UC_ARM64_REG_X0)]
   ret=u.reg_read(UC_ARM64_REG_LR)
   self.dependency(name,ret,args,self.ready,self.held)
   tests=[(name,ret+4,args,self.ready,self.held),(name,ret,args+[0],self.ready,self.held),(name,ret,args,False,self.held),(name,ret,args,self.ready,not self.held)]
   for k in range(len(args)):
    a=args.copy();a[k]+=1;tests.append((name,ret,a,self.ready,self.held))
   if name in ("AcquireSRWLockExclusive","ReleaseSRWLockExclusive"):
    old=self.srw_held;self.srw_held=not old
    try:self.reject(self.dependency,[(name,ret,args,self.ready,self.held)])
    finally:self.srw_held=old
    old=self.srw_ready;self.srw_ready=False
    try:self.reject(self.dependency,[(name,ret,args,self.ready,self.held)])
    finally:self.srw_ready=old
   self.reject(self.dependency,tests)
   if name=="EnterCriticalSection":self.held=True
   elif name=="LeaveCriticalSection":self.held=False
   elif name=="AcquireSRWLockExclusive":self.srw_held=True
   elif name=="ReleaseSRWLockExclusive":self.srw_held=False
   self.next_dep+=1;self.dep_names.append(name)
   # Void/no-effect dependency adapters deliberately return arbitrary volatile X0 values.
   u.reg_write(UC_ARM64_REG_X0,self.diag_clobber if name.startswith("diagnostic") else self.api_clobber)
   u.reg_write(UC_ARM64_REG_PC,ret);return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4),("unqualified code reached",hex(r))
  if r in (0x1df30,0x1df90):
   assert self.callback is None and u.reg_read(UC_ARM64_REG_X0)==self.obj
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+(0x5de7b4 if r==0x1df30 else 0x5df6e4)
   self.callback={"ret":u.reg_read(UC_ARM64_REG_LR),"saved":{k:u.reg_read(k) for k in NONVOL}}
  if r==0x1a8c0:
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+(0x5de7b0 if not self.held else 0x5df6e0)
   self.cfg_visits+=1
  assert len(self.trace)<300;self.trace.append(r);i=INS[r]
  if i.mnemonic.startswith(("str","stp","stur")):
   memory=next(o for o in i.operands if o.type==capstone.arm64.ARM64_OP_MEM)
   assert not memory.mem.index
   at=reg(u,C.reg_name(memory.mem.base))+memory.mem.disp
   ops=i.operands[:2] if i.mnemonic=="stp" else i.operands[:1]
   for k,o in enumerate(ops):
    name=C.reg_name(o.reg)
    size=16 if name.startswith("q") else 8 if name.startswith(("x","d")) or name in ("fp","lr") else 4
    addr=at+k*size;v=reg(u,name)&((1<<(size*8))-1)
    self.patch_stack(addr,v.to_bytes(size,"little"));self.pending[addr,size]=v
 def write(self,u,access,at,size,value,_):
  value&=(1<<(size*8))-1
  assert self.pending.pop((at,size),None)==value
  self.stores+=1
 def read(self,u,access,at,size,value,_):
  n=self.n
  if n.stack<=at and at+size<=n.stack+65536:return
  allowed={(n.base+0x1607000,8),(n.base+0x160a218,8),(n.base+0x1608858,4),
   (self.obj,8),(n.base+0x1330a70,8),(n.base+0x1330a78,8),(n.base+0xf7e7b8,8),
   (n.base+0x17350e0,4)}|{(n.base+cell,8) for cell in BINDINGS.values()}
  allowed|={(n.base+0x5df760,8),(n.base+0x5df768,8),(n.base+0x16a3740,4),(n.base+0x17a4220,4),(self.teb+88,8),(self.array+self.index*8,8),(self.block+16,4)}
  assert (at,size) in allowed,("unowned nonstack read",hex(at-n.base),size)
 def run(self):
  n=self.n;u=self.u
  args=(0x5de700,self.stacktop,n.end,self.obj,self.ready,self.held);self.entry(*args)
  bad=[]
  for k in range(4):
   a=list(args);a[k]+=4;bad.append(tuple(a))
  bad.extend([(*args[:4],False,False),(*args[:4],True,True)])
  self.reject(self.entry,bad)
  checks=[(self.obj,n.base+0x1330a70,8),(n.base+0x1330a70,n.base+0x1df34,8),(n.base+0x1330a78,n.base+0x1df94,8),(n.base+0xf7e7b8,n.base+0x1a8c4,8),(n.base+0x17350e0,(self.bound+1)&0xffffffff,4)]
  checks+=[(n.base+cell,self.apis[name]+4,8) for name,cell in BINDINGS.items()]
  checks+=[(n.base+0x16a3740,self.index+1,4),(self.teb+88,self.array+8,8),(self.array+self.index*8,self.block+8,8),(self.block+16,self.epoch+1,4),(n.base+0x17a4220,1,4)]
  checks+=[(n.base+field,self.sentinel^1,4) for field in (0x17350ec,0x17350e4)]

  for at,v,size in checks:
   old=bytes(u.mem_read(at,size));self.wr(at,v,size)
   try:self.reject(self.entry,[args])
   finally:u.mem_write(at,old)
  self.before=self.snapshot();self.expected_stack=bytearray(u.mem_read(n.stack,65536))
  saved={k:u.reg_read(k) for k in NONVOL}
  hooks=[u.hook_add(UC_HOOK_CODE,self.code),u.hook_add(UC_HOOK_MEM_WRITE,self.write),u.hook_add(UC_HOOK_MEM_READ,self.read)]
  try:u.emu_start(n.base+0x5de700,n.end,count=500)
  finally:
   for h in hooks:u.hook_del(h)
  assert not self.pending and self.callback is None
  assert self.dep_names==self.expected_deps
  assert self.callbacks==1 and self.guard_returns==1
  assert self.cfg_visits==self.callbacks
  assert self.stopped and u.reg_read(UC_ARM64_REG_PC)==n.base+0x2ee1a0 and self.held and not self.srw_held
  assert self.guard_callback is None and self.field_order==list(FIELDS) and self.field_stores==3
  after=self.snapshot();assert after.keys()==self.before.keys()
  for k,v in self.before.items():
   assert after[k]==(bytes(self.expected_stack) if k[0]==n.stack else bytes(self.models[k]) if k in self.models else v),"whole mapped memory mismatch"

  return {"stack_bias":self.bias,"loader_index":self.index,"thread_epoch":self.epoch,"initial_bound_sentinel":self.sentinel,"diagnostic_X0":self.diag_clobber,"OS_void_X0":self.api_clobber,
   "original_instruction_visits":len(self.trace),"first_helper_instruction_visits":sum(0x5b80a8<=r<=0x5b90af for r in self.trace),
   "guard_instruction_visits":sum(0xce7ad8<=r<=0xce7b93 for r in self.trace),"frame_helper_instruction_visits":sum(r<0x1300 for r in self.trace),
   "callback_returns_ABI_exact":self.callbacks,"guard_returns_ABI_exact":self.guard_returns,"owned_OS_API_calls":3,"owned_diagnostic_calls":1,
   "stack_store_chunks":self.stores-self.field_stores,"nonstack_field_store_chunks":self.field_stores,"invalid_owned_dependency_requests_rejected":self.negatives,
   "whole_mapped_memory_and_permissions_exact":True,"immutable_source_and_loader_regions":True,"registry_logical_lock_held":self.held,"SRW_logical_lock_held":self.srw_held,
   "stop_before_RVA":"0x2ee1a0","caller_return_RVA":"0x5b9094","next_object_RVA":hex(self.next_args[0]),"next_scalar_argument":self.next_args[1],"parent_returned":False,"first_helper_returned":False}
def main():
 rows=[]
 for bias in (0,16,128,512):
  for index in (0,37):
   for epoch in (0x80000000,0xfffffffe):
    for sentinel in (0,0xffffffff):
     for diag in (0,0x8877665544332211):
      for api in (0,0xffeeddccbbaa9988):
       rows.append(Case(bias,index,epoch,sentinel,diag,api).run())
 fields=("original_instruction_visits","first_helper_instruction_visits","guard_instruction_visits","frame_helper_instruction_visits","callback_returns_ABI_exact","guard_returns_ABI_exact","owned_OS_API_calls","owned_diagnostic_calls","stack_store_chunks","nonstack_field_store_chunks","invalid_owned_dependency_requests_rejected")
 report={"experiment":"E011DP","status":"PASS_BOUNDED_ORIGINAL_COLD_BOUNDS_AND_FIRST_HELPER_GUARD","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,
 "literal_definitions":[{"definition_RVA":hex(r),"constant":v} for r,v in LITERALS],
 "expected_nonstack_fields":[{"store_RVA":hex(r),"field_RVA":hex(f),"bytes":z,"value":v} for (r,f,z),v in FIELDS.items()],
 "standard_OS_IAT_RVAs":{k:hex(v) for k,v in BINDINGS.items()},"first_helper_RVA":"0x5b80a8","first_helper_caller_return_RVA":"0x5de844",
 "guard_RVA":"0xce7ad8","guard_caller_return_RVA":"0x5b9074","stop_before_RVA":"0x2ee1a0","next_caller_return_RVA":"0x5b9094",
 "loader_TLS_and_OS_resource_readiness_operations_are_owned_models":True,"diagnostic_no_effect_dependency_is_owned_model":True,
 "bound_or_helper_or_guard_result_fixture_used":False,"whole_mapped_memory_and_permissions_exact":True,"immutable_source_and_loader_regions":True,
 "first_helper_complete_return_qualified":False,"cold_parent_return_or_unlock_qualified":False,"full_cold_registry_initialization_qualified":False,
 "descriptor_construction_allocation_and_publication_qualified":False,"native_Windows_OS_resources_qualified":False,
 "selected_runtime_reader_profile_qualified":False,"populated_RS_identity_generation_lifetime_qualified":False,"normal_AFD_input_authority_closed":False,
 "complete_deterministic_source_bootstrap_closed":False,"independent_enabled_output_retirement_proven":False,"native_rear_runtime_allowed":False,
 "new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,"production_code_changed":False,"private_raw_material_exported":False,"next_experiment":"E011DQ",
 "details":rows,"totals":{k:sum(r[k] for r in rows) for k in fields}}
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({k:report[k] for k in ("status","scenarios","totals","next_experiment")}),flush=True)
if __name__=="__main__":main()
