#!/usr/bin/env python3
"""E011BH bounded original module metadata/name/strcmp helpers in owned memory."""
from pathlib import Path
import importlib.util,hashlib,json,struct,pefile,capstone
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
FIXTURE=load("bh_fixture",HERE/"metadata-fixture-private.py")
def facts():
 blob=FIXTURE.DLL.read_bytes();assert hashlib.sha256(blob).hexdigest()==FIXTURE.SHA
 pe=pefile.PE(data=blob);c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);c.detail=True
 def ins(r):return next(c.disasm(pe.get_data(r,4),r))
 for r,target in [(0x6f46ac,0xcae7c0),(0x6f46c0,0xcae7c0),(0x6f46d8,0xcae7c0),(0x6f46ec,0x6f4ac0)]:
  i=ins(r);assert i.mnemonic=="bl" and i.operands[0].imm==target
 i=ins(0x123d58);assert i.mnemonic=="ldr" and c.reg_name(i.operands[0].reg)=="x8" and c.reg_name(i.operands[-1].mem.base)=="x19" and i.operands[-1].mem.disp==0
 for r,dst,src,offset,kind in [(0x123d5c,"x5","x19",72,"add"),(0x123d68,"w3","x19",68,"ldr"),(0x123d74,"x6","x8",0,"ldr")]:
  i=ins(r);assert i.mnemonic==kind and c.reg_name(i.operands[0].reg)==dst
  if kind=="add":assert c.reg_name(i.operands[1].reg)==src and i.operands[2].imm==offset
  else:assert c.reg_name(i.operands[-1].mem.base)==src and i.operands[-1].mem.disp==offset
 assert pe.get_data(0x1375e50,64).split(b"\0")[0]==b"aecxhwstatsconfig"
 return {"constructor_rva":"0x6F45D8","name_helper_rva":"0x6F4AC0","comparison_rva":"0xF5DF00","constructor_copy_calls":["0x6F46AC","0x6F46C0","0x6F46D8"],"constructor_name_helper_call":"0x6F46EC","parent_profile_argument_address_rva":"0x123D5C","parent_profile_reader_offset":72,"parent_minor_argument_load_rva":"0x123D68","parent_minor_reader_offset":68,"parent_filename_argument_load_rva":"0x123D74","filename_context_pointer_offset":0,"parent_reader_context_pointer_load_rva":"0x123D58","original_parent_literal_matches_typed_AEC_name":True}
