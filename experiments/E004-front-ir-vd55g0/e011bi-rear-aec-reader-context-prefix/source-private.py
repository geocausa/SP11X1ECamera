#!/usr/bin/env python3
"""E011BI: bounded original reader initializer and ID/name prefix, private same-SP11."""
from pathlib import Path
import importlib.util,hashlib,json,struct,pefile,capstone
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;EX=HERE.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
BH=load("bi_metadata",EX/"e011bh-rear-aec-metadata-authority/source-private.py")
def facts():
 b=BH.FIXTURE.DLL.read_bytes();assert hashlib.sha256(b).hexdigest()==BH.FIXTURE.SHA
 p=pefile.PE(data=b);c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);c.detail=True
 for site,target in [(0x6f4e84,0x6f47b8),(0x6f4864,0xf5d480)]:
  i=next(c.disasm(p.get_data(site,4),site));assert i.mnemonic=="bl" and i.operands[0].imm==target
 for site,base,offset in [(0x6f4a7c,"x5",0),(0x6f4a84,"x8",0)]:
  i=next(c.disasm(p.get_data(site,4),site));assert i.mnemonic=="ldr" and c.reg_name(i.operands[-1].mem.base)==base and i.operands[-1].mem.disp==offset
 i=next(c.disasm(p.get_data(0x6f4a98,4),0x6f4a98));assert i.mnemonic=="blr" and c.reg_name(i.operands[0].reg)=="x15"
 return {"initializer_rva":"0x6F4790","table_builder_rva":"0x6F4CA8","initializer_reference_is_not_claimed_as_direct_call":True,"reader_constructor_rva":"0x6F47B8","reader_constructor_call_rva":"0x6F4E84","original_name_memcpy_call_rva":"0x6F4864","prefix_boundary_rva":"0x6F4870","later_parser_interface_dispatch_rva":"0x6F4A98","later_parser_interface_dispatch_executed":False}
def owned_record(label,sid):
 assert isinstance(label,bytes) and len(label)<=32 and b"\0" not in label and all(x<128 for x in label)
 assert isinstance(sid,int) and 0<=sid<=0xffffffff
 return struct.pack("<I",sid)+label.ljust(32,b"\0")+struct.pack("<IIIII",0x00020001,0,0xffffffff,12,48)
