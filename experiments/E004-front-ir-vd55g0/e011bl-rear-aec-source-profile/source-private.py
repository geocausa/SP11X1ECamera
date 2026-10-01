#!/usr/bin/env python3
"""E011BL: original loader-to-source-profile bridge, all originals stay on SP11."""
from pathlib import Path
import importlib.util,struct,collections,hashlib,json
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;EX=HERE.parent
s=importlib.util.spec_from_file_location("bl_callback",EX/"e011bk-rear-aec-profile-callback/source-private.py")
BK=importlib.util.module_from_spec(s);s.loader.exec_module(BK);BH=BK.BH
Native=BH.FIXTURE.load("bl_native",EX/"e011ai-rear-neutral-scalar-full-integration/native-private.py").Native
def describe(blob):
 h,sy,_,info=BH.FIXTURE.source(blob);sec=h["sections"][2]
 assert sec["size"]%20==0
 records={}
 for off in range(sec["offset"],sec["end"],20):
  row=struct.unpack_from("<5I",blob,off);sid=row[0]
  assert sid not in records;records[sid]=row
 assert set(records)==set(range(len(records)))
 for sid,row in records.items():
  assert row[3] in records or row[3]==0xffffffff
  seen=set();cur=sid
  while cur is not None:
   assert cur not in seen;seen.add(cur)
   p=records[cur][3];cur=None if p in [cur,0xffffffff] else p
 return h,sy,info,records
def text(records,sid):
 row=records[sid];p=row[3]
 before="" if p in [sid,0xffffffff] else text(records,p)
 part="" if row[2] else str(row[1]&65535)+"."+str(row[1]>>16)
 return "|".join(x for x in [before,part] if x)
def profile_buf(initial,records,sid):
 out=bytearray(initial);out[0]=0;value=text(records,sid).encode()
 assert len(value)<=127
 if value:out[:len(value)+1]=value+b"\0";out[127]=0
 return bytes(out)
