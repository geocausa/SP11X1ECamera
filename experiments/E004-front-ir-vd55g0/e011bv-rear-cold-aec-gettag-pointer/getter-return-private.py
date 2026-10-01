#!/usr/bin/env python3
"""Original Node return ABI with explicit flag/pointer fixtures, no metadata API implementation."""
from pathlib import Path
import importlib.util,json,random,struct
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("bv_bt",HERE.parent/"e011bt-rear-cold-aec-metadata-route/source-private.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def main():
 m.source();f=m.Fixture();u=f.u;n=f.n;cases=0
 for bias in [0,1,0x40,0x1230]:
  for seed in range(32):
   f.route(bias,seed,1,2)
   assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x5c4d78
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+0x5d5180
   f.calls=[];u.reg_write(UC_ARM64_REG_X0,1)
   u.emu_start(u.reg_read(UC_ARM64_REG_LR),n.end,count=100000)
   assert len(f.calls)==1 and f.calls[0][0]==0x5c2fc0
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+0x5d54d0
   assert f.calls[0][1][:2]==[f.store,0x5000001c]
   payload=random.Random(seed+bias).randbytes(2072);u.mem_write(f.src,payload)
   before=bytes(u.mem_read(n.heap,0x30000));f.calls=[];f.writes=[]
   u.reg_write(UC_ARM64_REG_X0,f.src)
   u.emu_start(u.reg_read(UC_ARM64_REG_LR),n.end,count=100000)
   assert u.reg_read(UC_ARM64_REG_PC)==n.end and not f.calls
   assert bytes(u.mem_read(f.outvec,40))==bytes(16)+struct.pack("<Q",f.src)+bytes(16)
   assert bytes(u.mem_read(f.src,2072))==payload
   after=bytes(u.mem_read(n.heap,0x30000));allowed=set(range(f.trace-n.heap,f.trace-n.heap+0x100))|set(range(f.outvec-n.heap+16,f.outvec-n.heap+24))
   assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,after)))
   cases+=1
 out={"experiment":"E011BV","status":"PASS_BOUNDED_ORIGINAL_NODE_GETTER_RETURN_ABI","original_Node_return_cases":cases,"base_placements":4,"property_ID":"0x5000001C","published_flag_check_RVA":"0x5C4D78","published_flag_check_return_RVA":"0x5D5180","explicit_published_flag_fixture":1,"actual_GetTag_RVA":"0x5C2FC0","actual_GetTag_return_RVA":"0x5D54D0","output_pointer_vector_index":2,"GetTag_result_X0_feeds_output_vector":True,"metadata_API_implementations_executed":False,"typed_API_flag_and_pointer_results_injected_and_excluded":True,"live_pointer_identity_closed":False,"numeric_initialization_closed":False,"captured_scalars_used":False,"originals_exported":False,"native_rear_runtime_allowed":False}
 (HERE/"GETTER-ABI-SAFE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+chr(10));print(json.dumps(out))
if __name__=="__main__":main()
