#!/usr/bin/env python3
"""Same-SP11 original statistics-list construction and query, in owned memory only."""
from pathlib import Path
import importlib.util,struct,json,hashlib,collections
import pefile,capstone
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent
BASE="2573b773125ad500e696d046b8391c72b56357e7"
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
BZ=load("ca_initialized",EX/"e011bz-rear-source-grid-initialization/source-private.py")
BY=BZ.BY;BW=BY.BW;BB=BZ.BB
NUMERIC={
 0x39f0b4:{0x3a8730},0x39f0d4:{0x3a8730},0x3a8754:{0x3af540},0x3af560:{0x3aebb0},
 0x39f388:{0x3a0d70},0x39f6bc:{0x3a14e0,0x39d7e0},0x39f90c:{0x3a2440},
 0x85276c:{0x36e460},0x36e610:{0x374050},0x36e634:{0x372e40},0x3740b4:{0x3ae320},
 0x39eacc:{0x2dbc0,0x29ea50,0x39d840},0x39eb10:{0x39d7c0,0x39d830},
 0x39eb94:{0x3a0db0},0x39ec18:{0x2dbc0},0x39ecdc:{0x3a0db0}}
LOG={0x39f330,0x39f60c,0x39f8ac,0x39ec68,0x3a0fe4,0x3a1080,0x3a1108,
 0x373fb0,0x372efc,0x36e53c}
INIT={0x3a0d70,0x3a14e0,0x39d7e0,0x3a2440}
def authority():
 raw=BW.N.DLL.read_bytes();assert hashlib.sha256(raw).hexdigest()==BW.N.DLL_SHA
 p=pefile.PE(data=raw);c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);c.detail=True
 def ins(r):return next(c.disasm(p.get_data(r,4),r))
 for site in set(NUMERIC)|LOG:
  i=ins(site);assert i.mnemonic=="blr" and c.reg_name(i.operands[0].reg)=="x17"
  i=ins(site+4);assert i.mnemonic=="blr" and c.reg_name(i.operands[0].reg)=="x15"
 for site,dest in [(0x36d3d0,0x39f070),(0x36d3d8,0x39faf8)]:
  i=ins(site);assert i.mnemonic=="bl" and i.operands[0].imm==dest
 # Two source-created 20-slot, 160-byte ring stores. The latter is not the capacity field.
 for site,offset in [(0x36d35c,0x618),(0x36d390,0x630)]:
  i=ins(site);assert i.mnemonic=="str" and i.operands[-1].mem.disp==offset
 prior=list(c.disasm(p.get_data(0x36d320,24),0x36d320))
 assert any(i.mnemonic=="mov" and c.reg_name(i.operands[0].reg) in ["x0","w0"] and i.operands[1].imm==1664 for i in prior)
 for start,compare,branch,full,store,count_store in [
  (0x39f390,0x39f39c,0x39f3a0,0x39f450,0x39f3c0,0x39f3cc),
  (0x39f6c4,0x39f6d0,0x39f6d4,0x39f790,0x39f6f4,0x39f700),
  (0x39f914,0x39f920,0x39f924,0x39fa98,0x39f944,0x39f950)]:
  i=ins(compare-4);assert i.mnemonic=="ldp" and [c.reg_name(o.reg) for o in i.operands[:2]]==["w9","w10"]
  assert ins(branch).mnemonic=="b.hs" and ins(branch).operands[0].imm==full
  i=ins(count_store);assert i.mnemonic=="str" and i.operands[-1].mem.disp==0x614
 assert ins(0x39eb24).mnemonic=="b.eq" and ins(0x39eb24).operands[0].imm==0x39ec98
 i=ins(0x39eb28);assert i.mnemonic=="mov" and [c.reg_name(o.reg) for o in i.operands]==["w22","w20"]
 return p,c,{"original_DLL_sha256":BW.N.DLL_SHA,"source_manager_allocation_bytes":1664,
 "source_collection_storage_bytes_each":160,"source_collection_capacity_each":20,
 "primary_ring_pointer_offset":0x608,"primary_ring_head_u32_offset":0x610,
 "primary_ring_count_u32_offset":0x614,"primary_ring_capacity_u32_offset":0x618,
 "secondary_ring_pointer_offset":0x620,"secondary_ring_head_u32_offset":0x628,
 "secondary_ring_count_u32_offset":0x62c,"secondary_ring_capacity_u32_offset":0x630,
 "collection_slot_stride_bytes":8,
 "source_ranges":[{"RVA":hex(r),"bytes":z,"sha256":hashlib.sha256(p.get_data(r,z)).hexdigest()}
 for r,z in [(0x36d320,184),(0x39f070,2652),(0x39ea40,688),(0x3a8730,56),(0x3af540,64),(0x3aebb0,8)]]}
