#!/usr/bin/env python3
"""Private, bounded scalar-reader differential. Original bytes stay on SP11."""
from pathlib import Path
import importlib.util,hashlib,json,struct,random,subprocess,tempfile
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent;PRIVATE=ROOT.parent/"private"
ARCHIVE=ROOT.parents[1]/"00-RE-archive/sp11-driverdump"
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
FILES=(
("qccamplatform8380.inf_arm64_16d44e9aca3becfb/com.qti.tuned.default.bin","aa685fb55e528e717eaf115112dd08bffb5d15c7cd00c4570282163667008150"),
("surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.qti.tuned.default.bin","ca620fbcfd9bde3c25157289ac7172244fb39744b36d293ea53ab94422eea634"),
("surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin","4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"))
def qualified_root(blob):
    d=load("av_chrom",ROOT/"experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py")
    h=d.parse_header(blob);symbols,_=d.parse_symbol_table(blob,h["sections"][0],h["sections"][1])
    roots=[r for r in symbols.values() if r["type"]=="bgStatsConfigV1"]
    assert len(roots)==1,"ambiguous named module"
    r=roots[0]
    assert (r["version_major"],r["version_minor"],r["mode_id"],r["data_bytes"])==(1,0,0,93)
    sec=h["sections"][2];assert sec["size"]%20==0
    records=[struct.unpack_from("<5I",blob,i) for i in range(sec["offset"],sec["end"],20)]
    byid={v[0]:v for v in records};assert len(byid)==len(records)
    node=byid[r["mode_symbol_id"]]
    assert node==(6,0,6,0,0xffffffff),"unsupported selector"
    assert byid[node[3]]==(0,0,0,0,0xffffffff),"not Default ancestry"
    wire=d.data_bytes(blob,h["sections"][1],r);assert len(wire)==93
    return wire
def source_records():
    wires=[]
    for name,sha in FILES:
        b=(ARCHIVE/name).read_bytes();assert hashlib.sha256(b).hexdigest()==sha
        wires.append(qualified_root(b))
    return wires
class NativeScalar:
    def __init__(self):
        self.n=load("av_image",EX/"e011ai-rear-neutral-scalar-full-integration/native-private.py").Native()
        n=self.n;u=n.u
        self.obj=n.heap+0x18000
        def returned(v=None):
            if v is not None:u.reg_write(UC_ARM64_REG_X0,v)
            u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
        def hook(uc,address,size,user):
            r=address-n.base
            if r in (0x11d0,0x11f0,0x6f4ac0,0x6f45d8):
                returned();return
            if r==0xf5df00:returned(0);return
            if r==0xcae740:
                assert u.reg_read(UC_ARM64_REG_X0)==392
                returned(self.obj);return
            if r==0xf5e600:
                dst=u.reg_read(UC_ARM64_REG_X0);count=u.reg_read(UC_ARM64_REG_X2)
                assert n.heap<=dst and dst+count<=n.heap+0x30000
                u.mem_write(dst,bytes([u.reg_read(UC_ARM64_REG_X1)&255])*count)
                returned(dst)
        u.hook_add(UC_HOOK_CODE,hook)
    def prefix(self,wire):
        n=self.n;u=n.u;reader=n.heap+0x1000;src=n.heap+0x10000
        u.mem_write(n.heap,bytes(0x30000));u.mem_write(n.stack,bytes(0x10000))
        u.mem_write(src,wire);u.mem_write(reader+0xc8,struct.pack("<I",len(wire)))
        u.mem_write(reader+0xd0,struct.pack("<Q",src))
        u.mem_write(reader,struct.pack("<Q",n.heap+0x2000))
        u.mem_write(n.heap+0x2000,struct.pack("<Q",n.end))
        for reg,value in ((UC_ARM64_REG_X0,n.heap),(UC_ARM64_REG_X1,reader),(UC_ARM64_REG_X2,0),(UC_ARM64_REG_SP,n.stack+0xf000),(UC_ARM64_REG_LR,n.end)):
            u.reg_write(reg,value)
        u.emu_start(n.base+0x236ed0,n.base+0x2372ac,count=100000)
        assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x2372ac
        return bytes(u.mem_read(self.obj+0x130,28))
