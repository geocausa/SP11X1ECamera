#!/usr/bin/env python3
"""Original AEC parent-to-first-grid prefix in owned memory on the same SP11."""
from pathlib import Path
import importlib.util,hashlib,json,random,struct
import pefile,capstone
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
import unicorn.arm64_const as arm
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent
SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
AY=load("az_schema",EX/"e011ay-rear-aec-cache-construction/scalar-private.py")
DEC=AY.DEC;AV=AY.AV
DLL=ROOT.parents[1]/"00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"
def source(blob):
 wire,info=AY.source(blob)
 h=DEC.parse_header(blob);sy,_=DEC.parse_symbol_table(blob,h["sections"][0],h["sections"][1])
 return h,sy,wire,info
def source_facts():
 blob=DLL.read_bytes();assert hashlib.sha256(blob).hexdigest()==SHA
 pe=pefile.PE(data=blob);base=pe.OPTIONAL_HEADER.ImageBase
 c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);c.detail=True
 def ins(r):return next(c.disasm(pe.get_data(r,4),base+r))
 def mem(r,op,reg,owner,offset):
  i=ins(r);assert i.mnemonic==op and c.reg_name(i.operands[0].reg)==reg
  m=i.operands[-1];assert m.type==capstone.arm64.ARM64_OP_MEM
  assert (c.reg_name(m.mem.base),m.mem.disp)==(owner,offset)
 mem(0x6f4f88,"ldr","x10","x1",0xd8)
 mem(0x6f4f90,"ldr","w12","x1",0xc8)
 mem(0x6f4fa4,"ldr","x8","x1",0xd0)
 mem(0x6f4fc8,"ldr","w8","x9",0x18)
 mem(0x6f4fdc,"ldr","x9","x9",0x28)
 i=ins(0x6f4fe0);assert i.mnemonic=="mov" and i.operands[1].imm==224
 mem(0x123fa4,"str","x27","x20",0x38)
 mem(0x124024,"ldr","x8","x20",0x38)
 for r,target in [(0x124034,0x123550),(0x123814,0xf5d480)]:
  i=ins(r);assert i.mnemonic=="bl" and i.operands[0].imm==base+target
 i=ins(0x124030)
 assert i.mnemonic=="umaddl" and [c.reg_name(o.reg) for o in i.operands]==["x1","w21","w22","x8"]
