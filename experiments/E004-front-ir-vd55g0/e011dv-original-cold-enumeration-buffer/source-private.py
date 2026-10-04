#!/usr/bin/env python3
"""Original cold enumeration buffer allocation, zeroing and publication in the retained parent."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011du-original-existing-table-registration-publication/source-private.py"
assert hashlib.sha256(P.read_bytes()).hexdigest()=="ad69ec51632ffaa0bc46521ac818bec180863250aa132067147b82cf28957ab6"
s=importlib.util.spec_from_file_location("dv_actual_du_parent",P);DU=importlib.util.module_from_spec(s);s.loader.exec_module(DU)
DT=DU.DT;DS=DU.DS;DR=DU.DR;PE=DU.PE;M=DU.M;C=DU.C;INS=DU.INS;PINS=DU.PINS;NONVOL=DU.NONVOL
OUT=Path(__file__).resolve().parent
SEC=next(x for x in PE.sections if x.VirtualAddress<=0x1731598<x.VirtualAddress+x.Misc_VirtualSize)
ZERO_AUTHORITY={"RVA":"0x1731598","bytes":4,"section_virtual_start_RVA":hex(SEC.VirtualAddress),"section_virtual_bytes":SEC.Misc_VirtualSize,
 "section_raw_bytes":SEC.SizeOfRawData,"section_flags":hex(SEC.Characteristics),"outside_file_backed_span":True,"virtual_loader_zero_fill_model":True}
assert ZERO_AUTHORITY=={"RVA":"0x1731598","bytes":4,"section_virtual_start_RVA":"0x1607000","section_virtual_bytes":5429539,"section_raw_bytes":635904,
 "section_flags":"0xc0000040","outside_file_backed_span":True,"virtual_loader_zero_fill_model":True}
assert 0x1731598>=SEC.VirtualAddress+SEC.SizeOfRawData and 0x1731598+4<=SEC.VirtualAddress+SEC.Misc_VirtualSize
assert PE.get_data(0x1731598,4)==b"" and PE.get_data(0x169fdf0,8)==bytes(8) and PE.get_data(0x169fde8,4)==bytes(4)
class Case(DU.Case):
 def __init__(self,*args):
  super().__init__(*args);n=self.n
  self.dv_ready=True;self.dv_alloc_ready=True;self.dv_lease=None;self.dv_frames=[];self.dv_frame_returns=0
  self.dv_buffer=n.heap+0x10000+self.bias;self.dv_bytes=18832;self.dv_scalar=n.base+0x1731598
  self.dv_pointer=n.base+0x169fdf0;self.dv_refcount=n.base+0x169fde8
  assert self.rd(self.dv_scalar,4)==self.rd(self.dv_pointer,8)==self.rd(self.dv_refcount,4)==0
  self.u.mem_write(self.dv_buffer-32,bytes([self.poison])*(self.dv_bytes+64))
  self.dv_trace=[];self.dv_scalar_reads=0;self.dv_literal_reads=[];self.dv_clear_visits=0;self.dv_clear_chunks=0;self.dv_stopped=False;self.dv_order=[]
  self.dv_fields={(0x5f8e58,self.dv_pointer,8):self.dv_buffer,(0x5f8e5c,self.dv_refcount,4):1}
 def logical(self):
  return super().logical()+(getattr(self,"dv_ready",False),getattr(self,"dv_alloc_ready",False),getattr(self,"dv_lease",None),
   len(getattr(self,"dv_frames",[])),getattr(self,"dv_frame_returns",0),getattr(self,"dv_clear_chunks",0),tuple(getattr(self,"dv_order",[])))
 def dv_layout(self):
  n=self.n;u=self.u;self.du_layout(2,0x80000042)
  assert self.dv_ready and self.dv_alloc_ready and not self.crt_held and not self.srw_held and self.held and self.inner_held
  assert self.rd(self.dv_scalar,4)==0 and self.rd(self.teb+8,8)==n.stack+65536 and self.rd(self.teb+16,8)==n.stack
  assert all(self.dv_buffer+self.dv_bytes<=a or a+width<=self.dv_buffer for a,width in self.leases+[(self.exit_storage,256)]+self.dt_leases)
 def dv_entry(self,site,sp,ready):
  n=self.n;u=self.u;self.dv_layout()
  assert ready and site==0x5f8e24 and u.reg_read(UC_ARM64_REG_PC)==n.base+site and sp==u.reg_read(UC_ARM64_REG_SP) and sp%16==0
  assert self.du_stopped and self.du_wakes==1 and self.du_frame_returns==8 and not self.du_frames and self.dv_lease is None and not self.dv_frames
  assert self.rd(self.dv_pointer,8)==self.rd(self.dv_refcount,4)==0 and not self.dv_order
  assert bytes(u.mem_read(self.dv_buffer,self.dv_bytes))==bytes([self.poison])*self.dv_bytes
 def dv_allocator(self,site,ret,args,pointer,ready):
  n=self.n;u=self.u;self.dv_layout()
  assert ready and site==0xcae740 and ret==n.base+0x5f8e38 and args==[self.dv_bytes] and pointer==self.dv_buffer and pointer%16==0
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+site and self.dv_lease is None and not self.dv_frames and not self.dv_order and self.dv_scalar_reads==1
  assert self.rd(self.dv_pointer,8)==self.rd(self.dv_refcount,4)==0 and bytes(u.mem_read(pointer,self.dv_bytes))==bytes([self.poison])*self.dv_bytes
 def dv_clear(self,site,ret,args,ready):
  n=self.n;u=self.u;self.dv_layout()
  assert ready and site==0xf5e600 and u.reg_read(UC_ARM64_REG_PC)==n.base+site and ret==n.base+0x5f8e54 and args==[self.dv_buffer,0,self.dv_bytes]
  assert self.dv_lease==(self.dv_buffer,self.dv_bytes) and not self.dv_frames and not self.dv_order and self.dv_clear_chunks==0
  assert self.rd(self.dv_pointer,8)==self.rd(self.dv_refcount,4)==0 and bytes(u.mem_read(self.dv_buffer,self.dv_bytes))==bytes([self.poison])*self.dv_bytes
 def dv_patch(self,at,data):
  n=self.n;u=self.u;site=u.reg_read(UC_ARM64_REG_PC)-n.base
  if n.stack<=at and at+len(data)<=n.stack+65536:self.patch_stack(at,data);return
  if self.dv_buffer<=at and at+len(data)<=self.dv_buffer+self.dv_bytes:
   assert 0xf5e600<=site<=0xf5e7ab and data==bytes(len(data)) and self.dv_lease==(self.dv_buffer,self.dv_bytes)
   assert self.dv_frames and self.dv_frames[-1]["entry"]==0xf5e600 and self.dv_frame_returns==0 and not self.dv_order
   self.dv_clear_chunks+=1
  else:
   key=(site,at,len(data));assert self.dv_fields.get(key)==int.from_bytes(data,"little") and key==list(self.dv_fields)[len(self.dv_order)]
   assert self.dv_frame_returns==1 and not self.dv_frames and self.dv_lease==(self.dv_buffer,self.dv_bytes)
   assert bytes(u.mem_read(self.dv_buffer,self.dv_bytes))==bytes(self.dv_bytes);self.dv_order.append(key)
  region=next(k for k in self.before if k[0]<=at and at+len(data)<=k[1]+1)
  if region not in self.models:self.models[region]=bytearray(self.before[region])
  self.models[region][at-region[0]:at-region[0]+len(data)]=data
 def dv_read(self,u,access,at,size,value,_):
  n=self.n
  if (at,size)==(self.dv_scalar,4):
   assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x5f8e24 and self.rd(at,size)==0 and self.dv_ready
   self.dv_scalar_reads+=1;return
  if (at,size)==(n.base+0xf5e644,1):
   assert self.dv_frames and bytes(u.mem_read(at,size))==PE.get_data(at-n.base,size);self.dv_literal_reads.append(["0xf5e644",1]);return
  self.du_read(u,access,at,size,value,_)
 def dv_code(self,u,pc,z,_):
  n=self.n;r=pc-n.base;assert not self.pending
  if self.dv_frames and pc==self.dv_frames[-1]["ret"]:
   f=self.dv_frames.pop();assert all(u.reg_read(k)==v for k,v in f["saved"].items()),"DV clear callee ABI not restored"
   assert u.reg_read(UC_ARM64_REG_X0)==self.dv_buffer and bytes(u.mem_read(self.dv_buffer,self.dv_bytes))==bytes(self.dv_bytes)
   self.dv_frame_returns+=1
  if r==0x5f8ea4:
   assert self.dv_frame_returns==1 and not self.dv_frames and self.dv_order==list(self.dv_fields) and self.dv_scalar_reads==1
   self.dv_layout();self.dv_stopped=True;u.emu_stop();return
  if r==0xcae740:
   ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_X0)];owned=(r,ret,args,self.dv_buffer,self.dv_alloc_ready);self.dv_allocator(*owned)
   self.reject(self.dv_allocator,[(r+4,ret,args,self.dv_buffer,True),(r,ret+4,args,self.dv_buffer,True),(r,ret,[self.dv_bytes-1],self.dv_buffer,True),
    (r,ret,args+[0],self.dv_buffer,True),(r,ret,args,self.dv_buffer+16,True),(r,ret,args,self.dv_buffer,False),(r,ret,args,self.exit_storage,True)])
   for flag in ("dv_alloc_ready","dv_ready","held","inner_held","exit_allocated"):
    old=getattr(self,flag);setattr(self,flag,False)
    try:self.reject(self.dv_allocator,[owned])
    finally:setattr(self,flag,old)
   old=self.dv_lease;self.dv_lease=(self.dv_buffer,self.dv_bytes)
   try:self.reject(self.dv_allocator,[owned])
   finally:self.dv_lease=old
   old=bytes(u.mem_read(self.dv_buffer,1));self.wr(self.dv_buffer,self.poison^1,1)
   try:self.reject(self.dv_allocator,[owned])
   finally:u.mem_write(self.dv_buffer,old)
   self.dv_lease=(self.dv_buffer,self.dv_bytes);u.reg_write(UC_ARM64_REG_X0,self.dv_buffer);u.reg_write(UC_ARM64_REG_PC,ret);return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4),("unqualified DV source",hex(r))
  if r==0xf5e600:
   ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2)];owned=(r,ret,args,self.dv_ready);self.dv_clear(*owned)
   self.reject(self.dv_clear,[(r+4,ret,args,True),(r,ret+4,args,True),(r,ret,[args[0]+8,0,args[2]],True),(r,ret,[args[0],1,args[2]],True),
    (r,ret,[args[0],0,args[2]-8],True),(r,ret,args+[0],True),(r,ret,args,False)])
   old=self.dv_lease;self.dv_lease=None
   try:self.reject(self.dv_clear,[owned])
   finally:self.dv_lease=old
   for flag in ("dv_ready","dv_alloc_ready","held","inner_held"):
    old=getattr(self,flag);setattr(self,flag,False)
    try:self.reject(self.dv_clear,[owned])
    finally:setattr(self,flag,old)
   self.dv_frames.append({"entry":r,"ret":ret,"saved":{k:u.reg_read(k) for k in NONVOL}})
  self.dv_trace.append(r);i=INS[r]
  if 0xf5e600<=r<=0xf5e7ab:self.dv_clear_visits+=1
  if i.mnemonic.startswith(("str","stp","stnp","st1","stur")):
   mi=next(k for k,o in enumerate(i.operands) if o.type==capstone.arm64.ARM64_OP_MEM);mem=i.operands[mi];assert not mem.mem.index
   at=DR.reg(u,C.reg_name(mem.mem.base))+mem.mem.disp
   ops=list(i.operands[:mi]) if i.mnemonic=="st1" else i.operands[:2] if i.mnemonic in ("stp","stnp") else i.operands[:1]
   for k,o in enumerate(ops):
    name=C.reg_name(o.reg)
    if i.mnemonic=="st1":assert name.startswith("v") and o.vas in (capstone.arm64.ARM64_VAS_16B,capstone.arm64.ARM64_VAS_8B);name="q"+name[1:]
    width=16 if name.startswith("q") else 8 if name.startswith(("x","d")) or name in ("fp","lr") else 2 if name.startswith("h") else 1 if name.startswith("b") else 4
    if i.mnemonic=="st1":width=16 if o.vas==capstone.arm64.ARM64_VAS_16B else 8
    elif i.mnemonic.endswith("h"):width=2
    elif i.mnemonic.endswith("b"):width=1
    data=(DR.reg(u,name)&((1<<(width*8))-1)).to_bytes(width,"little")
    for off in range(0,width,8):
     addr=at+k*width+off;chunk=data[off:off+8];self.dv_patch(addr,chunk);self.pending[addr,len(chunk)]=int.from_bytes(chunk,"little")
 def run(self):
  prior=super().run();n=self.n;u=self.u;start_stores=self.stores;start_negatives=self.negatives
  args=(0x5f8e24,u.reg_read(UC_ARM64_REG_SP),True);self.dv_entry(*args)
  self.reject(self.dv_entry,[(args[0]+4,args[1],True),(args[0],args[1]+16,True),(args[0],args[1],False)])
  for flag in ("dv_ready","dv_alloc_ready","held","inner_held","exit_allocated","dt_alloc_ready"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.dv_entry,[args])
   finally:setattr(self,flag,old)
  for at,value,width in ((self.dv_scalar,1,4),(self.dv_pointer,1,8),(self.dv_refcount,1,4),(self.dv_buffer,self.poison^1,1),
   (self.block+16,0x80000041,4),(self.dt_enum_guard,0xffffffff,4),(self.exit_table+8,self.encode(self.exit_storage+8),8),(self.teb+16,0,8)):
   old=bytes(u.mem_read(at,width));self.wr(at,value,width)
   try:self.reject(self.dv_entry,[args])
   finally:u.mem_write(at,old)
  hooks=[u.hook_add(UC_HOOK_CODE,self.dv_code),u.hook_add(UC_HOOK_MEM_WRITE,self.write),u.hook_add(UC_HOOK_MEM_READ,self.dv_read)]
  try:u.emu_start(n.base+0x5f8e24,n.end,count=10000)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.dv_stopped and not self.pending and u.reg_read(UC_ARM64_REG_PC)==n.base+0x5f8ea4
  self.dv_layout();assert self.dv_lease==(self.dv_buffer,self.dv_bytes) and self.rd(self.dv_pointer,8)==self.dv_buffer and self.rd(self.dv_refcount,4)==1
  assert self.dv_frame_returns==1 and self.dv_order==list(self.dv_fields) and self.dv_scalar_reads==1 and bytes(u.mem_read(self.dv_buffer,self.dv_bytes))==bytes(self.dv_bytes)
  after=self.snapshot();assert after.keys()==self.before.keys()
  for key,before in self.before.items():assert after[key]==(bytes(self.expected_stack) if key[0]==n.stack else bytes(self.models[key]) if key in self.models else before),"combined retained parent DV memory mismatch"
  added={"original_instruction_visits":len(self.dv_trace),"clear_instruction_visits":self.dv_clear_visits,"clear_store_chunks":self.dv_clear_chunks,
   "exact_source_store_chunks":self.stores-start_stores,"nonstack_field_store_chunks":len(self.dv_order),"rejected_owned_requests":self.negatives-start_negatives,
   "original_clear_returns_ABI_exact":self.dv_frame_returns,"owned_allocation_calls":1,"owned_allocation_bytes":self.dv_bytes,"owned_OS_API_calls":0,
   "loader_zero_scalar_reads":self.dv_scalar_reads,"clear_literal_data_reads":self.dv_literal_reads,"original_clear_return_RVA":"0x5f8e54",
   "published_pointer_RVA":"0x169fdf0","published_reference_count_RVA":"0x169fde8","published_reference_count":1,"published_buffer_bytes_zero":self.dv_bytes,
   "six_distinct_live_allocations_retained":True,"whole_entry_to_frontier_memory_and_permissions_exact":True,
   "ancestor_callbacks_epochs_nodes_redzones_and_container_retained":True,"factory_guard_in_progress":True,"outer_and_nested_registry_locks_held":True,"CRT_and_SRW_released":True,
   "stop_before_RVA":"0x5f8ea4","next_target_RVA":"0x600368","next_actual_return_RVA":"0x5f8ea8"}
  return {"DU":prior,"added":added}
def main():
 rows=[]
 for args in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)):
  rows.append(Case(*args).run())
  if len(rows)%32==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 ancestor=json.loads((P.parent/"SOURCE-SAFE.json").read_text())
 report={"experiment":"E011DV","status":"PASS_BOUNDED_ACTUAL_COLD_ENUMERATION_BUFFER_PUBLICATION","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,
  "scalar_zero_fill_authority":ZERO_AUTHORITY,"source_result_fixture_used":False,"native_rear_runtime_allowed":False,"full_factory_or_first_helper_return_qualified":False,
  "full_descriptor_registry_publication_qualified":False,"native_OS_CRT_allocator_construction_and_failure_paths_qualified":False,
  "native_runtime_scalar_selection_qualified":False,"alternate_nonzero_scalar_branch_qualified":False,"next_callee_execution_qualified":False,"stack_growth_guard_page_OS_qualified":False,
  "actual_cold_scalar_branch_qualified_under_loader_zero_model":True,"original_allocation_clear_and_buffer_publication_qualified":True,
  "prior_callback_table_epochs_and_five_allocations_retained":True,"next_experiment":"E011DW","details":rows,"new_camera_starts":0,"new_reboots":0,
  "new_kernel_build":False,"production_code_changed":False,"private_raw_material_exported":False}
 keys=("original_instruction_visits","clear_instruction_visits","clear_store_chunks","exact_source_store_chunks","nonstack_field_store_chunks","rejected_owned_requests",
  "original_clear_returns_ABI_exact","owned_allocation_calls","owned_allocation_bytes","owned_OS_API_calls","loader_zero_scalar_reads")
 report["added_totals"]={k:sum(r["added"][k] for r in rows) for k in keys}
 report["inherited_DU_totals"]=ancestor["added_totals"];report["inherited_DT_totals"]=ancestor["inherited_DT_totals"];report["inherited_DS_totals"]=ancestor["inherited_DS_totals"]
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"status":report["status"],"scenarios":len(rows),"added_totals":report["added_totals"]}),flush=True)
if __name__=="__main__":main()
