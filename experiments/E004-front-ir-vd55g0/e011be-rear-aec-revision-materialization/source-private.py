#!/usr/bin/env python3
"""E011BE: original parent revision and four-grid materialization, same SP11 only."""
from pathlib import Path
import importlib.util,hashlib,json,struct,pefile,capstone
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
BB=load("be_bb",EX/"e011bb-rear-aec-four-grid-deserialization/source-private.py")
BASE=load("be_parent",HERE/"parent-fixture-private.py")
def source(blob):
 h,sy,wire,info=BB.source(blob)
 r=sy[info["root_symbol_id"]];raw=blob[r["data_abs_offset"]:r["data_abs_offset"]+r["data_bytes"]]
 count,sid=struct.unpack_from("<II",raw,12)
 assert count==2 and sid in sy,"revision fixture requires a two-byte revision"
 revision=sy[sid]
 assert (revision["type"],revision["version_major"],revision["version_minor"],revision["mode_id"],revision["mode_symbol_id"],revision["data_bytes"])==("revision",0,0,0,0xffffffff,2),"unsupported revision symbol"
 data=blob[revision["data_abs_offset"]:revision["data_abs_offset"]+2]
 assert len(data)==2 and data[0]!=0 and data[1]==0,"revision fixture requires a bounded terminated string"
 return h,sy,wire,dict(info,revision_symbol_id=sid,revision_count=count)
def facts():
 b=BASE.DLL.read_bytes();assert hashlib.sha256(b).hexdigest()==BASE.SHA
 pe=pefile.PE(data=b);c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);c.detail=True
 def ins(r):return next(c.disasm(pe.get_data(r,4),r))
 def regs(i):return [c.reg_name(o.reg) for o in i.operands if o.type==capstone.arm64.ARM64_OP_REG]
 for r,dst,src in [(0xdb3bc,"x21","x0"),(0xdb3c4,"x26","x1"),(0xdb3cc,"x22","x2"),(0xdb3d0,"x23","x3")]:
  i=ins(r);assert i.mnemonic=="mov" and regs(i)==[dst,src]
 i=ins(0xdb464);assert i.mnemonic=="cbnz" and regs(i)==["x23"] and i.operands[1].imm==0xdb46c
 i=ins(0xdb468);assert i.mnemonic=="brk" and i.operands[0].imm==0xf004
 i=ins(0xdb46c);assert i.mnemonic=="udiv" and regs(i)==["x8","x22","x23"]
 i=ins(0xdb450);assert i.mnemonic=="mov" and regs(i)==["x3"] and i.operands[1].imm&((1<<64)-1)==(1<<64)-1
 i=ins(0xdb45c);assert i.mnemonic=="bl" and i.operands[0].imm==0xcae7c0
 return {"reader_rva":"0xDB3A0","count_argument":"x2","alignment_argument":"x3","zero_alignment_guard_rva":"0xDB468","quotient_rva":"0xDB46C","copy_helper_rva":"0xCAE7C0","copy_call_rva":"0xDB45C","copy_fourth_argument":"U64_MAX"}
