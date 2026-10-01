#!/usr/bin/env python3
"""E011BO: original production-constructor AEC request with real source reader."""
from pathlib import Path
import importlib.util,struct,json,hashlib
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;EX=HERE.parent
sp=importlib.util.spec_from_file_location("bo_join",EX/"e011bm-rear-aec-original-context/source-private.py")
BM=importlib.util.module_from_spec(sp);sp.loader.exec_module(BM)
class Joined(BM.Joined):
 def __init__(self,blob,bias):
  super().__init__(blob,bias);self.factory_proto=None;self.factory_return=None;self.factory_call=None;self.factory_registrations=0;self.released=set();self.release_sizes=[]
  self.n.u.hook_add(UC_HOOK_CODE,self.factory_watch)
 def factory_watch(self,u,pc,size,user):
  if pc==self.n.base+0xcae730:
   ptr=u.reg_read(UC_ARM64_REG_X0)
   assert ptr in dict(self.allocs) and ptr not in self.released
   count=dict(self.allocs)[ptr]
   assert bytes(u.mem_read(ptr-32,32))==b"\xa5"*32 and bytes(u.mem_read(ptr+count,32))==b"\xa5"*32
   self.released.add(ptr);self.release_sizes.append(count);self.stubs[0xcae730]+=1
   # Deferred retirement: do not reuse/free the owned arena bytes.
   # The original caller and registry operations continue unchanged.
   u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR));return
  if self.phase!="factory_request":return
  if pc==self.n.base+0xda7d0:self.factory_registrations+=1
  if pc==self.n.base+0x1231d8:
   assert self.factory_proto is None
   self.factory_proto=u.reg_read(UC_ARM64_REG_X0);self.factory_return=u.reg_read(UC_ARM64_REG_LR)
   self.factory_call=self.factory_return-self.n.base-4
   assert any(ptr==self.factory_proto and count==384 for ptr,count in self.allocs)
  elif self.factory_return is not None and pc==self.factory_return:
   assert u.reg_read(UC_ARM64_REG_X0)==self.factory_proto
   self.factory_AEC_returned=True
 def factory_request(self):
  n=self.n;u=n.u;obj=n.heap+0x8000+self.bias
  heap_before=bytes(u.mem_read(n.heap,0x30000));arena_before=bytes(u.mem_read(self.arena,self.arena_size))
  alloc_before=len(self.allocs);stack_context=bytes(u.mem_read(self.context,48))
  self.phase="factory_request"
  for i in range(8):u.reg_write(globals()["UC_ARM64_REG_X"+str(i)],0)
  u.reg_write(UC_ARM64_REG_X0,obj);u.reg_write(UC_ARM64_REG_SP,n.stack+0xd000);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(n.base+0xd2bb0,n.end,count=5000000)
  assert self.factory_proto is not None and self.factory_AEC_returned and u.reg_read(UC_ARM64_REG_PC)==n.end
  assert u.reg_read(UC_ARM64_REG_X0)==obj and self.factory_registrations==565
  requests=[self.readq(obj+1112+8*i) for i in range(565)]
  assert len(set(requests))==565 and all(ptr in dict(self.allocs) for ptr in requests)
  assert self.readq(obj+0x13b0)==self.factory_proto and self.factory_proto in requests
  self.factory_constructor_allocations=len(self.allocs)-alloc_before
  self.factory_constructor_releases=len(self.released)
  assert self.factory_constructor_allocations==1880 and self.factory_constructor_releases==3
  self.phase="lookup";request_before=bytes(u.mem_read(self.factory_proto,384))
  self.lookup_returns=0
  for _ in range(2):
   # Name is read from the original source reader; request metadata is OEM-produced.
   self.invoke_low(0xd2a20,[obj,self.root_reader+12])
   assert u.reg_read(UC_ARM64_REG_X0)==self.factory_proto
   assert bytes(u.mem_read(self.factory_proto,384))==request_before
   self.lookup_returns+=1
  assert self.readq(obj)==n.base+0x1335288
  expect=bytearray(heap_before);at=obj-n.heap;expect[at:at+5696]=bytes(u.mem_read(obj,5696))
  assert bytes(u.mem_read(n.heap,0x30000))==expect
  expected=bytearray(arena_before)
  for ptr,count in self.allocs[alloc_before:]:
   at=ptr-self.arena;expected[at:at+count]=bytes(u.mem_read(ptr,count))
  assert bytes(u.mem_read(self.arena,self.arena_size))==expected
  assert bytes(u.mem_read(self.context,48))==stack_context
  assert bytes(u.mem_read(self.map,self.map_size))==self.file_before
  # Full factory and actual name lookup are qualified, then scratch is restored.
  # Direct AEC join remains separate from complete loader selection/lifetime.
  u.mem_write(obj,heap_before[obj-n.heap:obj-n.heap+5696]);self.phase="joined"
  self.factory_allocations=len(self.allocs)-alloc_before
  return self.factory_proto
 def join(self):
  n=self.n;u=n.u;rr=self.root_reader;ctx=self.context
  proto=n.heap+0x1000+self.bias;proto_before=bytes(u.mem_read(proto,384))
  all_heap=bytes(u.mem_read(n.heap,0x30000));stack_context=bytes(u.mem_read(ctx,48))
  proto=self.factory_request()
  name=self.name_bytes(rr+12,32);profile=self.name_bytes(rr+72,127);filename=self.name_bytes(self.readq(ctx),128)
  assert self.readq(proto)==n.base+0x1335598 and self.readq(proto+60)==10
  assert self.readq(proto+60)==self.readq(rr+52)
  assert self.name_bytes(proto+16,32)==name
  assert bytes(u.mem_read(self.readq(proto+8),len(name)+1))==name+b"\0"
  assert self.readi(proto+68)==0 and self.readq(proto+72)==0 and bytes(u.mem_read(proto+208,1))==bytes(1)
  assert bytes(u.mem_read(n.heap,0x30000))==all_heap
  assert bytes(u.mem_read(ctx,48))==stack_context
  # Real comparison and version gates must reject incompatible owned requests.
  negative_returns=0
  for at in [16,60]:
   original=bytes(u.mem_read(proto+at,1));alloc_count=len(self.allocs)
   u.mem_write(proto+at,bytes([original[0]^1]));heap_before=bytes(u.mem_read(n.heap,0x30000))
   arena_before=bytes(u.mem_read(self.arena,self.arena_size))
   self.invoke_low(0x123cc0,[proto,rr,1])
   assert u.reg_read(UC_ARM64_REG_X0)==0 and len(self.allocs)==alloc_count
   assert bytes(u.mem_read(n.heap,0x30000))==heap_before
   assert bytes(u.mem_read(self.arena,self.arena_size))==arena_before
   u.mem_write(proto+at,original);negative_returns+=1
  table_before=bytes(u.mem_read(self.table,(max(self.sy)+1)*224))
  arena_before=bytes(u.mem_read(self.arena,self.arena_size));alloc_count=len(self.allocs)
  heap_before=bytes(u.mem_read(n.heap,0x30000));nodes_before=bytes(u.mem_read(self.nodes,len(self.records)*160))
  self.invoke_low(0x123cc0,[proto,rr,1])
  new=self.allocs[alloc_count:];module=u.reg_read(UC_ARM64_REG_X0)
  assert module==new[0][0] and new[0][1]==384 and new[1][1]==len(name)+1
  assert len(new)==12+2*self.info["hist_count"]
  self.metadata(module,rr,10,0x1335598)
  # Unwritten embedded-name tail/padding differs between A5 owned request and zeroed parent.
  # Name bytes/termination are verified above; opaque helper tail is not independently claimed.
  assert bytes(u.mem_read(n.heap,0x30000))==heap_before and bytes(u.mem_read(ctx,48))==stack_context
  assert bytes(u.mem_read(self.nodes,len(self.records)*160))==nodes_before
  payload=module+288;data=lambda sid:self.blob[self.sy[sid]["data_abs_offset"]:self.sy[sid]["data_abs_offset"]+self.sy[sid]["data_bytes"]]
  # Name allocation shifts inherited sibling indices by one.
  assert [count for _,count in new[:8]]==[384,len(name)+1,2,480,4,4,4,4]
  revision=new[2][0];grids=new[3][0]
  assert self.readq(payload+32)==revision and bytes(u.mem_read(revision,2))==data(self.info["revision_symbol_id"])
  assert self.readi(payload+44)==4 and self.readq(payload+56)==grids
  for i in range(4):
   for at,size in [(20,12),(32,16),(48,16)]:
    assert bytes(u.mem_read(grids+120*i+at,size))==self.wire[101*i+at:101*i+at+size]
   sid=struct.unpack_from("<I",self.wire,101*i+93)[0];nested=new[4+i][0]
   assert self.readq(grids+120*i+104)==nested and bytes(u.mem_read(nested,4))==data(sid)
  count=self.info["hist_count"];histarray=new[8][0];histwire=data(self.info["hist_symbol_id"])
  assert new[8][1]==200*count and self.readi(payload+64)==count and self.readq(payload+72)==histarray
  for i,(dsid,vsid,vcount) in enumerate(self.info["hist_children"]):
   wire=histwire[172*i:172*(i+1)];out=bytes(u.mem_read(histarray+200*i,200))
   assert out[:148]==wire[:148] and out[152:156]==wire[148:152]
   assert out[168:172]==wire[156:160] and out[172:176]==wire[160:164] and out[192:196]==wire[168:172]
   # Reserved bytes/padding are not source-field claims.
   for j,(sid,size,at) in enumerate([(dsid,4,160),(vsid,4*vcount,184)]):
    ptr,nbytes=new[9+2*i+j];assert nbytes==size and struct.unpack_from("<Q",out,at)[0]==ptr
    assert bytes(u.mem_read(ptr,size))==data(sid)
  bidx=9+2*count;bfw,combo,nested=[new[bidx+j][0] for j in range(3)]
  assert [c for _,c in new[bidx:]]==[160,160,4]
  assert self.readi(payload+80)==1 and self.readq(payload+88)==bfw
  wire=data(self.info["bfw_symbol_id"]);out=bytes(u.mem_read(bfw,160))
  assert out[:16]==wire[:16] and out[32:144]==wire[20:132] and out[144:148]==wire[132:136]
  # BFW reserved/padding bytes are not source-field claims.
  assert struct.unpack_from("<Q",out,24)[0]==combo and struct.unpack_from("<Q",out,152)[0]==nested
  assert bytes(u.mem_read(combo,160))==data(self.info["combo_symbol_id"])
  assert bytes(u.mem_read(nested,4))==data(self.info["bfw_data_symbol_id"])
  expected_cursors={self.info["root_symbol_id"]:48,self.info["revision_symbol_id"]:2,
   self.info["grid_symbol_id"]:404,self.info["hist_symbol_id"]:172*count,
   self.info["bfw_symbol_id"]:140,self.info["combo_symbol_id"]:160,self.info["bfw_data_symbol_id"]:4}
  for i in range(4):
   sid=struct.unpack_from("<I",self.wire,101*i+93)[0];expected_cursors[sid]=4
  for dsid,vsid,vcount in self.info["hist_children"]:
   expected_cursors[dsid]=4;expected_cursors[vsid]=4*vcount
  for sid in self.sy:assert self.readq(self.table+sid*224+216)==expected_cursors.get(sid,0)
  # All pre-existing allocation bytes outside reader cursor fields must survive.
  expect=bytearray(arena_before)
  for sid in self.sy:
   ix=self.table+sid*224+216-self.arena;expect[ix:ix+8]=struct.pack("<Q",expected_cursors.get(sid,0))
  for ptr,size in new:
   ix=ptr-self.arena;expect[ix:ix+size]=bytes(u.mem_read(ptr,size))
  assert bytes(u.mem_read(self.arena,self.arena_size))==expect
  assert bytes(u.mem_read(self.map,self.map_size))==self.file_before
  self.bounds()
  assert set(self.stubs)<=set([0x11d0,0x11f0,0xcae740,0xf5e600,0xcae730])
  return {"symbol_reader_full_returns":self.returns,"source_mode_records":len(self.records),
    "original_symbol_table_builder_returns":1,"original_AEC_parent_full_returns":1,
    "original_metadata_constructor_returns":1,"original_factory_AEC_request_constructor_returns":1,"original_gate_rejections":negative_returns,
    "parent_allocations":len(new),"histogram_entries":count,"grids":4,"BFW_records":1,
    "original_stack_context_qualified":True,"all_preexisting_non_cursor_allocation_bytes_preserved":True}

