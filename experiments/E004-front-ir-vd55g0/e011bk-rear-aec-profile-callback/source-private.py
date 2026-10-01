#!/usr/bin/env python3
"""E011BK: bounded original interface, callback, formatter and complete reader."""
from pathlib import Path
import importlib.util, hashlib, json, struct, pefile
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;EX=HERE.parent
s=importlib.util.spec_from_file_location("bk_width",EX/"e011bj-rear-aec-reader-width-authority/source-private.py")
BJ=importlib.util.module_from_spec(s);s.loader.exec_module(BJ);BH=BJ.BH
BIAS=[0,1,0x1230,0x8010]
def facts():
 b=BH.FIXTURE.DLL.read_bytes();assert hashlib.sha256(b).hexdigest()==BH.FIXTURE.SHA
 p=pefile.PE(data=b);base=p.OPTIONAL_HEADER.ImageBase
 tables=[0x1335288,0x133b740,0x133de98,0x133e228]
 assert all(struct.unpack("<Q",p.get_data(x,8))[0]-base==0x6f3b50 for x in tables)
 return {"manager_constructor_rva":"0x6F3D08","manager_primary_table_rva":"0x133B740",
 "matching_interface_slot0_rvas":[hex(x) for x in tables],"callback_target_rva":"0x6F3B50",
 "profile_formatter_rva":"0x6F2208","original_bounded_decimal_formatter_rva":"0xCB6300",
 "reader_dispatch_rva":"0x6F4A98","callback_node_table_offset":1072,
 "callback_node_count_offset":1080,"callback_node_stride":160,
 "callback_numeric_source_offset":4,"callback_numeric_bytes":8,
 "formatter_u16_offsets":[4,6],"formatter_suppress_u32_offset":8,
 "formatter_parent_pointer_offset":24,"reader_callback_index_wire_offset":44,
 "reader_callback_numeric_output_offset":60,"reader_callback_profile_output_offset":72}
def validate(nodes,index,count,null=False):
 assert isinstance(index,int) and 0<=index<2**32
 assert isinstance(count,int) and 0<=count<=len(nodes)<=12
 for a,b,flag,parent in nodes:
  assert isinstance(a,int) and 0<=a<2**16 and isinstance(b,int) and 0<=b<2**16
  assert isinstance(flag,int) and 0<=flag<2**32
  assert parent is None or isinstance(parent,int) and 0<=parent<len(nodes)
 for start in range(len(nodes)):
  seen=set();cur=start
  while cur is not None:
   assert cur not in seen,"owned graph cycle excluded before execution"
   seen.add(cur);cur=nodes[cur][3]
  assert len(profile(nodes,start))<=100,"owned profile length scope"
 return not null and index<count and index<2**31
def profile(nodes,index):
 a,b,flag,parent=nodes[index]
 before="" if parent is None else profile(nodes,parent)
 part="" if flag else str(a)+"."+str(b)
 return "|".join(x for x in [before,part] if x)
def profile_bytes(nodes,index,initial):
 out=bytearray(initial);out[0]=0;text=profile(nodes,index).encode()
 if text:out[:len(text)+1]=text+b"\0";out[127]=0
 return bytes(out)
