#!/usr/bin/env python3
"""Bounded original cached-object setup, nested lock and large image-buffer clear."""
from pathlib import Path
import hashlib,importlib.util,json,inspect,textwrap,itertools
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011dr-original-cleanup-registration-publication/source-private.py"
assert hashlib.sha256(P.read_bytes()).hexdigest()=="5a616434a4a64d22c07dd122d1f5afe0137e5ef9edb717aaa4aed3fe78a931d0"
s=importlib.util.spec_from_file_location("dr_original",P);DR=importlib.util.module_from_spec(s);s.loader.exec_module(DR)
import capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
M=DR.M;PE=DR.PE;INS=DR.INS;C=DR.C;PINS=DR.PINS;NONVOL=DR.NONVOL;BINDINGS=DR.BINDINGS
OUT=Path(__file__).resolve().parent
LITERAL_AUTHORITY={"window_RVA":"0xf5e600","window_bytes":428,"sha256":"d25748e9674f7a7b1505aff0e9b9517c5dc96221e1e0b6f37fcc0eef2b22d4f3","permitted_read_RVA":"0xf5e64c","permitted_read_bytes":1}
assert hashlib.sha256(PE.get_data(0xf5e600,428)).hexdigest()==LITERAL_AUTHORITY["sha256"]
class Case(DR.Case):
 def __init__(self,*args):
  super().__init__(*args);n=self.n
  self.ext=False;self.ext_ready=True;self.inner_ready=True;self.inner_held=False;self.ext_dep=0;self.ext_frame=None;self.ext_cfg=None
  self.ext_callbacks=self.ext_cfg_returns=self.ext_clear_returns=self.clear_stores=0;self.clearing=False;self.ext_visits=[];self.literal_reads=0
  self.cached=n.base+0x1731880;self.inline=n.base+0x17a4230;self.inner_obj=n.base+0x1623598;self.inner_resource=self.inner_obj+8
  self.clear_at=self.inline+56;self.clear_bytes=11808
  self.wr(self.cached,0,8)
  assert self.rd(self.inner_obj,8)==n.base+0x1330a68
  assert self.rd(self.inline+44,4)==self.rd(n.base+0x17a1180,4)==0
  assert bytes(self.u.mem_read(self.inline,56))==bytes(56)
  self.u.mem_write(self.clear_at,bytes([self.poison])*self.clear_bytes)
  self.u.mem_write(self.inline+20,bytes([self.poison])*4)
  for site,off,width,value in ((0x5b8138,0,8,self.inline),(0x5b822c,40,8,32769),(0x5b822c,48,8,0),(0x5b8234,0,8,0),(0x5b8234,8,8,0),(0x5b8240,16,4,0),(0x5b8248,24,8,0),(0x5b8248,32,8,0)):
   self.fields[site,self.cached if site==0x5b8138 else self.inline+off,width]=value
  assert len(self.fields)==130
 def logical(self):
  return super().logical()+(getattr(self,"ext_ready",False),getattr(self,"inner_ready",False),getattr(self,"inner_held",False),getattr(self,"ext_dep",0),getattr(self,"ext_callbacks",0),getattr(self,"ext_cfg_returns",0),getattr(self,"ext_clear_returns",0),getattr(self,"clear_stores",0))
 def entry(self,*args):
  super().entry(*args);n=self.n
  assert self.ext_ready and self.inner_ready and not self.inner_held and self.ext_dep==0
  assert self.rd(self.inner_obj,8)==n.base+0x1330a68 and self.rd(self.cached,8)==0
  assert self.rd(self.inline+44,4)==self.rd(n.base+0x17a1180,4)==0
  assert bytes(self.u.mem_read(self.clear_at,self.clear_bytes))==bytes([self.poison])*self.clear_bytes
 def ext_dependency(self,name,ret,args,ready,held):
  n=self.n;k=self.ext_dep
  assert self.ext_ready and self.inner_ready and ready and self.held and held==self.inner_held
  names=("cache_diag","inner_diag","inner_enter","init_diag");assert 0<=k<4 and name==names[k]
  targets=(0x5b8130,0x1df68,0x1df78,0x5b81d0);assert ret==n.base+targets[k]
  expected=([4,65535,n.base+0x13dacd8,n.base+0x13dae80,469,self.resource],[5,65535,n.base+0x1352650,n.base+0x1352590,41,self.inner_resource],[self.inner_resource],[4,65535,n.base+0x13dad10,n.base+0x13dae80,478,self.inner_resource])
  assert args==expected[k] and self.inner_held==(k==3)
  if k in (1,2):assert self.ext_frame is not None and self.ext_frame["kind"]=="callback"
  assert self.rd(self.inner_obj,8)==n.base+0x1330a68 and self.rd(n.base+0x1330a70,8)==n.base+0x1df30
  assert self.rd(n.base+0xf7e7b8,8)==n.base+0x1a8c0
 def patch_stack(self,a,data):
  if self.clearing and self.clear_at<=a and a+len(data)<=self.clear_at+self.clear_bytes:
   assert data==bytes(len(data)) and self.inner_held and self.held
   assert 0xf5e600<=self.u.reg_read(UC_ARM64_REG_PC)-self.n.base<=0xf5e7ab
   self.clear_stores+=1;key=next(k for k in self.before if k[0]<=a and a+len(data)<=k[1]+1)
   if key not in self.models:self.models[key]=bytearray(self.before[key])
   self.models[key][a-key[0]:a-key[0]+len(data)]=bytes(len(data));return
  super().patch_stack(a,data)
 def code(self,u,pc,z,_):
  n=self.n;r=pc-n.base
  if not self.ext and r!=0x5b8104:return super().code(u,pc,z,_)
  if r==0x5b8104:
   assert self.next_dep==9 and self.frame_returns==11 and not self.frames and not self.callback
   self.published();self.ext=True
  assert not self.pending
  if self.ext_cfg and pc==self.ext_cfg["ret"]:
   assert all(u.reg_read(k)==v for k,v in self.ext_cfg["saved"].items());self.ext_cfg=None;self.ext_cfg_returns+=1
  if self.ext_frame and pc==self.ext_frame["ret"]:
   f=self.ext_frame;assert all(u.reg_read(k)==v for k,v in f["saved"].items())
   if f["kind"]=="callback":self.ext_callbacks+=1
   else:
    assert u.reg_read(UC_ARM64_REG_X0)==self.clear_at and bytes(u.mem_read(self.clear_at,self.clear_bytes))==bytes(self.clear_bytes)
    self.ext_clear_returns+=1;self.clearing=False
   self.ext_frame=None
  if r==0x5b8268:
   assert self.ext_dep==4 and self.ext_callbacks==self.ext_cfg_returns==self.ext_clear_returns==1 and not self.ext_frame and not self.ext_cfg
   assert self.inner_held and self.held and not self.crt_held and not self.srw_held
   self.stopped=True;u.emu_stop();return
  if r==0x1aca8 or pc==self.apis["EnterCriticalSection"]:
   name=("cache_diag","inner_diag","inner_enter","init_diag")[self.ext_dep]
   args=[u.reg_read(globals()["UC_ARM64_REG_X"+str(k)]) for k in range(6)] if r==0x1aca8 else [u.reg_read(UC_ARM64_REG_X0)]
   ret=u.reg_read(UC_ARM64_REG_LR);owned=(name,ret,args,self.ext_ready,self.inner_held);self.ext_dependency(*owned)
   bad=[(name,ret+4,args,self.ext_ready,self.inner_held),(name,ret,args+[0],self.ext_ready,self.inner_held),(name,ret,args,False,self.inner_held),(name,ret,args,self.ext_ready,not self.inner_held)]
   for k in range(len(args)):
    altered=args.copy();altered[k]+=1;bad.append((name,ret,altered,self.ext_ready,self.inner_held))
   self.reject(self.ext_dependency,bad)
   for flag in ("inner_ready",):
    old=getattr(self,flag);setattr(self,flag,False)
    try:self.reject(self.ext_dependency,[owned])
    finally:setattr(self,flag,old)
   if name=="inner_enter":self.inner_held=True
   self.ext_dep+=1;u.reg_write(UC_ARM64_REG_X0,self.api_clobber if name=="inner_enter" else self.diag_clobber);u.reg_write(UC_ARM64_REG_PC,ret);return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4),("unqualified original code reached",hex(r))
  if r==0x1a8c0:
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+0x5b8160 and u.reg_read(UC_ARM64_REG_X15)==n.base+0x1df30 and not self.ext_cfg
   self.ext_cfg={"ret":n.base+0x5b8160,"saved":{k:u.reg_read(k) for k in DR.ALLREG if k not in (UC_ARM64_REG_PC,UC_ARM64_REG_LR)}}
  if r==0x1df30:
   assert u.reg_read(UC_ARM64_REG_X0)==self.inner_obj and u.reg_read(UC_ARM64_REG_LR)==n.base+0x5b8164 and self.ext_frame is None and not self.inner_held
   self.ext_frame={"kind":"callback","ret":n.base+0x5b8164,"saved":{k:u.reg_read(k) for k in NONVOL}}
  if r==0xf5e600:
   assert self.ext_frame is None and self.inner_held and self.ext_dep==4
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+0x5b8250 and [u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2)]==[self.clear_at,0,self.clear_bytes]
   self.clearing=True;self.ext_frame={"kind":"clear","ret":n.base+0x5b8250,"saved":{k:u.reg_read(k) for k in NONVOL}}
  self.trace.append(r);self.ext_visits.append(r);assert len(self.trace)<20000;i=INS[r]
  if i.mnemonic.startswith(("str","stp","stnp","st1","stur")):
   memory=next(o for o in i.operands if o.type==capstone.arm64.ARM64_OP_MEM);assert not memory.mem.index
   at=DR.reg(u,C.reg_name(memory.mem.base))+memory.mem.disp
   ops=list(i.operands[:next(k for k,o in enumerate(i.operands) if o.type==capstone.arm64.ARM64_OP_MEM)]) if i.mnemonic=="st1" else i.operands[:2] if i.mnemonic in ("stp","stnp") else i.operands[:1]
   for k,o in enumerate(ops):
    name=C.reg_name(o.reg)
    if i.mnemonic=="st1":assert name.startswith("v") and o.vas in (capstone.arm64.ARM64_VAS_16B,capstone.arm64.ARM64_VAS_8B);name="q"+name[1:]
    size=16 if name.startswith("q") else 8 if name.startswith(("x","d")) or name in ("fp","lr") else 4
    if i.mnemonic=="st1":size=16 if o.vas==capstone.arm64.ARM64_VAS_16B else 8
    at_k=at+k*size;value=DR.reg(u,name)&((1<<(size*8))-1);data=value.to_bytes(size,"little")
    for off in range(0,size,8):
     chunk=data[off:off+8];self.patch_stack(at_k+off,chunk);self.pending[at_k+off,len(chunk)]=int.from_bytes(chunk,"little")
 def read(self,u,access,at,size,value,_):
  if (at,size)==(self.n.base+0xf5e64c,1):
   assert self.clearing and self.inner_held;self.literal_reads+=1;return
  if (at,size) in ((self.cached,8),(self.inner_obj,8),(self.inline+44,4),(self.n.base+0x17a1180,4)):return
  super().read(u,access,at,size,value,_)
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
  checks+=[(n.base+0x1607b04,self.global_epoch+1,4)]+[(self.exit_table+offset,self.encode(0)^1,8) for offset in (0,8,16)]
  for flag in ("exit_ready","exit_alloc_ready","crt_ready","cv_ready"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.entry,[args])
   finally:setattr(self,flag,old)

  for at,v,size in checks:
   old=bytes(u.mem_read(at,size));self.wr(at,v,size)
   try:self.reject(self.entry,[args])
   finally:u.mem_write(at,old)
  extra=[(self.cached,1,8),(self.inner_obj,n.base+0x1330a70,8),(self.inline+44,1,4),(n.base+0x17a1180,1,4),(self.clear_at,self.poison^1,1)]
  for at,value,width in extra:
   old=bytes(u.mem_read(at,width));self.wr(at,value,width)
   try:self.reject(self.entry,[args])
   finally:u.mem_write(at,old)
  for flag in ("ext_ready","inner_ready"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.entry,[args])
   finally:setattr(self,flag,old)
  self.before=self.snapshot();self.expected_stack=bytearray(u.mem_read(n.stack,65536))
  saved={k:u.reg_read(k) for k in NONVOL}
  hooks=[u.hook_add(UC_HOOK_CODE,self.code),u.hook_add(UC_HOOK_MEM_WRITE,self.write),u.hook_add(UC_HOOK_MEM_READ,self.read)]
  try:u.emu_start(n.base+0x5de700,n.end,count=20000)
  finally:
   for h in hooks:u.hook_del(h)
  assert not self.pending and self.callback is None
  assert self.dep_names==self.expected_deps
  assert self.callbacks==1 and self.guard_returns==1
  assert self.cfg_visits==self.callbacks
  assert self.stopped and u.reg_read(UC_ARM64_REG_PC)==n.base+0x5b8268 and self.held and not self.srw_held
  assert self.guard_callback is None and self.constructor is None and self.constructor_returns==1 and self.field_order==list(self.fields) and self.field_stores==130 and self.frame_returns==11 and not self.frames
  self.published()
  self.constructed()
  after=self.snapshot();assert after.keys()==self.before.keys()
  for k,v in self.before.items():
   assert after[k]==(bytes(self.expected_stack) if k[0]==n.stack else bytes(self.models[k]) if k in self.models else v),"whole mapped memory mismatch"

  row={"stack_bias":self.bias,"loader_index":self.index,"thread_epoch":self.epoch,"initial_bound_sentinel":self.sentinel,"diagnostic_X0":self.diag_clobber,"OS_void_X0":self.api_clobber,
   "allocation_poison":self.poison,"constructor_returns_ABI_exact":self.constructor_returns,"owned_allocation_calls":self.alloc_count,"owned_allocation_bytes":152,"allocation_redzones_and_relations_exact":True,
   "original_instruction_visits":len(self.trace),"constructor_instruction_visits":sum(0x2ee1a0<=r<=0x2ee2a3 for r in self.trace),"registration_wrapper_instruction_visits":sum(0xca34a0<=r<=0xca34c3 for r in self.trace),"first_helper_instruction_visits":sum(0x5b80a8<=r<=0x5b90af for r in self.trace),
   "guard_instruction_visits":sum(0xce7ad8<=r<=0xce7b93 for r in self.trace),"frame_helper_instruction_visits":sum(r<0x1300 for r in self.trace),
   "callback_returns_ABI_exact":self.callbacks,"guard_returns_ABI_exact":self.guard_returns,"owned_OS_API_calls":8,"owned_diagnostic_calls":1,
   "stack_store_chunks":self.stores-self.field_stores-self.clear_stores,"nonstack_field_store_chunks":self.field_stores,"invalid_owned_dependency_requests_rejected":self.negatives,
   "whole_mapped_memory_and_permissions_exact":True,"immutable_source_and_unmodified_loader_regions":True,"thread_epoch_update_exact":True,"registry_logical_lock_held":self.held,"SRW_logical_lock_held":self.srw_held,
   "initial_global_epoch":self.global_epoch,"published_epoch":self.published_epoch,"original_registration_publication_returns_ABI_exact":self.frame_returns,
   "original_CRT_registration_instruction_visits":sum(r>=0xca0000 and not(0xce7a48<=r<=0xce7b93) for r in self.trace),
   "publication_instruction_visits":sum(0xce7a48<=r<=0xce7ad3 for r in self.trace),"owned_exit_reallocation_calls":int(self.exit_allocated),"owned_exit_reallocation_bytes":256,
   "exit_table_used_pointer_entries":1,"exit_table_capacity_pointer_entries":32,"owned_wake_calls":self.wakes,"CRT_logical_lock_held":self.crt_held,
   "stop_before_RVA":"0x5b8268","next_factory_pointer_RVA":"0x1731880","parent_returned":False,"first_helper_returned":False}
  assert self.rd(self.cached,8)==self.inline and self.rd(self.inline+40,8)==32769
  assert self.rd(self.inline+48,8)==0 and bytes(u.mem_read(self.clear_at,self.clear_bytes))==bytes(self.clear_bytes)
  assert bytes(u.mem_read(self.inline+20,4))==bytes([self.poison])*4
  row.update({"added_source_instruction_visits":len(self.ext_visits),"added_clear_instruction_visits":sum(0xf5e600<=r<=0xf5e7ab for r in self.ext_visits),"added_nested_callback_returns_ABI_exact":self.ext_callbacks,"added_CFG_returns_exact":self.ext_cfg_returns,"added_clear_returns_ABI_exact":self.ext_clear_returns,"owned_extra_OS_calls":1,"owned_extra_diagnostic_calls":3,"large_clear_store_chunks":self.clear_stores,"nested_registry_logical_lock_held":self.inner_held,"cache_pointer_is_actual_inline_object":True,"large_clear_exact":True,"large_clear_padding_redzones_and_constructed_container_exact":True,"next_factory_caller_return_RVA":"0x5b826c","actual_pre_factory_call_X0_RVA":hex(u.reg_read(UC_ARM64_REG_X0)-n.base),"clear_literal_data_reads":self.literal_reads,"inherited_E011DR_source_visits":len(self.trace)-len(self.ext_visits)})
  row["original_CRT_registration_instruction_visits"]=sum(r>=0xca0000 and not(0xce7a48<=r<=0xce7b93) for r in self.trace[:len(self.trace)-len(self.ext_visits)])
  return row