def main():
 results=[]
 for name,sha in BM.BL.BH.FIXTURE.AV.FILES[1:]:
  blob=(BM.BL.BH.FIXTURE.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  for bias in [0,1]:
   f=Joined(blob,bias);f.build();r=f.join()
   results.append({"source_sha256":sha,"placement":bias,"factory_AEC_constructor_call_RVA":hex(f.factory_call),"factory_constructor_allocations":f.factory_constructor_allocations,"factory_registration_stores":f.factory_registrations,"factory_constructor_owned_releases":f.factory_constructor_releases,"original_factory_full_returns":1,"original_name_lookup_returns":f.lookup_returns,"total_owned_release_calls":len(f.released),**r})
   print(json.dumps(results[-1]),flush=True)
 result={"experiment":"E011BO","status":"PASS_BOUNDED_FULL_FACTORY_REGISTRY_AEC_LOOKUP_AND_SOURCE_READER_JOIN",
 "base_commit":"1606909a7a5c31fb800aebfbb332e6f29ceef4fe","source_cases":results,
 "original_symbol_reader_returns":sum(r["symbol_reader_full_returns"] for r in results),
 "original_factory_AEC_request_constructor_returns":4,"original_AEC_parent_full_returns":4,
 "original_metadata_constructor_returns":4,"original_name_version_rejections":8,
 "request_version_not_taken_from_tuning_file":True,"request_name_not_taken_from_tuning_file":True,
 "actual_production_constructor_AEC_call_executed":True,"whole_production_constructor_return_claimed":True,
 "original_factory_full_returns":4,"original_registry_registration_stores":2260,"original_name_lookup_returns":8,
 "factory_AEC_name_lookup_closed_for_tested_sources":True,
 "production_slot8_is_deleting_destructor_not_lookup":True,"production_slot24_name_lookup_RVA":"0xD2A20",
 "allocator_release_fixture_contract":"owned allocation start only, no double release, canaries checked, deferred retirement without reuse",
 "OEM_heap_release_failure_claimed":False,"released_allocation_reuse_and_factory_destruction_qualified":False,
 "whole_loader_profile_selection_closed":False,"whole_loader_return_claimed":False,
 "direct_consumer_join_uses_original_source_stack_context":True,
 "all_prior_qualified_revision_grid_histogram_BFW_fields_retained":True,
 "all_unrelated_source_allocation_bytes_preserved":True,
 "opaque_name_tail_padding_every_root_grid_field_closed":False,
 "opened_filesystem_filename_policy_closed":False,"platform_path_closed":False,
 "retained_shims":["0x11D0","0x11F0","0xCAE740","0xF5E600","0xCAE730"],
 "original_DLL_sha256":BM.BL.BH.FIXTURE.SHA,"originals_exported":False,"captured_scalars_as_producer_inputs":False,
 "production_C_changed":False,"kernel_build_performed":False,"new_camera_starts":0,"new_reboots":0,
 "observer_armed":False,"native_rear_runtime_allowed":False}
 (HERE/"REGISTRY-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":result["status"],"reader_returns":result["original_symbol_reader_returns"],"factory_request_returns":4,"parent_returns":4}),flush=True)
if __name__=="__main__":main()