class Fixture:
 def __init__(self,blob):
  self.o=BH.Owned(blob);self.n=self.o.n;self.trace={}
  self.n.u.hook_add(UC_HOOK_CODE,self.observe)
 def observe(self,u,address,size,user):
  r=address-self.n.base
  if r in [0x6f3d08,0x6f3b50,0x6f2208,0xcb6300,0x6f4a98]:
   key=hex(r);self.trace[key]=self.trace.get(key,0)+1
 def reset(self,bias):
  self.trace={};return self.o.reset(bias)
 def constructor(self,bias):
  n=self.n;u=self.reset(bias);obj=n.heap+0x6000+bias
  before=bytes(u.mem_read(n.heap,0x30000));self.o.invoke(0x6f3d08,[obj]);expected=bytearray(before)
  fields=[(0,struct.pack("<Q",n.base+0x133b740)),(8,struct.pack("<Q",n.base+0x1419fc8)),
  (16,bytes(8)),(24,bytes(4)),(28,bytes(1)),(1056,bytes(16)),(1072,bytes(8)),
  (1080,bytes(4)),(1088,bytes(16)),(1104,bytes(8))]
  for at,data in fields:
   off=obj-n.heap+at;expected[off:off+len(data)]=data
  assert bytes(u.mem_read(n.heap,0x30000))==expected
  assert u.reg_read(UC_ARM64_REG_X0)==obj and not self.o.f.stub_counts and not self.o.f.allocs
 def setup(self,nodes,index,count,null,bias):
  valid=validate(nodes,index,count,null);n=self.n;u=self.reset(bias)
  manager=n.heap+0x6000+bias;table=n.heap+0x8000+bias
  self.o.invoke(0x6f3d08,[manager])
  for k,(a,b,flag,parent) in enumerate(nodes):
   at=table+k*160;u.mem_write(at+4,struct.pack("<HHI",a,b,flag))
   u.mem_write(at+24,struct.pack("<Q",0 if parent is None else table+160*parent))
  u.mem_write(manager+1072,struct.pack("<QI",0 if null else table,count))
  return u,manager,table,valid
 def checks(self):
  assert set(self.o.f.stub_counts)<=set(["0x11d0","0x11f0"])
  assert not self.o.f.allocs
 def callback(self,nodes,index,count,null,bias):
  u,manager,table,valid=self.setup(nodes,index,count,null,bias);n=self.n
  numeric=n.heap+0x4000+bias;dest=n.heap+0x4100+bias
  before=bytes(u.mem_read(n.heap,0x30000));self.o.invoke(0x6f3b50,[manager,index,numeric,dest])
  expected=bytearray(before);off=numeric-n.heap
  expected[off:off+8]=struct.pack("<HHI",*nodes[index][:3]) if valid else bytes(8)
  if valid:
   off=dest-n.heap;expected[off:off+128]=profile_bytes(nodes,index,before[off:off+128])
  assert bytes(u.mem_read(n.heap,0x30000))==expected
  assert self.trace.get("0x6f3b50")==1
  assert self.trace.get("0x6f2208",0)==(self.depth(nodes,index) if valid else 0)
  self.checks()
 def depth(self,nodes,index):
  n=0
  while index is not None:n+=1;index=nodes[index][3]
  return n
 def formatter(self,nodes,index,bias):
  u,manager,table,valid=self.setup(nodes,index,len(nodes),False,bias);n=self.n
  assert valid;dest=n.heap+0x4100+bias;u.mem_write(dest,bytes(4))
  before=bytes(u.mem_read(n.heap,0x30000));self.o.invoke(0x6f2208,[table+160*index,dest])
  expected=bytearray(before);off=dest-n.heap
  expected[off:off+128]=profile_bytes(nodes,index,before[off:off+128])
  assert bytes(u.mem_read(n.heap,0x30000))==expected
  assert self.trace.get("0x6f2208")==self.depth(nodes,index);self.checks()
