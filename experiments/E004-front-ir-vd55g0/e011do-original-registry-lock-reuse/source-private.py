#!/usr/bin/env python3
"""Same-SP11 original registry lock/reuse path under owned OS/diagnostic contracts."""
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
 0x5de700:[(0x5de700,0x5df75b)],0x1df30:[(0x1df30,0x1df8b)],0x1df90:[(0x1df90,0x1dfeb)],
 0x1a8c0:[(0x1a8c0,0x1a8c3)],0x11d0:[(0x11d0,0x11e7)],
 0x11f0:[(0x11f0,0x120f),(0x1214,0x121b),(0x1220,0x1233)]}
PINS={hex(entry):{"body_bytes":sum(hi-lo+1 for lo,hi in ranges),"ranges":[[hex(lo),hex(hi)] for lo,hi in ranges],
"sha256":hashlib.sha256(b"".join(PE.get_data(lo,hi-lo+1) for lo,hi in ranges)).hexdigest()} for entry,ranges in RANGES.items()}
assert PINS["0x5de700"]["sha256"]=="776092eab939986d2258713b25723c3ad4c1ddcdc8231881da140e25a9960533"
C=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);C.detail=True
INS={i.address:i for ranges in RANGES.values() for lo,hi in ranges for i in C.disasm(PE.get_data(lo,hi-lo+1),lo)}
BINDINGS={}
for e in PE.DIRECTORY_ENTRY_IMPORT:
 for x in e.imports:
  name=(x.name or b"").decode()
  if name in ("EnterCriticalSection","LeaveCriticalSection"):BINDINGS[name]=x.address-PE.OPTIONAL_HEADER.ImageBase
assert BINDINGS=={"EnterCriticalSection":0xf7e0b8,"LeaveCriticalSection":0xf7e0c0}
NONVOL=[UC_ARM64_REG_SP,*[globals()["UC_ARM64_REG_X"+str(k)] for k in range(19,30)],*[globals()["UC_ARM64_REG_D"+str(k)] for k in range(8,16)]]
ALLREG=[UC_ARM64_REG_PC,UC_ARM64_REG_LR,*[globals()["UC_ARM64_REG_X"+str(k)] for k in range(29)],UC_ARM64_REG_SP]
def reg(u,name):
 if name in ("xzr","wzr"):return 0
 name={"fp":"x29","lr":"x30"}.get(name,name)
 if name.startswith("w"):return u.reg_read(globals()["UC_ARM64_REG_X"+name[1:]])&0xffffffff
 return u.reg_read(globals()["UC_ARM64_REG_"+name.upper()])
class Case:
 def __init__(self,bias,bound,diag_clobber,api_clobber):
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
  self.expected_deps=["diagnostic_enter","EnterCriticalSection"]+([] if bound==0 else ["diagnostic_leave","LeaveCriticalSection"])
 def wr(self,a,v,z):self.u.mem_write(a,(v&((1<<(z*8))-1)).to_bytes(z,"little"))
 def rd(self,a,z):return int.from_bytes(self.u.mem_read(a,z),"little")
 def regs(self):return {r:self.u.reg_read(r) for r in ALLREG}
 def snapshot(self):return {(lo,hi,p):bytes(self.u.mem_read(lo,hi-lo+1)) for lo,hi,p in self.u.mem_regions()}
 def logical(self):return self.ready,self.held,self.next_dep,self.callbacks,self.stores
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
 def dependency(self,name,ret,args,ready,held):
  n=self.n;assert ready and name==self.expected_deps[self.next_dep]
  if name.startswith("diagnostic"):
   enter=name=="diagnostic_enter"
   assert ret==n.base+(0x1df68 if enter else 0x1dfc8)
   assert args==[5,65535,n.base+(0x1352650 if enter else 0x1352688),n.base+0x1352590,41 if enter else 50,self.resource]
   assert held==(not enter)
  else:
   assert ret==n.base+(0x1df78 if name=="EnterCriticalSection" else 0x1dfd8)
   assert args==[self.resource] and held==(name=="LeaveCriticalSection")
 def patch_stack(self,a,data):
  assert self.n.stack<=a and a+len(data)<=self.n.stack+65536
  self.expected_stack[a-self.n.stack:a-self.n.stack+len(data)]=data
 def code(self,u,pc,z,_):
  n=self.n;assert not self.pending
  if self.callback and pc==self.callback["ret"]:
   assert all(u.reg_read(r)==v for r,v in self.callback["saved"].items()),"callback callee ABI did not restore"
   self.callback=None;self.callbacks+=1
  r=pc-n.base
  if self.bound==0 and r==0x5de800:
   assert self.held and self.callback is None and self.next_dep==2
   self.stopped=True;u.emu_stop();return
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
   self.reject(self.dependency,tests)
   if name=="EnterCriticalSection":self.held=True
   elif name=="LeaveCriticalSection":self.held=False
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
  assert len(self.trace)<200;self.trace.append(r);i=INS[r]
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
  assert self.callbacks==(1 if self.bound==0 else 2)
  assert self.cfg_visits==self.callbacks
  if self.bound==0:assert self.stopped and u.reg_read(UC_ARM64_REG_PC)==n.base+0x5de800 and self.held
  else:
   assert u.reg_read(UC_ARM64_REG_PC)==n.end and not self.held
   assert all(u.reg_read(k)==v for k,v in saved.items()),"initializer ABI did not restore"
  after=self.snapshot();assert after.keys()==self.before.keys()
  for k,v in self.before.items():
   assert after[k]==(bytes(self.expected_stack) if k[0]==n.stack else v),"whole mapped memory mismatch"
  return {"stack_bias":self.bias,"initial_bound_fixture":self.bound,"diagnostic_X0":self.diag_clobber,"OS_void_X0":self.api_clobber,
   "path":"cold_prefix" if self.bound==0 else "initialized_reuse","original_instruction_visits":len(self.trace),
   "callback_instruction_visits":sum(0x1df30<=r<0x1df8c or 0x1df90<=r<0x1dfec for r in self.trace),
   "original_CFG_nop_visits":self.cfg_visits,"original_frame_helper_visits":sum(r<0x1300 for r in self.trace),
   "callback_returns_ABI_exact":self.callbacks,"owned_OS_API_calls":sum(not x.startswith("diagnostic") for x in self.dep_names),
   "owned_diagnostic_calls":sum(x.startswith("diagnostic") for x in self.dep_names),"stack_store_chunks":self.stores,
   "invalid_owned_dependency_requests_rejected":self.negatives,"source_and_nonstack_memory_immutable":True,"logical_lock_held_at_boundary":self.held,
   "parent_returned":self.bound!=0,"stop_before_RVA":"0x5de800" if self.bound==0 else None}