class Reader:
 def __init__(self,blob):
  self.o=BH.Owned(blob);self.n=self.o.n
 def initializer(self,bias):
  n=self.n;u=self.o.reset(bias);obj=n.heap+0x4000+bias
  before=bytes(u.mem_read(n.heap,0x30000));self.o.invoke(0x6f4790,[obj])
  expected=bytearray(before)
  for offset,length in [(0,8),(52,16),(208,16)]:
   at=obj-n.heap+offset;expected[at:at+length]=bytes(length)
  assert bytes(u.mem_read(n.heap,0x30000))==expected
  assert not self.o.f.allocs and not self.o.f.stub_counts and not self.o.f.copies
 def prefix(self,record,bias,start):
  assert len(record)==56 and 0<=start<=31
  label=record[4:36].split(b"\0",1)[0];assert all(x<128 for x in label)
  n=self.n;u=self.o.reset(bias);obj=n.heap+0x4000+bias;src=n.heap+0x1000+bias;cursor=n.heap+0x2000+bias;context=n.heap+0x3000+bias;payload=n.heap+0x5000+bias;interface=n.heap+0x6000+bias
  packed=bytes([0x5a])*start+record
  u.mem_write(src,packed);u.mem_write(cursor,struct.pack("<Q",start));u.mem_write(obj,struct.pack("<Q",context))
  before=bytes(u.mem_read(n.heap,0x30000))
  # x2 is available source bytes, x3 points to an offset; neither is a name length.
  for i,value in enumerate([obj,src,len(packed),cursor,payload,interface,1]):
   u.reg_write(globals()["UC_ARM64_REG_X"+str(i)],value)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(n.base+0x6f47b8,n.base+0x6f4870,count=10000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x6f4870
  assert bytes(u.mem_read(obj+8,4))==record[:4]
  assert bytes(u.mem_read(obj+12,33))==record[4:36]+b"\0"
  assert bytes(u.mem_read(cursor,8))==struct.pack("<Q",start)
  assert self.o.f.copies==[(obj+12,src+start+4,32)]
  expected=bytearray(before)
  for offset,data in [(8,record[:4]),(12,record[4:36]+b"\0"),(208,bytes(8))]:
   at=obj-n.heap+offset;expected[at:at+len(data)]=data
  assert bytes(u.mem_read(n.heap,0x30000))==expected
  assert not self.o.f.allocs and not self.o.f.stub_counts
def main():
 anchors=facts();roots=[];audit=[]
 for name,sha in BH.FIXTURE.AV.FILES:
  blob=(BH.FIXTURE.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  _,sy,_,info=BH.FIXTURE.source(blob);r=sy[info["root_symbol_id"]]
  assert r["type"]=="aecxhwstatsconfig"
  record=blob[r["record_offset"]:r["record_offset"]+56]
  assert record[4:36].split(b"\0",1)[0]==b"aecxhwstatsconfig"
  roots.append((blob,record));audit.append({"path":name,"sha256":sha,"typed_root_symbol_id":r["symbol_id"]})
 f=Reader(roots[-1][0]);initializers=0;prefixes=0
 for bias in [0,1,0x1230,0x8010]:
  f.initializer(bias);initializers+=1
  for _,record in roots:f.prefix(record,bias,0);prefixes+=1
  for j,label in enumerate([b"",b"x",b"OwnedMixedCase",b"a"*31,b"b"*32,b"owned.name_123"]):
   for sid in [0,0xffffffff]:
    f.prefix(owned_record(label,sid),bias,[0,1,7,31][j%4]);prefixes+=1
 rejected=0
 for label,sid in [(b"x"*33,0),(b"bad\0name",0),(b"\x80",0),(b"owned",-1),(b"owned",1<<32)]:
  before=bytes(f.n.u.mem_read(f.n.heap,0x30000))
  try:owned_record(label,sid)
  except AssertionError:rejected+=1
  else:raise AssertionError("fixture scope violation accepted")
  assert bytes(f.n.u.mem_read(f.n.heap,0x30000))==before
 record=owned_record(b"owned",1)
 for bad,start in [(record[:-1],0),(record+b"\0",0),(record,-1),(record,32)]:
  before=bytes(f.n.u.mem_read(f.n.heap,0x30000))
  try:f.prefix(bad,0,start)
  except AssertionError:rejected+=1
  else:raise AssertionError("prefix scope violation accepted")
  assert bytes(f.n.u.mem_read(f.n.heap,0x30000))==before
 result={"experiment":"E011BI","status":"PASS_BOUNDED_ORIGINAL_READER_INITIALIZER_ID_NAME_PREFIX_PARSER_INTERFACE_OPEN","base_commit":"4d73c93a3bc5ee155574a13df37f7144a126f294","original_DLL_sha256":BH.FIXTURE.SHA,"source_files":audit,"anchors":anchors,"original_initializer_full_returns":initializers,"original_reader_ID_name_prefix_cases":prefixes,"typed_original_root_prefix_cases":12,"owned_record_prefix_cases":48,"memory_placements":4,"owned_source_cursor_offsets":[0,1,7,31],"fixture_scope_rejections_before_execution":rejected,"initializer_zero_ranges":[[0,8],[52,16],[208,16]],"symbol_ID_reader_offset":8,"name_reader_offset":12,"name_source_offset":4,"name_copy_bytes":32,"name_terminator_reader_offset":44,"name_case_preserved":True,"prefix_source_cursor_preserved_before_later_write":True,"x1_source_base_x2_available_source_bytes_x3_offset_pointer_qualified_in_owned_prefix":True,"prefix_alignment_argument_x6":1,"constructor_caller_alignment_policy_closed":False,"all_heap_bytes_outside_qualified_prefix_writes_preserved":True,"source_bytes_and_context_pointer_preserved":True,"original_memcpy_stubbed":False,"prefix_helper_stubs_executed":False,"numeric_version_fields_or_profile_validated":False,"full_reader_constructor_return_claimed":False,"full_reader_constructor_parser_interface_qualified":False,"full_parent_metadata_stubs_removed":False,"whole_parent_metadata_materialization_closed":False,"exact_opened_tuning_filename_closed":False,"whole_profile_materialization_closed":False,"whole_loader_alignment_policy_closed":False,"every_grid_member_validated":False,"cold_metadata_bridge_closed":False,"RS_count_offset_authority_closed":False,"complete_deterministic_bootstrap_closed":False,"WM16_retirement_closed":False,"Linux_optical_parity_closed":False,"captured_scalars_used_as_producer_inputs":False,"private_original_bytes_exported":False,"production_C_changed":False,"new_kernel_build_performed":False,"runtime_actions_performed":False,"observer_armed":False,"new_camera_starts":0,"new_reboots":0,"native_rear_runtime_allowed":False}
 (HERE/"READER-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in result.items() if k!="source_files"},indent=2))
if __name__=="__main__":main()