class Owned:
 def __init__(self,blob):
  self.f=FIXTURE.ParentPrefix(blob);self.n=self.f.n
 def reset(self,bias):
  n=self.n;u=n.u
  u.mem_write(n.heap,bytes([0xa5])*0x30000);u.mem_write(n.stack,bytes(0x10000))
  for collection in [self.f.allocs,self.f.symbols,self.f.calls,self.f.copies,self.f.redzones]:collection.clear()
  self.f.stub_counts.clear();self.f.next_alloc=n.heap+0x18000+bias
  return u
 def invoke(self,rva,args):
  u=self.n.u
  for index,value in enumerate(args):u.reg_write(globals()["UC_ARM64_REG_X"+str(index)],value)
  u.reg_write(UC_ARM64_REG_SP,self.n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,self.n.end)
  u.emu_start(self.n.base+rva,self.n.end,count=100000)
  assert u.reg_read(UC_ARM64_REG_PC)==self.n.end
 def name(self,label,bias):
  assert b"\0" not in label and len(label)<=32 and all(c<128 for c in label)
  n=self.n;u=self.reset(bias);src=n.heap+0x1000+bias;out=n.heap+0x4000+bias
  u.mem_write(src,label+b"\0");before=bytes(u.mem_read(n.heap,0x30000))
  self.invoke(0x6f4ac0,[out,src])
  result=bytes(u.mem_read(out,40))
  prefix=label[:32]
  assert result[:len(prefix)+1]==prefix+b"\0"
  expected=bytearray(before);at=out-n.heap;expected[at:at+40]=result
  assert bytes(u.mem_read(n.heap,0x30000))==bytes(expected)
  assert not self.f.allocs
  return result
 def constructor(self,label,profile,filename,major,minor,mode,bias):
  assert b"\0" not in label+profile+filename and len(label)<=32 and len(profile)<=160 and len(filename)<=96 and all(c<128 for c in label+profile+filename)
  assert all(isinstance(v,int) and 0<=v<=0xffffffff for v in [major,minor,mode])
  canonical=self.name(label,bias)
  stored_profile=profile[:127];stored_filename=filename[:64]
  n=self.n;u=self.reset(bias);obj=n.heap+0x4000+bias;ptrs=[n.heap+off+bias for off in [0x1000,0x1200,0x1400]]
  for ptr,text in zip(ptrs,[label,profile,filename]):u.mem_write(ptr,text+b"\0")
  before=bytes(u.mem_read(n.heap,0x30000))
  self.invoke(0x6f45d8,[obj,ptrs[0],major,minor,mode,ptrs[1],ptrs[2]])
  result=bytes(u.mem_read(obj,384))
  assert u.reg_read(UC_ARM64_REG_X0)==obj
  assert len(self.f.allocs)==1 and self.f.allocs[0][1]==len(label)+1
  allocated=self.f.allocs[0][0]
  assert int.from_bytes(result[:8],"little")==n.base+0x133b770
  assert int.from_bytes(result[8:16],"little")==allocated
  assert bytes(u.mem_read(allocated,len(label)+1))==label+b"\0"
  assert result[16:56]==canonical
  assert result[56:60]==bytes(4) and result[60:64]==struct.pack("<I",major)
  assert result[64:68]==bytes(4) and result[68:72]==struct.pack("<I",minor)
  assert result[72:76]==struct.pack("<I",mode) and result[76:80]==bytes(4)
  assert result[80:80+len(stored_profile)+1]==stored_profile+b"\0"
  assert result[208:208+len(stored_filename)+1]==stored_filename+b"\0"
  assert result[280:288]==bytes(8)
  # Compare the complete heap outside explicitly written fields and the one name allocation.
  expected=bytearray(before)
  for offset,length in [(0,80),(80,len(stored_profile)+1),(208,len(stored_filename)+1),(280,8)]:
   at=obj-n.heap+offset;expected[at:at+length]=result[offset:offset+length]
  at=allocated-n.heap;expected[at:at+len(label)+1]=label+b"\0"
  assert bytes(u.mem_read(n.heap,0x30000))==bytes(expected)
  assert all(bytes(u.mem_read(at,32))==bytes([0xa5])*32 for at in self.f.redzones)
  assert all(bytes(u.mem_read(ptr,len(text)+1))==text+b"\0" for ptr,text in zip(ptrs,[label,profile,filename]))
  assert set(self.f.stub_counts)<=set(["0x11d0","0x11f0","0xcae740","0xf5e600"])
 def scope_rejections(self):
  valid=[b"owned",b"profile",b"file",10,0,0]
  bad=[]
  for index,values in [(0,[b"n"*33,b"n\0x",b"\x80"]),(1,[b"p"*161,b"p\0x",b"\x80"]),(2,[b"f"*97,b"f\0x",b"\x80"]),(3,[-1,1<<32]),(4,[-1,1<<32]),(5,[-1,1<<32])]:
   for value in values:
    args=valid.copy();args[index]=value;bad.append(args)
  before=bytes(self.n.u.mem_read(self.n.heap,0x30000))
  for args in bad:
   try:self.constructor(*args,0)
   except AssertionError:pass
   else:raise AssertionError("out-of-scope metadata fixture input accepted")
   assert bytes(self.n.u.mem_read(self.n.heap,0x30000))==before
  return len(bad)
 def comparison(self,left,right,bias,third_argument):
  n=self.n;u=self.reset(bias);p=n.heap+0x1001+bias;q=n.heap+0x2003+bias
  u.mem_write(p,left+b"\0");u.mem_write(q,right+b"\0");before=bytes(u.mem_read(n.heap,0x30000))
  self.invoke(0xf5df00,[p,q,third_argument])
  raw=u.reg_read(UC_ARM64_REG_W0);signed=raw if raw<(1<<31) else raw-(1<<32)
  a=left.split(b"\0")[0];b=right.split(b"\0")[0]
  assert (signed>0)-(signed<0)==(a>b)-(a<b)
  assert bytes(u.mem_read(n.heap,0x30000))==before
  assert not self.f.allocs and not self.f.stub_counts