class ParentPrefix:
 def __init__(self,blob):
  self.h,self.sy,self.wire,self.info=source(blob)
  self.n=load("az_image",EX/"e011ai-rear-neutral-scalar-full-integration/native-private.py").Native()
  self.table_map=0x72000000;self.data_map=0x74000000
  self.table_size=((max(self.sy)+1)*224+0x2000+4095)&~4095
  self.n.u.mem_map(self.table_map,self.table_size)
  obj=self.h["sections"][1]
  self.data_size=(obj["size"]+0x2000+4095)&~4095
  self.n.u.mem_map(self.data_map,self.data_size)
  self.data=blob[obj["offset"]:obj["end"]]
  self.allocs=[];self.symbols=[];self.calls=[];self.copies=[]
  self.parent_context=None;self.stub_counts={};self.redzones=[]
  def returned(value=None):
   u=self.n.u
   if value is not None:u.reg_write(UC_ARM64_REG_X0,value)
   u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
  def hook(uc,pc,size,_):
   n=self.n;u=n.u;r=pc-n.base
   if r in [0x11d0,0x11f0,0x6f4ac0,0x6f45d8,0xf5df00,0xdb3a0,0xcae740,0xf5e600]:
    self.stub_counts[hex(r)]=self.stub_counts.get(hex(r),0)+1
   if r in [0x11d0,0x11f0,0x6f4ac0,0x6f45d8]:returned();return
   if r==0xf5df00:returned(0);return
   # Revision metadata is excluded. No grid scalar reader or symbol resolver is stubbed.
   if r==0xdb3a0:returned(1);return
   if r==0xcae740:
    count=u.reg_read(UC_ARM64_REG_X0);assert 0<count<0x10000
    out=self.next_alloc+32;self.next_alloc=out+((count+31)&~31)+32
    assert self.next_alloc<n.heap+0x30000
    for at in [out-32,out+count]:
     u.mem_write(at,bytes([0xa5])*32);self.redzones.append(at)
    self.allocs.append((out,count));returned(out);return
   if r==0xf5e600:
    out=u.reg_read(UC_ARM64_REG_X0);count=u.reg_read(UC_ARM64_REG_X2)
    assert any(start<=out and out+count<=start+length for start,length in self.allocs)
    u.mem_write(out,bytes([u.reg_read(UC_ARM64_REG_X1)&255])*count);returned(out);return
   if r==0x6f4f88:
    rr=u.reg_read(UC_ARM64_REG_X1)
    cursor=struct.unpack("<Q",u.mem_read(rr+0xd8,8))[0]
    src=struct.unpack("<Q",u.mem_read(rr+0xd0,8))[0]
    sid=struct.unpack("<I",u.mem_read(src+cursor,4))[0]
    self.symbols.append((u.reg_read(UC_ARM64_REG_LR)-n.base-4,(rr-self.table)//224,cursor,sid))
   if r==0x124034:
    self.parent_context={getattr(arm,"UC_ARM64_REG_X"+str(i)):u.reg_read(getattr(arm,"UC_ARM64_REG_X"+str(i))) for i in range(29)}
    rr=u.reg_read(UC_ARM64_REG_X0);out=u.reg_read(UC_ARM64_REG_X1)
    self.calls.append((rr,out,u.reg_read(UC_ARM64_REG_W22)))
   if r==0xf5d480:
    self.copies.append((u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2)))
  self.n.u.hook_add(UC_HOOK_CODE,hook)
 def run(self,wire,bias,check_stride=False):
  n=self.n;u=n.u
  u.mem_write(n.heap,bytes(0x30000));u.mem_write(n.stack,bytes(0x10000))
  self.allocs.clear();self.symbols.clear();self.calls.clear();self.copies.clear();self.stub_counts.clear();self.redzones.clear()
  self.table=self.table_map+bias;self.datas=self.data_map+bias;self.file=n.heap+0x800+bias
  self.next_alloc=n.heap+0x18000+bias
  u.mem_write(self.datas,self.data)
  buf=bytearray(self.table_size-bias)
  for sid,r in self.sy.items():
   at=sid*224
   struct.pack_into("<Q",buf,at,self.file)
   struct.pack_into("<I",buf,at+0xc8,r["data_bytes"])
   struct.pack_into("<Q",buf,at+0xd0,self.datas+r["data_offset"])
  u.mem_write(self.table,bytes(buf))
  u.mem_write(self.file+0x18,struct.pack("<I",max(self.sy)))
  u.mem_write(self.file+0x28,struct.pack("<Q",self.table))
  grid=self.sy[self.info["grid_symbol_id"]]
  src=self.datas+grid["data_offset"];u.mem_write(src,wire)
  root_sid=self.info["root_symbol_id"];root=self.sy[root_sid]
  parent_wire=self.data[root["data_offset"]:root["data_offset"]+root["data_bytes"]]
  reader=self.table+root_sid*224
  for reg,val in [(UC_ARM64_REG_X0,self.file),(UC_ARM64_REG_X1,reader),
                  (UC_ARM64_REG_X2,0),(UC_ARM64_REG_SP,n.stack+0xf000),(UC_ARM64_REG_LR,n.end)]:
   u.reg_write(reg,val)
  u.emu_start(n.base+0x123cc0,n.base+0x123818,count=100000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x123818
  assert [length for _,length in self.allocs]==[384,480]
  module,array=self.allocs[0][0],self.allocs[1][0];payload=module+0x120
  assert self.parent_context[UC_ARM64_REG_X20]==payload
  assert self.symbols==[(0x123f00,root_sid,16,struct.unpack_from("<I",parent_wire,16)[0]),
                        (0x123f5c,root_sid,28,self.info["grid_symbol_id"])]
  assert self.calls==[(self.table+self.info["grid_symbol_id"]*224,array,120)]
  assert struct.unpack("<I",u.mem_read(payload+0x2c,4))[0]==4
  assert struct.unpack("<Q",u.mem_read(payload+0x38,8))[0]==array,{"actual_parent_base_relative_module":self.parent_context[UC_ARM64_REG_X20]-module}
  assert self.copies==[(array+20,src+20,12)]
  result=bytes(u.mem_read(array+20,12));assert result==wire[20:32]
  assert all(bytes(u.mem_read(at,32))==bytes([0xa5])*32 for at in self.redzones)
  assert bytes(u.mem_read(src,len(wire)))==wire
  assert bytes(u.mem_read(self.datas+root["data_offset"],root["data_bytes"]))==parent_wire
  stride_cases=0
  if check_stride:
   before=bytes(u.mem_read(n.heap,0x30000))
   for index in range(4):
    for reg,val in self.parent_context.items():u.reg_write(reg,val)
    u.reg_write(UC_ARM64_REG_W21,index)
    u.emu_start(n.base+0x124024,n.base+0x124034,count=4)
    assert u.reg_read(UC_ARM64_REG_X1)==array+120*index
    assert bytes(u.mem_read(n.heap,0x30000))==before
    stride_cases+=1
  return result,stride_cases
 def symbol_negatives(self):
  n=self.n;u=n.u;probe=n.heap+0x2000;wire=n.heap+0x10000
  cases=[(self.info["grid_symbol_id"],4,self.info["grid_symbol_id"]),
         (self.info["root_symbol_id"],4,self.info["root_symbol_id"]),
         (0,4,0),(max(self.sy)+1,4,None),(0xffffffff,4,None),
         (self.info["grid_symbol_id"],3,None)]
  # Probe calls are not counted as parent materializations.
  self.symbols.clear()
  for sid,size,expected_sid in cases:
   u.mem_write(probe,bytes(224));u.mem_write(probe+0xc8,struct.pack("<I",size))
   u.mem_write(probe+0xd0,struct.pack("<Q",wire));u.mem_write(wire,struct.pack("<I",sid))
   for reg,val in [(UC_ARM64_REG_X0,self.file),(UC_ARM64_REG_X1,probe),
                   (UC_ARM64_REG_X2,0),(UC_ARM64_REG_LR,n.end)]:
    u.reg_write(reg,val)
   u.emu_start(n.base+0x6f4f88,n.end,count=100)
   assert u.reg_read(UC_ARM64_REG_PC)==n.end
   expected=self.table+expected_sid*224 if expected_sid is not None else 0
   assert u.reg_read(UC_ARM64_REG_X0)==expected,{"owned_probe_symbol_id":sid,"owned_probe_length":size,"returned_table_base":u.reg_read(UC_ARM64_REG_X0)==self.table,"returned_null":u.reg_read(UC_ARM64_REG_X0)==0}
   assert bytes(u.mem_read(wire,4))==struct.pack("<I",sid)
  return len(cases)
def authority_negatives(blob):
 h,sy,wire,info=source(blob)
 r=sy[info["root_symbol_id"]];g=sy[info["grid_symbol_id"]]
 fields=[(r["record_offset"]+36,11),(r["record_offset"]+40,1),(r["record_offset"]+44,7),
         (r["record_offset"]+52,47),(r["data_abs_offset"]+24,0),
         (r["data_abs_offset"]+24,3),(r["data_abs_offset"]+24,5),
         (r["data_abs_offset"]+28,max(sy)+1),(r["data_abs_offset"]+28,0),(r["data_abs_offset"]+28,struct.unpack_from("<I",blob,r["data_abs_offset"]+16)[0]),
         (g["record_offset"]+36,1),(g["record_offset"]+40,1),
         (g["record_offset"]+44,6),(g["record_offset"]+52,403)]
 mutations=[]
 for offset,value in fields:
  b=bytearray(blob);struct.pack_into("<I",b,offset,value);mutations.append(bytes(b))
 b=bytearray(blob);b[g["record_offset"]+4:g["record_offset"]+36]=b"unsupported".ljust(32,b"\0");mutations.append(bytes(b))
 other=next(x for x in sy.values() if x["symbol_id"]!=r["symbol_id"])
 b=bytearray(blob);b[other["record_offset"]+4:other["record_offset"]+36]=b"aecxhwstatsconfig".ljust(32,b"\0");mutations.append(bytes(b))
 for b in mutations:
  try:source(b)
  except (AssertionError,ValueError,KeyError):pass
  else:raise AssertionError("unsupported source authority accepted")
 return len(mutations)
def main():
 source_facts();reports=[];results=[];executions=0;stride=0;symbols=0
 blobs=[]
 for name,sha in AV.FILES:
  b=(AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(b).hexdigest()==sha;blobs.append(b)
 authority_cases=authority_negatives(blobs[-1])
 for file_index,((name,sha),blob) in enumerate(zip(AV.FILES,blobs)):
  native=ParentPrefix(blob);w=native.wire;cases=[w]
  if file_index==2:
   for value in [0,1,0x3f800000,0x80000000,0x7fc00000,0xffffffff]:
    b=bytearray(w);b[20:32]=struct.pack("<3I",value,value,value);cases.append(bytes(b))
   rng=random.Random(0xe011a2)
   for _ in range(128):
    b=bytearray(w);b[20:32]=rng.randbytes(12);cases.append(bytes(b))
  for bias in [0,0x200,0x400,0x800]:
   for index,wire in enumerate(cases):
    out,nstride=native.run(wire,bias,check_stride=index==0)
    executions+=1;stride+=nstride
    if bias==0 and index==0:results.append(out)
  symbols+=native.symbol_negatives()
  reports.append({"path":name,"sha256":sha,"root_symbol_id":native.info["root_symbol_id"],
                  "grid_symbol_id":native.info["grid_symbol_id"],"owned_cases":4*len(cases)})
 observed=(ROOT.parent/"private/E011AX-20261001-0055A-captured/capture/INIT01_CACHE.bin").read_bytes()
 assert len(observed)==96 and all(x==observed[20:32] for x in results)
 safe={"experiment":"E011AZ","status":"PASS_BOUNDED_ORIGINAL_PARENT_FIRST_GRID_WEIGHT_MATERIALIZATION",
  "original_DLL_sha256":SHA,"source_files":reports,"parent_grid_prefix_cases":executions,
  "array_address_fragment_cases":stride,"original_symbol_lookup_cases":symbols,
  "symbol_zero_returns_slot_zero_requires_type_authority":True,
  "source_authority_rejected_cases":authority_cases,
  "parent_reader_rva":"0x123CC0","symbol_reader_rva":"0x6F4F88","symbol_reader_record_stride":224,
  "parent_grid_array_pointer_store_rva":"0x123FA4","parent_grid_array_pointer_offset":56,
  "parent_payload_adjustment":288,"parent_object_allocation_bytes":384,
  "qualified_Default_grid_count":4,"grid_array_allocation_bytes":480,"runtime_grid_element_stride":120,
  "parent_grid_child_symbol_wire_offset":28,"parent_grid_child_resolution_call_rva":"0x123F5C",
  "first_grid_reader_call_rva":"0x124034","grid_scalar_reader_rva":"0x123550",
  "first_weight_copy_call_rva":"0x123814","prefix_stop_rva":"0x123818",
  "serialized_and_runtime_grid_weight_offset":20,"weight_copy_bytes":12,
  "original_symbol_resolver_stubbed":False,"original_parent_count_reader_stubbed":False,
  "original_grid_weight_reader_or_memcpy_stubbed":False,
  "allocation_memset_name_security_comparison_helpers_stubbed":True,
  "revision_materialization_stubbed_and_excluded":True,
  "bounded_parent_to_first_grid_weight_mapping_verified":True,
  "three_installed_Default_sources_match_private_observation":True,
  "captured_weights_used_as_producer_inputs":False,"source_bytes_preserved":True,
  "owned_allocation_canaries_preserved":True,
  "full_parent_and_grid_aggregate_deserialization_closed":False,
  "ARM64EC_post_copy_array_bookkeeping_qualified":False,
  "live_named_module_and_grid_selection_join_closed":False,
  "cold_weight_initialization_policy_closed":False,
  "whole_deterministic_bootstrap_closed":False,"cold_metadata_bridge_closed":False,
  "native_rear_runtime_allowed":False,"production_C_changed":False,
  "new_kernel_build_performed":False,"runtime_actions_performed":False,"private_original_bytes_exported":False}
 (HERE/"MATERIALIZATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in safe.items() if k!="source_files"}))
if __name__=="__main__":main()
