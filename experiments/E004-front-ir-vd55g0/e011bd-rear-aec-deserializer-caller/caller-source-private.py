#!/usr/bin/env python3
"""Bounded original context initialization and deserializer argument forwarding."""
from pathlib import Path
import hashlib, importlib.util, json, struct
import pefile, capstone
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def load(path):
 spec=importlib.util.spec_from_file_location("bd_native",path)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
native=load(HERE.parent/"e011ai-rear-neutral-scalar-full-integration/native-private.py")
blob=native.DLL.read_bytes();assert hashlib.sha256(blob).hexdigest()==native.DLL_SHA
pe=pefile.PE(data=blob);base=pe.OPTIONAL_HEADER.ImageBase
md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);md.detail=True
i=next(md.disasm(pe.get_data(0x6f26c4,4),base+0x6f26c4))
assert i.mnemonic in ("mov","movz") and i.operands[1].imm==1
i=next(md.disasm(pe.get_data(0x6f26c8,4),base+0x6f26c8))
assert i.mnemonic=="str" and i.reg_name(i.operands[0].reg).startswith("x")
assert i.operands[-1].mem.base==capstone.arm64.ARM64_REG_X26 and i.operands[-1].mem.disp==0x48
i=next(md.disasm(pe.get_data(0x6f3594,4),base+0x6f3594))
assert i.mnemonic=="ldr" and i.reg_name(i.operands[0].reg)=="x2"
assert i.operands[-1].mem.base==capstone.arm64.ARM64_REG_X26 and i.operands[-1].mem.disp==0x48
i=next(md.disasm(pe.get_data(0x6f35ac,4),base+0x6f35ac))
assert i.mnemonic=="blr" and i.reg_name(i.operands[0].reg)=="x15"
initializer=[];forwarded=[]
for bias in (0x100,0x230,0x1010,0x8010):
 n=native.Native();u=n.u;context=n.heap+bias
 before=bytes([0xa5])*0x30000;u.mem_write(n.heap,before)
 u.reg_write(UC_ARM64_REG_X26,context)
 u.emu_start(base+0x6f26c4,base+0x6f26cc,count=16)
 assert u.reg_read(UC_ARM64_REG_PC)==base+0x6f26cc
 expected=bytearray(before);expected[bias+0x48:bias+0x50]=struct.pack("<Q",1)
 assert bytes(u.mem_read(n.heap,0x30000))==bytes(expected)
 initializer.append(dict(placement_bias=hex(bias),initialized_alignment_one=True,
   all_other_heap_bytes_preserved=True,helper_stubs=0))
 for value in (0,1,2,4,8,0xffffffffffffffff):
  n=native.Native();u=n.u;context=n.heap+bias;module=n.heap+0x10000;reader=n.heap+0x11000
  u.mem_write(n.heap,before);u.mem_write(context+0x48,struct.pack("<Q",value));u.mem_write(module,struct.pack("<Q",base+0x1335598))
  expected=bytes(u.mem_read(n.heap,0x30000));guard=[]
  def hook(uc,pc,size,user):
   if pc==base+0x6f35a8:
    guard.append(pc);uc.reg_write(UC_ARM64_REG_PC,pc+4)
  u.hook_add(UC_HOOK_CODE,hook)
  for register,v in ((UC_ARM64_REG_X0,module),(UC_ARM64_REG_X1,reader),
      (UC_ARM64_REG_X26,context),(UC_ARM64_REG_X27,reader),
      (UC_ARM64_REG_SP,n.stack+0xf000)):
   u.reg_write(register,v)
  u.emu_start(base+0x6f3584,base+0x6f35ac,count=64)
  assert u.reg_read(UC_ARM64_REG_PC)==base+0x6f35ac
  assert u.reg_read(UC_ARM64_REG_X2)==value
  assert u.reg_read(UC_ARM64_REG_X0)==module and u.reg_read(UC_ARM64_REG_X1)==reader
  assert u.reg_read(UC_ARM64_REG_X15)==base+0x123cc0
  assert len(guard)==1 and bytes(u.mem_read(n.heap,0x30000))==expected
  forwarded.append(dict(placement_bias=hex(bias),alignment_case_index=(0,1,2,4,8,0xffffffffffffffff).index(value),
    third_argument_exact=True,other_arguments_and_source_heap_preserved=True))
safe=dict(experiment="E011BD",status="PASS_BOUNDED_ORIGINAL_ALIGNMENT_INITIALIZATION_FORWARDING",
 original_DLL_sha256=native.DLL_SHA,context_stack_retention_rva="0x6f22f0",
 initializer_rvas=["0x6f26c4","0x6f26c8"],context_alignment_offset="0x48",
 context_alignment_bytes=8,third_argument_load_rva="0x6f3594",
 original_indirect_deserializer_call_rva="0x6f35ac",
 initializer_cases=initializer,forwarding_cases=len(forwarded),
 forwarding_cases_exact=True,forwarding_alignments_exercised=6,
 source_heap_preserved=True,original_guard_check_skipped_at_rva="0x6f35a8",
 full_loader_executed=False,indirect_target_loading_executed_in_fixture=True,
 module_vtable_seeded_from_source_and_live_qualified_table=True,
 indirect_target_computed_by_original_vtable_slot_load=True,
 zero_alignment_accepted_by_deserializer=False,
 revision_profile_and_all_paths_policy_closed=False,
 captured_scalars_used_as_producer_inputs=False,production_C_changed=False,
 original_bytes_exported=False,native_rear_runtime_allowed=False)
(HERE/"CALLER-SOURCE-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
print(json.dumps(safe,indent=2,sort_keys=True))
