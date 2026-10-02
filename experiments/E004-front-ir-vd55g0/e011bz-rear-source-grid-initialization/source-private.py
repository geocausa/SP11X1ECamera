#!/usr/bin/env python3
"""Same-SP11 source-derived grid Init and initialized typed query; no OS/driver calls."""
from pathlib import Path
import importlib.util,struct,json,hashlib,collections
import pefile,capstone
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent
BASE="01c3e15659545965841c20ddff988054bcc11022"
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
BY=load("bz_previous",EX/"e011by-rear-query-forwarder-context/source-private.py")
BB=BY.BW.BB
def authority():
 raw=BY.BW.N.DLL.read_bytes();assert hashlib.sha256(raw).hexdigest()==BY.BW.N.DLL_SHA
 p=pefile.PE(data=raw);cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);cs.detail=True
 def ins(r):return next(cs.disasm(p.get_data(r,4),r))
 # This is the same process-wide diagnostic callback slot used by the outer logger.
 i=ins(0x39ec48);assert i.mnemonic=="adrp" and cs.reg_name(i.operands[0].reg)=="x8"
 page=i.operands[1].imm
 i=ins(0x39ec4c);assert i.mnemonic=="ldr" and cs.reg_name(i.operands[0].reg)=="x8"
 assert cs.reg_name(i.operands[1].mem.base)=="x8" and i.operands[1].mem.disp==560
 assert page+560==0x16a4230
 for r in [0x39ec68]:
  assert ins(r).mnemonic=="blr" and cs.reg_name(ins(r).operands[0].reg)=="x17"
  assert ins(r+4).mnemonic=="blr" and cs.reg_name(ins(r+4).operands[0].reg)=="x15"
 assert struct.unpack("<Q",p.get_data(0x13381a0,8))[0]==p.OPTIONAL_HEADER.ImageBase+0x3a0d70
 assert ins(0x3a0da0).mnemonic=="ret"
 return {"original_DLL_sha256":BY.BW.N.DLL_SHA,
 "source_grid_vtable_RVA":"0x13381A0","source_Init_slot_offset":0,
 "source_Init_RVA":"0x3A0D70","normalization_helper_RVA":"0x388630",
 "initialized_grid_diagnostic_dispatch_RVA":"0x39EC68",
 "diagnostic_global_callback_slot_RVA":"0x16A4230",
 "source_ranges":[{"RVA":hex(r),"bytes":count,"sha256":hashlib.sha256(p.get_data(r,count)).hexdigest()} for r,count in [(0x3a0d70,52),(0x388630,316),(0x39ec40,48)]]}
