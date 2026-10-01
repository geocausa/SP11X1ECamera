#!/usr/bin/env python3
"""Same-SP11 AEC module-selection authority; original bytes never exported."""
from pathlib import Path
import hashlib,importlib.util,json,struct
import pefile,capstone
from unicorn import UC_HOOK_CODE,UcError
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
DLL=ROOT.parents[1]/"00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"
def main():
 blob=DLL.read_bytes();assert hashlib.sha256(blob).hexdigest()==SHA
 pe=pefile.PE(data=blob);base=pe.OPTIONAL_HEADER.ImageBase
 cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);cs.detail=True
 def ins(r):return next(cs.disasm(pe.get_data(r,4),base+r))
 def memory(r,op,dst,owner,offset):
  i=ins(r);assert i.mnemonic==op and cs.reg_name(i.operands[0].reg)==dst
  o=i.operands[-1];assert o.type==capstone.arm64.ARM64_OP_MEM
  assert (cs.reg_name(o.mem.base),o.mem.disp)==(owner,offset)
 def address(r,dst,owner,offset):
  i=ins(r);assert i.mnemonic=="add"
  assert [cs.reg_name(x.reg) for x in i.operands[:2]]==[dst,owner]
  assert i.operands[2].type==capstone.arm64.ARM64_OP_IMM and i.operands[2].imm==offset
 # Qualified source route and both original dispatch layers.
 memory(0x39f098,"ldr","x0","x23",0x670)
 memory(0x39f0a4,"ldr","x8","x0",0x138)
 memory(0x39f0bc,"ldr","x25","x0",0xf0)
 memory(0x39f190,"ldr","x8","x25",0x38)
 memory(0x3a873c,"ldr","x0","x0",0)
 memory(0x3a8740,"ldr","x8","x0",0)
 memory(0x3a8744,"ldr","x8","x8",0x138)
 memory(0x3af54c,"ldr","x8","x0",8)
 assert ins(0x3af54c).writeback, "bank subobject adjustment must be qualified"
 memory(0x3af550,"ldr","x8","x8",0x68)
 address(0x3aebb0,"x0","x0",0xef8)
 assert ins(0x3aebb4).mnemonic=="ret"
 assert struct.unpack("<Q",pe.get_data(0x1338428+0x138,8))[0]==base+0x3af540
 assert struct.unpack("<Q",pe.get_data(0x13383b8+0x68,8))[0]==base+0x3aebb0
 # Constructor first installs a pure base table, later the concrete bank table.
 address(0x3a8db8,"x21","x20",8)
 import capstone.arm64 as ca
 block=list(cs.disasm(pe.get_data(0x3a8db8,0x3a9434-0x3a8db8),base+0x3a8db8))
 assert len(block)==(0x3a9434-0x3a8db8)//4 and block[-1].address-base==0x3a9430
 writes=[i.address-base for i in block if ca.ARM64_REG_X21 in i.regs_access()[1]]
 assert writes==[0x3a8db8]
 memory(0x3a9430,"str","x8","x21",0)
 page=ins(0x3a9424);add=ins(0x3a9428)
 assert page.mnemonic=="adrp" and add.mnemonic=="add"
 assert page.operands[1].imm+add.operands[2].imm==base+0x13383b8
 # Public interface slots written by constructor.
 pair=ins(0x3a9e64)
 assert pair.mnemonic=="stp"
 assert [cs.reg_name(o.reg) for o in pair.operands[:2]]==["x9","x8"]
 assert pair.operands[-1].mem.disp==0x130
 page=ins(0x3a9e5c);add=ins(0x3a9e60)
 assert page.mnemonic=="adrp" and add.mnemonic=="add"
 assert page.operands[1].imm+add.operands[2].imm==base+0x3a8730
 # Only the ARM64EC checked-dispatch helper is stubbed; all three accessors execute.
 cfi_sites={0x3a8754,0x3af560}
 for r in cfi_sites:
  i=ins(r);assert i.mnemonic=="blr" and cs.reg_name(i.operands[0].reg)=="x17"
 for r in [0x3a8758,0x3af564]:
  i=ins(r);assert i.mnemonic=="blr" and cs.reg_name(i.operands[0].reg)=="x15"
 spec=importlib.util.spec_from_file_location("native",ROOT/"experiments/E004-front-ir-vd55g0/e011ai-rear-neutral-scalar-full-integration/native-private.py")
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 n=mod.Native();u=n.u;lookups=[];dispatch=[];fixture_base=0
 def string(addr):
  try:return bytes(u.mem_read(addr,96)).split(b"\0")[0].decode("ascii")
  except (ValueError,UnicodeError,UcError):return None
 def hook(uc,pc,size,_):
  r=pc-n.base
  if r==0x6f39f8:
   names=[string(u.reg_read(q)) for q in [UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2]]
   name=next((x for x in names if x and x.startswith("aecx")),None);assert name
   marker=n.heap+0x10000+len(lookups)*0x200
   lookups.append((name,marker))
   u.reg_write(UC_ARM64_REG_X0,marker);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
  elif r in cfi_sites:
   target=u.reg_read(UC_ARM64_REG_X8);owner=u.reg_read(UC_ARM64_REG_X0)
   assert owner==fixture_base+(0 if r==0x3a8754 else 8)
   expected=n.base+(0x3af540 if r==0x3a8754 else 0x3aebb0)
   assert target==expected
   dispatch.append(r)
   u.reg_write(UC_ARM64_REG_X15,target);u.reg_write(UC_ARM64_REG_PC,pc+4)
 u.hook_add(UC_HOOK_CODE,hook)
 def call(r,arg):
  u.reg_write(UC_ARM64_REG_X0,arg);u.reg_write(UC_ARM64_REG_X1,n.heap+0x8000)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(n.base+r,n.end,count=100000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end
  return u.reg_read(UC_ARM64_REG_X0)
 cases=0;module_records=None
 for bias in [0,0x200,0x400,0x800]:
  for seed in range(32):
   u.mem_write(n.heap,bytes(0x30000));u.mem_write(n.stack,bytes(0x10000))
   lookups.clear();dispatch.clear();fixture_base=n.heap+bias;core=fixture_base;bank=core+8
   call(0x3ca4a0,bank)
   assert len(lookups)==43 and len({x[0] for x in lookups})==43
   chosen=dict(lookups)["aecxhwstatsconfig"]+0x120
   assert struct.unpack("<Q",u.mem_read(bank+0xfe8,8))[0]==chosen
   assert struct.unpack("<Q",u.mem_read(bank+0xf18,8))[0]==dict(lookups)["aecxcorestatsconfig"]+0x120
   if module_records is None:
    body=bytes(u.mem_read(bank,0x2000))
    module_records=[{"name":name,"bank_holder_member_offset":body.index(struct.pack("<Q",marker+0x120))}
                    for name,marker in lookups]
   wrapper=n.heap+0x9000;cache=n.heap+0x20000+(seed%4)*0x100
   owned=bytes((seed*17+i*29+bias//0x200)%256 for i in range(96))
   u.mem_write(cache,owned);u.mem_write(chosen+0x38,struct.pack("<Q",cache))
   u.mem_write(wrapper,struct.pack("<QQ",core,0))
   u.mem_write(core,struct.pack("<QQ",n.base+0x1338428,n.base+0x13383b8))
   before=bytes(u.mem_read(n.heap,0x30000))
   result=call(0x3a8730,wrapper)
   assert result==bank+0xef8 and dispatch==[0x3a8754,0x3af560]
   assert bytes(u.mem_read(n.heap,0x30000))==before
   # Execute actual bounded ConfigureHWStats loads with returned core-data pointer.
   u.emu_start(n.base+0x39f0bc,n.base+0x39f0c0,count=1)
   assert u.reg_read(UC_ARM64_REG_X25)==chosen
   u.emu_start(n.base+0x39f190,n.base+0x39f194,count=1)
   assert u.reg_read(UC_ARM64_REG_X8)==cache
   assert bytes(u.mem_read(cache,96))==owned
   assert bytes(u.mem_read(n.heap,0x30000))==before
   cases+=1
 report={"experiment":"E011AY","status":"PASS_BOUNDED_NAMED_HWSTATS_MODULE_SELECTION",
  "original_DLL_sha256":SHA,"owned_fixture_cases":cases,"fixture_base_variants":4,
  "named_lookup_calls_per_case":43,"total_named_lookup_calls":cases*43,
  "original_named_lookup_function_rva":"0x3CA4A0","lookup_stubbed":True,
  "public_interface_data_accessor_rva":"0x3A8730","core_data_accessor_rva":"0x3AF540",
  "concrete_bank_data_accessor_rva":"0x3AEBB0","core_bank_table_rva":"0x13383B8",
  "core_bank_table_install_rva":"0x3A9430","bank_subobject_offset":8,"data_offset_relative_to_bank":0xef8,"data_offset_relative_to_core":0xf00,
  "selected_member_relative_to_core_data":0xf0,"selected_member_relative_to_bank":0xfe8,"selected_member_relative_to_core":0xff0,
  "selected_module_name":"aecxhwstatsconfig","module_pointer_payload_adjustment":0x120,
  "cache_pointer_relative_to_selected_module_payload":0x38,
  "fixture_heap_source_and_neighbor_bytes_preserved":True,
  "ARM64EC_checked_dispatch_helper_stubbed":True,"virtual_accessor_callbacks_stubbed":False,
  "complete_constructor_executed":False,"complete_ConfigureHWStats_executed":False,
  "live_core_interface_and_named_source_join_qualified":False,
  "numeric_weight_initialization_closed":False,"module_deserialization_closed":False,
  "whole_profile_selection_closed":False,"cold_metadata_bridge_closed":False,
  "runtime_actions_performed":False,"production_C_changed":False,
  "native_rear_runtime_allowed":False,"private_original_bytes_exported":False,
  "module_holder_map":module_records}
 (HERE/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in report.items() if k!="module_holder_map"}))
if __name__=="__main__":main()