class CompleteReader(BJ.Reader):
 def __init__(self,blob,seed=None):
  super().__init__(blob,seed);self.trace={}
  self.n.u.hook_add(UC_HOOK_CODE,self.observe)
 def observe(self,u,address,size,user):
  if address-self.n.base in [0x6f3b50,0x6f2208,0xcb6300,0x6f4a98]:
   k=hex(address-self.n.base);self.trace[k]=self.trace.get(k,0)+1
 def run_full(self,bias,graph):
  n=self.n;u=self.o.reset(bias);self.trace={}
  obj=n.heap+0x4000+bias;cursor=n.heap+0x2000+bias;context=n.heap+0x3000+bias
  manager=n.heap+0x6000+bias;table=n.heap+0x8000+bias;filebase=self.map+bias
  off=self.sy[self.info["root_symbol_id"]]["record_offset"];record=self.blob[off:off+56]
  index=struct.unpack_from("<I",record,44)[0]
  # Both graph choices are owned policy fixtures, never a captured profile or source selector.
  if index<8:
   nodes=[(12,34,0,None)]*(index+1)
   if graph:
    nodes=nodes+[(56,78,0,None)];nodes[index]=(12,34,0,len(nodes)-1)
   count=len(nodes)
  else:nodes=[(12,34,0,None)];count=1
  valid=validate(nodes,index,count)
  self.o.invoke(0x6f3d08,[manager])
  u.mem_write(manager+1072,struct.pack("<QI",table,count))
  for k,(a,b,flag,parent) in enumerate(nodes):
   u.mem_write(table+160*k+4,struct.pack("<HHI",a,b,flag))
   u.mem_write(table+160*k+24,struct.pack("<Q",0 if parent is None else table+160*parent))
  u.mem_write(self.map,bytes([0xa5])*self.size);u.mem_write(filebase,self.blob)
  u.mem_write(cursor,struct.pack("<Q",off));u.mem_write(context,bytes(128));u.mem_write(obj,struct.pack("<Q",context))
  before=bytes(u.mem_read(n.heap,0x30000));file_before=bytes(u.mem_read(self.map,self.size))
  self.o.invoke(0x6f47b8,[obj,filebase,len(self.blob),cursor,self.h["sections"][1]["offset"],manager,1])
  relative=struct.unpack_from("<I",record,48)[0]
  fields=[(8,record[:4]),(12,record[4:36]+b"\0"),(52,record[36:44]),
  (60,struct.pack("<HHI",*nodes[index][:3]) if valid else bytes(8)),(68,record[44:48]),
  (200,record[52:56]),(208,struct.pack("<Q",filebase+self.h["sections"][1]["offset"]+relative))]
  expected=bytearray(before)
  for at,data in fields:
   x=obj-n.heap+at;expected[x:x+len(data)]=data
  x=obj-n.heap+72;initial=bytearray(before[x:x+128]);initial[0]=0
  expected[x:x+128]=profile_bytes(nodes,index,initial) if valid else initial
  x=cursor-n.heap;expected[x:x+8]=struct.pack("<Q",off+56)
  assert bytes(u.mem_read(n.heap,0x30000))==expected
  assert bytes(u.mem_read(self.map,self.size))==file_before
  assert self.trace.get("0x6f4a98")==1 and self.trace.get("0x6f3b50")==1
  assert self.trace.get("0x6f2208",0)==((2 if graph else 1) if valid else 0)
  assert set(self.o.f.stub_counts)<=set(["0x11d0","0x11f0"])
  assert not self.o.f.allocs
  assert (obj+12,filebase+off+4,32) in self.o.f.copies
