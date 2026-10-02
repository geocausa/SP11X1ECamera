#!/usr/bin/env python3
"""Same-SP11 original query forwarder differential in owned memory; no driver/runtime access."""
from pathlib import Path
import collections,hashlib,importlib.util,json,random,struct
import pefile,capstone
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
BW=load("by_weights",EX/"e011bw-rear-source-cold-aec-weights/source-private.py")
class Forward(BW.Flow):
 def __init__(self):
  super().__init__();self.forward_events=[];self.context_id=0;self.native_backend=False
 def hook(self,u,pc,size,user):
  r=pc-self.n.base
  if r in [0x85276c,0x36e610,0x36e634]:
   target=u.reg_read(UC_ARM64_REG_X15 if r==0x85276c else UC_ARM64_REG_X8)
   wanted={0x85276c:0x36e460,0x36e610:0x374050,0x36e634:0x372e40}[r]
   assert target==self.n.base+wanted,"owned dispatch target mismatch"
   if r==0x36e610:
    assert u.reg_read(UC_ARM64_REG_X0)==self.inner
    assert u.reg_read(UC_ARM64_REG_W1)==self.context_id
   if r==0x36e634:assert u.reg_read(UC_ARM64_REG_X0)==self.inner
   self.forward_events.append(("dispatch",r,wanted))
   self.stubs["checked_forward_dispatch"]+=1
   u.reg_write(UC_ARM64_REG_X15,target);u.reg_write(UC_ARM64_REG_PC,pc+4);return
  if r==0x3740b4:
   wanted=0x3ae320 if self.native_backend else 0x1a8c0
   assert u.reg_read(UC_ARM64_REG_X8)==self.n.base+wanted
   assert u.reg_read(UC_ARM64_REG_X0)==self.sink and u.reg_read(UC_ARM64_REG_W1)==self.context_id
   self.stubs["checked_native_core_context_dispatch" if self.native_backend else "controlled_core_context_setter"]+=1
   u.reg_write(UC_ARM64_REG_X15,self.n.base+wanted);u.reg_write(UC_ARM64_REG_PC,pc+4);return
  if r==0x36e53c:
   self.stubs["forward_logging"]+=1;u.reg_write(UC_ARM64_REG_X15,self.n.base+0x1a8c0)
   u.reg_write(UC_ARM64_REG_PC,pc+4);return
  if r in [0x36e460,0x374050,0x372e40,0x3ae320]:self.forward_events.append(("entry",r,0))
  if r in [0x36e668,0x3740cc,0x3ae368]:self.forward_events.append(("return",r,u.reg_read(UC_ARM64_REG_X0)))
  super().hook(u,pc,size,user)
 def reset(self,cache,bias,selector,allocated=92,kind=None):
  super().reset(cache,bias,selector,allocated,kind)
  n=self.n;u=self.u;self.inner=n.heap+0x26000+bias
  # Explicit owned inner-class/manager composition; its constructor is excluded.
  u.mem_write(self.inner,struct.pack("<Q",n.base+0x1337fd8))
  u.mem_write(self.inner+0x28,struct.pack("<Q",self.manager))
  self.coretable=n.heap+0x25000;self.box=n.heap+0x26800;self.sink=n.heap+0x26900
  u.mem_write(self.inner+8,struct.pack("<Q",self.box));u.mem_write(self.box,struct.pack("<Q",self.sink))
  u.mem_write(self.sink,struct.pack("<Q",n.base+0x1338428 if self.native_backend else self.coretable))
  # Original inner setter runs; baseline backend is inert, native variant uses the original core setter.
  u.mem_write(self.coretable+296,struct.pack("<Q",n.base+0x1a8c0))
  u.mem_write(self.wrapper+8,struct.pack("<Q",n.base+0x36e460))
  u.mem_write(self.wrapper+0x28,struct.pack("<Q",self.inner))
  u.mem_write(self.wrapper+68,struct.pack("<I",self.context_id))
  self.forward_events=[]
 def supported(self,cache,bias,selector,context_id):
  self.context_id=context_id
  result=self.run(cache,bias,selector)
  for tag,rva in [("entry",0x36e460),("entry",0x374050),("entry",0x372e40),("return",0x36e668),("return",0x3740cc)]:
   assert sum(t==tag and r==rva for t,r,v in self.forward_events)==1,"full original forwarder/setter return"
  assert [target for tag,site,target in self.forward_events if tag=="dispatch"]==[0x36e460,0x374050,0x372e40]
  assert self.stubs["checked_native_core_context_dispatch" if self.native_backend else "controlled_core_context_setter"]==1
  if self.native_backend:
   assert self.stubs["controlled_core_context_setter"]==0
   for tag,rva in [("entry",0x3ae320),("return",0x3ae368)]:
    assert sum(t==tag and r==rva for t,r,v in self.forward_events)==1
  tls=bytes(self.u.mem_read(self.tls+0x2000+304,4))
  assert struct.unpack("<I",tls)[0]==context_id,"original TLS context propagation"
  assert bytes(self.u.mem_read(self.inner+0x28,8))==struct.pack("<Q",self.manager)
  assert next(v for t,r,v in self.forward_events if t=="return" and r==0x36e668)==0
  return result
