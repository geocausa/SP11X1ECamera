#!/usr/bin/env python3
"""E011BP: full rear loaders and retained AEC ownership; originals stay on SP11."""
from pathlib import Path
import importlib.util,json,struct,hashlib,bisect
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;EX=HERE.parent
sp=importlib.util.spec_from_file_location("bp_loader",EX/"e011bo-rear-aec-factory-registry/loader-private.py")
BO=importlib.util.module_from_spec(sp);sp.loader.exec_module(BO)
BASE_NATIVE=BO.BO.BM.BL.Native
class ScopedNative(BASE_NATIVE):
 def __init__(self):
  super().__init__();original=self.u.hook_add;self.scoped_hook_count=0
  sites={"hook":[0x6f31b4,0x6f3420,0x6f1bf0,0x6f3b50,0x6f2208,0xcb6300,0x6f4a98,0x11d0,0x11f0,0xcae740,0xf5e600],
   "watch":[0x6f45d8,0x6f4ac0,0xf5df00,0x6f3524,0x6f4e84,0x6f4e88],
   "factory_watch":[0xcae730,0x1231d8,0xd979a0,0xda7d0],
   "loader_watch":[0xd2a20,0x6f35ac,0x123cc0,0x6f35b0,0x6f3654,0x6f3658]}
  def scoped(kind,callback,*args,**kwargs):
   if kind!=BO.UC_HOOK_CODE:return original(kind,callback,*args,**kwargs)
   assert not args and not kwargs and callback.__name__ in sites
   handles=[original(kind,callback,begin=self.base+r,end=self.base+r) for r in sites[callback.__name__]]
   self.scoped_hook_count+=len(handles);return handles[0]
  self.u.hook_add=scoped
