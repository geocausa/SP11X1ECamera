from pathlib import Path
import importlib.util,json,collections,struct,hashlib
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;EX=HERE.parent
sp=importlib.util.spec_from_file_location("bo",EX/"e011bo-rear-aec-factory-registry/source-private.py");BO=importlib.util.module_from_spec(sp);sp.loader.exec_module(BO)
class Production(BO.Joined):
 def __init__(self,blob,bias):
  super().__init__(blob,bias);self.dispatches=0;self.AEC_pending=None;self.AEC_returns=0;self.lookup_calls=0
  self.n.u.hook_add(UC_HOOK_CODE,self.loader_watch)
 def bounds(self):
  u=self.n.u;allowed=bytearray(self.arena_size)
  for ptr,count in self.allocs:
   assert bytes(u.mem_read(ptr-32,32))==b"\xa5"*32 and bytes(u.mem_read(ptr+count,32))==b"\xa5"*32
   off=ptr-self.arena;allowed[off:off+count]=bytes([1])*count
  raw=bytes(u.mem_read(self.arena,self.arena_size));assert all(b==0xa5 for b,keep in zip(raw,allowed) if not keep)
  heap=bytes(u.mem_read(self.n.heap,0x30000));off=self.manager-self.n.heap
  assert heap[:off]==b"\xa5"*off and heap[off+5696:]==b"\xa5"*(0x30000-off-5696)
 def prefix(self):
  n=self.n;u=n.u;m=self.manager
  self.phase="factory_request"
  for i in range(8):u.reg_write(globals()["UC_ARM64_REG_X"+str(i)],0)
  u.reg_write(UC_ARM64_REG_X0,m);u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(n.base+0xd2bb0,n.end,count=5000000);assert u.reg_read(UC_ARM64_REG_PC)==n.end
  assert self.factory_registrations==565 and len(self.allocs)==1880 and len(self.released)==3
  assert self.readq(m)==n.base+0x1335288 and self.readq(m+0x13b0)==self.factory_proto
  self.bounds();self.phase="prefix"
  for i,v in enumerate([m,self.filebase,len(self.blob)]):u.reg_write(globals()["UC_ARM64_REG_X"+str(i)],v)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(n.base+0x6f22c8,n.base+0x6f3520,count=200000000);assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x6f3520
  self.nodes=self.readq(m+1072);assert self.readi(m+1080)==len(self.records)
  for sid,row in self.records.items():
   at=self.nodes+160*sid;assert bytes(u.mem_read(at,12))==struct.pack("<3I",*row[:3])
   assert self.readq(at+24)==(0 if row[3] in [sid,0xffffffff] else self.nodes+160*row[3])
  assert self.readq(m+16)==self.filebase+88 and bytes(u.mem_read(m+1104,8))==self.blob[32:40]
  self.bounds();self.file_before=bytes(u.mem_read(self.map,self.map_size))
 def loader_watch(self,u,pc,size,user):
  if self.phase!="loader":return
  r=pc-self.n.base
  if r==0xd2a20:self.lookup_calls+=1
  if r==0x6f35ac:self.dispatches+=1
  if r==0x123cc0:
   assert self.AEC_pending is None
   rr=u.reg_read(UC_ARM64_REG_X1);proto=u.reg_read(UC_ARM64_REG_X0)
   assert rr==self.root_reader and proto==self.factory_proto and proto not in self.released
   assert u.reg_read(UC_ARM64_REG_X2)==1 and u.reg_read(UC_ARM64_REG_LR)==self.n.base+0x6f35b0
   assert self.name_bytes(proto+16,32)==self.name_bytes(rr+12,32) and self.readq(proto+60)==self.readq(rr+52)==10
   self.AEC_pending={"alloc_count":len(self.allocs),"arena_before":bytes(u.mem_read(self.arena,self.arena_size)),
    "heap_before":bytes(u.mem_read(self.n.heap,0x30000)),"stack_context":bytes(u.mem_read(self.context,48)),
    "nodes_before":bytes(u.mem_read(self.nodes,len(self.records)*160)),
    "cursor_baseline":{sid:self.readq(self.table+sid*224+216) for sid in self.sy}}
  elif r==0x6f35b0 and self.AEC_pending is not None:
   self.verify_actual_AEC();self.AEC_pending=None;self.AEC_returns+=1
 def verify_actual_AEC(self):
  n=self.n;u=n.u;rr=self.root_reader;ctx=self.context;p=self.AEC_pending
  alloc_count=p["alloc_count"];arena_before=p["arena_before"];heap_before=p["heap_before"]
  stack_context=p["stack_context"];nodes_before=p["nodes_before"];name=self.name_bytes(rr+12,32)
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
  for sid in expected_cursors:assert p["cursor_baseline"][sid]==0
  for sid in self.sy:assert self.readq(self.table+sid*224+216)==expected_cursors.get(sid,p["cursor_baseline"][sid])
  # All pre-existing allocation bytes outside reader cursor fields must survive.
  expect=bytearray(arena_before)
  for sid in self.sy:
   ix=self.table+sid*224+216-self.arena;expect[ix:ix+8]=struct.pack("<Q",expected_cursors.get(sid,p["cursor_baseline"][sid]))
  for ptr,size in new:
   ix=ptr-self.arena;expect[ix:ix+size]=bytes(u.mem_read(ptr,size))
  assert bytes(u.mem_read(self.arena,self.arena_size))==expect
  assert bytes(u.mem_read(self.map,self.map_size))==self.file_before
 def run_full(self):
  self.build();self.phase="loader";u=self.n.u
  u.emu_start(self.n.base+0x6f3524,self.n.end,count=200000000)
  assert u.reg_read(UC_ARM64_REG_PC)==self.n.end and u.reg_read(UC_ARM64_REG_X0)==1
  assert self.AEC_returns==1 and self.AEC_pending is None
  assert self.dispatches==self.lookup_calls and self.dispatches>0
  assert bytes(u.mem_read(self.map,self.map_size))==self.file_before
  self.bounds()
  return {"placement":self.bias,"original_production_factory_full_returns":1,"source_reader_full_returns":self.returns,
   "original_loader_full_returns":1,"original_loader_success_boolean":True,"original_lookup_calls":self.lookup_calls,
   "original_module_dispatches":self.dispatches,"actual_AEC_parent_full_returns":self.AEC_returns,
   "actual_AEC_caller_return_RVA":"0x6F35B0","actual_AEC_request_from_original_registry":True,
   "actual_AEC_alignment":1,"qualified_revision_grid_histogram_BFW_fields_pass":True,
   "AEC_preexisting_non_cursor_allocation_bytes_preserved":True,"source_map_and_allocation_guards_pass":True,
   "total_owned_allocations":len(self.allocs),"total_owned_releases":len(self.released)}
