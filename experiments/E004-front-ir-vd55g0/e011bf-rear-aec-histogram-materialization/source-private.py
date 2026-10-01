#!/usr/bin/env python3
"""E011BF original histogram sibling materialization in owned memory on SP11."""
from pathlib import Path
import importlib.util,hashlib,json,random,struct,pefile,capstone
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
BE=load("bf_revision",EX/"e011be-rear-aec-revision-materialization/source-private.py")
def source(blob):
 h,sy,wire,info=BE.source(blob);root=sy[info["root_symbol_id"]]
 count,sid=struct.unpack_from("<II",blob,root["data_abs_offset"]+32)
 assert count in (7,9) and sid in sy,"unsupported histogram root shape"
 hist=sy[sid]
 assert (hist["type"],hist["version_major"],hist["version_minor"],hist["mode_id"],hist["mode_symbol_id"],hist["data_bytes"])==("histStatsConfig",0,0,0,0xffffffff,172*count),"unsupported histogram symbol"
 children=[]
 for index in range(count):
  off=hist["data_abs_offset"]+172*index
  dcount,dsid=struct.unpack_from("<II",blob,off+148);vcount,vsid=struct.unpack_from("<II",blob,off+160)
  assert dcount==1 and dsid in sy and vsid in sy and 0<vcount<=1024,"unsupported histogram nested shape"
  for child_id,kind,nbytes in [(dsid,"data",4),(vsid,"values",4*vcount)]:
   child=sy[child_id]
   assert (child["type"],child["version_major"],child["version_minor"],child["mode_id"],child["mode_symbol_id"],child["data_bytes"])==(kind,0,0,0,0xffffffff,nbytes),"unsupported histogram nested symbol"
  children.append((dsid,vsid,vcount))
 return h,sy,wire,dict(info,hist_symbol_id=sid,hist_count=count,hist_children=children)
def facts():
 b=BE.BASE.DLL.read_bytes();assert hashlib.sha256(b).hexdigest()==BE.BASE.SHA
 pe=pefile.PE(data=b);c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);c.detail=True
 def ins(r):return next(c.disasm(pe.get_data(r,4),r))
 def mem(r,reg,offset):
  i=ins(r);assert i.mnemonic=="str" and c.reg_name(i.operands[0].reg)==reg
  m=i.operands[-1];assert m.type==capstone.arm64.ARM64_OP_MEM and c.reg_name(m.mem.base)=="x20" and m.mem.disp==offset
 mem(0x124124,"x26",72)
 i=ins(0x1248f0);assert i.mnemonic=="b" and i.operands[0].imm==0x124160
 i=ins(0x12416c);assert i.mnemonic.startswith("b.") and i.operands[0].imm==0x124970
 spans=[(0x124378,16,16),(0x1244d8,44,32),(0x124550,76,32),(0x1245cc,108,28),(0x124630,136,12)]
 for r,off,size in spans:
  i=ins(r);assert i.mnemonic=="bl" and i.operands[0].imm==0xf5d480
 for r in [0x12473c,0x124878]:
  i=ins(r);assert i.mnemonic=="bl" and i.operands[0].imm==0xea758
 return {"hist_array_store_rva":"0x124124","hist_array_payload_offset":72,"hist_loop_rva":"0x124160","hist_loop_back_edge_rva":"0x1248F0","prefix_stop_rva":"0x124970","original_nested_reader_rva":"0xEA758","scalar_copy_spans":[{"callsite":hex(r),"wire_and_runtime_member_offset":off,"bytes":size} for r,off,size in spans]}