class RevisionParent(BASE.ParentPrefix):
 def __init__(self,blob):
  h,sy,wire,info=source(blob);super().__init__(blob);self.info=info
  self.n.u.mem_map(self.table_map+self.table_size,0x10000);self.table_size+=0x10000
  self.n.u.mem_map(self.data_map+self.data_size,0x10000);self.data_size+=0x10000
  self.entries=[];self.returns=[];self.revision_entries=[];self.revision_returns=[];self.checked_copies=[];self.traps=[]
  def hook(u,pc,size,_):
   r=pc-self.n.base
   if r==0xdb3a0:
    rr=u.reg_read(UC_ARM64_REG_X0);out=u.reg_read(UC_ARM64_REG_X1)
    self.revision_return_pc=u.reg_read(UC_ARM64_REG_LR)
    self.revision_entries.append((rr,out,u.reg_read(UC_ARM64_REG_X2),u.reg_read(UC_ARM64_REG_X3)))
   elif pc==getattr(self,"revision_return_pc",None):
    rr=self.table+self.info["revision_symbol_id"]*224
    self.revision_returns.append((u.reg_read(UC_ARM64_REG_W0),struct.unpack("<Q",u.mem_read(rr+216,8))[0]))
   if r==0xcae7c0:
    self.checked_copies.append(tuple(u.reg_read(reg) for reg in [UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3]))
   if r==0xdb468:self.traps.append(r)
   if r==0x123550:
    rr=u.reg_read(UC_ARM64_REG_X0);out=u.reg_read(UC_ARM64_REG_X1)
    self.entries.append((struct.unpack("<Q",u.mem_read(rr+216,8))[0],out,u.reg_read(UC_ARM64_REG_X2)))
   elif r==0x124038:
    rr=self.table+self.info["grid_symbol_id"]*224
    self.returns.append((u.reg_read(UC_ARM64_REG_W0),struct.unpack("<Q",u.mem_read(rr+216,8))[0]))
  self.n.u.hook_add(UC_HOOK_CODE,hook)
 def run(self,bias,full_parent=False):
  n=self.n;u=n.u;wire=self.wire
  u.mem_write(n.heap,bytes(0x30000));u.mem_write(n.stack,bytes(0x10000))
  for x in [self.allocs,self.symbols,self.calls,self.copies,self.redzones,self.entries,self.returns,self.revision_entries,self.revision_returns,self.checked_copies,self.traps]:x.clear()
  self.stub_counts.clear();self.revision_return_pc=None
  self.table=self.table_map+bias;self.datas=self.data_map+bias;self.file=n.heap+0x800+bias
  self.next_alloc=n.heap+0x18000+bias
  u.mem_write(self.datas,self.data)
  table=bytearray(self.table_size-bias)
  for sid,r in self.sy.items():
   off=sid*224;struct.pack_into("<Q",table,off,self.file)
   struct.pack_into("<I",table,off+200,r["data_bytes"])
   struct.pack_into("<Q",table,off+208,self.datas+r["data_offset"])
  u.mem_write(self.table,bytes(table))
  u.mem_write(self.file+24,struct.pack("<I",max(self.sy)));u.mem_write(self.file+40,struct.pack("<Q",self.table))
  reader=self.table+self.info["root_symbol_id"]*224
  for reg,value in [(UC_ARM64_REG_X0,self.file),(UC_ARM64_REG_X1,reader),(UC_ARM64_REG_X2,1),(UC_ARM64_REG_SP,n.stack+0xf000),(UC_ARM64_REG_LR,n.end)]:u.reg_write(reg,value)
  stop=n.end if full_parent else n.base+0x124040
  u.emu_start(n.base+0x123cc0,stop,count=200000)
  assert u.reg_read(UC_ARM64_REG_PC)==stop,"original parent did not reach its boundary"
  assert [v[1] for v in self.allocs[:7]]==[384,2,480,4,4,4,4]
  if not full_parent:assert len(self.allocs)==7
  module,revptr,array=self.allocs[0][0],self.allocs[1][0],self.allocs[2][0];payload=module+288
  rev=self.sy[self.info["revision_symbol_id"]];revreader=self.table+self.info["revision_symbol_id"]*224
  assert self.revision_entries==[(revreader,payload+32,2,1)]
  assert self.revision_returns==[(1,2)] and not self.traps
  assert struct.unpack("<Q",u.mem_read(payload+32,8))[0]==revptr
  assert bytes(u.mem_read(revptr,2))==self.data[rev["data_offset"]:rev["data_offset"]+2]
  assert self.checked_copies==[(revptr,2,self.datas+rev["data_offset"],(1<<64)-1)]
  assert "0xdb3a0" not in self.stub_counts and "0xcae7c0" not in self.stub_counts
  assert self.entries==[(101*i,array+120*i,1) for i in range(4)]
  assert self.returns==[(1,101*(i+1)) for i in range(4)]
  gridreader=self.table+self.info["grid_symbol_id"]*224
  assert self.calls==[(gridreader,array+120*i,120) for i in range(4)]
  assert struct.unpack("<Q",u.mem_read(gridreader+216,8))[0]==404
  assert struct.unpack("<Q",u.mem_read(payload+56,8))[0]==array
  assert struct.unpack("<I",u.mem_read(payload+44,4))[0]==4
  assert struct.unpack("<I",u.mem_read(payload+48,4))[0]==0
  grid=self.sy[self.info["grid_symbol_id"]]
  for i in range(4):
   for off,size in [(20,12),(32,16),(48,16)]:
    assert bytes(u.mem_read(array+120*i+off,size))==wire[101*i+off:101*i+off+size]
    assert self.copies[4*i+[20,32,48].index(off)]==(array+120*i+off,self.datas+grid["data_offset"]+101*i+off,size)
   nested=self.allocs[3+i][0];sid=struct.unpack_from("<I",wire,101*i+93)[0];child=self.sy[sid]
   assert struct.unpack("<Q",u.mem_read(array+120*i+104,8))[0]==nested
   assert self.copies[4*i+3]==(nested,self.datas+child["data_offset"],4)
   assert bytes(u.mem_read(nested,4))==self.data[child["data_offset"]:child["data_offset"]+4]
  assert all(bytes(u.mem_read(at,32))==bytes([0xa5])*32 for at in self.redzones)
  assert bytes(u.mem_read(self.datas,len(self.data)))==self.data
  # Reader records may change only their cursors.
  actual=bytearray(u.mem_read(self.table,len(table)))
  for sid in self.sy:
   off=sid*224+216;actual[off:off+8]=table[off:off+8]
  assert actual==table
  assert struct.unpack("<Q",u.mem_read(reader+216,8))[0]==(48 if full_parent else 32)
  return {"allocations":len(self.allocs),"original_grid_returns":4}
