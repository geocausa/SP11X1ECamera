#!/usr/bin/env python3
"""E011BJ: original reader pre-callback mapping and metadata numeric widths."""
from pathlib import Path
import importlib.util,hashlib,json,struct,pefile,capstone
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;EX=HERE.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
BI=load("bj_reader",EX/"e011bi-rear-aec-reader-context-prefix/source-private.py");BH=BI.BH
def facts():
 b=BH.FIXTURE.DLL.read_bytes();assert hashlib.sha256(b).hexdigest()==BH.FIXTURE.SHA
 p=pefile.PE(data=b);c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);c.detail=True
 for site,role,base,off in [(0x6f4630,"x2","x19",60),(0x6f4638,"x4","x19",72),(0x123d60,"x4","x19",60),(0x123d68,"w3","x19",68)]:
  i=next(c.disasm(p.get_data(site,4),site));assert c.reg_name(i.operands[0].reg)==role and c.reg_name(i.operands[-1].mem.base)==base and i.operands[-1].mem.disp==off
 i=next(c.disasm(p.get_data(0x123d70,4),0x123d70));assert i.mnemonic=="mov" and c.reg_name(i.operands[0].reg)=="x2" and i.operands[1].imm==10
 return {"metadata_x2_u64_store_rva":"0x6F4630","metadata_x2_output_offset":60,"metadata_x4_u64_store_rva":"0x6F4638","metadata_x4_output_offset":72,"parent_x4_u64_reader_load_rva":"0x123D60","parent_x4_reader_offset":60,"parent_x3_u32_reader_load_rva":"0x123D68","parent_x3_reader_offset":68,"parent_x2_literal_rva":"0x123D70","parent_x2_literal":10,"reader_pre_callback_boundary_rva":"0x6F4A7C","callback_dispatch_rva":"0x6F4A98"}
class Meta(BH.Owned):
 def constructor64(self,a2,a3,a4,bias):
  assert isinstance(a2,int) and 0<=a2<(1<<64) and isinstance(a3,int) and 0<=a3<(1<<32) and isinstance(a4,int) and 0<=a4<(1<<64)
  label=b"OwnedWidthMetadata";profile=b"owned-profile";filename=b"owned-fixture.bin"
  canonical=self.name(label,bias)
  n=self.n;u=self.reset(bias);obj=n.heap+0x4000+bias;ptrs=[n.heap+off+bias for off in [0x1000,0x1200,0x1400]]
  for ptr,text in zip(ptrs,[label,profile,filename]):u.mem_write(ptr,text+b"\0")
  before=bytes(u.mem_read(n.heap,0x30000))
  self.invoke(0x6f45d8,[obj,ptrs[0],a2,a3,a4,ptrs[1],ptrs[2]])
  out=bytes(u.mem_read(obj,384));allocated=self.f.allocs[0][0]
  assert u.reg_read(UC_ARM64_REG_X0)==obj and len(self.f.allocs)==1 and self.f.allocs[0][1]==len(label)+1
  desired=bytearray(before);fields=[(0,struct.pack("<Q",n.base+0x133b770)),(8,struct.pack("<Q",allocated)),(16,canonical),(56,bytes(4)),(60,struct.pack("<Q",a2)),(68,struct.pack("<I",a3)),(72,struct.pack("<Q",a4)),(80,profile+b"\0"),(208,filename+b"\0"),(280,bytes(8))]
  for off,value in fields:
   assert out[off:off+len(value)]==value
   at=obj-n.heap+off;desired[at:at+len(value)]=value
  at=allocated-n.heap;desired[at:at+len(label)+1]=label+b"\0"
  assert bytes(u.mem_read(n.heap,0x30000))==desired
  assert all(bytes(u.mem_read(at,32))==bytes([0xa5])*32 for at in self.f.redzones)
  assert set(self.f.stub_counts)<=set(["0x11d0","0x11f0","0xcae740","0xf5e600"])