def facts():
 raw=BW.N.DLL.read_bytes();assert hashlib.sha256(raw).hexdigest()==BW.N.DLL_SHA
 p=pefile.PE(data=raw);base=p.OPTIONAL_HEADER.ImageBase
 cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);cs.detail=True
 def ins(r):return next(cs.disasm(p.get_data(r,4),r))
 for r in [0x36e610,0x36e634,0x3740b4]:
  i=ins(r);assert i.mnemonic=="blr" and cs.reg_name(i.operands[0].reg)=="x17"
  i=ins(r+4);assert i.mnemonic=="blr" and cs.reg_name(i.operands[0].reg)=="x15"
 for r in [0x36e668,0x3740cc,0x3ae368]:assert ins(r).mnemonic=="ret"
 for r,owner,offset in [(0x36e5f4,"x20",40),(0x36e5f8,"x20",68),(0x36e600,"x8",32),(0x36e624,"x8",24),(0x374098,"x21",8),(0x3740a4,"x8",296)]:
  i=ins(r);assert i.mnemonic=="ldr"
  o=i.operands[-1];assert cs.reg_name(o.mem.base)==owner and o.mem.disp==offset
 assert struct.unpack("<Q",p.get_data(0x1337fd8+24,8))[0]-base==0x372e40
 assert struct.unpack("<Q",p.get_data(0x1337fd8+32,8))[0]-base==0x374050
 assert struct.unpack("<Q",p.get_data(0x1338428+296,8))[0]-base==0x3ae320
 return {"original_DLL_sha256" :BW.N.DLL_SHA,"actual_outer_callback_RVA":"0x36E460",
 "outer_inner_object_pointer_offset":40,"outer_context_ID_u32_offset":68,
 "inner_original_vtable_RVA":"0x1337FD8","inner_context_setter_slot_offset":32,
 "inner_context_setter_RVA":"0x374050","inner_GetParam_slot_offset":24,"inner_GetParam_RVA":"0x372E40",
 "inner_manager_pointer_offset":40,"inner_backend_interface_box_offset":8,
 "backend_context_setter_slot_offset":296,"original_TLS_context_u32_offset":304,"source_core_vtable_RVA":"0x1338428","original_core_context_setter_RVA":"0x3AE320",
 "source_ranges":[{"RVA":hex(r),"bytes":z,"sha256":hashlib.sha256(p.get_data(r,z)).hexdigest()}
 for r,z in [(0x36e460,524),(0x374050,128),(0x372e40,4616),(0x3ae320,76)]]}
def main():
 authority=facts();roots,audit=BW.source_roots();cases=list(roots);rng=random.Random(0xe011b9)
 for bits in [0,1,0x3d000000,0x3f800000,0x80000000,0x7fc00000,0xffffffff]+[None]*64:
  wire,cache=roots[-1];w=bytearray(wire);c=bytearray(cache)
  block=struct.pack("<3I",*([bits]*3 if bits is not None else [rng.randrange(0x3f800001) for _ in range(3)]))
  for i in range(4):w[101*i+20:101*i+32]=block
  c[20:32]=block;cases.append((bytes(w),bytes(c)))
 f=Forward();calls=0
 for context in [0,1,0xffffffff]:
  for bias in [0,1,0x40,0x1230]:
   for wire,cache in cases:
    results=[]
    for native in [False,True]:
     f.native_backend=native
     a=f.supported(cache,bias,12,context);b=f.supported(cache,bias,20,context)
     assert a==b;results.append(a);calls+=2
    assert results[0]==results[1],"full native context setter must preserve normal query outputs"
  print(json.dumps({"experiment":"E011BY","phase":"source_forwarder","completed_queries":calls}),flush=True)
 out={"experiment":"E011BY","status":"PASS_BOUNDED_ORIGINAL_OUTER_QUERY_AND_CONTEXT_FORWARDING",
  "base_commit":"b074d4730289253ef8580b61c00f01506444683b",**authority,
  "source_files":audit,"owned_source_cases":len(cases),"owned_memory_placements":4,"owned_context_ID_patterns":3,
  "original_complete_engine_outer_setter_GetParam_manager_getter_chains":calls,
  "original_outer_returns":calls,"original_context_setter_returns":calls,"original_GetParam_manager_getter_returns_each":calls,
  "typed_result_bytes":92,"numeric_callbacks_unmodified":True,"original_TLS_context_propagation_verified":True,
  "controlled_interfaces":["checked dispatch","allocation/free","TLS diagnostics","logging","inner backend context setter in baseline comparison only"],
  "inner_backend_context_setter_source_qualified_and_executed_returns":calls//2,
  "native_context_variant_has_no_backend_context_stub":True,
  "inner_backend_context_setter_implementation_qualified_in_source_fixture":True,"whole_inner_or_manager_construction_qualified":False,
  "actual_live_inner_vtable_or_context_ID_captured":False,"live_outer_full_loaded_code_qualification_closed":False,
  "source_forwarding_ABI_closed_in_owned_fixture":True,"actual_opened_filename_closed":False,
  "new_camera_Starts":0,"new_reboots":0,"native_rear_runtime_allowed":False,"original_bytes_exported":False}
 (HERE/"FORWARD-SAFE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out),flush=True)
if __name__=="__main__":main()