def authority_negatives():
    blob=(ARCHIVE/FILES[-1][0]).read_bytes()
    d=load("av_schema",ROOT/"experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py")
    h=d.parse_header(blob);sy,_=d.parse_symbol_table(blob,h["sections"][0],h["sections"][1])
    r=sy[173]["record_offset"];sec=h["sections"][2]
    node=next(i for i in range(sec["offset"],sec["end"],20) if struct.unpack_from("<I",blob,i)[0]==6)
    root=next(i for i in range(sec["offset"],sec["end"],20) if struct.unpack_from("<I",blob,i)[0]==0)
    fields=((r+36,2),(r+36,0x10001),(r+40,1),(r+44,7),(r+52,92),
        (node+8,2),(node+4,2),(node+12,17),(node+16,0),(root+8,1))
    mutations=[]
    for offset,value in fields:
        b=bytearray(blob);struct.pack_into("<I",b,offset,value);mutations.append(bytes(b))
    b=bytearray(blob);b[r+4:r+36]=b"unsupported".ljust(32,b"\0");mutations.append(bytes(b))
    other=next(v["record_offset"] for v in sy.values() if v["symbol_id"]!=173)
    b=bytearray(blob);b[other+4:other+36]=b"bgStatsConfigV1".ljust(32,b"\0");mutations.append(bytes(b))
    for b in mutations:
        try:qualified_root(b)
        except (AssertionError,ValueError,KeyError):pass
        else:raise AssertionError("malformed source authority accepted")
    return len(mutations)
def main(return_source=False):
    authority_cases=authority_negatives()
    roots=source_records();native=NativeScalar();cases=list(roots)
    for value in (0,1,2,256,0x01020304,0xffffffff):
        b=bytearray(roots[-1]);struct.pack_into("<I",b,24,value);cases.append(bytes(b))
    rng=random.Random(0xe011a7)
    for i in range(128):
        b=bytearray(roots[-1]);b[8:36]=rng.randbytes(28)
        struct.pack_into("<I",b,24,i%2);cases.append(bytes(b))
    for b in cases:assert native.prefix(b)==b[8:36],"scalar prefix mapping mismatch"
    live=(PRIVATE/"E011AU-20260930-2327B-captured/capture/BGSTATSCONFIG_SOURCE.bin").read_bytes()
    assert len(live)==96 and native.prefix(roots[-1])==live[16:44]
    reports=[];source_quad=None
    with tempfile.TemporaryDirectory(prefix="e011av-scalar-",dir=PRIVATE) as tmp:
        for compiler in ("gcc","clang"):
            binary=Path(tmp)/compiler
            build=subprocess.run([compiler,"-std=c11","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-g",str(HERE/"quad-check.c"),"-o",str(binary)],capture_output=True)
            assert build.returncode==0,"quad build failure"
            run=subprocess.run([str(binary)],input=b"".join(cases),capture_output=True)
            if run.returncode:(PRIVATE/("E011AV-"+compiler+"-failure.raw")).write_bytes(run.stderr)
            assert run.returncode==0 and len(run.stdout)==8*len(cases),"quad run failure"
            for i,b in enumerate(cases):
                result,out=struct.unpack_from("<iI",run.stdout,i*8);value=struct.unpack_from("<I",b,24)[0]
                assert (result,out)==((0,value) if value<=1 else (-34,0xa5a5a5a5))
            q=struct.unpack_from("<iI",run.stdout,2*8)[1]
            if source_quad is not None:assert q==source_quad
            source_quad=q
            reports.append({"compiler":compiler,"cases":len(cases),"invalid_boolean_cases":4,"length_negative_cases":99,"schema_negative_cases":2,"null_negative_cases":2})
    assert all(struct.unpack_from("<I",b,24)[0]==source_quad for b in roots)
    safe={"experiment":"E011AV","status":"PASS_BOUNDED_SOURCE_COLD_QUAD_SCALAR","source_files":[{"path":p,"sha256":s} for p,s in FILES],
        "authority_negative_cases":authority_cases,"original_DLL_sha256":"c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35","qualified_named_Default_roots":3,"serialized_bytes_per_root":93,"wire_quad_offset":24,"runtime_quad_offset":32,
        "compiler_runs":reports,"original_scalar_cases":len(cases),"scalar_prefix_bytes_per_case":28,
        "live_scalar_prefix_matching_bytes":28,"source_quad":source_quad,"captured_bytes_used_as_producer_inputs":False,
        "original_executable_modified":False,"original_payload_scalar_reader_executed":True,
        "metadata_allocation_security_and_name_helpers_stubbed":True,"full_module_deserialization_closed":False,
        "exact_loaded_source_file_attribution_closed":False,"source_file_invariant_quad_for_three_qualified_roots":True,
        "bounded_cold_quad_numeric_policy_closed":True,"complete_source_profile_materialization_closed":False,
        "native_rear_runtime_allowed":False,"OS_driver_invocations":False,"private_bytes_exported":False}
    (HERE/"SCALAR-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    if return_source:return roots[-1],source_quad,safe
    print(json.dumps(safe,indent=2))
if __name__=="__main__":main()