def main():
 anchors=facts();path,sha=FIXTURE.AV.FILES[-1];blob=(FIXTURE.AV.ARCHIVE/path).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
 cases=[(b"aecxhwstatsconfig",b"Default",b"owned-fixture.bin",10,0,0),
        (b"",b"",b"",0,0,0),
        (b"OwnedMixedCase",b"owned-profile",b"owned-source.bin",123,456,7),
        (b"x"*31,b"p"*127,b"f"*71,0xffffffff,0xffffffff,0xffffffff),
        (b"n",b"p",b"f",1,2,3),
        (b"Owned.Name_123",b"profile/path",b"fixture-A.bin",0xffffffff,0,0),
        (b"lower-name",b"alternate",b"fixture-B.bin",0,0xffffffff,1),
        (b"UPPER-NAME",b"Default",b"fixture-C.bin",65535,65536,0x80000000),
        (b"a"*32,b"p"*128,b"f"*65,10,1,0),
        (b"b"*32,b"p"*140,b"f"*72,11,2,1),
        (b"c"*31,b"p"*160,b"f"*96,12,3,2)]
 pairs=[(b"a",b"a"),(b"a",b"b"),(b"b",b"a"),(b"a",b"ab"),(b"ab",b"a"),(b"A",b"a"),(b"",b""),(b"",b"x"),(b"x",b""),(b"owned-name",b"owned-name"),(b"a\0z",b"a\0q"),(b"x"*63,b"x"*62+b"y")]
 owned=Owned(blob);constructors=0;names=0;comparisons=0
 for bias in [0,1,0x1230,0x8010]:
  for label,profile,filename,major,minor,mode in cases:owned.constructor(label,profile,filename,major,minor,mode,bias);constructors+=1;names+=1
  for left,right in pairs:
   for third in [0,1,384,(1<<64)-1]:owned.comparison(left,right,bias,third);comparisons+=1
 rejected=owned.scope_rejections()
 result={"experiment":"E011BH","status":"PASS_BOUNDED_ORIGINAL_METADATA_NAME_COMPARISON_OWNED_FIXTURES_PARENT_JOIN_OPEN","base_commit":"368c06da4895d291d42d7ed531057e397107cdce","original_DLL_sha256":FIXTURE.SHA,"source_candidate_sha256":sha,"anchors":anchors,"original_metadata_constructor_cases":constructors,"original_name_helper_cases_standalone":names,"original_name_helper_calls_in_constructor":constructors,"original_comparison_cases":comparisons,"fixture_scope_rejections_before_emulation":rejected,"memory_placements":4,"name_length_scope_maximum":32,"profile_string_length_scope_maximum":160,"filename_string_length_scope_maximum":96,"embedded_name_character_scope":32,"longer_name_encoding_closed":False,"embedded_name_prefix_truncation_claimed":False,"profile_copy_limit":127,"filename_copy_limit":64,"allocated_primary_name_retains_full_input":True,"bounded_string_truncation_verified":True,"metadata_base_vtable_rva":"0x133B770","allocated_name_pointer_offset":8,"embedded_name_helper_output_offset":16,"major_output_offset":60,"minor_output_offset":68,"numeric_argument_x4_output_offset":72,"profile_output_offset":80,"filename_output_offset":208,"constructor_returns_owned_object":True,"original_helper_case_preserving_name_copy_verified":True,"opaque_name_helper_tail_algorithm_independently_derived":False,"comparison_case_sensitive_null_terminated_lexical_sign_verified":True,"third_argument_changes_do_not_change_bounded_comparison_result":True,"all_heap_bytes_outside_qualified_fields_and_name_allocation_preserved":True,"source_strings_and_allocation_canaries_preserved":True,"metadata_name_comparison_helpers_stubbed_in_this_isolated_fixture":False,"remaining_isolated_fixture_stubs":["0x11D0","0x11F0","0xCAE740","0xF5E600"],"parent_fixture_metadata_stubs_removed":False,"complete_parent_context_metadata_authority_closed":False,"actual_filename_or_profile_from_owned_strings_inferred":False,"whole_parent_metadata_materialization_closed":False,"whole_profile_materialization_closed":False,"every_grid_member_validated":False,"exact_opened_tuning_filename_closed":False,"whole_loader_alignment_policy_closed":False,"cold_metadata_bridge_closed":False,"RS_count_offset_authority_closed":False,"complete_deterministic_bootstrap_closed":False,"WM16_retirement_closed":False,"Linux_optical_parity_closed":False,"captured_scalars_used_as_producer_inputs":False,"private_original_bytes_exported":False,"production_C_changed":False,"new_kernel_build_performed":False,"runtime_actions_performed":False,"observer_armed":False,"new_camera_starts":0,"new_reboots":0,"native_rear_runtime_allowed":False}
 (HERE/"METADATA-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