BO.BO.BM.BL.Native=ScopedNative
class Production(BO.Production):
 def __init__(self,blob,bias):
  self.actual_module=None;self.module_slot=None;self.store_pending=False
  super().__init__(blob,bias)
 def hook(self,u,pc,size,user):
  if pc!=self.n.base+0xf5e600:return super().hook(u,pc,size,user)
  # Same non-overlapping owned-allocation predicate as BL, with logarithmic lookup.
  out=u.reg_read(UC_ARM64_REG_X0);count=u.reg_read(UC_ARM64_REG_X2)
  ix=bisect.bisect_right(self.allocs,out,key=lambda item:item[0])-1
  assert ix>=0
  ptr,extent=self.allocs[ix];assert ptr<=out and out+count<=ptr+extent and ptr not in self.released
  self.stubs[0xf5e600]+=1;u.mem_write(out,bytes([u.reg_read(UC_ARM64_REG_X1)&255])*count)
  u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
 def verify_actual_AEC(self):
  super().verify_actual_AEC();self.actual_module=self.n.u.reg_read(UC_ARM64_REG_X0)
  self.actual_allocs=self.allocs[self.AEC_pending["alloc_count"]:]
  self.actual_before={ptr:bytes(self.n.u.mem_read(ptr,size)) for ptr,size in self.actual_allocs}
 def loader_watch(self,u,pc,size,user):
  super().loader_watch(u,pc,size,user)
  if self.phase!="loader":return
  r=pc-self.n.base
  if r==0x6f3654 and u.reg_read(UC_ARM64_REG_X23)==self.actual_module:
   assert self.module_slot is None
   self.module_slot=u.reg_read(UC_ARM64_REG_X0);self.module_leaf=u.reg_read(UC_ARM64_REG_X22);self.module_owner=u.reg_read(UC_ARM64_REG_X27)
   source_sid=struct.unpack_from("<I",self.blob,self.sy[self.info["root_symbol_id"]]["record_offset"]+44)[0]
   assert self.module_leaf==self.nodes+160*source_sid
   alias=self.readq(self.module_leaf+48);assert self.module_owner==(alias if alias else self.module_leaf)
   self.store_pending=True
  elif r==0x6f3658 and self.store_pending:
   assert self.readq(self.module_slot)==self.actual_module;self.store_pending=False
 def active(self,ptr,size=1):
  ix=bisect.bisect_right(self.starts,ptr)-1
  assert ix>=0
  start=self.starts[ix];assert start not in self.released and ptr+size<=start+self.sizes[start]
  return start,self.sizes[start],ptr-start
 def immutable(self):
  u=self.n.u
  for ptr,size in self.actual_allocs:
   assert ptr not in self.released
   actual=bytes(u.mem_read(ptr,size));expected=self.actual_before[ptr]
   # +280 is the OEM sibling-list link, deliberately updated after parent return.
   if ptr==self.actual_module:assert actual[:280]==expected[:280] and actual[288:]==expected[288:]
   else:assert actual==expected
 def original_map_lookup(self,node,name):
  u=self.n.u;tmp=self.n.heap+0x2000+self.bias
  u.mem_write(tmp,bytes(32))
  before=len(self.allocs);self.invoke_low(0x2e2e0,[tmp,name,len(self.name_bytes(name,32))])
  self.invoke_low(0x6f3f48,[node+96,tmp]);slot=u.reg_read(UC_ARM64_REG_X0)
  cap=self.readq(tmp+24)
  if cap>15:self.invoke_low(0xf078,[self.readq(tmp)])
  # Restore owned query scratch; it is separate from the production object.
  u.mem_write(tmp,b"\xa5"*32)
  assert len(self.allocs)-before==1
  return slot
 def ownership(self,loader_result):
  u=self.n.u;self.phase="ownership"
  self.starts=[ptr for ptr,size in self.allocs];self.sizes=dict(self.allocs)
  assert self.module_slot is not None and not self.store_pending
  start,size,offset=self.active(self.module_slot,8);assert offset==48 and size==56
  self.active(self.actual_module,384);self.active(self.nodes,160*len(self.records));self.immutable()
  assert self.readq(self.module_slot)==self.actual_module
  name=self.name_bytes(self.actual_module+16,32);entry=start
  assert self.readq(entry+32)==len(name)
  key=entry+16 if self.readq(entry+40)<=15 else self.readq(entry+16)
  assert self.name_bytes(key,32)==name
  if key!=entry+16:self.active(key,len(name)+1)
  # Verify all source nodes' OEM sibling lists and locate the actual AEC object.
  linked=set();AEC_memberships=0
  for sid in self.records:
   node=self.nodes+160*sid;ptr=self.readq(node+80);tail=self.readq(node+88);local=set();last=0
   while ptr:
    self.active(ptr,288);assert ptr not in local;local.add(ptr);linked.add(ptr);last=ptr
    if ptr==self.actual_module:
     assert node==self.module_leaf;AEC_memberships+=1
    ptr=self.readq(ptr+280)
   assert last==tail
  assert AEC_memberships==1
  rootids=[sid for sid,row in self.records.items() if row[3] in [sid,0xffffffff]];assert rootids==[0]
  root=self.nodes;assert self.readq(self.manager+1064)==root
  # One-record query is the root profile: OEM selector ignores index0.
  query=self.n.heap+0x1000+self.bias;row=self.records[0]
  u.mem_write(query,struct.pack("<2I",row[1]&65535,row[1]>>16))
  before_alloc=len(self.allocs);before_release=len(self.released)
  self.invoke_low(0x6f3bd0,[self.manager,query,1]);selected=u.reg_read(UC_ARM64_REG_X0)
  assert selected==root and self.module_owner==root
  assert len(self.allocs)==before_alloc and len(self.released)==before_release
  self.starts=[ptr for ptr,size in self.allocs];self.sizes=dict(self.allocs)
  slot=self.original_map_lookup(selected,self.actual_module+16)
  assert slot==self.module_slot and self.readq(slot)==self.actual_module
  # Retire the source/context from this fixture, then repeat the actual OEM lookup.
  u.mem_write(query,b"\xa5"*8);self.bounds()
  assert self.readq(self.manager+16)==self.filebase+88
  context=self.context;u.mem_write(context,b"\xd3"*48)
  u.mem_unmap(self.map,self.map_size)
  self.sizes=dict(self.allocs);self.starts=[ptr for ptr,size in self.allocs]
  retired=sorted((ptr,self.sizes[ptr]) for ptr in self.released)
  for ptr,size in retired:u.mem_write(ptr,b"\xd7"*size)
  retired_starts=[ptr for ptr,size in retired]
  def reject_retired_read(u,access,address,size,value,user):
   ix=bisect.bisect_right(retired_starts,address+size-1)-1
   if ix>=0:
    ptr,count=retired[ix];assert address>=ptr+count or address+size<=ptr,"post-return lookup read retired storage"
  u.hook_add(UC_HOOK_MEM_READ,reject_retired_read,begin=self.arena,end=self.arena+self.arena_size-1)
  def reject_context_read(u,access,address,size,value,user):raise AssertionError("post-return lookup read old source stack context")
  u.hook_add(UC_HOOK_MEM_READ,reject_context_read,begin=context,end=context+47)
  u.mem_write(query,struct.pack("<2I",row[1]&65535,row[1]>>16))
  self.invoke_low(0x6f3bd0,[self.manager,query,1]);selected=u.reg_read(UC_ARM64_REG_X0);assert selected==root
  slot=self.original_map_lookup(selected,self.actual_module+16);assert slot==self.module_slot and self.readq(slot)==self.actual_module
  self.immutable();u.mem_write(query,b"\xa5"*8);self.bounds()
  return {**loader_result,"runtime_node_lists_verified":len(self.records),"unique_linked_modules_verified":len(linked),
   "actual_AEC_node_list_memberships":AEC_memberships,"actual_AEC_map_entry_extent":56,"actual_AEC_map_value_offset":48,
   "actual_AEC_deep_allocations_retained":len(self.actual_allocs),"actual_AEC_immutable_metadata_and_payload_preserved":True,
   "AEC_sibling_link_offset280_is_mutable":True,"AEC_name_map_key_is_owned_terminated_copy":True,
   "actual_AEC_leaf_is_source_flagged_node":bool(self.records[self.readi(self.actual_module+68)][2]),
   "actual_AEC_map_owner_is_root_profile":True,"original_root_profile_selector_returns":2,"original_loaded_module_name_map_returns":2,
   "source_file_unmapped_old_context_overwritten_retired_storage_poisoned":True,
   "postretirement_lookup_reads_no_old_context_or_retired_allocations":True,"postretirement_AEC_immutable_fields_pass":True,
   "retained_fixture_shims_unchanged":True,"scoped_hook_sites":self.n.scoped_hook_count}
