#!/usr/bin/env python3
"""E011BM: original symbol builder/context and bounded AEC metadata join on SP11."""
from pathlib import Path
import importlib.util,json,struct,hashlib,collections
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;EX=HERE.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
BL=load("bm_source_profile",EX/"e011bl-rear-aec-source-profile/source-private.py")
BG=load("bm_siblings",EX/"e011bg-rear-aec-bfw-materialization/source-private.py")
class Joined(BL.Loader):
 def __init__(self,blob,bias):
  super().__init__(blob,bias)
  _,_,self.wire,self.info=BG.source(blob)
  self.phase="prefix";self.pending=None;self.returns=0;self.seen=set();self.helper_counts=collections.Counter()
  self.n.u.hook_add(UC_HOOK_CODE,self.watch)
 def readq(self,ptr):return struct.unpack("<Q",self.n.u.mem_read(ptr,8))[0]
 def readi(self,ptr):return struct.unpack("<I",self.n.u.mem_read(ptr,4))[0]
 def watch(self,u,a,size,user):
  r=a-self.n.base
  if r in [0x6f45d8,0x6f4ac0,0xf5df00]:self.helper_counts[r]+=1
  if self.phase=="builder":
   if r==0x6f3524:u.emu_stop();return
   if r==0x6f4e84:
    assert self.pending is None
    obj=u.reg_read(UC_ARM64_REG_X0);cursor=u.reg_read(UC_ARM64_REG_X3);off=self.readq(cursor)
    assert u.reg_read(UC_ARM64_REG_X1)==self.filebase and u.reg_read(UC_ARM64_REG_X2)==len(self.blob)
    assert u.reg_read(UC_ARM64_REG_X4)==self.h["sections"][1]["offset"]
    assert u.reg_read(UC_ARM64_REG_X5)==self.manager and u.reg_read(UC_ARM64_REG_X6)==1
    assert self.arena<=obj and obj+224<=self.arena+self.arena_size
    raw=self.blob[off:off+56];sid=struct.unpack_from("<I",raw)[0]
    assert sid in self.sy and sid not in self.seen
    self.pending=(obj,cursor,off,raw,bytes(u.mem_read(obj,224)),sid)
   elif r==0x6f4e88:
    assert self.pending is not None
    obj,cursor,off,raw,before,sid=self.pending;selector=struct.unpack_from("<I",raw,44)[0]
    rel=struct.unpack_from("<I",raw,48)[0];expected=bytearray(before)
    fields=[(8,raw[:4]),(12,raw[4:36]+b"\0"),(52,raw[36:44]),
      (60,struct.pack("<2I",*self.records[selector][1:3]) if selector in self.records else bytes(8)),
      (68,raw[44:48]),(200,raw[52:56]),(208,struct.pack("<Q",self.filebase+self.h["sections"][1]["offset"]+rel))]
    for at,value in fields:expected[at:at+len(value)]=value
    initial=bytearray(before[72:200]);initial[0]=0
    expected[72:200]=BL.profile_buf(initial,self.records,selector) if selector in self.records else initial
    assert bytes(u.mem_read(obj,224))==expected,"original reader field/guard mismatch"
    assert self.readq(cursor)==off+56
    ctx=self.readq(obj);assert self.n.stack<=ctx and ctx+48<=self.n.stack+0x10000
    if sid==self.info["root_symbol_id"]:self.root_reader=obj;self.context=ctx
    self.seen.add(sid);self.returns+=1;self.pending=None
 def invoke_low(self,rva,args):
  u=self.n.u;n=self.n
  for i,v in enumerate(args):u.reg_write(globals()["UC_ARM64_REG_X"+str(i)],v)
  # Preserve the original loader's live upper stack frame/context.
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xd000);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(n.base+rva,n.end,count=1000000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end
 def build(self):
  self.prefix();n=self.n;u=n.u;self.phase="builder"
  u.emu_start(n.base+0x6f3520,n.end,count=200000000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x6f3524 and self.pending is None
  assert self.seen==set(self.sy) and self.returns==len(self.sy)
  ctx=self.context;table=self.readq(ctx+40)
  assert self.readi(ctx+24)==max(self.sy)
  assert self.readq(ctx)==self.filebase+88 and bytes(u.mem_read(ctx+8,8))==self.blob[32:40]
  assert self.root_reader==table+self.info["root_symbol_id"]*224
  for sid,r in self.sy.items():
   rr=table+sid*224;assert self.readq(rr)==ctx and self.readi(rr+8)==sid
   assert self.readi(rr+200)==r["data_bytes"]
   assert self.readq(rr+208)==self.filebase+r["data_abs_offset"] and self.readq(rr+216)==0
  assert bytes(u.mem_read(self.map,self.map_size))==self.file_before
  self.table=table;self.phase="joined";self.bounds()
 def name_bytes(self,ptr,limit):return bytes(self.n.u.mem_read(ptr,limit+1)).split(b"\0")[0]
 def metadata(self,module,reader,major,vtable=0x133b770):
  u=self.n.u;name=self.name_bytes(reader+12,32);profile=self.name_bytes(reader+72,127)
  filename=self.name_bytes(self.readq(self.context),128)
  nameptr=self.readq(module+8)
  assert self.readq(module)==self.n.base+vtable
  assert bytes(u.mem_read(nameptr,len(name)+1))==name+b"\0"
  assert bytes(u.mem_read(module+16,len(name)+1))==name+b"\0"
  assert self.readi(module+56)==(self.readi(reader+8) if vtable==0x1335598 else 0)
  assert self.readq(module+60)==major and self.readi(module+68)==self.readi(reader+68)
  assert self.readq(module+72)==self.readq(reader+60)
  assert bytes(u.mem_read(module+80,len(profile[:127])+1))==profile[:127]+b"\0"
  assert bytes(u.mem_read(module+208,len(filename[:64])+1))==filename[:64]+b"\0"
  assert bytes(u.mem_read(module+280,8))==bytes(8)
  return name,profile,filename
 def join(self):
  n=self.n;u=n.u;rr=self.root_reader;ctx=self.context
  proto=n.heap+0x1000+self.bias;proto_before=bytes(u.mem_read(proto,384))
  all_heap=bytes(u.mem_read(n.heap,0x30000));stack_context=bytes(u.mem_read(ctx,48))
  self.invoke_low(0x6f45d8,[proto,rr+12,self.readq(rr+52),self.readi(rr+68),self.readq(rr+60),rr+72,self.readq(ctx)])
  name,profile,filename=self.metadata(proto,rr,self.readq(rr+52))
  expected=bytearray(all_heap);off=proto-n.heap;raw=bytes(u.mem_read(proto,384))
  for at,size in [(0,80),(80,len(profile[:127])+1),(208,len(filename[:64])+1),(280,8)]:
   expected[off+at:off+at+size]=raw[at:at+size]
  assert bytes(u.mem_read(n.heap,0x30000))==expected
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
  u.mem_write(proto,proto_before);self.bounds()
  assert set(self.stubs)<=set([0x11d0,0x11f0,0xcae740,0xf5e600])
  return {"symbol_reader_full_returns":self.returns,"source_mode_records":len(self.records),
    "original_symbol_table_builder_returns":1,"original_AEC_parent_full_returns":1,
    "original_metadata_constructor_returns":2,"original_gate_rejections":negative_returns,
    "parent_allocations":len(new),"histogram_entries":count,"grids":4,"BFW_records":1,
    "original_stack_context_qualified":True,"all_preexisting_non_cursor_allocation_bytes_preserved":True}
def main():
 results=[]
 for name,sha in BL.BH.FIXTURE.AV.FILES[1:]:
  blob=(BL.BH.FIXTURE.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  for bias in [0,1]:
   f=Joined(blob,bias);f.build();r=f.join()
   results.append({"source_sha256":sha,"placement":bias,**r});print(json.dumps(results[-1]),flush=True)
 summary={"experiment":"E011BM","status":"PASS_BOUNDED_ORIGINAL_SYMBOL_TABLE_CONTEXT_AND_SOURCE_REQUEST_AEC_JOIN",
  "base_commit":"e97dade62f4a816a9de015b726448845f021a359","source_cases":results,
  "symbol_reader_full_returns":sum(r["symbol_reader_full_returns"] for r in results),
  "original_symbol_table_builder_returns":4,"original_AEC_parent_full_returns":4,
  "original_metadata_constructor_returns":8,"original_name_or_version_gate_rejections":8,
  "actual_original_loader_stack_context_used":True,"owned_source_backed_request_descriptor":True,
  "actual_factory_request_policy_closed":False,"entire_loader_full_return_claimed":False,
  "opened_filesystem_filename_authority_closed":False,"header_module_name_used_for_metadata":True,
  "parent_metadata_name_comparison_stubs_removed":True,"platform_path_qualified":False,
  "every_root_or_grid_field_validated":False,"all_runtime_padding_zero_policy_closed":False,"opaque_embedded_name_tail_independently_derived":False,"whole_camera_stack_parity_closed":False,
  "retained_shims":["0x11D0","0x11F0","0xCAE740","0xF5E600"],
  "original_DLL_sha256":BL.BH.FIXTURE.SHA,"originals_exported":False,"captured_scalars_as_producer_inputs":False,
  "production_C_changed":False,"kernel_build_performed":False,"camera_starts":0,"reboots":0,
  "observer_armed":False,"native_rear_runtime_allowed":False}
 (HERE/"CONTEXT-JOIN-SAFE.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":summary["status"],"symbol_reader_full_returns":summary["symbol_reader_full_returns"],"parent_returns":4}),flush=True)
if __name__=="__main__":main()
