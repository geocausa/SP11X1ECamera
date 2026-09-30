#!/usr/bin/env python3
"""Private source-input and original ARM64 weight/quad differential."""
from pathlib import Path
import contextlib, hashlib, importlib.util, io, json, random, struct, subprocess, tempfile
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent;PRIVATE=ROOT.parent/"private"
AJ=EX/"e011aj-rear-bg-geometry-threshold-integration"
AK=EX/"e011ak-rear-stats-input-observer"
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def source_inputs():
    validator=load("e011al_capture",AK/"validate-private.py")
    with contextlib.redirect_stdout(io.StringIO()):validator.main()
    c=PRIVATE/"E011AK-20260930-1025A/capture"
    read=lambda name,n,label:(c/f"{name}{n:02}_{label}.bin").read_bytes()
    cold_weights=read("AEC",1,"REC")[0x30:0x3c]
    normal_weights=read("AECPRODUCE",3,"FRAME")[0x44:0x50]
    cold_quad=struct.unpack_from("<I",read("AWB",1,"REC"),0x4c)[0]
    normal_quad=struct.unpack_from("<I",read("AWBPRODUCE",1,"IO"),0x54)[0]
    assert normal_weights==read("AEC",2,"REC")[0x30:0x3c]
    assert struct.pack("<I",normal_quad)==read("AWB",2,"REC")[0x4c:0x50]
    # Cold weights/quad are independent observed consumer inputs.
    # Their earlier initialization policy is NOT claimed source-closed.
    return [(*struct.unpack("<3I",cold_weights),cold_quad),
            (*struct.unpack("<3I",normal_weights),normal_quad)]
class Native:
    def __init__(self):self.n=load("e011al_image",AJ/"native-private.py").Native().oracle
    def produce(self,x,rva):
        n=self.n;u=n.u;b=n.heap;obj=b;opt=b+0x1000;rec=b+0x2000;out=b+0x3000
        u.mem_write(b,bytes(0x30000));u.mem_write(n.stack,bytes(0x10000))
        u.mem_write(obj+0x20,struct.pack("<Q",out))
        u.mem_write(rec,struct.pack("<10I",64,48,0,0,3658,2058,*([0x3ffff]*4)))
        u.mem_write(rec+0x28,struct.pack("<I",18))
        u.mem_write(rec+0x30,struct.pack("<3I",*x[:3]))
        u.mem_write(rec+0x40,struct.pack("<2I",42,56))
        u.mem_write(rec+0x4c,struct.pack("<I",x[3]))
        if rva==0xb3f860:
            u.mem_write(opt+8,struct.pack("<Q",rec))
            u.mem_write(opt+0x14,struct.pack("<IH",1,0xffff))
        elif rva==0xb39950:
            u.mem_write(opt,struct.pack("<Q",rec))
            u.mem_write(opt+8,struct.pack("<I",1));u.mem_write(opt+0x10,struct.pack("<H",0xffff))
        else:raise ValueError("unsupported pack entry")
        for r,v in ((UC_ARM64_REG_X0,obj),(UC_ARM64_REG_X1,opt),(UC_ARM64_REG_SP,n.stack+0xf000),(UC_ARM64_REG_LR,n.end)):
            u.reg_write(r,v)
        u.emu_start(n.base+rva,n.end,count=100000)
        assert u.reg_read(UC_ARM64_REG_PC)==n.end
        # Original register-image storage differs from register address order:
        # weights are word15, config word17. Never feed these outputs to C.
        weights=struct.unpack("<I",u.mem_read(out+60,4))[0]
        cfg=struct.unpack("<I",u.mem_read(out+68,4))[0]
        return (*[(weights>>s)&0x7f for s in (9,17,25)],(cfg>>9)&1)
def cases(source):
    result=list(source)
    edges=[0,0x80000000,1,0x007fffff,0x00800000,0x3cffffff,0x3d000000,0x3f800000]
    result.extend((x,x,x,i%2) for i,x in enumerate(edges))
    # One-ULP below / exact / above every positive half-integer Q4 boundary.
    for k in range(16):
        bits=struct.unpack("<I",struct.pack("<f",(k+0.5)/16))[0]
        for delta in (-1,0,1):result.append((bits+delta,bits,bits-delta,k%2))
    rng=random.Random(0xe011a1)
    for _ in range(1024):
        weights=[struct.unpack("<I",struct.pack("<f",rng.random()))[0] for _ in range(3)]
        result.append((*weights,rng.randrange(2)))
    return result
def main(return_source=False):
    source=source_inputs();xs=cases(source);n=Native()
    expected={rva:[n.produce(x,rva) for x in xs] for rva in (0xb3f860,0xb39950)}
    assert expected[0xb3f860]==expected[0xb39950]
    reports=[];clean_source=None
    with tempfile.TemporaryDirectory(prefix="e011al-weight-private-",dir=PRIVATE) as tmp:
        td=Path(tmp)
        for compiler in ("gcc","clang"):
            binary=td/compiler
            build=subprocess.run([compiler,"-std=c11","-Wall","-Wextra","-Werror",
                "-fsanitize=address,undefined","-g",str(HERE/"weight-quad-check.c"),"-o",str(binary)],capture_output=True)
            if build.returncode:
                (PRIVATE/(td.name+"-"+compiler+"-build-failure.raw")).write_bytes(build.stderr)
                raise RuntimeError("weight producer compile failed; private diagnostic retained")
            run=subprocess.run([str(binary)],input=b"".join(struct.pack("<4I",*x) for x in xs),capture_output=True)
            if run.returncode:
                (PRIVATE/(td.name+"-"+compiler+"-run-failure.raw")).write_bytes(run.stderr)
                raise RuntimeError("weight producer run failed; private diagnostic retained")
            assert len(run.stdout)==len(xs)*4
            actual=[tuple(run.stdout[i*4:i*4+4]) for i in range(len(xs))]
            for i,(a,b) in enumerate(zip(actual,expected[0xb3f860])):
                assert a==b,{"case":i,"matching_fields":sum(x==y for x,y in zip(a,b))}
            if clean_source is None:clean_source=actual[:2]
            else:assert clean_source==actual[:2]
            reports.append({"compiler":compiler,"input_cases":len(xs),"source_cases":2,
                "synthetic_cases":len(xs)-2,"original_pack_functions":2,
                "original_cases_exact":len(xs)*2,"original_fields_exact":len(xs)*8})
    safe={"experiment":"E011AL","status":"PASS_INTEGER_WEIGHT_QUAD_ORIGINAL_DIFFERENTIAL",
        "compiler_runs":reports,"input_authority":"E011AK cold semantic consumer and normal producer inputs",
        "retained_registers_used_as_inputs":False,"integer_only_binary32_quantization":True,
        "domain":"nonnegative finite weights0..1; boolean quad; negative zero accepted",
        "cold_initialization_policy_closed":False,"normal_producer_field_handoffs_verified":True,
        "original_executable_modified":False,"OS_driver_invocations":False,"private_bytes_exported":False}
    (HERE/"ARITHMETIC-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    if return_source:return clean_source,safe
    print(json.dumps(safe,indent=2))
if __name__=="__main__":main()
