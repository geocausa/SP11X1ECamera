#!/usr/bin/env python3
"""Original nested enumeration-container construction and stack clear in the retained parent."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011dv-original-cold-enumeration-buffer/source-private.py"
assert hashlib.sha256(P.read_bytes()).hexdigest()=="04c760aad6de641deb2e1bb6580e82384f96006078aa1cdc80f91ee1e28db1ed"
s=importlib.util.spec_from_file_location("dw_actual_dv_parent",P);DV=importlib.util.module_from_spec(s);s.loader.exec_module(DV)
DT=DV.DT;DS=DV.DS;DR=DV.DR;PE=DV.PE;M=DV.M;C=DV.C;INS=dict(DV.INS);PINS=dict(DV.PINS);NONVOL=DV.NONVOL
EXTRA_PINS={"0x600368":{"body_bytes":1120,"ranges":[["0x600368","0x6007c7"]],"sha256":"18d45d94302157df5a5ce15d232191f9fca4a63bc1c910af535a9dc24b4b7e43"},
 "0x5e81b8":{"body_bytes":540,"ranges":[["0x5e81b8","0x5e83d3"]],"sha256":"ec5c36864ecc63597070f754e40553dfe358c067243ceb4b44b8390ca757dd16"}}
for entry,pin in EXTRA_PINS.items():
 body=b"".join(PE.get_data(int(lo,16),int(hi,16)-int(lo,16)+1) for lo,hi in pin["ranges"])
 assert len(body)==pin["body_bytes"] and hashlib.sha256(body).hexdigest()==pin["sha256"]
 for lo,hi in pin["ranges"]:
  for r in range(int(lo,16),int(hi,16)+1,4):
   i=list(C.disasm(PE.get_data(r,4),r));assert len(i)==1;INS[r]=i[0]
 PINS[entry]=pin
OUT=Path(__file__).resolve().parent
class Case(DV.Case):
 def __init__(self,*args):
  super().__init__(*args);n=self.n
  self.dw_ready=True;self.dw_alloc_ready=True;self.dw_allocations=[(n.heap+0x16000+self.bias,16),(n.heap+0x18000+self.bias,64),(n.heap+0x1a000+self.bias,8192)]
  self.dw_leases=[];self.dw_record_reads=[];self.dw_trace=[];self.dw_frames=[];self.dw_nested_returns=0;self.dw_heap_clear_returns=0;self.dw_stack_clear_returns=0
  self.dw_clear_visits=0;self.dw_heap_clear_chunks=0;self.dw_stack_clear_chunks=0;self.dw_order=[];self.dw_stopped=False;self.dw_entry_sp=None;self.dw_nested_call_X0=None;self.dw_stack_receiver=None
  for at,width in self.dw_allocations:self.u.mem_write(at-32,bytes([self.poison])*(width+64))
  node,header,array=[at for at,width in self.dw_allocations]
  plans=[(0x6003a4,node,8,n.base+0x133a100),(0x6003a4,node+8,8,0)]
  plans.extend((site,header+off,8,0) for site,offset in ((0x5e81e4,0),(0x5e81e8,32)) for off in range(offset,offset+32,8))
  plans.extend([(0x5e81f8,header,8,0),(0x5e81f8,header+8,8,4),(0x5e81fc,header+16,8,0),
   (0x5e820c,header,4,1024),(0x5e8220,header+4,4,0x3f800000),(0x5e8264,header+24,8,array),
   (0x5e8264,header+32,8,4),(0x5e8278,header+40,8,0),(0x5e8280,header+40,8,8),(0x5e828c,header+48,8,12),(0x6003d4,node+8,8,header)])
  self.dw_fields={(site,at,width):value for site,at,width,value in plans};assert len(self.dw_fields)==21
 def logical(self):
  return super().logical()+(getattr(self,"dw_ready",False),getattr(self,"dw_alloc_ready",False),tuple(getattr(self,"dw_leases",[])),
   len(getattr(self,"dw_frames",[])),getattr(self,"dw_nested_returns",0),getattr(self,"dw_heap_clear_returns",0),getattr(self,"dw_stack_clear_returns",0),tuple(getattr(self,"dw_order",[])))
 def dw_layout(self):
  n=self.n;u=self.u;self.dv_layout()
  assert self.dw_ready and self.dw_alloc_ready and not self.crt_held and not self.srw_held and self.held and self.inner_held
  assert self.dv_lease==(self.dv_buffer,self.dv_bytes) and self.rd(self.dv_pointer,8)==self.dv_buffer and self.rd(self.dv_refcount,4)==1
  assert bytes(u.mem_read(self.dv_buffer,self.dv_bytes))==bytes(self.dv_bytes)
  old=self.leases+[(self.exit_storage,256)]+self.dt_leases+[self.dv_lease]
  all_leases=old+self.dw_allocations
  assert all(a+width<=b or b+size<=a for k,(a,width) in enumerate(all_leases) for b,size in all_leases[k+1:])
  assert self.dw_leases==self.dw_allocations[:len(self.dw_leases)]
 def dw_entry(self,site,sp,arg,ready):
  n=self.n;u=self.u;self.dw_layout()
  assert ready and site==0x5f8ea4 and u.reg_read(UC_ARM64_REG_PC)==n.base+site and sp==u.reg_read(UC_ARM64_REG_SP) and sp%16==0
  assert arg==u.reg_read(UC_ARM64_REG_X0)==self.dv_buffer and self.dv_stopped and self.dv_frame_returns==1 and not self.dv_frames
  assert not self.dw_leases and not self.dw_frames and not self.dw_order
  assert all(bytes(u.mem_read(at,width))==bytes([self.poison])*width for at,width in self.dw_allocations)
 def dw_allocator(self,site,ret,args,pointer,ready):
  n=self.n;u=self.u;self.dw_layout();k=len(self.dw_leases)
  assert ready and k<3 and site==0xcae740 and u.reg_read(UC_ARM64_REG_PC)==n.base+site
  assert ret==n.base+(0x600398,0x5e81d8,0x5e8244)[k] and args==[self.dw_allocations[k][1]] and pointer==self.dw_allocations[k][0] and pointer%16==0
  assert bytes(u.mem_read(pointer,args[0]))==bytes([self.poison])*args[0]
  assert not self.dw_frames if k==0 else self.dw_frames[-1]["kind"]=="nested"
  assert len(self.dw_order)==(0,2,15)[k]
 def dw_constructed(self):
  n=self.n;u=self.u;node,header,array=[at for at,width in self.dw_allocations]
  assert self.dw_leases==self.dw_allocations and self.rd(header,4)==1024 and self.rd(header+4,4)==0x3f800000
  assert [self.rd(header+off,8) for off in (8,16,24,32,40,48,56)]==[4,0,array,4,8,12,0]
  assert bytes(u.mem_read(array,8192))==bytes(8192) and self.rd(node,8)==n.base+0x133a100
 def dw_clear(self,site,ret,args,ready):
  n=self.n;u=self.u;self.dw_layout();array=self.dw_allocations[2][0]
  assert ready and site==0xf5e600 and u.reg_read(UC_ARM64_REG_PC)==n.base+site
  if self.dw_nested_returns==0:
   assert ret==n.base+0x5e8258 and args==[array,0,8192] and self.dw_leases==self.dw_allocations and len(self.dw_order)==15
   assert self.dw_frames and self.dw_frames[-1]["kind"]=="nested" and self.dw_heap_clear_chunks==0
   assert bytes(u.mem_read(array,8192))==bytes([self.poison])*8192
  else:
   assert self.dw_nested_returns==1 and ret==n.base+0x6003f0 and args==[self.dw_entry_sp-1392,0,640]
   assert not self.dw_frames and len(self.dw_order)==21 and self.dw_stack_clear_chunks==0 and self.dw_heap_clear_returns==1
   self.dw_constructed();assert self.rd(self.dw_allocations[0][0]+8,8)==self.dw_allocations[1][0]
 def dw_patch(self,at,data):
  n=self.n;u=self.u;site=u.reg_read(UC_ARM64_REG_PC)-n.base
  if n.stack<=at and at+len(data)<=n.stack+65536:
   if self.dw_frames and self.dw_frames[-1]["kind"]=="clear_stack":
    assert self.dw_stack_receiver<=at and at+len(data)<=self.dw_stack_receiver+640 and data==bytes(len(data));self.dw_stack_clear_chunks+=1
   self.patch_stack(at,data);return
  if self.dw_allocations[2][0]<=at and at+len(data)<=self.dw_allocations[2][0]+8192:
   assert self.dw_leases==self.dw_allocations and self.dw_frames and self.dw_frames[-1]["kind"]=="clear_heap" and data==bytes(len(data))
   assert 0xf5e600<=site<=0xf5e7ab;self.dw_heap_clear_chunks+=1
  else:
   key=(site,at,len(data));assert self.dw_fields.get(key)==int.from_bytes(data,"little") and key==list(self.dw_fields)[len(self.dw_order)]
   assert any(start<=at and at+len(data)<=start+width for start,width in self.dw_leases)
   self.dw_order.append(key)
  region=next(k for k in self.before if k[0]<=at and at+len(data)<=k[1]+1)
  if region not in self.models:self.models[region]=bytearray(self.before[region])
  self.models[region][at-region[0]:at-region[0]+len(data)]=data
 def dw_record_read(self,site,at,width,value,ready):
  header=self.dw_allocations[1][0];k=len(self.dw_record_reads)
  expected=((0x5e8200,0,0),(0x5e8210,4,0),(0x5e8258,8,4),(0x5e8274,12,0),(0x5e8290,16,0))
  assert ready and self.dw_ready and self.held and self.inner_held and k<5 and len(self.dw_leases)>=2
  source,offset,want=expected[k];assert (site,at,width,value)==(source,header+offset,4,want) and self.rd(at,width)==want
 def dw_read(self,u,access,at,size,value,_):
  if any(start<=at and at+size<=start+width for start,width in self.dw_leases):
   site=u.reg_read(UC_ARM64_REG_PC)-self.n.base;data=self.rd(at,size);owned=(site,at,size,data,self.dw_ready);self.dw_record_read(*owned)
   self.reject(self.dw_record_read,[(site+4,at,size,data,True),(site,at+4,size,data,True),(site,at,size+4,data,True),(site,at,size,data+1,True),(site,at,size,data,False)])
   self.dw_record_reads.append((hex(site),at-self.dw_allocations[1][0],size));return
  self.dv_read(u,access,at,size,value,_)
 def dw_code(self,u,pc,z,_):
  n=self.n;r=pc-n.base;assert not self.pending and n.stack<=u.reg_read(UC_ARM64_REG_SP)<=n.stack+65536
  if self.dw_frames and pc==self.dw_frames[-1]["ret"]:
   f=self.dw_frames.pop();assert all(u.reg_read(k)==v for k,v in f["saved"].items()),"DW callee ABI not restored"
   if f["kind"]=="nested":
    self.dw_constructed();assert u.reg_read(UC_ARM64_REG_X0)==self.dw_allocations[1][0]
    self.dw_nested_returns+=1
   elif f["kind"]=="clear_heap":
    assert u.reg_read(UC_ARM64_REG_X0)==self.dw_allocations[2][0] and bytes(u.mem_read(self.dw_allocations[2][0],8192))==bytes(8192)
    self.dw_heap_clear_returns+=1
   else:
    assert u.reg_read(UC_ARM64_REG_X0)==self.dw_stack_receiver and bytes(u.mem_read(self.dw_stack_receiver,640))==bytes(640)
    self.dw_stack_clear_returns+=1
  if r==0x600420:
   assert self.dw_nested_returns==self.dw_heap_clear_returns==self.dw_stack_clear_returns==1 and not self.dw_frames and len(self.dw_order)==21
   self.dw_layout();self.dw_constructed();self.dw_stopped=True;u.emu_stop();return
  if r==0xcae740:
   k=len(self.dw_leases);ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_X0)];pointer,width=self.dw_allocations[k];owned=(r,ret,args,pointer,self.dw_alloc_ready);self.dw_allocator(*owned)
   self.reject(self.dw_allocator,[(r+4,ret,args,pointer,True),(r,ret+4,args,pointer,True),(r,ret,[width+1],pointer,True),(r,ret,args+[0],pointer,True),
    (r,ret,args,pointer+16,True),(r,ret,args,pointer,False),(r,ret,args,self.dv_buffer,True)])
   for flag in ("dw_ready","dw_alloc_ready","held","inner_held","exit_allocated"):
    old=getattr(self,flag);setattr(self,flag,False)
    try:self.reject(self.dw_allocator,[owned])
    finally:setattr(self,flag,old)
   old=bytes(u.mem_read(pointer,1));self.wr(pointer,self.poison^1,1)
   try:self.reject(self.dw_allocator,[owned])
   finally:u.mem_write(pointer,old)
   self.dw_leases.append((pointer,width));u.reg_write(UC_ARM64_REG_X0,pointer);u.reg_write(UC_ARM64_REG_PC,ret);return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4),("unqualified DW source",hex(r))
  if r==0x600368:
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+0x5f8ea8 and u.reg_read(UC_ARM64_REG_X0)==self.dv_buffer and u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp
   self.dw_nested_call_X0=self.dw_entry_sp-1416;self.dw_stack_receiver=self.dw_entry_sp-1392
   assert n.stack<=self.dw_nested_call_X0 and self.dw_stack_receiver+640<=n.stack+65536
  if r==0x5e81b8:
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+0x6003cc and u.reg_read(UC_ARM64_REG_X0)==self.dw_nested_call_X0 and len(self.dw_leases)==1 and len(self.dw_order)==2
   assert not self.dw_frames
   self.dw_frames.append({"kind":"nested","ret":n.base+0x6003cc,"saved":{k:u.reg_read(k) for k in NONVOL}})
  if r==0xf5e600:
   ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2)];owned=(r,ret,args,self.dw_ready);self.dw_clear(*owned)
   self.reject(self.dw_clear,[(r+4,ret,args,True),(r,ret+4,args,True),(r,ret,[args[0]+8,0,args[2]],True),(r,ret,[args[0],1,args[2]],True),
    (r,ret,[args[0],0,args[2]-8],True),(r,ret,args+[0],True),(r,ret,args,False)])
   for flag in ("dw_ready","dw_alloc_ready","held","inner_held"):
    old=getattr(self,flag);setattr(self,flag,False)
    try:self.reject(self.dw_clear,[owned])
    finally:setattr(self,flag,old)
   self.dw_frames.append({"kind":"clear_heap" if self.dw_nested_returns==0 else "clear_stack","ret":ret,"saved":{k:u.reg_read(k) for k in NONVOL}})
  self.dw_trace.append(r);i=INS[r]
  if 0xf5e600<=r<=0xf5e7ab:self.dw_clear_visits+=1
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
     addr=at+k*width+off;chunk=data[off:off+8];self.dw_patch(addr,chunk);self.pending[addr,len(chunk)]=int.from_bytes(chunk,"little")
 def run(self):
  prior=super().run();n=self.n;u=self.u;start_stores=self.stores;start_negatives=self.negatives;self.dw_entry_sp=u.reg_read(UC_ARM64_REG_SP)
  args=(0x5f8ea4,self.dw_entry_sp,self.dv_buffer,True);self.dw_entry(*args)
  self.reject(self.dw_entry,[(args[0]+4,args[1],args[2],True),(args[0],args[1]+16,args[2],True),(args[0],args[1],args[2]+8,True),(*args[:3],False)])
  for flag in ("dw_ready","dw_alloc_ready","held","inner_held","exit_allocated","dv_alloc_ready"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.dw_entry,[args])
   finally:setattr(self,flag,old)
  for at,value,width in ((self.dv_pointer,0,8),(self.dv_refcount,0,4),(self.dv_buffer,1,1),(self.dw_allocations[0][0],self.poison^1,1),
   (self.dw_allocations[1][0],self.poison^1,1),(self.dw_allocations[2][0],self.poison^1,1),(self.block+16,0x80000041,4),(self.exit_table+8,self.encode(self.exit_storage+8),8)):
   old=bytes(u.mem_read(at,width));self.wr(at,value,width)
   try:self.reject(self.dw_entry,[args])
   finally:u.mem_write(at,old)
  hooks=[u.hook_add(UC_HOOK_CODE,self.dw_code),u.hook_add(UC_HOOK_MEM_WRITE,self.write),u.hook_add(UC_HOOK_MEM_READ,self.dw_read)]
  try:u.emu_start(n.base+0x5f8ea4,n.end,count=10000)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.dw_stopped and not self.pending and u.reg_read(UC_ARM64_REG_PC)==n.base+0x600420 and not self.dw_frames
  self.dw_layout();self.dw_constructed()
  assert self.rd(self.dw_allocations[0][0]+8,8)==self.dw_allocations[1][0] and bytes(u.mem_read(self.dw_stack_receiver,640))==bytes(640)
  after=self.snapshot();assert after.keys()==self.before.keys()
  for key,before in self.before.items():assert after[key]==(bytes(self.expected_stack) if key[0]==n.stack else bytes(self.models[key]) if key in self.models else before),"combined retained DW memory mismatch"
  added={"original_instruction_visits":len(self.dw_trace),"clear_instruction_visits":self.dw_clear_visits,"heap_clear_store_chunks":self.dw_heap_clear_chunks,
   "stack_clear_store_chunks":self.dw_stack_clear_chunks,"exact_source_store_chunks":self.stores-start_stores,"nonstack_field_store_chunks":len(self.dw_order),
   "rejected_owned_requests":self.negatives-start_negatives,"exact_owned_header_read_contracts":self.dw_record_reads,"original_nested_constructor_returns_ABI_exact":self.dw_nested_returns,
   "original_heap_clear_returns_ABI_exact":self.dw_heap_clear_returns,"original_stack_clear_returns_ABI_exact":self.dw_stack_clear_returns,
   "owned_allocation_calls":len(self.dw_leases),"owned_allocation_bytes":8272,"owned_OS_API_calls":0,
   "nine_distinct_live_allocations_retained":True,"nested_header_and_zero_1024_slot_array_constructed":True,"original_640_byte_stack_clear_exact":True,
   "whole_entry_to_frontier_memory_and_permissions_exact":True,"ancestor_callbacks_epochs_nodes_redzones_container_and_buffer_retained":True,
   "factory_guard_in_progress":True,"outer_and_nested_registry_locks_held":True,"CRT_and_SRW_released":True,
   "stop_before_RVA":"0x600420","next_dependency_RVA":"0x10f03a0","next_dependency_bytes":8,"nested_actual_return_RVA":"0x6003cc",
   "heap_clear_actual_return_RVA":"0x5e8258","stack_clear_actual_return_RVA":"0x6003f0","outer_callee_return_not_reached_RVA":"0x5f8ea8"}
  return {"DV":prior,"added":added}
def main():
 rows=[]
 for args in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)):
  rows.append(Case(*args).run())
  if len(rows)%32==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 ancestor=json.loads((P.parent/"SOURCE-SAFE.json").read_text())
 report={"experiment":"E011DW","status":"PASS_BOUNDED_ACTUAL_NESTED_ENUMERATION_CONTAINER_CONSTRUCTION","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,
  "source_result_fixture_used":False,"native_rear_runtime_allowed":False,"full_factory_or_first_helper_return_qualified":False,"full_descriptor_registry_publication_qualified":False,
  "native_OS_CRT_allocator_construction_and_failure_paths_qualified":False,"native_runtime_scalar_selection_qualified":False,"alternate_nonzero_scalar_branch_qualified":False,
  "full_outer_callee_return_qualified":False,"next_constant_data_dependency_qualified":False,"stack_growth_guard_page_OS_qualified":False,
  "original_nested_constructor_and_two_clear_returns_qualified":True,"actual_nested_owner_relations_constructed":True,"prior_callback_table_epochs_and_six_allocations_retained":True,
  "next_experiment":"E011DX","details":rows,"new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,"production_code_changed":False,"private_raw_material_exported":False}
 keys=("original_instruction_visits","clear_instruction_visits","heap_clear_store_chunks","stack_clear_store_chunks","exact_source_store_chunks","nonstack_field_store_chunks",
  "rejected_owned_requests","original_nested_constructor_returns_ABI_exact","original_heap_clear_returns_ABI_exact","original_stack_clear_returns_ABI_exact","owned_allocation_calls","owned_allocation_bytes","owned_OS_API_calls")
 report["added_totals"]={k:sum(r["added"][k] for r in rows) for k in keys}
 report["inherited_DV_totals"]=ancestor["added_totals"];report["inherited_DU_totals"]=ancestor["inherited_DU_totals"];report["inherited_DT_totals"]=ancestor["inherited_DT_totals"];report["inherited_DS_totals"]=ancestor["inherited_DS_totals"]
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"status":report["status"],"scenarios":len(rows),"added_totals":report["added_totals"]}),flush=True)
if __name__=="__main__":main()
