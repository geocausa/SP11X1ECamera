#!/usr/bin/env python3
"""Verify original AWB descriptor and field ownership in private owned memory."""
from pathlib import Path
import hashlib,importlib.util,json,struct
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; EX=HERE.parent
AL=EX/"e011al-rear-bg-weight-quad-integration"
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    m=load("e011an_native",AL/"native-private.py");n=m.Native().n
    u=n.u;b=n.heap;opt=b+0x8000
    def reset(io):
        u.mem_write(b,bytes(0x30000));u.mem_write(n.stack,bytes(0x10000))
        u.mem_write(io+0x2554,struct.pack("<Q",b+0x12000))
        u.mem_write(io+0x27b0,struct.pack("<Q",b+0x13000))
    def call(rva,io,x1,x2):
        for r,v in ((UC_ARM64_REG_X0,io),(UC_ARM64_REG_X1,x1),(UC_ARM64_REG_X2,x2),
                    (UC_ARM64_REG_SP,n.stack+0xf000),(UC_ARM64_REG_LR,n.end)):
            u.reg_write(r,v)
        u.emu_start(n.base+rva,n.end,count=100000)
        assert u.reg_read(UC_ARM64_REG_PC)==n.end
    descriptor_cases=0;field_cases=0
    for off in (0,0x100,0x800,0x1000):
        io=b+off
        for seed in (0,1,85,170):
            for selector in (None,2,12):
                reset(io);sentinel=bytes((j+seed)&255 for j in range(92))
                u.mem_write(io+0xcb4,sentinel)
                if selector is not None:u.mem_write(opt,struct.pack("<I",selector))
                call(0x845368 if selector is None else 0x845658,io,0,opt)
                assert bytes(u.mem_read(io+0xcb4,92))==sentinel
                start=io+(0x2080 if selector is None else 0x2238)
                count=15 if selector is None else 11
                matches=[]
                for idx in range(count):
                    rec=bytes(u.mem_read(start+idx*24,24))
                    if struct.unpack_from("<Q",rec)[0]==io+0xcb4:
                        matches.append((idx,*struct.unpack_from("<4I",rec,8)))
                assert matches==([] if selector==2 else [(5,92,0,5,0)] if selector is None else [(10,92,0,10,0)])
                descriptor_cases+=1
        for value in [0,0xffffffff]+[1<<bit for bit in range(32)]:
            reset(io);u.mem_write(io+0xd08,struct.pack("<I",value));out=b+0x10000
            call(0x846020,io,b+0x18000,out)
            assert struct.unpack("<I",u.mem_read(out+0x4c,4))[0]==value
            assert struct.unpack("<I",u.mem_read(io+0xd08,4))[0]==value
            field_cases+=1
    source=m.source_inputs()
    assert [x[3] for x in source]==[1,1]
    assert source[0][:3]==source[1][:3]
    safe={"experiment":"E011AN","status":"PASS_ORIGINAL_AWB_DESCRIPTOR_AND_FIELD_OWNERSHIP",
      "parent_git_revision":"a3c81299111f8c1f46c9a0f2a0531293cd7a2ea9",
      "original_descriptor_cases":descriptor_cases,"original_quad_field_cases":field_cases,
      "total_original_calls":descriptor_cases+field_cases,"owned_IO_base_offsets":4,
      "BG_output_bytes":92,"quad_IO_offset":"0xD08","quad_record_offset":"0x4C",
      "expected_output_helper_rva":"0x845368","expected_output_BG_index":5,"expected_output_BG_type":5,
      "getparam_descriptor_helper_rva":"0x845658","getparam_selector":12,
      "getparam_BG_output_index":10,"getparam_BG_output_type":10,
      "selector2_has_BG_output":False,"descriptor_helpers_preserve_BG_payload":True,
      "FillBG_rva":"0x846020","FillBG_preserves_full_u32_quad_input":True,
      "sampled_cold_and_normal_quad":1,"sampled_weights_unchanged":True,
      "quad_value_generated_by_descriptor_helper":False,"algorithm_value_policy_closed":False,
      "original_executable_modified":False,"OS_driver_invocations":False,"private_bytes_exported":False,
      "native_rear_runtime_allowed":False}
    (HERE/"ORIGIN-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps(safe))
if __name__=="__main__":main()