def main():
 results=[];name,sha=BO.BM.BL.BH.FIXTURE.AV.FILES[-1]
 blob=(BO.BM.BL.BH.FIXTURE.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
 for bias in [0,1]:
  f=Production(blob,bias);r=f.run_full();results.append({"source_sha256":sha,**r});print(json.dumps(results[-1]),flush=True)
 result={"experiment":"E011BO","status":"PASS_BOUNDED_REAR_SPECIFIC_PRODUCTION_LOADER_FULL_RETURN_AND_ACTUAL_AEC_SOURCE_FIELDS",
  "base_commit":"1606909a7a5c31fb800aebfbb332e6f29ceef4fe","source_cases":results,"original_loader_full_returns":len(results),
  "original_reader_full_returns":sum(r["source_reader_full_returns"] for r in results),
  "actual_AEC_parent_full_returns":sum(r["actual_AEC_parent_full_returns"] for r in results),
  "whole_camera_stack_parity_closed":False,"all_dispatched_module_fields_validated":False,
  "all_profile_selection_and_node_container_policy_closed":False,"larger_rear_default_loader_return_qualified":False,
  "source_context_lifetime_after_loader_return_qualified":False,"factory_destruction_and_released_storage_reuse_qualified":False,
  "opened_filesystem_filename_policy_closed":False,"platform_path_qualified":False,
  "retained_shims":["0x11D0","0x11F0","0xCAE740","0xF5E600","0xCAE730"],
  "originals_exported":False,"captured_scalars_as_producer_inputs":False,
  "new_camera_starts":0,"new_reboots":0,"native_rear_runtime_allowed":False}
 (HERE/"LOADER-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":result["status"],"loader_returns":len(results)}),flush=True)
if __name__=="__main__":main()