class Histogram(BE.RevisionParent):
 def __init__(self,blob):
  _,_,_,info=source(blob);super().__init__(blob);self.info=info
  self.hist_entries=[];self.nested_entries=[];self.nested_returns=[];self.pending_nested=None
  def hook(u,pc,size,_):
   r=pc-self.n.base
   if r==0x124180:
    rr=self.table+self.info["hist_symbol_id"]*224
    self.hist_entries.append(int.from_bytes(u.mem_read(rr+216,8),"little"))
   if r==0xea758:
    call=u.reg_read(UC_ARM64_REG_LR)-self.n.base-4
    if call in (0x12473c,0x124878):
     rr=u.reg_read(UC_ARM64_REG_X0);sid=(rr-self.table)//224
     assert rr==self.table+sid*224 and sid in self.sy
     histreader=self.table+self.info["hist_symbol_id"]*224
     self.nested_entries.append((call,sid,int.from_bytes(u.mem_read(histreader+216,8),"little"),u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2)))
     self.pending_nested=(u.reg_read(UC_ARM64_REG_LR),call,sid,rr)
   if self.pending_nested and pc==self.pending_nested[0]:
    _,call,sid,rr=self.pending_nested
    self.nested_returns.append((call,sid,u.reg_read(UC_ARM64_REG_X0),int.from_bytes(u.mem_read(rr+216,8),"little")))
    self.pending_nested=None
  self.n.u.hook_add(UC_HOOK_CODE,hook)
 def run(self,bias,full_parent=False):
  n=self.n;u=n.u;wire=self.wire
  self.hist_entries.clear();self.nested_entries.clear();self.nested_returns.clear();self.pending_nested=None
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
  stop=n.end if full_parent else n.base+0x124970
  u.emu_start(n.base+0x123cc0,stop,count=200000)
  assert u.reg_read(UC_ARM64_REG_PC)==stop,"original parent did not reach its boundary"
  assert [v[1] for v in self.allocs[:7]]==[384,2,480,4,4,4,4]
  if not full_parent:assert len(self.allocs)==8+2*self.info["hist_count"]
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
  assert struct.unpack("<Q",u.mem_read(reader+216,8))[0]==(48 if full_parent else 40)
  return self.validate_histogram()
 def validate_histogram(self):
  u=self.n.u;count=self.info["hist_count"];hist=self.sy[self.info["hist_symbol_id"]];array=self.allocs[7][0];payload=self.allocs[0][0]+288
  assert self.allocs[7][1]==200*count
  assert int.from_bytes(u.mem_read(payload+64,4),"little")==count
  assert bytes(u.mem_read(payload+68,4))==bytes(4)
  assert int.from_bytes(u.mem_read(payload+72,8),"little")==array
  assert self.hist_entries==[172*i for i in range(count)]
  assert int.from_bytes(u.mem_read(self.table+self.info["hist_symbol_id"]*224+216,8),"little")==172*count
  entries=[];returns=[]
  for i,(dsid,vsid,vcount) in enumerate(self.info["hist_children"]):
   wire=self.data[hist["data_offset"]+172*i:hist["data_offset"]+172*(i+1)];r=bytes(u.mem_read(array+200*i,200))
   assert r[:148]==wire[:148]
   assert r[152:156]==wire[148:152] and r[168:172]==wire[156:160]
   assert r[172:176]==wire[160:164] and r[192:196]==wire[168:172]
   assert all(r[off:off+4]==bytes(4) for off in (148,156,176,180,196))
   for j,(sid,nbytes,ptr_offset,call,cursor) in enumerate([(dsid,4,160,0x12473c,156),(vsid,4*vcount,184,0x124878,168)]):
    start,length=self.allocs[8+2*i+j];child=self.sy[sid]
    assert length==nbytes and int.from_bytes(r[ptr_offset:ptr_offset+8],"little")==start
    assert bytes(u.mem_read(start,length))==self.data[child["data_offset"]:child["data_offset"]+length]
    # The actual selected reader ID is checked even when source spans alias.
    entries.append((call,sid,172*i+cursor,1 if j==0 else vcount,1))
    returns.append((call,sid,start,nbytes))
    assert self.copies[16+7*i+5+j]==(start,self.datas+child["data_offset"],nbytes)
   for j,(off,nbytes) in enumerate([(16,16),(44,32),(76,32),(108,28),(136,12)]):
    assert self.copies[16+7*i+j]==(array+200*i+off,self.datas+hist["data_offset"]+172*i+off,nbytes)
  assert self.nested_entries==entries and self.nested_returns==returns
  return {"histogram_entries":count,"nested_arrays":2*count,"scalar_copy_spans":5*count}
def negatives(blob):
 _,sy,_,info=source(blob);root=sy[info["root_symbol_id"]];hist=sy[info["hist_symbol_id"]];cases=[]
 fields=[(root["data_abs_offset"]+32,0),(root["data_abs_offset"]+32,8),(root["data_abs_offset"]+36,0),(root["data_abs_offset"]+36,max(sy)+1),(root["data_abs_offset"]+36,info["grid_symbol_id"]),(hist["record_offset"]+36,1),(hist["record_offset"]+40,1),(hist["record_offset"]+44,6),(hist["record_offset"]+52,hist["data_bytes"]-1)]
 for i,(dsid,vsid,vcount) in enumerate(info["hist_children"]):
  off=hist["data_abs_offset"]+172*i
  fields.extend([(off+148,0),(off+148,2),(off+152,0),(off+152,max(sy)+1),(off+152,vsid),(off+160,0),(off+160,1025),(off+164,0),(off+164,max(sy)+1),(off+164,dsid)])
  for sid in [dsid,vsid]:
   r=sy[sid];fields.extend([(r["record_offset"]+36,1),(r["record_offset"]+40,1),(r["record_offset"]+44,6),(r["record_offset"]+52,r["data_bytes"]-1)])
 for off,value in fields:
  b=bytearray(blob);struct.pack_into("<I",b,off,value);cases.append(bytes(b))
 for sid in [info["hist_symbol_id"]]+[s for d,v,c in info["hist_children"] for s in [d,v]]:
  r=sy[sid];b=bytearray(blob);b[r["record_offset"]+4:r["record_offset"]+36]=b"unsupported".ljust(32,b"\0");cases.append(bytes(b))
 for b in cases:
  try:source(b)
  except (AssertionError,ValueError,KeyError):pass
  else:raise AssertionError("unsupported histogram source accepted")
 return len(cases)
