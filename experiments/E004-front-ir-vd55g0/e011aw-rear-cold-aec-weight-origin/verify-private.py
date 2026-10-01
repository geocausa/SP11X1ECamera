#!/usr/bin/env python3
"""Bounded same-SP11 original AEC descriptor route and weight-copy audit."""
from pathlib import Path
import hashlib,importlib.util,json,random,struct
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent;PRIVATE=ROOT.parent/"private"
DLL_SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class Oracle:
    def __init__(self):
        self.n=load("aw_image",EX/"e011ai-rear-neutral-scalar-full-integration/native-private.py").Native()
        self.state=None;self.n.u.hook_add(UC_HOOK_CODE,self.hook)
    def hook(self,uc,addr,size,user):
        n=self.n;r=addr-n.base
        if self.state["mode"]=="route" and r in (0x39ea40,0x373f28):
            self.state["stop"]=r
            if r==0x39ea40:
                self.state["args"]=[uc.reg_read(reg) for reg in (UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3,UC_ARM64_REG_X4,UC_ARM64_REG_X5)]
            uc.emu_stop()
    def reset(self,shift):
        n=self.n;u=n.u;u.mem_write(n.heap,bytes(0x30000));u.mem_write(n.stack,bytes(0x10000))
        self.obj=n.heap+shift;self.src=n.heap+0x14000;self.out=n.heap+0x18000
        u.mem_write(self.out,bytes([0xa5])*128)
        u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
    def weights(self,values,shift):
        n=self.n;u=n.u;self.reset(shift);self.state={"mode":"weights"}
        source=bytearray(range(96));struct.pack_into("<3I",source,20,*values)
        u.mem_write(self.src,bytes(source));u.mem_write(self.obj+0x18,struct.pack("<Q",self.src))
        u.reg_write(UC_ARM64_REG_X0,self.obj);u.reg_write(UC_ARM64_REG_X1,self.out);u.reg_write(UC_ARM64_REG_X2,92)
        # Stop before TLS-dependent diagnostics and the remaining function tail.
        u.emu_start(n.base+0x3a0db0,n.base+0x3a0f18,count=10000)
        assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x3a0f18
        assert bytes(u.mem_read(self.src,96))==bytes(source)
        result=bytes(u.mem_read(self.out,128));assert result[92:]==bytes([0xa5])*36
        assert result[68:80]==struct.pack("<3I",*values)
        assert result[64:68]==bytes(source[16:20])
        assert result[80:84]==bytes(source[12:16])
        return result[68:80]
    def consumer(self,weight_bytes,shift):
        n=self.n;u=n.u;self.reset(shift);self.state={"mode":"consumer"}
        frame=n.heap+0x14000
        u.mem_write(frame+0x1ec,weight_bytes)
        before=bytes(u.mem_read(self.out,128))
        u.reg_write(UC_ARM64_REG_X21,frame);u.reg_write(UC_ARM64_REG_X19,self.out)
        u.emu_start(n.base+0x83e01c,n.base+0x83e034,count=10000)
        assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x83e034
        expected=bytearray(before);expected[48:60]=weight_bytes
        assert bytes(u.mem_read(self.out,128))==bytes(expected)
        assert bytes(u.mem_read(frame+0x1ec,12))==weight_bytes
    def route(self,selector,kind,allocated,shift,decoys=0,count=None):
        n=self.n;u=n.u;self.reset(shift);self.state={"mode":"route"}
        manager=n.heap+0x10000;query=n.heap+0x17000;desc=n.heap+0x19000
        u.mem_write(self.obj+0x28,struct.pack("<Q",manager))
        descriptors=b"".join(struct.pack("<3Q",self.out,92,0xffffffff) for _ in range(decoys))
        descriptors+=struct.pack("<3Q",self.out,allocated,kind)
        u.mem_write(desc,descriptors);u.mem_write(query,struct.pack("<I",selector))
        u.mem_write(query+0x18,struct.pack("<QI",desc,decoys+1 if count is None else count))
        u.reg_write(UC_ARM64_REG_X0,self.obj);u.reg_write(UC_ARM64_REG_X1,query)
        u.emu_start(n.base+0x372e40,n.end,count=10000)
        assert "stop" in self.state,"unsupported route fixture termination"
        assert bytes(u.mem_read(self.out,128))==bytes([0xa5])*128
        accepted=self.state["stop"]==0x39ea40
        if accepted:
            assert self.state["args"]==[manager,0,0,self.out,92,0]
        return accepted
