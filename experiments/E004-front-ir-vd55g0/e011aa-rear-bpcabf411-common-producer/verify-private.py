#!/usr/bin/env python3
"""SP11-local source execution and private-output comparison; emit counts only."""
from pathlib import Path
import hashlib, importlib.util, json, random, struct, sys
import pefile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import *
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DLL = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
TUNE = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin")
DLL_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
TUNE_SHA = "4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"

def load(path, name):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)
    return m
P = load(HERE/"producer.py","e011aa_producer")
D = load(ROOT/"experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py","e011aa_decoder")
DEC = load(ROOT/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py","e011aa_commands")

def source_runner():
    blob=DLL.read_bytes();assert hashlib.sha256(blob).hexdigest()==DLL_SHA
    pe=pefile.PE(data=blob);base=pe.OPTIONAL_HEADER.ImageBase
    u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
    u.mem_map(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
    u.mem_write(base,pe.get_memory_mapped_image())
    heap=0x70000000;stack=0x71000000
    u.mem_map(heap,0x10000);u.mem_map(stack,0x10000)
    # Arithmetic source runs only inside Unicorn; there is no device access.
    def hook(uc,address,size,data):
        word=struct.unpack("<I",uc.mem_read(address,4))[0]
        if word in (0xD503237F,0xD50323FF): # PACIBSP/AUTIBSP, emulator-only
            uc.reg_write(UC_ARM64_REG_PC,address+4)
        elif word==0xD65F0FFF: # RETAB, emulator-only return to x30
            uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    def run(levels,preserve,curves,anchors):
        region=[0.0]*107
        region[82:84]=levels
        region[84:88]=[preserve[0][0],preserve[1][0],preserve[0][1],preserve[1][1]]
        region[88:98]=curves[0]+curves[1]
        u.mem_write(heap,struct.pack("<107f",*region))
        u.mem_write(heap+0x1000,bytes(0x1000))
        u.mem_write(heap+0x2000,struct.pack("<6f",0,*anchors))
        u.mem_write(stack,bytes(0x10000))
        u.reg_write(UC_ARM64_REG_SP,stack+0xF000)
        u.reg_write(UC_ARM64_REG_X20,heap)
        u.reg_write(UC_ARM64_REG_X21,heap+0x3000)
        u.reg_write(UC_ARM64_REG_X22,heap+0x1000)
        u.reg_write(UC_ARM64_REG_X24,heap+0x2000)
        u.reg_write(UC_ARM64_REG_X26,1)
        u.reg_write(UC_ARM64_REG_S11,struct.unpack("<I",struct.pack("<f",256.0))[0])
        u.reg_write(UC_ARM64_REG_S9,0)
        u.emu_start(base+0x9c1d34,base+0x9c223c,count=200000)
        assert u.reg_read(UC_ARM64_REG_PC)==base+0x9c223c
        u.reg_write(UC_ARM64_REG_S9,0)
        u.emu_start(base+0x9c2474,base+0x9c26f8,count=50000)
        assert u.reg_read(UC_ARM64_REG_PC)==base+0x9c26f8
        out=bytes(u.mem_read(heap+0x1000,0x100))
        def hs(start,n):return list(struct.unpack_from("<"+str(n)+"H",out,start))
        def ss(start,n):return list(struct.unpack_from("<"+str(n)+"h",out,start))
        return {"signed10":ss(0x50,2),"unsigned9":hs(0x4c,2),"nibble4":hs(0x54,2),
                "byte_group0":[hs(0x60,4),hs(0x68,4)],
                "byte_group1":[hs(0x70,4),hs(0x78,4)],
                "nibble_group":[hs(0x80,4),hs(0x88,4)]}
    return run

def main():
    b=TUNE.read_bytes();assert hashlib.sha256(b).hexdigest()==TUNE_SHA
    h=D.parse_header(b);r,_=D.parse_symbol_table(b,h["sections"][0],h["sections"][1])
    # Build all installed BPC leaf candidates. Selection is deliberately NOT
    # inferred from output matching and still requires request-side provenance.
    cases=[]
    for sid in (0x1a,0xf0,0x100,0x113):
        root=D.data_bytes(b,h["sections"][1],r[sid])
        trigger=struct.unpack_from("<I",root,len(root)-4)[0]
        anchors=struct.unpack_from("<5f",root,27*4)
        assert anchors[0]==0 and anchors[-1]==1
        for leaf in range(trigger+4,trigger+15,2):
            vals=struct.unpack("<107f",D.data_bytes(b,h["sections"][1],r[leaf]))
            cases.append((list(vals[82:84]),
                          [[vals[84],vals[86]],[vals[85],vals[87]]],
                          [list(vals[88:93]),list(vals[93:98])],list(anchors)))
    run=source_runner()
    source_checks=0
    candidates=[]
    for case in cases:
        clean=P.calculate(*case);original=run(*case)
        assert clean==original,"installed leaf calculation mismatch"
        source_checks+=1;candidates.append(P.pack(clean))
    rng=random.Random(0xE011AA)
    synthetic=120
    for n in range(synthetic):
        lo=rng.uniform(0,400);hi=lo+rng.uniform(1,300)
        curves=[[rng.uniform(0,1.2) for _ in range(5)] for _ in range(2)]
        preserve=[[rng.uniform(0,1.2) for _ in range(2)] for _ in range(2)]
        anchors=sorted([0,rng.uniform(.1,.3),rng.uniform(.35,.6),rng.uniform(.65,.9),1])
        case=([lo,hi],preserve,curves,anchors)
        assert P.calculate(*case)==run(*case),"synthetic calculation mismatch"
        source_checks+=1
    boundary_cases=[
        ([160,224],[[0.6,0.6],[0.8,0.8]],[[1]*5,[0]*5],[0,.4,.6,.8,1]),
        ([1,1],[[0,1],[1,0]],[[1,.75,.5,.25,0],[0,.25,.5,.75,1]],[0,.4,.6,.8,1]),
        ([0,1023],[[1,0],[0,1]],[[0,0,0,0,0],[1,1,1,1,1]],[0,.4,.6,.8,1]),
        ([0,1],[[0,1],[1,0]],[[1,.9,.8,.7,.6],[1,.9,.8,.7,.6]],[0,.4,.6,.8,1]),
        ([160,224],[[.001953125,.005859375],[.998046875,1.001953125]],
         [[.001953125,.005859375,.009765625,.013671875,.017578125],[1.2,1.1,1,.9,.8]],
         [0,.4,.6,.8,1])
    ]
    for case in boundary_cases:
        assert P.calculate(*case)==run(*case),"boundary calculation mismatch"
        source_checks+=1
    safe_case=cases[0]
    rejection_checks=0
    for bad in [
        (safe_case[0],[[float("nan"),0],[0,0]],safe_case[2],safe_case[3]),
        (safe_case[0],safe_case[1],[[float("inf")]*5,[0]*5],safe_case[3]),
        (safe_case[0],safe_case[1],[[-1]*5,[0]*5],safe_case[3]),
        (safe_case[0],safe_case[1],safe_case[2],[0,.8,.4,.9,1]),
        ([224,160],safe_case[1],safe_case[2],safe_case[3]),
        (safe_case[0],safe_case[1],safe_case[2],[0,0,0,0,0])
    ]:
        try:P.calculate(*bad)
        except ValueError:rejection_checks+=1
        else:raise AssertionError("invalid semantics admitted")
    recs=json.loads((ROOT.parent/"private/e006a/E006A-PRIVATE-RECORDS-v2.json").read_text(encoding="utf-8-sig"))
    checked=matched=startup=startup_matched=0
    for rec in recs["records"]:
        if rec.get("idx")!=1 or not rec.get("complete"):continue
        writes=DEC.decode(bytes.fromhex(rec["hex"]))["writes"]
        vals={reg:val for reg,val,_offset,_kind in writes if reg in P.REGS}
        if len(vals)!=7:continue
        checked+=1;ok=any(vals==candidate for candidate in candidates)
        matched+=int(ok)
        if rec["n"]<4:startup+=1;startup_matched+=int(ok)
    assert checked==matched==22 and startup==startup_matched==3
    safe={"experiment":"E011AA","status":"PASS" if startup==startup_matched==3 else "PARTIAL",
          "installed_leaf_source_cases":len(cases),"synthetic_source_cases":synthetic,
          "native_arithmetic_differential_cases":source_checks,
          "boundary_source_cases":len(boundary_cases),"invalid_input_rejections":rejection_checks,
          "private_records_checked":checked,"private_records_exact_candidate_match":matched,
          "private_startup_records_checked":startup,"private_startup_records_exact":startup_matched,
          "registers_per_record":7,"source_execution":"isolated Unicorn arithmetic only",
          "runtime_tuning_selection_proven":False,"serialized_reserve_runtime_mapping_proven":False,
          "packet_request_binding_proven":False,"complete_e008o_composition_closed":False,
          "native_rear_hardware_isp_runtime_authorized":False,
          "raw_register_values_emitted":False,"raw_tuning_bytes_emitted":False,
          "raw_packet_bytes_emitted":False}
    (HERE/"VALIDATION-SAFE.json").write_text(json.dumps(safe,indent=2)+"\n")
    print(json.dumps(safe,indent=2))
if __name__=="__main__":main()