def main():
 results=[]
 for name,sha in BO.BO.BM.BL.BH.FIXTURE.AV.FILES[1:]:
  blob=(BO.BO.BM.BL.BH.FIXTURE.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  for bias in [0,1]:
   f=Production(blob,bias);r=f.run_full();r=f.ownership(r);results.append({"source_sha256":sha,**r})
   print(json.dumps(results[-1]),flush=True)
 result={"experiment":"E011BP","status":"PASS_BOUNDED_BOTH_REAR_FULL_LOADERS_AND_RETAINED_AEC_ROOT_LOOKUP",
  "base_commit":"c43ff0f0b65468081606e6577e0b73b4a509e211","source_cases":results,
  "original_full_loader_returns":len(results),"original_exact_reader_returns":sum(r["source_reader_full_returns"] for r in results),
  "actual_AEC_parent_full_returns":sum(r["actual_AEC_parent_full_returns"] for r in results),
  "original_module_dispatches":sum(r["original_module_dispatches"] for r in results),
  "original_root_profile_selector_returns":sum(r["original_root_profile_selector_returns"] for r in results),
  "original_loaded_module_name_map_returns":sum(r["original_loaded_module_name_map_returns"] for r in results),
  "AEC_data_and_tested_root_lookup_independent_of_retired_source_context":True,
  "entire_manager_source_context_lifetime_closed":False,"manager_header_name_pointer_still_borrows_source":True,
  "nonroot_profile_selection_policy_closed":False,"all_module_fields_independently_validated":False,
  "factory_destruction_and_allocator_reuse_qualified":False,"platform_path_and_opened_filesystem_filename_closed":False,
  "retained_shims":["0x11D0","0x11F0","0xCAE740","0xF5E600","0xCAE730"],
  "scoped_hooks_change_emulated_source_instructions_or_semantics":False,
  "memset_owned_extent_guard_uses_nonoverlap_binary_search":True,
  "originals_exported":False,"captured_scalars_as_producer_inputs":False,
  "new_camera_starts":0,"new_reboots":0,"native_rear_runtime_allowed":False}
 (HERE/"OWNERSHIP-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":result["status"],"loader_returns":len(results)}),flush=True)
if __name__=="__main__":main()