def sources():
 cases=[];audit=[]
 for name,pin in BB.AZ.AV.FILES:
  blob=(BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  _,sy,wire,info=BB.source(blob)
  source=BB.FourGrid(blob);source.run(wire,0,full_parent=True)
  array=source.allocs[1][0]
  for index in range(4):
   cache=bytes(source.n.u.mem_read(array+index*120,120))
   nested=struct.unpack_from("<Q",cache,104)[0]
   child=bytes(source.n.u.mem_read(nested,4))
   assert cache[20:32]==wire[101*index+20:101*index+32]
   cases.append((cache,child))
  audit.append({"source_sha256":pin,"source_grid_records":4,
   "full_original_parent_reader_returned":True,"original_nested_data_shape_checked":True})
 return cases,audit
class Initialized(BY.Forward):
 def __init__(self):
  super().__init__();self.native_backend=True;self.init_count=0;self.initializer_events=[]
  self.accepted_queries=0;self.diagnostic_calls=0;self.mask_nonzero=0
 def hook(self,u,pc,size,user):
  r=pc-self.n.base
  if r==0x3a0d70:self.initializer_events.append("Init_entry")
  if r==0x388630:
   assert u.reg_read(UC_ARM64_REG_W0)==struct.unpack("<I",u.mem_read(self.src+88,4))[0]
   self.initializer_events.append("normalizer_entry")
  if r==0x3a0da0:self.initializer_events.append("Init_return")
  if r==0x39ec68:
   # The source loads this target from a process-wide diagnostic slot, not the grid vtable.
   target=struct.unpack("<Q",u.mem_read(self.n.base+0x16a4230,8))[0]
   assert u.reg_read(UC_ARM64_REG_X8)==target
   self.stubs["initialized_grid_diagnostic_interface"]+=1
   self.diagnostic_calls+=1
   u.reg_write(UC_ARM64_REG_X15,self.n.base+0x1a8c0);u.reg_write(UC_ARM64_REG_PC,pc+4);return
  super().hook(u,pc,size,user)
 def reset(self,*args,**kwargs):
  super().reset(*args,**kwargs)
  u=self.u;n=self.n;self.initializer_events=[]
  # The reader-proven one-element "data" child is relocated by its typed pointer member.
  self.child=n.heap+0x23000
  u.mem_write(self.child,self.current_child)
  u.mem_write(self.src+104,struct.pack("<Q",self.child))
  before=bytes(u.mem_read(n.heap,0x30000))
  result=self.call(0x3a0d70,[self.grid,self.src])
  mask=bytes(u.mem_read(self.grid+32,4))
  expected=bytearray(before)
  at=self.grid-n.heap+24;expected[at:at+8]=struct.pack("<Q",self.src)
  at=self.grid-n.heap+32;expected[at:at+4]=mask
  assert bytes(u.mem_read(n.heap,0x30000))==expected,"full source Init complete heap delta"
  assert self.initializer_events==["Init_entry","normalizer_entry","Init_return"]
  assert result==struct.unpack("<I",mask)[0],"observed return equals normalized field, not a status contract"
  self.init_count+=1;self.mask_nonzero+=struct.unpack("<I",mask)[0]!=0
  self.initialized_cache=bytes(u.mem_read(self.src,120))
  self.events=[];self.forward_events=[];self.stubs.clear();self.writes=[]
 def run(self,cache,bias,selector,allocated=92,kind=None):
  # BW's independent guard expects the relocated source cache rather than an old absolute pointer.
  relocated=bytearray(cache);struct.pack_into("<Q",relocated,104,self.n.heap+0x23000)
  result=super().run(bytes(relocated),bias,selector,allocated,kind)
  assert bytes(self.u.mem_read(self.child,4))==self.current_child
  assert bytes(self.u.mem_read(self.src,120))==self.initialized_cache
  return result
def main():
 facts=authority();cases,audit=sources();f=Initialized()
 positive=negative=0
 for bias in [0,1,0x40,0x1230]:
  for cache,child in cases:
   f.current_child=child
   for context in [0,1,0xffffffff]:
    a=f.supported(cache,bias,12,context);b=f.supported(cache,bias,20,context)
    assert a==b and a[68:80]==cache[20:32]
    positive+=2
  print(json.dumps({"experiment":"E011BZ","initialized_positive_queries_completed":positive}),flush=True)
  f.current_child=cases[0][1];f.context_id=0
  for selector in [12,20]:
   for size,kind in [(0,None),(91,None),(92,0xffffffff)]:
    assert f.run(cases[0][0],bias,selector,size,kind) is None
    negative+=1
 out={"experiment":"E011BZ","status":"PASS_BOUNDED_ORIGINAL_GRID_INIT_AND_INITIALIZED_TYPED_QUERY",
  "base_commit":BASE,**facts,"source_files":audit,
  "source_grid_records":len(cases),"source_full_parent_reader_returns":3,
  "owned_placements":4,"owned_context_patterns":3,"initialized_positive_queries":positive,
  "initialized_descriptor_rejections":negative,"complete_original_grid_Init_returns":f.init_count,
  "complete_original_normalizer_returns":f.init_count,"nonzero_source_normalized_masks":f.mask_nonzero,
  "initialized_diagnostic_interface_calls":f.diagnostic_calls,
  "source_Init_return_is_not_claimed_as_status":True,
  "source_normalized_field_offset":32,"source_normalizer_enum_member_offset":88,
  "source_cache_pointer_offset":24,"typed_nested_child_pointer_offset":104,
  "typed_nested_child_bytes":4,"numeric_callbacks_unmodified":True,
  "complete_Init_heap_delta_and_source_children_preserved":True,
  "source_weights_match_typed_query_and_primary_conversion":True,
  "controlled_interfaces":["one-primary-grid manager ownership","inner/core/outer composition",
  "checked dispatch","allocation/free","TLS diagnostics","logging"],
  "earlier_mask_zero_query_fixture_remains_bounded":True,
  "earlier_numeric_classification_of_39EC68_corrected_here":True,
  "whole_source_ConfigureHWStats_or_outer_constructor_qualified":False,
  "source_primary_grid_selection_policy_qualified":False,
  "actual_live_inner_vtable_or_context_ID_captured":False,
  "actual_opened_filename_closed":False,"native_rear_runtime_allowed":False,
  "new_camera_Starts":0,"new_reboots":0,"original_bytes_exported":False}
 (HERE/"INITIALIZED-SAFE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps(out),flush=True)
if __name__=="__main__":main()
