#!/usr/bin/env python3
"""Verify bounded upstream-cache and following-query source facts; no raw export."""
from pathlib import Path
import hashlib,json
import pefile,capstone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
def main():
 path=ROOT.parents[1]/"00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"
 b=path.read_bytes();assert hashlib.sha256(b).hexdigest()==SHA
 p=pefile.PE(data=b);c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);c.detail=True
 def instruction(r):return next(c.disasm(p.get_data(r,4),r))
 def memory(r,name,reg,base,offset):
  i=instruction(r);assert i.mnemonic==name and c.reg_name(i.operands[0].reg)==reg
  o=i.operands[1];assert o.type==capstone.arm64.ARM64_OP_MEM and c.reg_name(o.mem.base)==base and o.mem.disp==offset
 def immediate(r,reg,value):
  i=instruction(r);assert i.mnemonic=="mov" and c.reg_name(i.operands[0].reg)==reg
  assert i.operands[1].type==capstone.arm64.ARM64_OP_IMM and i.operands[1].imm==value
 memory(0x39f190,"ldr","x8","x25",56);memory(0x39f1ac,"str","x8","sp",56)
 memory(0x39f358,"ldr","x1","sp",56)
 immediate(0x852960,"w8",21);immediate(0x852968,"x8",92);immediate(0x85297c,"w1",20)
 i=instruction(0x852984);assert i.mnemonic=="bl" and i.operands[0].imm==0x852668
 safe={"experiment":"E011AX","status":"PASS_BOUNDED_UPSTREAM_POINTER_AND_FOLLOWING_BE_QUERY_SOURCE",
 "original_DLL_sha256":SHA,"ConfigureHWStats_function_rva":"0x39F070",
 "static_cache_pointer_load_rva":"0x39F190","static_cache_source_base_register":"x25","static_cache_source_member_offset":56,
 "static_cache_pointer_saved_rva":"0x39F1AC","static_cache_pointer_stack_offset":56,"static_cache_Init_argument_reload_rva":"0x39F358",
 "following_BE_query_call_rva":"0x852984","following_BE_query_wrapper_rva":"0x852668",
 "following_BE_query_selector":20,"following_BE_query_output_type":21,"following_BE_query_output_bytes":92,
 "actual_live_BE_callback_and_frame_binding_qualified":False,"second_observed_same_output_getter_selector_attributed":False,
 "cached_configuration_construction_and_weight_writer_closed":False,"numeric_initialization_closed":False,
 "metadata_bridge_closed":False,"runtime_action_in_this_audit":False,"private_bytes_exported":False}
 (HERE/"SOURCE-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n");print(json.dumps(safe))
if __name__=="__main__":main()
