#!/usr/bin/env python3
"""Same-SP11 original four-grid reader. Immutable OEM bytes never leave SP11."""
from pathlib import Path
import importlib.util,hashlib,json,random,struct,pefile,capstone
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
AZ=load("bb_previous",EX/"e011az-rear-aec-grid-materialization/source-private.py")
def source(blob):
 h,sy,wire,info=AZ.source(blob);children=[]
 for index in range(4):
  count,sid=struct.unpack_from("<II",wire,101*index+89)
  assert count==1 and sid in sy,"unsupported nested data-array shape"
  r=sy[sid]
  assert (r["type"],r["version_major"],r["version_minor"],r["mode_id"],r["mode_symbol_id"],r["data_bytes"])==("data",0,0,0,0xffffffff,4),"unsupported nested data symbol"
  children.append(sid)
 return h,sy,wire,dict(info,nested_symbol_ids=children)
def facts():
 p=pefile.PE(data=AZ.DLL.read_bytes());c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);c.detail=True
 def ins(r):return next(c.disasm(p.get_data(r,4),r))
 i=ins(0x123570);assert i.mnemonic=="mov" and [c.reg_name(o.reg) for o in i.operands]==["x21","x2"]
 i=ins(0x12381c);assert i.mnemonic=="cbnz" and c.reg_name(i.operands[0].reg)=="x21" and i.operands[1].imm==0x123824
 i=ins(0x123820);assert i.mnemonic=="brk" and i.operands[0].imm==0xf004
 i=ins(0x123824);assert i.mnemonic=="udiv" and [c.reg_name(o.reg) for o in i.operands]==["x9","x23","x21"]
 assert ins(0x12403c).mnemonic=="cbnz" and ins(0x12403c).operands[1].imm==0x124018
 return {"third_argument_retention_rva":"0x123570","zero_divisor_guard_rva":"0x123820","division_rva":"0x123824","grid_loop_end_rva":"0x124040"}