def main():
 anchors=facts();roots=[];audit=[]
 for name,sha in BE.BASE.AV.FILES:
  blob=(BE.BASE.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  _,sy,_,info=source(blob);roots.append(blob)
  audit.append({"path":name,"sha256":sha,"histogram_symbol_id":info["hist_symbol_id"],"histogram_count":info["hist_count"],"histogram_bytes":172*info["hist_count"],"nested_selected_symbol_ids":[[d,v] for d,v,c in info["hist_children"]],"values_counts":[c for d,v,c in info["hist_children"]]})
 _,sy,_,info=source(roots[-1]);hist=sy[info["hist_symbol_id"]];cases=list(roots);rng=random.Random(0xe011bf)
 for _ in range(8):
  b=bytearray(roots[-1])
  for i in range(info["hist_count"]):
   off=hist["data_abs_offset"]+172*i;b[off:off+148]=rng.randbytes(148);b[off+156:off+160]=rng.randbytes(4);b[off+168:off+172]=rng.randbytes(4)
  cases.append(bytes(b))
 for _ in range(8):
  b=bytearray(roots[-1])
  for d,v,c in info["hist_children"]:
   for sid in [d,v]:
    r=sy[sid];off=r["data_abs_offset"];b[off:off+r["data_bytes"]]=rng.randbytes(r["data_bytes"])
  cases.append(bytes(b))
 runs=0;full=0;hist_entries=0;nested=0;spans=0
 for blob in cases:
  f=Histogram(blob)
  for bias in [0,0x200,0x1230,0x8010]:
   result=f.run(bias);runs+=1;hist_entries+=result["histogram_entries"];nested+=result["nested_arrays"];spans+=result["scalar_copy_spans"]
 for blob in roots:
  f=Histogram(blob)
  result=f.run(0,full_parent=True);full+=1;hist_entries+=result["histogram_entries"];nested+=result["nested_arrays"];spans+=result["scalar_copy_spans"]
 rejected=negatives(roots[-1])
 result={"experiment":"E011BF","status":"PASS_BOUNDED_ORIGINAL_HISTOGRAM_SIBLING_MATERIALIZATION","base_commit":"56b786bc90ecb4b3861a23f300eadd8ae53a41aa","original_DLL_sha256":BE.BASE.SHA,"source_files":audit,"anchors":anchors,"unique_source_cases":len(cases),"owned_scalar_variants":8,"owned_nested_array_variants":8,"fixture_placements":4,"histogram_prefix_runs":runs,"full_parent_return_smoke_checks":full,"histogram_entries_verified":hist_entries,"typed_nested_arrays_verified":nested,"original_histogram_scalar_memcpy_spans_verified":spans,"source_scope_rejections":rejected,"histogram_wire_stride":172,"histogram_runtime_stride":200,"histogram_root_count_wire_offset":32,"histogram_root_symbol_wire_offset":36,"histogram_runtime_count_payload_offset":64,"histogram_runtime_pointer_payload_offset":72,"nested_data_runtime_pointer_offset":160,"nested_values_runtime_pointer_offset":184,"selected_nested_reader_IDs_qualified_even_for_aliased_source_spans":True,"source_data_reader_non_cursor_bytes_and_allocation_canaries_preserved":True,"original_revision_grid_histogram_nested_readers_and_copies_execute":True,"remaining_stubs":["0x11D0","0x11F0","0x6F4AC0","0x6F45D8","0xF5DF00","0xCAE740","0xF5E600"],"BFW_sibling_validated":False,"whole_parent_metadata_materialization_closed":False,"whole_profile_materialization_closed":False,"exact_opened_tuning_filename_closed":False,"whole_loader_alignment_policy_closed":False,"cold_metadata_bridge_closed":False,"RS_count_offset_authority_closed":False,"complete_deterministic_bootstrap_closed":False,"WM16_retirement_closed":False,"Linux_optical_parity_closed":False,"captured_scalars_used_as_producer_inputs":False,"private_original_bytes_exported":False,"production_C_changed":False,"new_kernel_build_performed":False,"runtime_actions_performed":False,"observer_armed":False,"new_camera_starts":0,"new_reboots":0,"native_rear_runtime_allowed":False}
 (HERE/"HISTOGRAM-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in result.items() if k!="source_files"},indent=2))
if __name__=="__main__":main()