def main():
    oracle=Oracle();rng=random.Random(0xe011a7)
    values=[(0,0,0),(0xffffffff,0xffffffff,0xffffffff)]
    for lane in range(3):
        for bit in range(32):
            v=[0,0,0];v[lane]=1<<bit;values.append(tuple(v))
    values.extend(tuple(rng.getrandbits(32) for _ in range(3)) for _ in range(128))
    # Observation is a comparison case, never independent numeric policy.
    sample=struct.unpack("<3I",(PRIVATE/"E011AK-20260930-1025A/capture/AEC01_REC.bin").read_bytes()[0x30:0x3c])
    values.append(sample);shifts=(0,0x40,0x1230,0x8010)
    for shift in shifts:
        for v in values:oracle.consumer(oracle.weights(v,shift),shift)
    routes=0;rejected=0
    for shift in shifts:
        for selector,kind in ((12,10),(20,21)):
            for size in (92,96,128):
                for decoys in (0,2):
                    assert oracle.route(selector,kind,size,shift,decoys);routes+=1
            for size in (0,91):
                assert not oracle.route(selector,kind,size,shift);rejected+=1
            assert not oracle.route(selector,0xffffffff,92,shift);rejected+=1
    safe={"experiment":"E011AW","status":"PASS_BOUNDED_AEC_TYPED_ROUTE_AND_CACHED_WEIGHT_COPY",
        "original_DLL_sha256":DLL_SHA,"original_executable_modified":False,
        "owned_base_offsets":len(shifts),"original_weight_copy_cases":len(values)*len(shifts),
        "weight_fields_exact":len(values)*len(shifts)*3,"primary_consumer_fragment_cases":len(values)*len(shifts),"primary_consumer_fragment_fields_exact":len(values)*len(shifts)*3,"source_and_output_neighbor_preservation_checked":True,
        "GetParam_descriptor_route_cases":routes,"GetParam_rejected_route_cases":rejected,
        "GetParam_selector_to_output_type":{"BG": {"selector":12,"output_type":10},"BE":{"selector":20,"output_type":21}},
        "query_output_descriptor_pointer_offset":24,"query_output_descriptor_count_offset":32,
        "dispatch_requested_bytes":92,"descriptor_bytes":24,"descriptor_pointer_offset":0,"descriptor_allocated_bytes_offset":8,"descriptor_type_offset":16,
        "route_stop_before_dispatch_rva":"0x39EA40","cache_dispatch_actor_field_offset":"0x28",
        "weight_copy_function_rva":"0x3A0DB0","weight_copy_stop_before_diagnostics_rva":"0x3A0F18",
        "grid_configuration_pointer_offset":24,"cached_weight_offsets":[20,24,28],"output_weight_offsets":[68,72,76],
        "primary_consumer_fragment_range":["0x83E01C","0x83E034"],"frame_weight_offsets":[492,496,500],"primary_stats_weight_offsets":[48,52,56],"bounded_getter_fragment_generates_numeric_weights":False,"cold_weight_numeric_policy_closed":False,
        "source_profile_weight_materialization_closed":False,"whole_GetParam_dispatch_return_proven":False,
        "whole_GetHWConfigOutput_return_proven":False,"diagnostic_and_constructor_behavior_excluded":True,
        "zero_output_count_diagnostic_path_excluded":True,"dispatch_manager_context_reproduction_closed":False,"retained_outputs_used_as_numeric_policy_inputs":False,
        "observed_weight_triple_comparison_only":True,"OS_driver_invocations":False,"private_bytes_exported":False,
        "native_rear_runtime_allowed":False}
    paths=[HERE/"verify-private.py",EX/"e011ai-rear-neutral-scalar-full-integration/native-private.py"]
    safe["source_locks"]=[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
    (HERE/"VALIDATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in safe.items() if k!="source_locks"},indent=2))
if __name__=="__main__":main()