class Collection:
 def __init__(self,p,c):
  self.n=BW.N.Native();self.u=self.n.u;self.u.mem_map(self.n.heap+0x30000,0xd0000)
  self.c=c;self.instructions={}
  for r,z in [(0x36d338,160),(0x39f070,2652),(0x3a8730,56),(0x3af540,64),(0x3aebb0,8),
   (0x39ea40,688),(0x372e40,4616),(0x3a0db0,896),(0x852668,0x300),
   (0x36e460,524),(0x374050,128),(0x3ae320,76)]:
   for i in c.disasm(p.get_data(r,z),r):self.instructions[i.address]=i
  self.u.hook_add(UC_HOOK_CODE,self.hook);self.guard_stop=set();self.total=collections.Counter()
 def ret(self,value=None):
  if value is not None:self.u.reg_write(UC_ARM64_REG_X0,value)
  self.u.reg_write(UC_ARM64_REG_PC,self.u.reg_read(UC_ARM64_REG_LR))
 def hook(self,u,pc,size,user):
  r=pc-self.n.base
  if r in self.guard_stop:u.emu_stop();return
  if r==0x36d3d8 and self.building:u.emu_stop();return
  if r==0x39f070:
   assert u.reg_read(UC_ARM64_REG_X0)==self.manager;self.events["full_Configure_entry"]+=1
  if r==0x36d3d4:self.events["full_Configure_return"]+=1
  if r in INIT:
   assert self.live(u.reg_read(UC_ARM64_REG_X0))
   assert self.n.heap<=u.reg_read(UC_ARM64_REG_X1)<self.n.heap+0x30000
   self.events["Init_"+hex(r)]+=1
  if r in [0x39f390,0x39f6c4,0x39f914] and self.building:self.events["Init_return_"+hex(r)]+=1
  if r==0x39ea40:
   assert u.reg_read(UC_ARM64_REG_X0)==self.manager
   self.request=(u.reg_read(UC_ARM64_REG_W1),u.reg_read(UC_ARM64_REG_W2));self.scan=[]
   assert u.reg_read(UC_ARM64_REG_W4)==92 and u.reg_read(UC_ARM64_REG_X3)==self.output
  if r==0x39ead4:self.pending_type=u.reg_read(UC_ARM64_REG_W0)
  if r==0x39eb18:self.scan.append((u.reg_read(UC_ARM64_REG_W0),self.pending_type))
  if r==0x3a0db0:self.selected.append(u.reg_read(UC_ARM64_REG_X0))
  if r in [0x36e668,0x3740cc,0x3ae368,0x373fe8,0x39ec94,0x3a1130]:
   self.events["return_"+hex(r)]+=1
  if r==0xcae740:
   count=u.reg_read(UC_ARM64_REG_X0);assert count in [1664,160,40,32,328,24]
   at=self.cursor+32;self.cursor=at+((count+31)&~31)+32;assert self.cursor<self.n.heap+0x68000
   u.mem_write(at-32,b"\xa5"*32);u.mem_write(at+count,b"\xa5"*32)
   self.allocs.append((at,count));self.freed[at]=False;self.ret(at);return
  if r==0xf5e600:
   at=u.reg_read(UC_ARM64_REG_X0);size=u.reg_read(UC_ARM64_REG_X2)
   assert any(a<=at and at+size<=a+z for a,z in self.allocs)
   u.mem_write(at,bytes([u.reg_read(UC_ARM64_REG_X1)&255])*size);self.ret(at);return
  if r==0xcae730:
   at=u.reg_read(UC_ARM64_REG_X0);assert self.live(at)
   assert not self.building and next(z for a,z in self.allocs if a==at)==24
   self.freed[at]=True;self.ret();return
  if r==0xce7c98:self.ret(self.tls+0x3000);return
  if r==0xcfe600:raise AssertionError("owned diagnostic TLS must already exist")
  if r==0x1aca8:self.ret();return
  i=self.instructions.get(r)
  if i and i.mnemonic=="blr" and self.c.reg_name(i.operands[0].reg)=="x17":
   assert r in NUMERIC or r in LOG,"unqualified checked dispatch"
   target=u.reg_read(UC_ARM64_REG_X15 if r in [0x85276c,0x39f330,0x39f60c,0x39f8ac] else UC_ARM64_REG_X8)
   if r in LOG:
    assert target==struct.unpack("<Q",u.mem_read(self.n.base+0x16a4230,8))[0]==0
    target=self.n.base+0x1a8c0;self.events["controlled_diagnostic"]+=1
   else:assert target-self.n.base in NUMERIC[r];self.events["checked_numeric_dispatch"]+=1
   u.reg_write(UC_ARM64_REG_X15,target);u.reg_write(UC_ARM64_REG_PC,pc+4)
 def live(self,at):return at in self.freed and not self.freed[at]
 def guards(self):
  for at,size in self.allocs:
   assert bytes(self.u.mem_read(at-32,32))==bytes(self.u.mem_read(at+size,32))==b"\xa5"*32
 def build(self,source,bias):
  u=self.u;n=self.n;h=n.heap;self.bias=bias
  u.mem_write(h,bytes(0x100000));u.mem_write(n.stack,bytes(0x10000))
  u.mem_write(h,bytes(source.n.u.mem_read(h,0x30000)))
  self.source_before=bytes(u.mem_read(h,0x30000))
  payload=source.allocs[0][0]+0x120
  self.source_counts=[struct.unpack("<I",u.mem_read(payload+off,4))[0] for off in [44,64,80]]
  self.expected_count=sum(self.source_counts);assert self.source_counts[0]==4 and 0<self.expected_count<=20
  self.interface=h+0x42000+bias;self.core=h+0x44000+bias;self.tls=h+0x48000
  self.inner=h+0x4a000+bias;self.output=h+0x4b000+bias;self.desc=h+0x4c000+bias
  self.inputs=h+0x4d000+bias;self.engine=h+0x4e000+bias;self.outer=h+0x4f000+bias
  self.cursor=h+0x50000+bias;self.manager=self.cursor+32
  self.allocs=[];self.freed={};self.events=collections.Counter();self.building=True;self.selected=[]
  u.mem_write(self.inner+8,struct.pack("<Q",self.interface))
  u.mem_write(self.interface,struct.pack("<Q",self.core))
  u.mem_write(self.interface+0x138,struct.pack("<Q",n.base+0x3a8730))
  u.mem_write(self.core,struct.pack("<QQ",n.base+0x1338428,n.base+0x13383b8))
  # Original accessors execute; core module placement and ordinary flag storage are owned interfaces.
  u.mem_write(self.core+0xff0,struct.pack("<Q",source.allocs[0][0]+0x120))
  u.mem_write(self.core+0xf20,struct.pack("<Q",h+0x47000+bias))
  u.mem_write(self.tls+88,struct.pack("<Q",self.tls+0x1000))
  u.mem_write(self.tls+0x1000,struct.pack("<64Q",*([self.tls+0x2000]*64)))
  u.mem_write(self.tls+0x2000+20,struct.pack("<I",1));u.reg_write(UC_ARM64_REG_X18,self.tls)
  u.reg_write(UC_ARM64_REG_X0,1664);u.reg_write(UC_ARM64_REG_X20,self.inner)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(n.base+0x36d338,n.end,count=200000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x36d3d8
  assert self.events["full_Configure_entry"]==self.events["full_Configure_return"]==1
  assert [z for a,z in self.allocs[:3]]==[1664,160,160]
  assert struct.unpack("<3I",u.mem_read(self.manager+0x610,12))==(0,self.expected_count,20)
  assert struct.unpack("<3I",u.mem_read(self.manager+0x628,12))==(0,0,20)
  self.ring=struct.unpack("<Q",u.mem_read(self.manager+0x608,8))[0]
  assert self.ring==self.allocs[1][0]
  assert struct.unpack("<Q",u.mem_read(self.manager+0x620,8))[0]==self.allocs[2][0]
  self.nodes=list(struct.unpack("<"+str(self.expected_count)+"Q",u.mem_read(self.ring,self.expected_count*8)))
  assert self.nodes==[a for a,z in self.allocs[3:]]
  assert bytes(u.mem_read(self.ring+self.expected_count*8,160-self.expected_count*8))==bytes(160-self.expected_count*8)
  assert self.events["Init_0x3a0d70"]==self.source_counts[0]
  assert self.events["Init_0x3a14e0"]+self.events["Init_0x39d7e0"]==self.source_counts[1]
  assert self.events["Init_0x3a2440"]==self.source_counts[2]
  assert [self.events["Init_return_"+hex(r)] for r in [0x39f390,0x39f6c4,0x39f914]]==self.source_counts
  self.cache_array=source.allocs[1][0]
  for k,node in enumerate(self.nodes[:4]):
   assert struct.unpack("<Q",u.mem_read(node+24,8))[0]==self.cache_array+k*120
  assert bytes(u.mem_read(h,0x30000))==self.source_before
  self.guards();self.total["source_collection_builds"]+=1;self.total["source_stats_Init_returns"]+=self.expected_count
  self.building=False
  u.mem_write(self.inner,struct.pack("<Q",n.base+0x1337fd8))
  u.mem_write(self.inner+40,struct.pack("<Q",self.manager))
  u.mem_write(self.engine+0x1088,struct.pack("<Q",self.outer))
  u.mem_write(self.outer+8,struct.pack("<Q",n.base+0x36e460))
  u.mem_write(self.outer+40,struct.pack("<Q",self.inner))
 def query(self,selector,context,allocated=92,kind=None):
  u=self.u;n=self.n;self.selected=[];self.events=collections.Counter()
  u.mem_write(self.output,b"\xa5"*160)
  u.mem_write(self.desc,struct.pack("<3Q",self.output,allocated,(10 if selector==12 else 21) if kind is None else kind))
  u.mem_write(self.outer+68,struct.pack("<I",context))
  before=bytes(u.mem_read(n.heap,0x100000));cursor_before=self.cursor
  for i,value in enumerate([self.engine,selector,self.inputs,self.desc,1]):u.reg_write(globals()["UC_ARM64_REG_X"+str(i)],value)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(n.base+0x852668,n.end,count=200000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end and u.reg_read(UC_ARM64_REG_X0)==0
  assert struct.unpack("<I",u.mem_read(self.tls+0x2000+304,4))[0]==context
  assert self.events["return_0x36e668"]==self.events["return_0x3740cc"]==self.events["return_0x3ae368"]==1
  self.guards();assert all(self.freed[a] for a,z in self.allocs if z==24)
  after=bytes(u.mem_read(n.heap,0x100000))
  allowed=[(self.output,92),(self.desc+12,4),(cursor_before,self.cursor-cursor_before),(self.tls+0x2000+304,4)]
  for at,(a,b) in enumerate(zip(before,after)):
   if a!=b:assert any(lo<=n.heap+at<lo+count for lo,count in allowed),"unexpected query heap delta"
  assert bytes(u.mem_read(n.heap,0x30000))==self.source_before
  written=struct.unpack("<I",u.mem_read(self.desc+12,4))[0]
  if allocated<92 or kind is not None:
   assert written==0 and not self.selected and bytes(u.mem_read(self.output,160))==b"\xa5"*160
   self.total["descriptor_rejections"]+=1;return None
  assert written==92 and self.request==(0,0) and len(self.scan)==self.expected_count
  # Source scans by requested role, immediately accepts exact type, otherwise retains last matching role.
  eligible=[k for k,(role,typ) in enumerate(self.scan) if role==self.request[0]]
  exact=[k for k in eligible if self.scan[k][1]==self.request[1]]
  assert not exact and eligible==[0,1,2,3]
  assert self.selected==[self.nodes[eligible[-1]]]==[self.nodes[3]]
  assert self.events["return_0x39ec94"]==self.events["return_0x3a1130"]==1
  output=bytes(u.mem_read(self.output,92))
  assert output[68:80]==bytes(u.mem_read(self.cache_array+3*120+20,12))
  assert bytes(u.mem_read(self.output+92,68))==b"\xa5"*68
  self.total["full_collection_positive_queries"]+=1
  self.total["fallback_last_matching_source_grid"]+=1
  return output
 def exact_source_grid_queries(self):
  u=self.u;n=self.n
  for typ,index in [(3,0),(4,1),(5,2)]:
   self.selected=[];self.events=collections.Counter()
   u.mem_write(self.output,b"\xa5"*160);u.mem_write(self.desc+12,bytes(4))
   before=bytes(u.mem_read(n.heap,0x100000))
   for i,value in enumerate([self.manager,0,typ,self.output,92,self.desc+8]):u.reg_write(globals()["UC_ARM64_REG_X"+str(i)],value)
   u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
   u.emu_start(n.base+0x39ea40,n.end,count=200000)
   assert u.reg_read(UC_ARM64_REG_PC)==n.end and u.reg_read(UC_ARM64_REG_X0)==1
   assert self.request==(0,typ) and self.scan[-1]==(0,typ)
   assert self.selected==[self.nodes[index]],"first exact source record, including repeated type3"
   assert struct.unpack("<I",u.mem_read(self.desc+12,4))[0]==0,"manager does not publish a descriptor count"
   assert bytes(u.mem_read(self.output+68,12))==bytes(u.mem_read(self.cache_array+index*120+20,12))
   assert bytes(u.mem_read(self.output+92,68))==b"\xa5"*68
   after=bytes(u.mem_read(n.heap,0x100000));allowed=[(self.output,92)]
   for at,(a,b) in enumerate(zip(before,after)):
    if a!=b:assert any(lo<=n.heap+at<lo+count for lo,count in allowed),"unexpected exact-query heap delta"
   self.guards();self.total["first_exact_source_grid_queries"]+=1
 def append_boundaries(self,bias):
  u=self.u;n=self.n;h=n.heap;mgr=h+0x70000+bias;ring=h+0x71000+bias;node=h+0x72000+bias
  count=0
  for start,end,full in [(0x39f390,0x39f3d0,0x39f450),(0x39f6c4,0x39f704,0x39f790),(0x39f914,0x39f954,0x39fa98)]:
   for head,used,capacity in [(0,0,20),(0,19,20),(19,1,20),(19,19,20),(0,20,20),(0,21,20),(0,0,0)]:
    u.mem_write(mgr,bytes(0x680));u.mem_write(ring,b"\xa5"*160)
    u.mem_write(mgr+0x608,struct.pack("<QIII",ring,head,used,capacity))
    u.mem_write(n.stack+0xf000+32,struct.pack("<Q",mgr));u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000)
    u.reg_write(UC_ARM64_REG_X19,node)
    before=bytes(u.mem_read(h+0x70000,0x30000))
    self.guard_stop={end,full};u.emu_start(n.base+start,n.end,count=30)
    expected=bytearray(before);accepted=used<capacity
    assert u.reg_read(UC_ARM64_REG_PC)==n.base+(end if accepted else full)
    if accepted:
     at=ring-(h+0x70000)+8*((head+used)%capacity)
     expected[at:at+8]=struct.pack("<Q",node)
     at=mgr-(h+0x70000)+0x614;expected[at:at+4]=struct.pack("<I",used+1)
    assert bytes(u.mem_read(h+0x70000,0x30000))==expected,"complete append/guard heap delta"
    count+=1
  self.guard_stop=set();self.total["original_append_boundary_cases"]+=count
def main():
 p,c,facts=authority();f=Collection(p,c);audit=[]
 for name,pin in BB.AZ.AV.FILES:
  blob=(BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  source=BB.FourGrid(blob);source.run(source.wire,0,full_parent=True)
  for bias in [0,1,0x40,0x1230]:
   f.build(source,bias)
   f.exact_source_grid_queries()
   for context in [0,1,0xffffffff]:
    assert f.query(12,context)==f.query(20,context)
   for selector in [12,20]:
    for size,kind in [(0,None),(91,None),(92,0xffffffff)]:assert f.query(selector,0,size,kind) is None
  audit.append({"source_sha256":pin,"source_parent_reader_returned":True,"source_stats_objects_per_collection":f.expected_count,"source_module_array_counts":f.source_counts})
  print(json.dumps({"experiment":"E011CA","completed_source_files":len(audit),"counts":dict(f.total)}),flush=True)
 for bias in [0,1,0x40,0x1230]:f.append_boundaries(bias)
 out={"experiment":"E011CA","status":"PASS_BOUNDED_SOURCE_COLLECTION_CREATION_AND_FALLBACK_QUERY",
  "base_commit":BASE,**facts,**dict(f.total),"source_files":audit,"placements":4,"contexts":3,
  "source_collection_creation_fragment_RVA":"0x36D338","fragment_stop_before_following_setup_RVA":"0x36D3D8",
  "full_original_ConfigureHWStats_RVA":"0x39F070","numeric_callbacks_unmodified":True,
  "original_allocation_zeroing_call_sites_ring_capacity_and_append_executed":True,
  "ordinary_selectors":[12,20],"owned_empty_input_query_role_and_type":[0,0],
  "exact_manager_selection_query_does_not_claim_descriptor_count_ABI":True,
  "bounded_fallback_policy":"last matching role when exact type absent",
  "selected_source_grid_record_zero_based":3,"full_source_collection_counts":[a["source_stats_objects_per_collection"] for a in audit],
  "complete_Query_and_append_heap_deltas_checked":True,"source_heap_and_allocation_canaries_preserved":True,
  "original_full_outer_context_setter_query_returns":f.total["full_collection_positive_queries"]+f.total["descriptor_rejections"],
  "controlled_interfaces":["caller-prefix X20 input and source allocator-size argument","core module slots and ordinary flag storage","inner/outer/core ownership","allocation/free/zeroing","checked dispatch","TLS diagnostics and logging"],
  "full_following_setup_39FAF8_qualified":False,"whole_original_outer_constructor_qualified":False,
  "live_primary_request_role_and_type_qualified":False,"actual_live_inner_vtable_or_context_ID_captured":False,
  "actual_opened_filename_closed":False,"native_rear_runtime_allowed":False,
  "new_camera_Starts":0,"new_reboots":0,"original_bytes_exported":False}
 (HERE/"COLLECTION-SAFE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps(out),flush=True)
if __name__=="__main__":main()
