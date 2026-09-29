#!/usr/bin/env python3
"""Same-SP11 private differential verification; emit safe aggregate facts only."""
from pathlib import Path
import hashlib,importlib.util,json,random,struct
import pefile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent
TUNE=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin")
DLL=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
DLL_SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
S=load("selector",HERE/"selector.py")
A=load("authority",HERE.parent/"e011ac-rear-bpcabf411-tuning-selection"/"authority.py")
def native():
    blob=DLL.read_bytes()
    assert hashlib.sha256(blob).hexdigest()==DLL_SHA
    pe=pefile.PE(data=blob);base=pe.OPTIONAL_HEADER.ImageBase
    u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
    u.mem_map(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
    u.mem_write(base,pe.get_memory_mapped_image())
    heap=0x70000000;stack=0x71000000;stop=heap+0xf000
    u.mem_map(heap,0x10000);u.mem_map(stack,0x10000)
    def hook(uc,address,size,data):
        word=struct.unpack("<I",uc.mem_read(address,4))[0]
        if word in (0xD503237F,0xD50323FF):uc.reg_write(UC_ARM64_REG_PC,address+4)
        elif word==0xD65F0FFF:uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    def run(rows,value,mode):
        parent=heap;block=heap+0x1000;children=heap+0x2000
        vector=heap+0x3000;values=heap+0x3100;records=heap+0x4000
        u.mem_write(heap,b"\x00"*0x8000)
        u.mem_write(parent+0x30,struct.pack("<Q",block))
        u.mem_write(parent+0x40,struct.pack("<I",2))
        if mode=="outer":
            u.mem_write(block,struct.pack("<I4xQ",len(rows),records))
            rva=0x8f67e0;last=0
        else:
            u.mem_write(block+0x10,struct.pack("<I4xQ",len(rows),records))
            rva=0x8f6a90;last=1 if mode=="terminal" else 0
        for i,(start,end) in enumerate(rows):
            u.mem_write(records+i*48+8,struct.pack("<2f",start,end))
            u.mem_write(records+i*48+0x28,struct.pack("<Q",heap+0x8000+i*512))
        u.mem_write(values,struct.pack("<2f",0,value))
        u.mem_write(vector,struct.pack("<3Q",values,values+8,values+8))
        for reg,val in ((UC_ARM64_REG_X0,last),(UC_ARM64_REG_X1,parent),
                        (UC_ARM64_REG_X2,children),(UC_ARM64_REG_X3,vector),
                        (UC_ARM64_REG_LR,stop),(UC_ARM64_REG_SP,stack+0xf000)):
            u.reg_write(reg,val)
        try:u.emu_start(base+rva,stop,count=200000)
        except Exception as error:raise RuntimeError({"original_helper_rva":hex(rva),"pc_rva":hex(u.reg_read(UC_ARM64_REG_PC)-base),"mode":mode}) from error
        assert u.reg_read(UC_ARM64_REG_PC)==stop,"original interval helper did not return"
        count=u.reg_read(UC_ARM64_REG_X0)
        assert count in (1,2)
        assert struct.unpack("<I",u.mem_read(parent+0x20,4))[0]==count
        indexes=[]
        for n in range(count):
            addr=struct.unpack("<Q",u.mem_read(children+n*72+0x30,8))[0]
            delta=addr-records;assert 0<=delta<len(rows)*48 and delta%48==0
            index=delta//48;indexes.append(index)
            if mode=="terminal":
                assert struct.unpack("<Q",u.mem_read(children+n*72+0x38,8))[0]==heap+0x8000+index*512
        ratio=bytes(u.mem_read(parent+0x24,4))
        return indexes[0],indexes[-1],ratio
    return run
def neighbor(value,up):
    bits=struct.unpack("<I",struct.pack("<f",value))[0]
    if value==0:bits=1 if up else 0x80000001
    else:bits+=1 if (value>0)==up else -1
    return struct.unpack("<f",struct.pack("<I",bits))[0]
def main():
    t=A.Authority(TUNE);run=native();cases=[];source_shapes=0
    for root in A.ROOT_IDS:
        rows,leaves=S.source_intervals(t,root)
        assert leaves==t.leaves(root);source_shapes+=1
        probes=[S.f32(rows[0][0]-1),S.f32(rows[-1][1]+1)]
        for start,end in rows:
            probes.extend((neighbor(start,False),start,neighbor(start,True),
                           neighbor(end,False),end,neighbor(end,True)))
        for (_,end),(start,_) in zip(rows,rows[1:]):
            probes.extend(S.f32(end+(start-end)*fraction) for fraction in (.01,.25,.5,.75,.99))
        cases.extend((rows,value) for value in probes)
    rng=random.Random(0xE011AD)
    for count in (1,2,3,4,6):
        for _ in range(64):
            rows=[];cursor=rng.uniform(-1000,1000)
            for i in range(count):
                start=S.f32(cursor);end=S.f32(start+rng.uniform(0,80))
                rows.append((start,end));cursor=end+rng.uniform(.1,80)
            value=S.f32(rng.uniform(rows[0][0]-100,rows[-1][1]+100))
            cases.append((tuple(rows),value))
    # Touching and zero-width plateaus, narrow gaps, broad finite range.
    for rows in (((0,0),(0,1),(1,1)),((-1,-1),(1,1)),((1,1),(neighbor(1,True),neighbor(1,True)))):
        for value in (-2,-1,0,neighbor(1,False),1,neighbor(1,True),2):
            cases.append((rows,S.f32(value)))
    counts={mode:0 for mode in ("outer","nested","terminal")}
    blends=plateaus=0
    for case,(rows,value) in enumerate(cases):
        lower,upper,ratio=S.select(rows,value)
        if lower==upper:plateaus+=1
        else:blends+=1
        expected=(lower,upper,struct.pack("<f",ratio))
        for mode in counts:
            try:actual=run(rows,value,mode)
            except Exception as error:raise RuntimeError({"case":case,"mode":mode,"interval_count":len(rows)}) from error
            assert actual==expected,{"case":case,"mode":mode}
            counts[mode]+=1
    rejects=0
    for rows,value in (([],0),([(1,0)],0),([(0,2),(1,3)],0),
                       ([(0,0)]*7,0),([(0,1)],float("nan")),
                       ([(0,float("inf"))],0)):
        try:S.select(rows,value)
        except ValueError:rejects+=1
        else:raise AssertionError("unsupported interval input admitted")
    # Validate full region generation at leaf plateaus, with exposure supplied explicitly.
    fields=0
    modes_by_root={0x1a:[(0,0)],0x100:[(0,0),(1,1),(2,2)]}
    for root,modes in modes_by_root.items():
        rows,leaves=S.source_intervals(t,root)
        for i,(start,end) in enumerate(rows):
            # Shared boundaries can legitimately select the previous plateau.
            value=S.f32((float(start)+float(end))/2)
            lower,upper,ratio=S.select(rows,value)
            result=S.produce(t,modes,value)
            expected=S.AC.I.interpolate(t.region(root,leaves[lower]),t.region(root,leaves[upper]),ratio)
            assert result["root"]==root and struct.pack("<107f",*result["region"])==struct.pack("<107f",*expected)
            assert len(result["registers"])==7;fields+=107
    report={"experiment":"E011AD","status":"OFFLINE_SOURCE_INTERVAL_PASS_REQUEST_SCALAR_BINDING_OPEN",
            "source_trigger_trees_validated":source_shapes,"validated_source_shape":[1,1,6],
            "interval_input_cases":len(cases),"native_helper_cases_exact":counts,
            "native_helper_comparisons_exact":sum(counts.values()),"blend_input_cases":blends,
            "plateau_input_cases":plateaus,"unsupported_domain_rejects":rejects,
            "source_scalar_producer_region_field_matches":fields,
            "intermediate_interval_arithmetic":"binary64_subtraction_division_final_binary32",
            "native_execution":"Unicorn source arithmetic only",
            "live_startup_exposure_scalar_binding_proven":False,
            "runtime_trigger_interval_selection_proven":False,
            "complete_e008o_composition_closed":False,
            "native_rear_linux_runtime_allowed":False,"raw_source_values_exported":False}
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
