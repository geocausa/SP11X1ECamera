#!/usr/bin/env python3
"""Same-SP11 original scalar arithmetic in Unicorn. No OS/driver invocation."""
from pathlib import Path
import hashlib,importlib.util,json,random,struct,subprocess,tempfile
import pefile,capstone
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRIVATE=ROOT.parent/"private"
DLL=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
DLL_SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def wire_input(x):
    return struct.pack("<13fI",x["demux_gain"],*x["bls"],*x["channel"],
        x["awb_g"],x["awb_b"],x["awb_r"],x["predictive_gain"],x["bayer"])
def outputs(raw):
    assert len(raw)%28==0
    return [struct.unpack_from("<4H4I2H",raw,i) for i in range(0,len(raw),28)]
class Native:
    def __init__(self):
        blob=DLL.read_bytes();assert hashlib.sha256(blob).hexdigest()==DLL_SHA
        pe=pefile.PE(data=blob);self.base=pe.OPTIONAL_HEADER.ImageBase
        cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
        ins=next(cs.disasm(pe.get_data(0x14d0,4),0x14d0))
        assert (ins.mnemonic,ins.op_str)==("frinta","s0, s0")
        assert struct.unpack("<f",pe.get_data(0x99947c,4))[0]==1024.0
        assert struct.unpack("<f",pe.get_data(0x9c0d9c,4))[0]==4096.0
        assert struct.unpack("<I",pe.get_data(0x132f610,4))[0]==131071
        self.u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
        self.u.mem_map(self.base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
        self.u.mem_write(self.base,pe.get_memory_mapped_image())
        self.heap=0x70000000;self.stack=0x71000000
        self.u.mem_map(self.heap,0x30000);self.u.mem_map(self.stack,0x10000)
        self.end=self.stack+0x100
    def call(self,rva,case):
        u=self.u;h=self.heap
        u.mem_write(h,bytes(0x30000));u.mem_write(self.stack,bytes(0x10000))
        dep,region,reserve,enable,out=(h,h+0x4000,h+0x8000,h+0xc000,h+0x10000)
        u.mem_write(enable,struct.pack("<4I",1,1,1,1))
        if rva==0x998e70:
            u.mem_write(dep+0x10,bytes([2]))
            u.mem_write(dep+0x1c,struct.pack("<f",case["demux_gain"]))
            u.mem_write(dep+0x48,struct.pack("<I",0x60800))
            u.mem_write(region,struct.pack("<4f",*case["bls"]))
            u.mem_write(reserve,struct.pack("<4f",*case["channel"]))
        elif rva==0x9c07c0:
            u.mem_write(dep+0x14,struct.pack("<I",1))
            u.mem_write(dep+0x4c,struct.pack("<f",1.0))
            u.mem_write(dep+0x54,struct.pack("<3f",case["awb_g"],case["awb_b"],case["awb_r"]))
            u.mem_write(dep+0x864,struct.pack("<I",0x60800))
        elif rva==0x995e60:
            u.mem_write(dep+0x10,struct.pack("<4f",case["awb_g"],case["awb_b"],case["awb_r"],case["predictive_gain"]))
        else:raise ValueError("unsupported original arithmetic entry")
        for reg,value in [(UC_ARM64_REG_X0,dep),(UC_ARM64_REG_X1,region),
                (UC_ARM64_REG_X2,reserve),(UC_ARM64_REG_X3,enable),
                (UC_ARM64_REG_X4,out),(UC_ARM64_REG_SP,self.stack+0xf000),
                (UC_ARM64_REG_LR,self.end)]:
            u.reg_write(reg,value)
        u.emu_start(self.base+rva,self.end,count=100000)
        assert u.reg_read(UC_ARM64_REG_PC)==self.end,"bounded original calculation did not return"
        assert u.reg_read(UC_ARM64_REG_X0)==1,"original supported calculation failed"
        if rva==0x998e70:return struct.unpack("<4H",u.mem_read(out+12,8))
        if rva==0x9c07c0:return struct.unpack("<4I",u.mem_read(out+36,16))
        wb=struct.unpack("<3H",u.mem_read(out+4,6))
        return wb[1],wb[2]
    def produce(self,case):
        return self.call(0x998e70,case)+self.call(0x9c07c0,case)+self.call(0x995e60,case)
def cases(live):
    result=list(live);rng=random.Random(0xE011A1)
    for _ in range(1024):
        x={"demux_gain":rng.choice([0.0,0.5,1.0,2.0,8.0,32.0]),
           "bls":[rng.uniform(0,1024) for _ in range(4)],
           "channel":[rng.uniform(0.25,4) for _ in range(4)],
           "awb_g":rng.uniform(0.1,8),"awb_b":rng.uniform(0.1,8),
           "awb_r":rng.uniform(0.1,8),"predictive_gain":rng.choice([0.001,0.5,1.0,2.0,8.0,32.0]),"bayer":2}
        packed=wire_input(x);f=struct.unpack("<13fI",packed)
        x={"demux_gain":f[0],"bls":list(f[1:5]),"channel":list(f[5:9]),
            "awb_g":f[9],"awb_b":f[10],"awb_r":f[11],"predictive_gain":f[12],"bayer":f[13]}
        result.append(x)
    # Source epsilon/fallback, lower/upper ratio clamps and gain normalization.
    for g,b,r in [(0,0,0),(1e-7,1,1),(1e-6,1,1),(1,0,0),(1,32,32),(32,0.001,0.001)]:
        result.append(dict(live[0],awb_g=g,awb_b=b,awb_r=r))
    return result
def main(return_source=False):
    authority=load("e011ai_authority",HERE/"authority-private.py")
    live,recovery=authority.get_inputs();inputs=cases(live)
    native=Native();expected=[native.produce(x) for x in inputs]
    reports=[]
    with tempfile.TemporaryDirectory(prefix="e011ai-scalar-private-",dir=PRIVATE) as temp:
        td=Path(temp)
        for compiler in ("gcc","clang"):
            binary=td/(compiler+"-scalar")
            build=subprocess.run([compiler,"-std=c11","-Wall","-Wextra","-Werror",
                "-fsanitize=address,undefined","-ffp-contract=off","-g",
                str(HERE/"scalar-check.c"),"-lm","-o",str(binary)],capture_output=True)
            if build.returncode:
                (PRIVATE/(td.name+"-build-failure.raw")).write_bytes(build.stderr)
                raise RuntimeError("scalar build failed; diagnostic retained privately")
            run=subprocess.run([str(binary)],input=b"".join(wire_input(x) for x in inputs),capture_output=True)
            if run.returncode:
                (PRIVATE/(td.name+"-run-failure.raw")).write_bytes(run.stderr)
                raise RuntimeError("scalar host run failed; diagnostic retained privately")
            actual=outputs(run.stdout)
            assert len(actual)==len(expected)
            for i,(a,b) in enumerate(zip(actual,expected)):
                assert a==b,{"case_index":i,"matching_scalar_fields":sum(x==y for x,y in zip(a,b))}
            reports.append({"compiler":compiler,"native_cases_exact":len(inputs),"scalar_fields_exact":len(inputs)*10})
    safe={"experiment":"E011AI","status":"PASS_NATIVE_SOURCE_SCALAR_DIFFERENTIAL",
        "private_recovery":recovery,"compiler_runs":reports,
        "native_boundaries":["Demux/BLS141 common0x998e70","PDPC311 ratio common0x9c07c0","WB201 ordinary common0x995e60"],
        "original_binary_used_only_in_private_local_unicorn":True,"runtime_driver_or_os_invocations":False,
        "optional_wb_normalization_supported":False,"other_bayer_policies_supported":False,
        "bind_inputs_from_clean_C_production_not_native_outputs":True,
        "raw_inputs_or_outputs_exported":False}
    (HERE/"SCALAR-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    if return_source:return actual[:3],safe
    print(json.dumps(safe,indent=2))
if __name__=="__main__":main()
