#!/usr/bin/env python3
"""Source-owned RS inputs, original ARM64 arithmetic and private capture checks."""
from pathlib import Path
import contextlib, importlib.util, io, itertools, json, random, struct, subprocess, tempfile
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent;PRIVATE=ROOT.parent/"private"
AJ=EX/"e011aj-rear-bg-geometry-threshold-integration"
AK=EX/"e011ak-rear-stats-input-observer"
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(name,n,label):
    return (PRIVATE/"E011AK-20260930-1025A/capture"/f"{name}{n:02}_{label}.bin").read_bytes()
def word(b,o=0):return struct.unpack_from("<I",b,o)[0]
def source_inputs():
    with contextlib.redirect_stdout(io.StringIO()):load("e011am_capture",AK/"validate-private.py").main()
    xs=[]
    for i in range(1,4):
        rec=read("RS",i,"REC");l,t,r,b=struct.unpack("<4I",read("RS",i,"CROP"))
        assert l==t==0
        xs.append((r-l+1,b-t+1,word(rec),word(rec,4),
            int(word(read("RS",i,"FORMAT"))==1),word(rec,0x80)))
    assert xs[0][2]!=xs[1][2] and xs[0][3]==xs[1][3]
    assert xs[1][2]==xs[2][2] and xs[1][3]!=xs[2][3]
    assert all(read("RS",i,"REC")==read("RS",3,"REC") for i in range(3,9))
    # Counts and color come from pre-adjustment semantic inputs, not packed
    # outputs. The whole-frame zero-offset caller policy is a bounded scope,
    # not a port of stripe policy or proof of earlier AFD initialization.
    return xs
class Native:
    def __init__(self):self.n=load("e011am_image",AJ/"native-private.py").Native().oracle
    def produce(self,x):
        w,h,hn,vn,half,color=x;n=self.n;u=n.u
        if half:w//=2
        u.mem_write(n.heap,bytes(0x30000));u.mem_write(n.stack,bytes(0x10000))
        u.mem_write(n.heap+0x60,struct.pack("<2I",hn,vn))
        u.mem_write(n.heap+0xe0,struct.pack("<I",color))
        u.mem_write(n.heap+0x10c,struct.pack("<2I",w,h))
        u.mem_write(n.heap+0xe4,struct.pack("<2I",w//hn,h//vn))
        # CheckDependenceChange derives region dimensions before AdjustROI.
        # Owned emulator objects deliberately select zero stripe offsets.
        for reg,value in ((UC_ARM64_REG_X0,n.heap),(UC_ARM64_REG_SP,n.stack+0xf000),(UC_ARM64_REG_LR,n.end)):
            u.reg_write(reg,value)
        u.emu_start(n.base+0xa0e538,n.end,count=100000)
        assert u.reg_read(UC_ARM64_REG_PC)==n.end
        data=bytes(u.mem_read(n.heap+0x60,164))
        return (*[word(data,o) for o in (0,4,0x84,0x88,0x8c,0x90,0x80)],
            struct.unpack("<H",u.mem_read(n.heap+0x130,2))[0])
def cases(source):
    xs=list(source)
    for x in itertools.product((16,31,512,8191,8192,8193,16384),
            (16,31,32,1023,1024,16384),(1,2,15,16),(1,2,16,1023,1024),(0,1),(0,1)):
        xs.append(x)
    rng=random.Random(0xe011a3)
    xs.extend((rng.randint(16,16384),rng.randint(16,16384),rng.randint(1,16),
        rng.randint(1,1024),rng.randrange(2),rng.randrange(2)) for _ in range(1024))
    return xs
def main(return_source=False):
    source=source_inputs();xs=cases(source);n=Native();expected=[n.produce(x) for x in xs]
    for i,v in enumerate(expected[:3],1):
        packed=read("RSPACK",i,"REC")
        assert v[:7]==tuple(word(packed,o) for o in (0,4,0x84,0x88,0x8c,0x90,0x80))
        assert v[7]==struct.unpack_from("<H",read("RSPACK",i,"OPT"),0x10)[0]
    reports=[];clean_source=None
    with tempfile.TemporaryDirectory(prefix="e011am-rs-private-",dir=PRIVATE) as tmp:
        td=Path(tmp)
        for compiler in ("gcc","clang"):
            binary=td/compiler
            build=subprocess.run([compiler,"-std=c11","-Wall","-Wextra","-Werror",
                "-fsanitize=address,undefined","-g",str(HERE/"rs-check.c"),"-o",str(binary)],capture_output=True)
            if build.returncode:
                (PRIVATE/(td.name+"-"+compiler+"-build-failure.raw")).write_bytes(build.stderr)
                raise RuntimeError("RS producer compile failed; private diagnostic retained")
            run=subprocess.run([str(binary)],input=b"".join(struct.pack("<6I",*x) for x in xs),capture_output=True)
            if run.returncode:
                (PRIVATE/(td.name+"-"+compiler+"-run-failure.raw")).write_bytes(run.stderr)
                raise RuntimeError("RS producer run failed; private diagnostic retained")
            assert len(run.stdout)==len(xs)*32
            actual=[struct.unpack_from("<8I",run.stdout,i*32) for i in range(len(xs))]
            for i,(a,b) in enumerate(zip(actual,expected)):
                assert a==b,{"case":i,"matching_fields":sum(x==y for x,y in zip(a,b))}
            if clean_source is None:clean_source=actual[:3]
            else:assert clean_source==actual[:3]
            reports.append({"compiler":compiler,"source_cases":3,"synthetic_cases":len(xs)-3,
                "original_cases_exact":len(xs),"original_fields_exact":len(xs)*8})
    safe={"experiment":"E011AM","status":"PASS_ORIGINAL_RS_ARITHMETIC_AND_SAMPLED_SHIFT_BINDING",
        "compiler_runs":reports,"original_adjust_rva":"0xa0e538",
        "sampled_pack_semantic_fields_exact":21,"sampled_pack_shift_fields_exact":3,
        "original_shift_state_offset":"0x130","pack_option_shift_offset":"0x10",
        "shift_binding_closed_for_sampled_whole_frame_startup":True,
        "input_authority":"E011AK pre-adjustment RS semantic counts/color/crop/format",
        "zero_offsets":"explicit bounded whole-frame caller policy; stripe policy not ported",
        "RS_normal_count_policy_origin_closed":False,"retained_output_words_used_as_inputs":False,
        "source_schedule":[0,1,2,2],"integer_only":True,
        "original_executable_modified":False,"OS_driver_invocations":False,"private_bytes_exported":False}
    (HERE/"ARITHMETIC-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    if return_source:return clean_source,safe
    print(json.dumps(safe,indent=2))
if __name__=="__main__":main()