def main():
 anchors=facts();roots=[];audit=[]
 for name,sha in BH.FIXTURE.AV.FILES:
  b=(BH.FIXTURE.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(b).hexdigest()==sha
  _,sy,_,info=BH.FIXTURE.source(b);roots.append(b)
  audit.append({"path":name,"sha256":sha,"typed_root_symbol_id":info["root_symbol_id"]})
 f=Fixture(roots[-1]);constructors=callbacks=formatters=0
 single=[(12,34,0,None)]
 graphs=[single,[(0,0,0,None)],[(65535,65535,0,None)],[(12,34,1,None)],
 [(12,34,0x12345678,None)],[(12,34,0,1),(56,78,0,None)],
 [(12,34,1,1),(56,78,0,None)],[(12,34,0,1),(56,78,1,None)],
 [(1,2,0,1),(3,4,0,2),(5,6,0,None)],
 [(1,2,1,1),(3,4,0,2),(5,6,1,None)],
 [(1,2,0,None),(3,4,0,None),(5,6,0,None)]]
 cases=[(g,0,len(g),False) for g in graphs]
 cases += [(graphs[-1],1,3,False),(graphs[-1],2,3,False),
 (single,1,1,False),(single,0xffffffff,1,False),(single,0x80000000,1,False),
 (single,0,0,False),(single,0,1,True)]
 for bias in BIAS:
  f.constructor(bias);constructors+=1
  for nodes,index,count,null in cases:
   f.callback(nodes,index,count,null,bias);callbacks+=1
  for g in graphs:
   f.formatter(g,0,bias);formatters+=1
 rejected=0
 malformed=[([(-1,0,0,None)],0,1),([(0,65536,0,None)],0,1),
 ([(0,0,2**32,None)],0,1),([(0,0,0,0)],0,1),([(0,0,0,2)],0,1),
 (single,-1,1),(single,2**32,1),(single,0,2)]
 for nodes,index,count in malformed:
  before=bytes(f.n.u.mem_read(f.n.heap,0x30000));tr=dict(f.trace)
  try:f.callback(nodes,index,count,False,0)
  except AssertionError:rejected+=1
  else:raise AssertionError("scope input accepted")
  assert bytes(f.n.u.mem_read(f.n.heap,0x30000))==before and f.trace==tr
 _,sy,_,info=BH.FIXTURE.source(roots[-1]);off=sy[info["root_symbol_id"]]["record_offset"]
 variants=[]
 for packed,index in [(0,0),(1<<32,1),(0x123456789abcdef0,3),((1<<64)-1,7),
 (0x8000000000000000,0x80000000),(0x000000010000000a,0xffffffff)]:
  b=bytearray(roots[-1]);struct.pack_into("<QI",b,off+36,packed,index);variants.append(bytes(b))
 reader_cases=0
 for i,b in enumerate(roots+variants):
  reader=CompleteReader(b,None if i<3 else roots[-1])
  for bias in BIAS:
   for graph in [False,True]:reader.run_full(bias,graph);reader_cases+=1
 result={"experiment":"E011BK","status":"PASS_BOUNDED_ORIGINAL_PROFILE_CALLBACK_FORMATTER_AND_COMPLETE_READER_OWNED_INTERFACE",
 "base_commit":"f990cbca50b9652cbfbd9778fd11dd9b1dbc41e2","original_DLL_sha256":BH.FIXTURE.SHA,
 "source_files":audit,"anchors":anchors,"original_interface_constructor_full_returns":constructors,
 "original_callback_full_returns":callbacks,"independent_original_recursive_formatter_full_returns":formatters,
 "original_reader_full_returns":reader_cases,"typed_pinned_record_reader_full_returns_with_owned_context":24,
 "owned_record_reader_full_returns":48,"scope_rejections_before_execution":rejected,"memory_placements":4,
 "original_decimal_formatter_executed_without_stub":True,"original_indirect_reader_callback_executed":True,
 "owned_node_u64_bytes4_12_copied_exactly":True,"callback_invalid_index_or_null_table_zeroes_u64_only":True,
 "profile_grammar":"ancestor-first unsuppressed U16 decimal pairs joined by vertical bar",
 "profile_suppress_flag_scope":"owned node U32 at8: zero formats pair; nonzero suppresses pair",
 "formatter_final_byte127_zero_when_text_formatted":True,"callback_profile_clear_bytes":1,
 "all_heap_and_file_bytes_outside_exact_qualified_writes_preserved":True,
 "interface_nodes_and_source_context_unchanged_by_callback_and_reader":True,
 "callback_node_stride_160_not_32":True,"new_helper_stubs_added":False,
 "executed_fixture_stub_rvas":["0x11D0","0x11F0"],"allocations":0,
 "original_base_interface_slot0_callback_target_qualified":True,
 "actual_loader_subclass_or_interface_instance_selected":False,
 "owned_nodes_not_pinned_source_mode_table_authority":True,
 "captured_scalars_used_as_producer_inputs":False,"private_original_bytes_exported":False,
 "actual_profile_selection_closed":False,"exact_opened_tuning_filename_closed":False,
 "full_parent_metadata_stubs_removed":False,"whole_profile_materialization_closed":False,
 "whole_loader_alignment_policy_closed":False,"every_grid_member_validated":False,
 "cold_metadata_bridge_closed":False,"RS_count_offset_authority_closed":False,
 "complete_deterministic_bootstrap_closed":False,"WM16_retirement_closed":False,
 "Linux_optical_parity_closed":False,"native_rear_runtime_allowed":False,
 "production_C_changed":False,"new_kernel_build_performed":False,"runtime_actions_performed":False,
 "observer_armed":False,"new_camera_starts":0,"new_reboots":0}
 (HERE/"CALLBACK-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in result.items() if k not in ["source_files","anchors"]},indent=2))
if __name__=="__main__":main()