class Loader:
 def __init__(self,blob,bias):
  self.blob=blob;self.h,self.sy,self.info,self.records=describe(blob)
  self.bias=bias;self.n=Native();n=self.n;u=n.u
  self.arena=0x78000000;self.arena_size=0x2000000;u.mem_map(self.arena,self.arena_size)
  self.map=0x76000000;self.filebase=self.map+bias;self.map_size=((len(blob)+0x10000+4095)//4096)*4096
  u.mem_map(self.map,self.map_size);u.mem_write(self.map,bytes([0xa5])*self.map_size);u.mem_write(self.filebase,blob)
  u.mem_write(n.heap,bytes([0xa5])*0x30000);u.mem_write(n.stack,bytes(0x10000))
  u.mem_write(self.arena,bytes([0xa5])*self.arena_size)
  self.next=self.arena+0x4000+bias;self.allocs=[];self.stubs=collections.Counter();self.trace=collections.Counter()
  self.manager=n.heap+0x4000+bias;u.hook_add(UC_HOOK_CODE,self.hook)
 def hook(self,u,a,size,user):
  n=self.n;r=a-n.base
  if r in [0x6f31b4,0x6f3420,0x6f1bf0,0x6f3b50,0x6f2208,0xcb6300,0x6f4a98]:
   self.trace[r]+=1
  if r in [0x11d0,0x11f0,0xcae740,0xf5e600]:
   self.stubs[r]+=1
   if r==0xcae740:
    count=u.reg_read(UC_ARM64_REG_X0);assert 0<count<0x1800000
    out=self.next+32;self.next=out+((count+31)&~31)+32
    assert self.next<self.arena+self.arena_size
    self.allocs.append((out,count));u.reg_write(UC_ARM64_REG_X0,out)
   elif r==0xf5e600:
    out=u.reg_read(UC_ARM64_REG_X0);count=u.reg_read(UC_ARM64_REG_X2)
    assert any(x<=out and out+count<=x+c for x,c in self.allocs)
    u.mem_write(out,bytes([u.reg_read(UC_ARM64_REG_X1)&255])*count)
   u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
 def invoke(self,rva,args):
  n=self.n;u=n.u
  for i,v in enumerate(args):u.reg_write(globals()["UC_ARM64_REG_X"+str(i)],v)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(n.base+rva,n.end,count=200000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end
 def bounds(self):
  u=self.n.u;allowed=bytearray(self.arena_size)
  for ptr,count in self.allocs:
   assert bytes(u.mem_read(ptr-32,32))==bytes([0xa5])*32
   assert bytes(u.mem_read(ptr+count,32))==bytes([0xa5])*32
   off=ptr-self.arena;allowed[off:off+count]=bytes([1])*count
  raw=bytes(u.mem_read(self.arena,self.arena_size))
  assert all(b==0xa5 for b,keep in zip(raw,allowed) if not keep)
  heap=bytes(u.mem_read(self.n.heap,0x30000));off=self.manager-self.n.heap
  assert heap[:off]==bytes([0xa5])*off and heap[off+1112:]==bytes([0xa5])*(0x30000-off-1112)
 def prefix(self):
  n=self.n;u=n.u;m=self.manager
  self.invoke(0x6f3d08,[m])
  for i,v in enumerate([m,self.filebase,len(self.blob)]):u.reg_write(globals()["UC_ARM64_REG_X"+str(i)],v)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(n.base+0x6f22c8,n.base+0x6f3520,count=200000000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x6f3520
  assert self.trace[0x6f31b4]==len(self.records) and self.trace[0x6f1bf0]==len(self.records)
  self.nodes=struct.unpack("<Q",u.mem_read(m+1072,8))[0]
  assert self.nodes==self.allocs[0][0]+8
  assert self.allocs[0][1]==len(self.records)*160+8
  assert struct.unpack("<I",u.mem_read(m+1080,4))[0]==len(self.records)
  for sid,row in self.records.items():
   at=self.nodes+160*sid
   assert bytes(u.mem_read(at,12))==struct.pack("<3I",*row[:3])
   parent=row[3];expected=0 if parent in [sid,0xffffffff] else self.nodes+160*parent
   assert struct.unpack("<Q",u.mem_read(at+24,8))[0]==expected
  assert struct.unpack("<Q",u.mem_read(m+16,8))[0]==self.filebase+88
  assert bytes(u.mem_read(m+1104,8))==self.blob[32:40]
  self.bounds()
  self.file_before=bytes(u.mem_read(self.map,self.map_size))
  assert self.file_before[:self.bias]==bytes([0xa5])*self.bias
  assert self.file_before[self.bias+len(self.blob):]==bytes([0xa5])*(self.map_size-self.bias-len(self.blob))
  assert self.file_before[self.bias:self.bias+len(self.blob)]==self.blob
 def callbacks(self):
  n=self.n;u=n.u;arena_before=bytes(u.mem_read(self.arena,self.arena_size))
  h_before=bytes(u.mem_read(n.heap,0x30000));count=0
  root=self.sy[self.info["root_symbol_id"]];index=struct.unpack_from("<I",self.blob,root["record_offset"]+44)[0]
  chosen=sorted(set([0,index,len(self.records)-1]+list(range(min(10,len(self.records))))))
  for sid in chosen+[0x80000000,0xffffffff,len(self.records)]:
   out=n.heap+0x1000+self.bias;dest=n.heap+0x1100+self.bias
   u.mem_write(out,bytes([0xa5])*8);u.mem_write(dest,bytes([0xa5])*128)
   before=bytes(u.mem_read(n.heap,0x30000));self.invoke(0x6f3b50,[self.manager,sid,out,dest])
   expect=bytearray(before);ix=out-n.heap
   expect[ix:ix+8]=struct.pack("<2I",self.records[sid][1],self.records[sid][2]) if sid in self.records else bytes(8)
   if sid in self.records:
    ix=dest-n.heap;expect[ix:ix+128]=profile_buf(before[ix:ix+128],self.records,sid)
   assert bytes(u.mem_read(n.heap,0x30000))==expect;count+=1
  assert bytes(u.mem_read(self.arena,self.arena_size))==arena_before
  assert bytes(u.mem_read(self.map,self.map_size))==self.file_before
  u.mem_write(n.heap,h_before)
  return count
 def first_reader(self):
  n=self.n;u=n.u
  # Continue the preserved original caller state? callbacks used their own stack,
  # so prefix callers are snapshotted and restored before this continuation.
  for reg,value in self.saved_regs.items():u.reg_write(reg,value)
  u.mem_write(n.stack,self.saved_stack)
  u.emu_start(n.base+0x6f3520,n.base+0x6f4e84,count=4000000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x6f4e84
  obj=u.reg_read(UC_ARM64_REG_X0);cursor=u.reg_read(UC_ARM64_REG_X3)
  assert u.reg_read(UC_ARM64_REG_X1)==self.filebase and u.reg_read(UC_ARM64_REG_X2)==len(self.blob)
  assert u.reg_read(UC_ARM64_REG_X4)==self.h["sections"][1]["offset"]
  assert u.reg_read(UC_ARM64_REG_X5)==self.manager and u.reg_read(UC_ARM64_REG_X6)==1
  off=struct.unpack("<Q",u.mem_read(cursor,8))[0];record=self.blob[off:off+56]
  assert off==self.h["sections"][0]["offset"]
  before=bytes(u.mem_read(self.arena,self.arena_size));heap_before=bytes(u.mem_read(n.heap,0x30000))
  u.emu_start(n.base+0x6f4e84,n.base+0x6f4e88,count=200000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x6f4e88
  sid=struct.unpack_from("<I",record,44)[0];rel=struct.unpack_from("<I",record,48)[0]
  expected=bytearray(before)
  fields=[(8,record[:4]),(12,record[4:36]+b"\0"),(52,record[36:44]),
  (60,struct.pack("<2I",self.records[sid][1],self.records[sid][2]) if sid in self.records else bytes(8)),
  (68,record[44:48]),(200,record[52:56]),(208,struct.pack("<Q",self.filebase+self.h["sections"][1]["offset"]+rel))]
  for at,value in fields:
   ix=obj-self.arena+at;expected[ix:ix+len(value)]=value
  ix=obj-self.arena+72;initial=bytearray(before[ix:ix+128]);initial[0]=0
  expected[ix:ix+128]=profile_buf(initial,self.records,sid) if sid in self.records else initial
  assert bytes(u.mem_read(self.arena,self.arena_size))==expected
  assert bytes(u.mem_read(n.heap,0x30000))==heap_before
  assert struct.unpack("<Q",u.mem_read(cursor,8))[0]==off+56
  assert bytes(u.mem_read(self.map,self.map_size))==self.file_before
  # Original table builder finishes context ownership after the constructor.
  u.emu_start(n.base+0x6f4e88,n.base+0x6f4e84,count=200000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x6f4e84
  return struct.unpack("<Q",u.mem_read(obj,8))[0]==self.manager+16
 def run(self):
  self.prefix();n=self.n;u=n.u
  self.saved_regs={globals()["UC_ARM64_REG_X"+str(i)]:u.reg_read(globals()["UC_ARM64_REG_X"+str(i)]) for i in range(31)}
  self.saved_regs.update({UC_ARM64_REG_SP:u.reg_read(UC_ARM64_REG_SP),UC_ARM64_REG_PC:u.reg_read(UC_ARM64_REG_PC)})
  self.saved_stack=bytes(u.mem_read(n.stack,0x10000))
  c=self.callbacks();ctx=self.first_reader()
  assert set(self.stubs)<=set([0x11d0,0x11f0,0xcae740,0xf5e600])
  return {"nodes":len(self.records),"callback_returns":c,"actual_reader_full_returns":1,
  "post_return_reader_context_manager_plus16":ctx,"original_reader_alignment":1,
  "source_records_ID_indexed_not_ordinal":True,"allocation_guards_pass":True}
def main():
 results=[];prefixes=callbacks=readers=nodes=0
 for name,sha in BH.FIXTURE.AV.FILES[1:]:
  blob=(BH.FIXTURE.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  for bias in [0,1]:
   f=Loader(blob,bias);r=f.run();prefixes+=1;callbacks+=r["callback_returns"];readers+=1;nodes+=r["nodes"]
   item={"path":name,"sha256":sha,"placement":bias,**r};results.append(item)
   print(json.dumps({"completed_source_sha256":sha,"placement":bias,**r}),flush=True)
 result={"experiment":"E011BL","status":"PASS_BOUNDED_ORIGINAL_LOADER_SOURCE_PROFILE_AND_ACTUAL_READER_CALLER",
 "base_commit":"7922b28b35df8166028edb760497699bd226569f","original_DLL_sha256":BH.FIXTURE.SHA,
 "source_cases":results,"source_scope":"two rear files; platform extension record path remains open","original_loader_prefixes":prefixes,"source_mode_records_verified":nodes,
 "original_source_profile_callback_returns":callbacks,"actual_table_builder_reader_full_returns":readers,
 "source_wire_stride":20,"runtime_node_stride":160,"source_records_indexed_by_serialized_ID":True,
 "source_wire0_12_to_runtime0_12_exact":True,"source_wire12_to_parent_pointer24_exact_except_self_or_sentinel":True,
 "loader_arg_x1_is_file_base_x2_is_byte_length":True,"original_full_header_and_mode_loops_executed":True,
 "original_loader_stopped_before_symbol_table_builder_at":"0x6F3520",
 "actual_reader_call_site":"0x6F4E84","actual_reader_indirect_profile_callback":"0x6F4A98",
 "actual_reader_alignment":1,"source_context_first_pointer_is_header_module_name_at88":True,
 "source_context_state_bytes24_32_policy_closed":False,"header_version_bytes1104_1112_match_wire32_40":True,
 "earlier_filename_argument_label_not_opened_filesystem_path_authority":True,
 "profile_nodes_no_longer_owned_numeric_substitutes":True,
 "captured_scalars_used_as_producer_inputs":False,"private_original_bytes_exported":False,
 "source_file_maps_and_padding_preserved":True,"allocation_canaries_and_outside_allocation_bytes_preserved":True,
 "callback_and_reader_exact_memory_guards_pass":True,
 "retained_fixture_shims":["0x11D0","0x11F0","0xCAE740","0xF5E600"],
 "allocator_shim_capacity_expanded_in_owned_arena":True,"no_parser_callback_or_formatter_shim":True,
 "all_node_strings_and_child_containers_independently_validated":False,
 "complete_loader_return_claimed":False,"full_parent_metadata_stubs_removed":False,
 "exact_opened_tuning_filename_closed":False,"whole_profile_materialization_closed":False,
 "cold_metadata_bridge_closed":False,"RS_count_offset_authority_closed":False,
 "complete_deterministic_bootstrap_closed":False,"WM16_retirement_closed":False,
 "Linux_optical_parity_closed":False,"production_C_changed":False,"new_kernel_build_performed":False,
 "new_camera_starts":0,"new_reboots":0,"observer_armed":False,"native_rear_runtime_allowed":False}
 (HERE/"SOURCE-PROFILE-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":result["status"],"prefixes":prefixes,"nodes":nodes,"callbacks":callbacks,"readers":readers}),flush=True)
if __name__=="__main__":main()