class FourGrid(AZ.ParentPrefix):
 def __init__(self,blob):
  source(blob);super().__init__(blob);self.entries=[];self.returns=[]
  # Allow the largest placement without changing any source record size.
  self.n.u.mem_map(self.table_map+self.table_size,0x10000);self.table_size+=0x10000
  self.n.u.mem_map(self.data_map+self.data_size,0x10000);self.data_size+=0x10000
  def hook(u,pc,size,_):
   r=pc-self.n.base
   if r==0x123550:
    rr=u.reg_read(UC_ARM64_REG_X0);out=u.reg_read(UC_ARM64_REG_X1)
    cursor=struct.unpack("<Q",u.mem_read(rr+0xd8,8))[0]
    self.entries.append((cursor,out,u.reg_read(UC_ARM64_REG_X2)))
   elif r==0x124038:
    rr=self.table+self.info["grid_symbol_id"]*224
    self.returns.append((u.reg_read(UC_ARM64_REG_W0),struct.unpack("<Q",u.mem_read(rr+0xd8,8))[0]))
  self.n.u.hook_add(UC_HOOK_CODE,hook)
 def run(self,wire,bias,alignment=1,full_parent=False):
  # Packed alignment is an explicit fixture input, not an asserted live policy.
  assert alignment==1,"only explicitly packed serialization is in this fixture's scope"
  assert len(wire)==404
  n=self.n;u=n.u
  u.mem_write(n.heap,bytes(0x30000));u.mem_write(n.stack,bytes(0x10000))
  for x in [self.allocs,self.symbols,self.calls,self.copies,self.redzones,self.entries,self.returns]:x.clear()
  self.stub_counts.clear()
  self.table=self.table_map+bias;self.datas=self.data_map+bias;self.file=n.heap+0x800+bias
  self.next_alloc=n.heap+0x18000+bias
  expected_data=bytearray(self.data);grid=self.sy[self.info["grid_symbol_id"]]
  expected_data[grid["data_offset"]:grid["data_offset"]+404]=wire
  u.mem_write(self.datas,bytes(expected_data))
  table=bytearray(self.table_size-bias)
  for sid,r in self.sy.items():
   off=sid*224;struct.pack_into("<Q",table,off,self.file)
   struct.pack_into("<I",table,off+0xc8,r["data_bytes"])
   struct.pack_into("<Q",table,off+0xd0,self.datas+r["data_offset"])
  u.mem_write(self.table,bytes(table))
  u.mem_write(self.file+0x18,struct.pack("<I",max(self.sy)));u.mem_write(self.file+0x28,struct.pack("<Q",self.table))
  reader=self.table+self.info["root_symbol_id"]*224
  for reg,value in [(UC_ARM64_REG_X0,self.file),(UC_ARM64_REG_X1,reader),(UC_ARM64_REG_X2,alignment),(UC_ARM64_REG_SP,n.stack+0xf000),(UC_ARM64_REG_LR,n.end)]:u.reg_write(reg,value)
  stop=n.end if full_parent else n.base+0x124040
  u.emu_start(n.base+0x123cc0,stop,count=200000)
  assert u.reg_read(UC_ARM64_REG_PC)==stop,"bounded original reader did not reach its boundary"
  assert [v[1] for v in self.allocs[:6]]==[384,480,4,4,4,4]
  if not full_parent:assert len(self.allocs)==6,"unexpected sibling allocation before grid boundary"
  module,array=self.allocs[0][0],self.allocs[1][0];payload=module+0x120
  grid_reader=self.table+self.info["grid_symbol_id"]*224
  assert self.entries==[(101*i,array+120*i,1) for i in range(4)]
  assert self.returns==[(1,101*(i+1)) for i in range(4)]
  assert self.calls==[(grid_reader,array+120*i,120) for i in range(4)]
  assert struct.unpack("<Q",u.mem_read(grid_reader+0xd8,8))[0]==404
  assert struct.unpack("<Q",u.mem_read(payload+0x38,8))[0]==array
  assert struct.unpack("<I",u.mem_read(payload+0x2c,4))[0]==4
  # +0x30 stays zero: it is not asserted to be a completed-element counter.
  assert struct.unpack("<I",u.mem_read(payload+0x30,4))[0]==0
  output=[]
  for i in range(4):
   for off,size in [(20,12),(32,16),(48,16)]:
    assert bytes(u.mem_read(array+120*i+off,size))==wire[101*i+off:101*i+off+size]
    assert self.copies[4*i+[20,32,48].index(off)]==(array+120*i+off,self.datas+grid["data_offset"]+101*i+off,size)
   nested=self.allocs[2+i][0];sid=struct.unpack_from("<I",wire,101*i+93)[0];child=self.sy[sid]
   assert struct.unpack("<Q",u.mem_read(array+120*i+104,8))[0]==nested
   assert self.copies[4*i+3]==(nested,self.datas+child["data_offset"],4)
   assert bytes(u.mem_read(nested,4))==self.data[child["data_offset"]:child["data_offset"]+4]
   output.append(bytes(u.mem_read(array+120*i+20,12)))
  assert all(bytes(u.mem_read(a,32))==bytes([0xa5])*32 for a in self.redzones)
  assert bytes(u.mem_read(self.datas,len(expected_data)))==bytes(expected_data)
  if full_parent:assert struct.unpack("<Q",u.mem_read(reader+0xd8,8))[0]==48
  return output
def negatives(blob):
 rejected=AZ.authority_negatives(blob);h,sy,wire,info=source(blob);grid=sy[info["grid_symbol_id"]]
 mutations=[]
 for i in range(4):
  count_at=grid["data_abs_offset"]+101*i+89;sid_at=count_at+4;r=sy[info["nested_symbol_ids"][i]]
  for offset,value in [(count_at,0),(count_at,2),(count_at,0xffffffff),(sid_at,0),(sid_at,max(sy)+1),(sid_at,info["grid_symbol_id"]),(r["record_offset"]+36,1),(r["record_offset"]+40,1),(r["record_offset"]+44,6),(r["record_offset"]+52,3),(r["record_offset"]+52,5)]:
   b=bytearray(blob);struct.pack_into("<I",b,offset,value);mutations.append(bytes(b))
  b=bytearray(blob);b[r["record_offset"]+4:r["record_offset"]+36]=b"unsupported".ljust(32,b"\0");mutations.append(bytes(b))
 for b in mutations:
  try:source(b)
  except (AssertionError,ValueError,KeyError):pass
  else:raise AssertionError("unsupported source shape accepted")
 return rejected+len(mutations)
