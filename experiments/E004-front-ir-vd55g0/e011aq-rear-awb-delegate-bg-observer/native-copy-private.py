#!/usr/bin/env python3
"""Bounded original PopulateOutput BG copy slice in private owned memory."""
from pathlib import Path
import importlib.util,json,struct
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def main():
    f=HERE.parent/"e011al-rear-bg-weight-quad-integration/native-private.py"
    s=importlib.util.spec_from_file_location("e011aq_native_parent",f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    n=m.Native().n;u=n.u;b=n.heap;u.mem_map(b+0x30000,0x1d0000)
    retained=(ROOT.parent/"private/E011AQ-20260930-1740A/capture/RETAINED_BG.bin").read_bytes();assert len(retained)==92
    cases=0
    for off in [0,0x100,0x800,0x1000]:
        for value in [0,1,0xffffffff]+[1<<i for i in range(32)]:
            u.mem_write(b,bytes(0x200000));u.mem_write(n.stack,bytes(0x10000))
            actor=b+off;engine=b+0x10000;param=b+0x180000;desc=b+0x181000;out=b+0x182000
            teb=b+0x1d0000;tls=b+0x1d1000;ctx=b+0x1d3000
            u.mem_write(actor+8,struct.pack("<Q",engine))
            u.mem_write(teb+0x58,struct.pack("<Q",tls));u.mem_write(tls,struct.pack("<Q",ctx)*512)
            source=bytearray(retained);struct.pack_into("<I",source,84,value);u.mem_write(actor+0xfb744,bytes(source))
            u.mem_write(param,struct.pack("<QI",desc,1));u.mem_write(desc,struct.pack("<Q4I",out,92,0,5,0))
            u.mem_write(out-64,bytes([0xa5])*220)
            for reg,v in [(UC_ARM64_REG_X0,actor),(UC_ARM64_REG_X1,param),(UC_ARM64_REG_X18,teb),
                          (UC_ARM64_REG_SP,n.stack+0xf000),(UC_ARM64_REG_LR,n.end)]:
                u.reg_write(reg,v)
            # Stop before post-copy diagnostic setup/callback. This is not a return.
            u.emu_start(n.base+0x68f490,n.base+0x68f9fc,count=100000)
            assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x68f9fc
            assert bytes(u.mem_read(out,92))==bytes(source)
            assert bytes(u.mem_read(actor+0xfb744,92))==bytes(source)
            assert bytes(u.mem_read(out-64,64))==bytes([0xa5])*64
            assert bytes(u.mem_read(out+92,64))==bytes([0xa5])*64
            cases+=1
    safe={"experiment":"E011AQ","status":"PASS_BOUNDED_ORIGINAL_BG_COPY_SLICE",
      "cases":cases,"owned_actor_base_offsets":4,"quad_u32_fixture_values":35,
      "whole_BG_bytes_exact_per_case":92,"source_preserved":True,"output_neighbors_preserved_bytes":128,
      "entry_RVA":"0x68F490","stop_RVA":"0x68F9FC","BG_case_type":5,
      "source_actor_offset":"0xFB744","quad_source_actor_offset":"0xFB798","quad_record_offset":"0x54",
      "full_u32_quad_preserved_not_coerced":True,"original_executable_modified":False,
      "post_copy_diagnostic_callback_executed":False,"complete_function_return_verified":False,
      "initial_numeric_value_policy_closed":False,"OS_driver_invocation":False,"private_payloads_exported":False}
    (HERE/"COPY-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps(safe))
if __name__=="__main__":main()