def main():
 live=PRIVATE/"E011DN-explore/windows-recovered/E011DN-20261003-1926B/capture/READY_META.bin"
 evidence=R/"experiments/E004-front-ir-vd55g0/e011dn-windows-registry-boundary/OBSERVATION-SAFE.json"
 authority=json.loads(evidence.read_text())
 snapshot_sha=hashlib.sha256(live.read_bytes()).hexdigest()
 assert snapshot_sha==authority["private_nonoptical_evidence_hashes"]["E011DN-20261003-1926B/capture/READY_META.bin"]
 observed_bound=struct.unpack_from("<I",live.read_bytes(),0)[0];assert observed_bound not in (0,1,0xffffffff)
 rows=[]
 for bias in (0,16,128,512):
  for bound in (0,1,observed_bound,0xffffffff):
   for diag in (0,0x8877665544332211):
    for api in (0,0xffeeddccbbaa9988):
     rows.append(Case(bias,bound,diag,api).run())
 report={"experiment":"E011DO","status":"PASS_BOUNDED_ORIGINAL_REGISTRY_LOCK_AND_INITIALIZED_REUSE","scenarios":len(rows),
 "cold_prefix_cases":sum(r["path"]=="cold_prefix" for r in rows),"initialized_reuse_cases":sum(r["path"]=="initialized_reuse" for r in rows),
 "source_pins":PINS,"image_sha256":M.DLL_SHA,"observed_ready_bound_fixture":observed_bound,
 "input_evidence_locks":{"E011DN_OBSERVATION_SAFE":hashlib.sha256(evidence.read_bytes()).hexdigest(),"private_READY_META":snapshot_sha},"default_callback_table_RVA":"0x1330a68","resource_object_RVA":"0x1626898","critical_section_offset":"0x8",
 "standard_OS_IAT_RVAs":{k:hex(v) for k,v in BINDINGS.items()},"cold_stop_before_RVA":"0x5de800",
 "next_cold_helper_RVA":"0x5b80a8","next_cold_helper_caller_return_RVA":"0x5de844",
 "pre_existing_bound_values_are_owned_fixtures":True,"OS_critical_section_readiness_and_operations_are_owned_models":True,
 "diagnostic_no_effect_dependency_is_owned_model":True,"native_Windows_OS_resources_qualified":False,
 "original_lock_callbacks_and_initialized_branch_executed":True,"callback_result_fixture_used":False,
 "whole_mapped_memory_and_permissions_exact":True,"source_and_nonstack_memory_immutable":True,"callback_callee_ABI_exact":True,
 "initialized_parent_return_ABI_exact":True,"cold_parent_return_or_unlock_qualified":False,"full_cold_registry_initialization_qualified":False,
 "descriptor_construction_allocation_and_publication_qualified":False,"selected_runtime_reader_profile_qualified":False,
 "populated_RS_identity_generation_lifetime_qualified":False,"normal_AFD_input_authority_closed":False,
 "complete_deterministic_source_bootstrap_closed":False,"independent_enabled_output_retirement_proven":False,"native_rear_runtime_allowed":False,
 "new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,"production_code_changed":False,"private_raw_material_exported":False,
 "next_experiment":"E011DP","details":rows}
 fields=("original_instruction_visits","callback_instruction_visits","original_CFG_nop_visits","original_frame_helper_visits","callback_returns_ABI_exact","owned_OS_API_calls","owned_diagnostic_calls","stack_store_chunks","invalid_owned_dependency_requests_rejected")
 report["totals"]={k:sum(r[k] for r in rows) for k in fields}
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({k:report[k] for k in ("status","scenarios","cold_prefix_cases","initialized_reuse_cases","totals","next_experiment")}))
if __name__=="__main__":main()