class Reader:
 def __init__(self,blob,layout_source=None):
  seed=blob if layout_source is None else layout_source
  self.h,self.sy,_,self.info=BH.FIXTURE.source(seed);self.blob=blob;self.o=BH.Owned(seed);self.n=self.o.n
  assert len(blob)==len(seed), "owned variant must retain pinned source layout"
  self.map=0x76000000;self.size=((len(blob)+0x10000+4095)//4096)*4096;self.n.u.mem_map(self.map,self.size)
 def run(self,bias):
  n=self.n;u=self.o.reset(bias);obj=n.heap+0x4000+bias;cursor=n.heap+0x2000+bias;context=n.heap+0x3000+bias;interface=n.heap+0x6000+bias
  filebase=self.map+bias;r=self.sy[self.info["root_symbol_id"]];off=r["record_offset"];record=self.blob[off:off+56]
  u.mem_write(self.map,bytes([0xa5])*self.size);u.mem_write(filebase,self.blob)
  u.mem_write(cursor,struct.pack("<Q",off));u.mem_write(context,bytes(128));u.mem_write(obj,struct.pack("<Q",context))
  before=bytes(u.mem_read(n.heap,0x30000));file_before=bytes(u.mem_read(self.map,self.size))
  # x4 is the object section offset relative to x1 file base; x5 is not used before the boundary.
  for i,value in enumerate([obj,filebase,len(self.blob),cursor,self.h["sections"][1]["offset"],interface,1]):u.reg_write(globals()["UC_ARM64_REG_X"+str(i)],value)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(n.base+0x6f47b8,n.base+0x6f4a7c,count=10000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x6f4a7c
  relative,length=struct.unpack_from("<II",record,48)
  fields=[(8,record[:4]),(12,record[4:36]+b"\0"),(52,record[36:44]),(68,record[44:48]),(72,b"\0"),(200,record[52:56]),(208,struct.pack("<Q",filebase+self.h["sections"][1]["offset"]+relative))]
  expected=bytearray(before)
  for at,value in fields:
   assert bytes(u.mem_read(obj+at,len(value)))==value
   ix=obj-n.heap+at;expected[ix:ix+len(value)]=value
  ix=cursor-n.heap;expected[ix:ix+8]=struct.pack("<Q",off+56)
  assert bytes(u.mem_read(n.heap,0x30000))==expected
  assert bytes(u.mem_read(self.map,self.size))==file_before
  assert self.o.f.copies==[(obj+12,filebase+off+4,32)]
  assert not self.o.f.allocs and not self.o.f.stub_counts
  assert bytes(u.mem_read(obj+60,8))==bytes([0xa5])*8
def main():
 anchors=facts();roots=[];audit=[]
 for name,sha in BH.FIXTURE.AV.FILES:
  blob=(BH.FIXTURE.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  h,sy,_,info=BH.FIXTURE.source(blob);r=sy[info["root_symbol_id"]];assert r["type"]=="aecxhwstatsconfig"
  roots.append(blob);audit.append({"path":name,"sha256":sha,"typed_root_symbol_id":r["symbol_id"]})
 blob=roots[-1];_,sy,_,info=BH.FIXTURE.source(blob);off=sy[info["root_symbol_id"]]["record_offset"]
 variants=list(roots)
 for packed,scalar in [(0,0),(1<<32,1),(0x123456789abcdef0,6),((1<<64)-1,(1<<32)-1),(0x8000000000000000,0x80000000),(0x000000010000000a,6),(0xabcdef0100000000,7),(0x0000ffff0000ffff,0)]:
  b=bytearray(blob);struct.pack_into("<QI",b,off+36,packed,scalar);variants.append(bytes(b))
 reader_cases=0
 for index,data in enumerate(variants):
  f=Reader(data,None if index<3 else roots[-1])
  for bias in [0,1,0x1230,0x8010]:f.run(bias);reader_cases+=1
 cases=[(0,0,0),(10,6,0),(1<<32,1,0),(0,2,1<<32),((1<<64)-1,(1<<32)-1,(1<<64)-1),(0x123456789abcdef0,6,0xfedcba9876543210),(0x8000000000000000,0x80000000,1),(0xffffffff,0,0xffffffff),(0x000000010000000a,7,0x0000000200000003),(0xabcdef0100000000,123,0x1234567800000000),(0x0000ffff0000ffff,0,0xffff0000ffff0000),(0x1111111122222222,0x33333333,0x4444444455555555)]
 meta=Meta(blob);metadata_cases=0
 for bias in [0,1,0x1230,0x8010]:
  for a2,a3,a4 in cases:meta.constructor64(a2,a3,a4,bias);metadata_cases+=1
 rejected=0
 for index in [0,1,2]:
  for value in [-1,(1<<32) if index==1 else (1<<64)]:
   args=[10,6,0];args[index]=value;before=bytes(meta.n.u.mem_read(meta.n.heap,0x30000))
   try:meta.constructor64(*args,0)
   except AssertionError:rejected+=1
   else:raise AssertionError("scope input accepted")
   assert bytes(meta.n.u.mem_read(meta.n.heap,0x30000))==before
 result={"experiment":"E011BJ","status":"PASS_BOUNDED_READER_PRE_CALLBACK_AND_ORIGINAL_METADATA_U64_WIDTHS_PROFILE_INTERFACE_OPEN","base_commit":"847796d7475f4bfe781130903da5e2b99256bb04","original_DLL_sha256":BH.FIXTURE.SHA,"source_files":audit,"anchors":anchors,"original_reader_pre_callback_cases":reader_cases,"typed_pinned_source_reader_cases":12,"owned_wide_record_reader_cases":32,"original_metadata_constructor_full_returns":metadata_cases,"independent_original_name_helper_returns":metadata_cases,"embedded_original_name_helper_calls":metadata_cases,"metadata_width_scope_rejections_before_execution":rejected,"memory_placements":4,"reader_wire_36_44_to_runtime_52_60_bytes":8,"reader_wire_44_48_to_runtime_68_72_bytes":4,"reader_wire_52_56_to_runtime_200_204_bytes":4,"reader_payload_pointer_formula":"x1_file_base + x4_object_section_offset + wire_u32_at_48","reader_cursor_advance":56,"reader_profile_first_byte_zeroed":True,"reader_callback_u64_output_60_68_unchanged_before_dispatch":True,"metadata_x2_width":64,"metadata_x3_width":32,"metadata_x4_width":64,"metadata_x2_high_half_preserved_at_64":True,"metadata_x4_high_half_preserved_at_76":True,"metadata_offsets_64_76_always_zero_claim_rejected":True,"earlier_E011BH_U32_fixture_passes_remain_valid":True,"earlier_numeric_minor_and_tag_labels_not_general_policy_authority":True,"numeric_propagation_not_version_or_selector_policy":True,"all_heap_and_source_bytes_outside_qualified_writes_preserved":True,"metadata_allocation_canaries_preserved":True,"reader_prefix_stubs_executed":False,"reader_callback_executed":False,"full_reader_constructor_return_claimed":False,"parser_interface_target_qualified":False,"full_parent_metadata_stubs_removed":False,"whole_parent_metadata_materialization_closed":False,"exact_opened_tuning_filename_closed":False,"whole_profile_materialization_closed":False,"whole_loader_alignment_policy_closed":False,"every_grid_member_validated":False,"cold_metadata_bridge_closed":False,"RS_count_offset_authority_closed":False,"complete_deterministic_bootstrap_closed":False,"WM16_retirement_closed":False,"Linux_optical_parity_closed":False,"captured_scalars_used_as_producer_inputs":False,"private_original_bytes_exported":False,"production_C_changed":False,"new_kernel_build_performed":False,"runtime_actions_performed":False,"observer_armed":False,"new_camera_starts":0,"new_reboots":0,"native_rear_runtime_allowed":False}
 (HERE/"WIDTH-READER-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in result.items() if k!="source_files"},indent=2))
if __name__=="__main__":main()