def main():
 rows=[]
 for bias,index,epoch,bound,diag,api,poison,global_epoch in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a),(0x80000040,41)):
  rows.append(Case(bias,index,epoch,bound,diag,api,poison,global_epoch).run())
  if len(rows)%64==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 report={"experiment":"E011DS","status":"PASS_BOUNDED_ORIGINAL_CACHED_OBJECT_NESTED_LOCK_AND_BUFFER_CLEAR","scenarios":len(rows),"image_sha256":M.DLL_SHA,"source_pins":PINS,"clear_literal_data_authority":LITERAL_AUTHORITY,"details":rows,"next_experiment":"E011DT","stop_before_RVA":"0x5b8268","next_factory_RVA":"0x5bde08","actual_factory_caller_return_RVA":"0x5b826c","cached_pointer_RVA":"0x1731880","source_inline_object_RVA":"0x17a4230","nested_lock_object_RVA":"0x1623598","nested_lock_resource_RVA":"0x16235a0","original_buffer_clear_RVA":"0xf5e600","original_buffer_clear_return_RVA":"0x5b8250","clear_destination_RVA":"0x17a4268","clear_bytes":11808,"source_memory_and_permissions_exact":True,"cache_or_nested_lock_or_clear_result_fixture_used":False,"ready_OS_and_loader_and_CRT_resources_are_owned_models":True,"cold_zero_control_cells_and_disabled_trace_are_owned_models":True,"buffer_poison_and_padding_are_robustness_fixtures":True,"full_inline_object_initialization_qualified":False,"factory_callee_executed_in_this_parent":False,"first_helper_complete_return_qualified":False,"full_metadata_descriptor_registry_publication_qualified":False,"selected_runtime_profile_qualified":False,"populated_RS_lifetime_qualified":False,"deterministic_bootstrap_closed":False,"independent_enabled_output_retirement_proven":False,"native_rear_runtime_allowed":False,"native_OS_CRT_allocator_construction_or_failure_paths_qualified":False,"new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,"production_code_changed":False,"private_raw_material_exported":False}
 totals_fields=("original_instruction_visits","added_source_instruction_visits","added_clear_instruction_visits","added_nested_callback_returns_ABI_exact","added_CFG_returns_exact","added_clear_returns_ABI_exact","owned_extra_OS_calls","owned_extra_diagnostic_calls","original_registration_publication_returns_ABI_exact","stack_store_chunks","nonstack_field_store_chunks","large_clear_store_chunks","invalid_owned_dependency_requests_rejected")
 report["totals"]={k:sum(r[k] for r in rows) for k in totals_fields};(OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"status":report["status"],"scenarios":len(rows),"totals":report["totals"]}),flush=True)
if __name__=="__main__":main()
