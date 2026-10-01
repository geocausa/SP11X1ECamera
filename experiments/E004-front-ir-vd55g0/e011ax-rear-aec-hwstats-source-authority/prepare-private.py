#!/usr/bin/env python3
"""Source qualification and bounded grid-init pointer checks; original stays on SP11."""
from pathlib import Path
import hashlib,importlib.util,json,random,struct
import pefile,capstone
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent;PRIVATE=ROOT.parent/"private"
SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 path=ROOT.parents[1]/"00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"
 blob=path.read_bytes();assert hashlib.sha256(blob).hexdigest()==SHA
 p=pefile.PE(data=blob);base=p.OPTIONAL_HEADER.ImageBase
 ranges=[("INIT",0x3a0d70,64),("GETPARAM",0x372e40,64),("GETTER",0x3a0db0,336),
 ("CONSUMER",0x83e01c,24),("COLD",0x73c074,36),("QUERY",0x8528b4,60)]
 codes=[{"name":name,"rva":rva,"bytes":size,"sha256":hashlib.sha256(p.get_data(rva,size)).hexdigest()} for name,rva,size in ranges]
 table=struct.unpack("<3Q",p.get_data(0x13381a0,24))
 assert tuple(x-base for x in table)==(0x3a0d70,0x3a1140,0x3a0db0)
 cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);cs.detail=True
 ins={i.address:i for i in cs.disasm(p.get_data(0x3a0d70,64),0x3a0d70)}
 assert ins[0x3a0d84].mnemonic=="str" and cs.reg_name(ins[0x3a0d84].operands[0].reg)=="x1"
 assert cs.reg_name(ins[0x3a0d84].operands[1].mem.base)=="x19" and ins[0x3a0d84].operands[1].mem.disp==24
 assert ins[0x3a0d8c].mnemonic=="bl" and ins[0x3a0d8c].operands[0].imm==0x388630
 n=load("ax_native",EX/"e011ai-rear-neutral-scalar-full-integration/native-private.py").Native();u=n.u;state={}
 def hook(uc,address,size,_):
  if address-n.base==0x388630:
   assert u.reg_read(UC_ARM64_REG_W0)==state["selector"]
   u.reg_write(UC_ARM64_REG_W0,state["helper_result"]);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);rng=random.Random(0xe011a8);cases=0
 for shift in [0,0x40,0x1230,0x8010]:
  for i in range(32):
   u.mem_write(n.heap,bytes(0x30000));u.mem_write(n.stack,bytes(0x10000))
   obj=n.heap+shift;src=n.heap+0x14000
   cache=rng.randbytes(96);before=rng.randbytes(48);u.mem_write(obj,before);u.mem_write(src,cache)
   state["selector"]=struct.unpack_from("<I",cache,88)[0];state["helper_result"]=rng.getrandbits(32)
   for reg,v in [(UC_ARM64_REG_X0,obj),(UC_ARM64_REG_X1,src),(UC_ARM64_REG_SP,n.stack+0xf000),(UC_ARM64_REG_LR,n.end)]:u.reg_write(reg,v)
   u.emu_start(n.base+0x3a0d70,n.end,count=1000)
   assert u.reg_read(UC_ARM64_REG_PC)==n.end
   expected=bytearray(before);struct.pack_into("<Q",expected,24,src);struct.pack_into("<I",expected,32,state["helper_result"])
   assert bytes(u.mem_read(obj,48))==bytes(expected);assert bytes(u.mem_read(src,96))==cache
   cases+=1
 result={"experiment":"E011AX","status":"PASS_SOURCE_QUALIFICATION_AND_BOUNDED_GRID_INIT_ALIAS",
 "base_commit":"b3a880cd9b80ec4705cad79fbc5111beb7b56e9b","original_DLL_sha256":SHA,
 "code_ranges":codes,"grid_vtable_rva":0x13381a0,"grid_vtable_first_three_target_rvas":[x-base for x in table],
 "grid_init_function_rva":"0x3A0D70","cache_pointer_store_rva":"0x3A0D84","cache_pointer_member_offset":24,
 "helper_input_cache_offset":88,"helper_result_self_offset":32,"bounded_init_cases":cases,
 "cache_bytes_preserved":True,"weights_initialized_by_this_pointer_boundary":False,
 "helper_numeric_policy_stubbed_and_excluded":True,"original_code_modified":False,
 "live_owner_callback_cache_lineage_closed":False,"cold_weight_initializer_policy_closed":False,
 "runtime_armed":False,"runtime_actions_performed":False,"native_rear_runtime_allowed":False,"private_bytes_exported":False}
 (HERE/"PREPARE-SAFE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in result.items() if k!="code_ranges"}))
if __name__=="__main__":main()