def main():
 anchors=facts();roots=[];audit=[]
 for name,sha in AZ.AV.FILES:
  blob=(AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  h,sy,wire,info=source(blob);roots.append((blob,wire))
  audit.append({"path":name,"sha256":sha,"grid_symbol_id":info["grid_symbol_id"],"nested_symbol_ids":info["nested_symbol_ids"]})
 fixtures=[FourGrid(b) for b,w in roots];cases=[(i,w) for i,(b,w) in enumerate(roots)]
 for value in [0,1,0x3f800000,0x80000000,0x7fc00000,0xffffffff]:
  b=bytearray(roots[-1][1])
  for i in range(4):b[i*101+20:i*101+32]=struct.pack("<3I",value,(value+i)&0xffffffff,value^0xffffffff)
  cases.append((2,bytes(b)))
 rng=random.Random(0xe011bb)
 for _ in range(128):
  b=bytearray(roots[-1][1])
  for i in range(4):b[101*i+20:101*i+32]=rng.randbytes(12)
  cases.append((2,bytes(b)))
 runs=0
 for bias in [0,0x200,0x1230,0x8010]:
  for fi,wire in cases:fixtures[fi].run(wire,bias);runs+=1
 comparisons=0;full_returns=0
 for fixture,(blob,wire) in zip(fixtures,roots):
  produced=fixture.run(wire,0,full_parent=True);full_returns+=1
  for i in range(4):
   live=(ROOT.parent/f"private/E011BA-20261001-0749A-captured/capture/INIT{i+1:02}_CACHE.bin").read_bytes()
   assert len(live)==120 and produced[i]==live[20:32];comparisons+=1
 rejected=negatives(roots[-1][0]);alignment_rejects=0
 for alignment in [0,2,4,8]:
  try:fixtures[-1].run(roots[-1][1],0,alignment=alignment)
  except AssertionError:alignment_rejects+=1
  else:raise AssertionError("fixture scope unexpectedly expanded")
 result={"experiment":"E011BB","status":"PASS_ORIGINAL_FOUR_GRID_MAPPING_CONDITIONAL_PACKED_ALIGNMENT","base_commit":"52d6ce487664492d476903c3d72505f6ba9d24fb",
 "original_DLL_sha256":AZ.SHA,"source_files":audit,"source_anchors":anchors,"unique_weight_cases":len(cases),"fixture_placements":4,"four_grid_prefix_executions":runs,"original_grid_reader_returns":runs*4,"weight_fields_matched":runs*12,"weight_blocks_matched":runs*4,
 "source_authority_rejected_cases":rejected,"fixture_alignment_scope_rejections":alignment_rejects,"native_parent_return_smoke_checks":full_returns,"private_live_grid_weight_comparisons":comparisons,"private_live_weight_bytes_compared":comparisons*12,
 "serialized_grid_entry_stride":101,"runtime_grid_entry_stride":120,"serialized_entry_cursors":[0,101,202,303],"serialized_return_cursors":[101,202,303,404],
 "weight_wire_offsets":[20,121,222,323],"weight_runtime_array_offsets":[20,140,260,380],"weights_bytes_per_grid":12,
 "additional_original_array_copy_spans_per_grid":[{"offset":32,"bytes":16},{"offset":48,"bytes":16}],"native_array_symbol_tail_helper_rva":"0x123B80","nested_array_count":1,"nested_array_bytes":4,"nested_runtime_pointer_offset":104,"typed_nested_source_copy_verified":True,"nested_symbol_type":"data","nested_symbol_version":[0,0],
 "payload_count_offset":44,"payload_count_value":4,"payload_nearby_offset48_value":0,"nearby_offset48_not_claimed_as_completed_count":True,
 "explicit_fixture_alignment":1,"alignment_semantics":"third argument controls serialized array alignment/round-up and is checked against zero before division",
 "live_alignment_argument_qualified":False,"independent_caller_alignment_policy_closed":False,
 "original_grid_symbol_array_readers_and_memcpy_executed":True,"native_memcpy_stubbed":False,"security_name_comparison_allocation_memset_helpers_stubbed":True,"revision_materialization_stubbed_and_excluded":True,
 "source_bytes_and_allocation_canaries_preserved":True,"bounded_four_grid_numeric_mapping_closed":True,"whole_parent_metadata_materialization_closed":False,"whole_profile_materialization_closed":False,
 "exact_loaded_tuning_filename_closed":False,"cold_weight_initialization_policy_closed":False,"cold_metadata_bridge_closed":False,"RS_count_offset_authority_closed":False,"complete_deterministic_bootstrap_closed":False,"WM16_retirement_closed":False,"Linux_optical_parity_closed":False,
 "captured_weights_used_as_producer_inputs":False,"private_bytes_exported":False,"production_C_changed":False,"new_kernel_build_performed":False,"runtime_actions_performed":False,"observer_armed":False,"new_camera_starts":0,"new_reboots":0,"native_rear_runtime_allowed":False}
 (HERE/"DESERIALIZATION-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in result.items() if k!="source_files"},indent=2))
if __name__=="__main__":main()
