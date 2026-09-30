#!/usr/bin/env python3
"""Source-owned BG inputs and private original geometry differential on SP11."""
from pathlib import Path
import hashlib,importlib.util,json,random,struct,subprocess,tempfile
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2];EX=HERE.parent;PRIVATE=ROOT.parent/"private"
AI=EX/"e011ai-rear-neutral-scalar-full-integration"
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def source_inputs():
    cold=json.loads((EX/"e011b-aec-bg-cold-slot-map/RESULT.json").read_text())
    aec=json.loads((EX/"e011n-rear-aecbe-request1-producer/RESULT.json").read_text())
    awb=json.loads((EX/"e011q-rear-awbbg-prerequest-seed-prepublish/RESULT.json").read_text())
    assert cold["cold_grid"]==[64,48]
    assert aec["request1_immediate_normal_producer_closed"]
    assert awb["closure"]["prerequest_normal_seed_origin_closed"]
    w,h=awb["normal_prerequest_record"]["default_sensor_resolution"]
    cap=json.loads((EX/"e011m-rs-titan680-capability-origin/RESULT.json").read_text())
    bit_depth=cap["literal_capability_words"]["0x9764"]
    assert bit_depth==18 # independently E011M Titan680 capability
    seed=[w,h,*cold["cold_grid"],0,0,w-w//10,h-h//10]+[(1<<bit_depth)-1]*4+[bit_depth,0x3f800000]
    a=aec["request1_normal_observation"];b=awb["normal_prerequest_record"]
    normal_aec=[w,h,a["horizontal_regions"],a["vertical_regions"],0,0,a["crop_width"],a["crop_height"]]+[int(x,16) for x in a["thresholds"]]+[bit_depth,0x3f800000]
    normal_awb=[w,h,b["horizontal_regions"],b["vertical_regions"],*b["effective_roi"]]+[int(x,16) for x in b["thresholds"]]+[bit_depth,0x3f800000]
    # ROI widths and thresholds are upstream observed semantic records, never
    # read from retained RT-CDM packets or tuned to their output values.
    return [seed,normal_aec,seed.copy(),normal_awb]
class Native:
    def __init__(self):
        self.oracle=load("e011aj_image",AI/"native-private.py").Native()
        u=self.oracle.u;base=self.oracle.base
        # Owned private emulator environment: logging disabled, original
        # executable bytes remain unchanged. No OS/runtime driver invocation.
        u.mem_write(base+0x1608858,struct.pack("<I",1))
        u.mem_write(base+0x160a218,bytes(8))
        # Both independently recovered hardware vtables use this same
        # capability producer. Verify the literal limits through original code.
        assert struct.unpack("<Q",u.mem_read(base+0x13464b0+0x30,8))[0]==base+0xb39870
        n=self.oracle;u.mem_write(n.heap+0x100,struct.pack("<I",18))
        for reg,value in [(UC_ARM64_REG_X0,n.heap+0x1000),(UC_ARM64_REG_X1,n.heap),
                (UC_ARM64_REG_X3,n.heap+0x100),(UC_ARM64_REG_SP,n.stack+0xf000),
                (UC_ARM64_REG_LR,n.end)]:u.reg_write(reg,value)
        u.emu_start(base+0xb39870,n.end,count=100000)
        assert u.reg_read(UC_ARM64_REG_PC)==n.end
        assert struct.unpack("<7I",u.mem_read(n.heap,28))==(16,512,16,512,64,64,0x3ffff)

    def produce(self,x,rva):
        obj=self.oracle;u=obj.u;heap=obj.heap
        u.mem_write(heap,bytes(0x30000));u.mem_write(obj.stack,bytes(0x10000))
        state,request,crop,trigger=heap,heap+0x4000,heap+0x21000,heap+0x22000
        w,h,hn,vn,ho,vo,rw,rh,*tail=x;threshold=tail[:4];depth,gain=tail[4:]
        u.mem_write(state+0x60,struct.pack("<10I",hn,vn,ho,vo,rw,rh,*threshold))
        limit=(1<<depth)-1
        if rva==0xa06288:
            u.mem_write(state+0xe0,struct.pack("<I",2))
            u.mem_write(state+0x108,struct.pack("<7I",16,512,16,512,64,64,limit))
            u.mem_write(request+0xf20,struct.pack("<Q",crop))
            u.mem_write(crop,struct.pack("<4I",0,0,w-1,h-1))
            u.mem_write(request+0x16d30,struct.pack("<Q",trigger))
            u.mem_write(trigger+0x44,struct.pack("<I",gain))
        elif rva==0x9fe120:
            u.mem_write(state+0xb4,struct.pack("<I",gain))
            u.mem_write(state+0xf8,struct.pack("<7I",16,512,16,512,64,64,limit))
            u.mem_write(state+0x118,struct.pack("<2I",w,h))
        else:raise ValueError("unsupported source geometry entry")
        for reg,value in [(UC_ARM64_REG_X0,state),(UC_ARM64_REG_X1,request),
                (UC_ARM64_REG_SP,obj.stack+0xf000),(UC_ARM64_REG_LR,obj.end)]:
            u.reg_write(reg,value)
        u.emu_start(obj.base+rva,obj.end,count=100000)
        assert u.reg_read(UC_ARM64_REG_PC)==obj.end,"bounded original geometry did not return"
        counts=struct.unpack("<4I",u.mem_read(state+0x60,16))
        rh2,rw2=struct.unpack("<2I",u.mem_read(state+0xa0,8))
        thresholds=struct.unpack("<4I",u.mem_read(state+0x78,16))
        # Offset even-floor is the independently established packer boundary;
        # AdjustROI keeps input offset; do not derive it from a captured word.
        return (*counts[:2],counts[2]&~1,counts[3]&~1,rw2,rh2,*thresholds)
def cases(source):
    result=list(source);rng=random.Random(0xe011a2)
    for _ in range(1024):
        w,h=rng.randint(512,16384),rng.randint(512,16384)
        ho,vo=rng.randint(0,w-32),rng.randint(0,h-32)
        result.append([w,h,rng.randint(1,64),rng.randint(1,64),ho,vo,
            rng.randint(16,w-ho),rng.randint(16,h-vo)]+
            [rng.randint(0,0x7ffff) for _ in range(4)]+[18,0x3f800000])
    return result
def main(return_source=False):
    inputs=source_inputs();xs=cases(inputs);native=Native()
    expected={rva:[native.produce(x,rva) for x in xs] for rva in (0xa06288,0x9fe120)}
    assert expected[0xa06288]==expected[0x9fe120]
    results=[]
    with tempfile.TemporaryDirectory(prefix="e011aj-bg-private-",dir=PRIVATE) as tmp:
        td=Path(tmp)
        for compiler in ("gcc","clang"):
            binary=td/compiler
            build=subprocess.run([compiler,"-std=c11","-Wall","-Wextra","-Werror",
                "-fsanitize=address,undefined","-g",str(HERE/"bg-check.c"),"-o",str(binary)],capture_output=True)
            run=None
            if build.returncode:
                (PRIVATE/(td.name+"-build-failure.raw")).write_bytes(build.stderr)
                raise RuntimeError("BG build failed; private diagnostic retained")
            run=subprocess.run([str(binary)],input=b"".join(struct.pack("<14I",*x) for x in xs),capture_output=True)
            if run.returncode:
                (PRIVATE/(td.name+"-run-failure.raw")).write_bytes(run.stderr)
                raise RuntimeError("BG run failed; private diagnostic retained")
            assert len(run.stdout)==len(xs)*40
            actual=[struct.unpack_from("<10I",run.stdout,i*40) for i in range(len(xs))]
            for i,(a,b) in enumerate(zip(actual,expected[0xa06288])):
                assert a==b,{"case":i,"matching_fields":sum(x==y for x,y in zip(a,b))}
            results.append({"compiler":compiler,"source_cases":4,"synthetic_cases":1024,
                "native_functions":2,"original_cases_exact":len(xs)*2,
                "original_fields_exact":len(xs)*20})
    safe={"experiment":"E011AJ","status":"PASS_ORIGINAL_BG_GEOMETRY_THRESHOLD_DIFFERENTIAL",
        "compiler_runs":results,"source_inputs":"E011B cold seed; E011N AEC normal frame control; E011Q AWB normal prerequest",
        "input_authority_is_retained_registers":False,"bound_clean_C_outputs":True,
        "gain_policy":"exact1.0 only; other scaling unsupported",
        "black_weights_quad_policy":"preserved seam; not produced by this slice",
        "original_executable_bytes_modified":False,"OS_driver_invocations":False,
        "private_values_or_original_decompiler_exported":False}
    (HERE/"BG-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    if return_source:return actual[:4],safe
    print(json.dumps(safe,indent=2))
if __name__=="__main__":main()