def negatives(blob):
 h,sy,wire,info=source(blob);r=sy[info["root_symbol_id"]];v=sy[info["revision_symbol_id"]];cases=[]
 for at,val in [(r["data_abs_offset"]+12,0),(r["data_abs_offset"]+12,1),(r["data_abs_offset"]+12,3),(r["data_abs_offset"]+16,0),(r["data_abs_offset"]+16,max(sy)+1),(r["data_abs_offset"]+16,info["grid_symbol_id"]),(v["record_offset"]+36,1),(v["record_offset"]+40,1),(v["record_offset"]+44,6),(v["record_offset"]+52,1),(v["record_offset"]+52,3)]:
  b=bytearray(blob);struct.pack_into("<I",b,at,val);cases.append(bytes(b))
 b=bytearray(blob);b[v["record_offset"]+4:v["record_offset"]+36]=b"unsupported".ljust(32,b"\0");cases.append(bytes(b))
 for off,val in [(0,0),(1,1)]:
  b=bytearray(blob);b[v["data_abs_offset"]+off]=val;cases.append(bytes(b))
 for blob in cases:
  try:source(blob)
  except (AssertionError,ValueError,KeyError):pass
  else:raise AssertionError("unsupported revision source accepted")
 return len(cases)
def main():
 anchors=facts();roots=[];audit=[]
 for name,sha in BASE.AV.FILES:
  blob=(BASE.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  h,sy,wire,info=source(blob);roots.append(blob)
  audit.append({"path":name,"sha256":sha,"revision_symbol_id":info["revision_symbol_id"],"revision_type":"revision","revision_version":[0,0],"revision_mode":0,"revision_selector":4294967295,"revision_bytes":2})
 cases=[(i,blob) for i,blob in enumerate(roots)]
 h,sy,wire,info=source(roots[-1]);v=sy[info["revision_symbol_id"]]
 for value in [1,2,31,32,65,127,128,254,255]:
  b=bytearray(roots[-1]);b[v["data_abs_offset"]]=value;cases.append((2,bytes(b)))
 runs=0;full=0;gridreturns=0
 for _,blob in cases:
  f=RevisionParent(blob)
  for bias in [0,0x200,0x1230,0x8010]:
   result=f.run(bias);runs+=1;gridreturns+=result["original_grid_returns"]
 for blob in roots:
  f=RevisionParent(blob)
  for bias in [0,0x200,0x1230,0x8010]:
   result=f.run(bias,full_parent=True);full+=1;gridreturns+=result["original_grid_returns"]
 rejected=negatives(roots[-1])
 result={"experiment":"E011BE","status":"PASS_BOUNDED_ORIGINAL_REVISION_AND_FOUR_GRID_MATERIALIZATION","base_commit":"cfd37df4e0d7915c357d5ee32cc84d51fff7bb6b","original_DLL_sha256":BASE.SHA,"source_files":audit,"anchors":anchors,"unique_source_cases":len(cases),"owned_revision_variants":9,"fixture_placements":4,"parent_revision_four_grid_prefix_cases":runs,"full_parent_return_smoke_checks":full,"original_revision_returns":runs+full,"original_checked_string_copy_calls":runs+full,"original_grid_returns":gridreturns,"revision_source_scope_rejections":rejected,"revision_return_cursor":2,"revision_destination_payload_offset":32,"revision_allocation_bytes":2,"revision_source_typed_and_terminated":True,"revision_alignment":1,"alignment_authority":"E011BD actual entry plus bounded original context initializer/caller forwarding","original_revision_reader_stubbed":False,"original_checked_string_copy_stubbed":False,"original_memcpy_stubbed":False,"original_parent_grid_and_nested_readers_stubbed":False,"source_data_reader_non_cursor_bytes_and_allocation_canaries_preserved":True,"remaining_stubs":["0x11D0","0x11F0","0x6F4AC0","0x6F45D8","0xF5DF00","0xCAE740","0xF5E600"],"full_parent_smokes_do_not_validate_sibling_metadata":True,"whole_parent_metadata_materialization_closed":False,"whole_profile_materialization_closed":False,"exact_opened_tuning_filename_closed":False,"whole_loader_alignment_policy_closed":False,"cold_metadata_bridge_closed":False,"RS_count_offset_authority_closed":False,"complete_deterministic_bootstrap_closed":False,"WM16_retirement_closed":False,"Linux_optical_parity_closed":False,"captured_scalars_used_as_producer_inputs":False,"private_original_bytes_exported":False,"production_C_changed":False,"new_kernel_build_performed":False,"runtime_actions_performed":False,"observer_armed":False,"new_camera_starts":0,"new_reboots":0,"native_rear_runtime_allowed":False}
 (HERE/"REVISION-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in result.items() if k!="source_files"},indent=2))
if __name__=="__main__":main()
