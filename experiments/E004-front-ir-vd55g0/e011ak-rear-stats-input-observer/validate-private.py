#!/usr/bin/env python3
"""Validate owned SP11 input records; publish only derived aggregates."""
from pathlib import Path
import hashlib, importlib.util, json, re, struct
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRIVATE=ROOT.parent/"private"
ATTEMPT="E011AK-20260930-1025A"
P=PRIVATE/ATTEMPT
C=P/"capture"
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(name,n,label):return (C/f"{name}{n:02}_{label}.bin").read_bytes()
def word(b,o=0):return struct.unpack_from("<I",b,o)[0]
def main():
    sizes={"AEC":{"REC":128,"CROP":16,"GAIN":4},"AWB":{"REC":128,"CROP":16,"GAIN":4},
        "RS":{"REC":132,"CROP":16,"FORMAT":4},"AECPACK":{"REC":128,"OPT":28},
        "AWBPACK":{"REC":128,"OPT":24},"RSPACK":{"REC":160,"OPT":24},
        "AECPRODUCE":{"FRAME":88},"AWBPRODUCE":{"IO":88}}
    counts={"AEC":8,"AWB":8,"RS":8,"AECPACK":2,"AWBPACK":4,"RSPACK":3,
        "AECPRODUCE":8,"AWBPRODUCE":8}
    raw=(P/"cdb-observer.raw").read_text(errors="replace")
    events=re.findall(r"E011AK_(AEC|AWB|RS|AECPACK|AWBPACK|RSPACK|AECPRODUCE|AWBPRODUCE) n=(\d+) req=(\d+) tid=([0-9a-f]+)",raw)
    requests=[int(v) for v in re.findall(r"E011AK_REQ req=(\d+)",raw)]
    assert requests==list(range(1,9))
    assert len(events)==49
    holder_bytes=(P/"holder.log").read_bytes()
    holder=holder_bytes.decode("utf-16" if holder_bytes.startswith((b"\xff\xfe",b"\xfe\xff")) else "utf-8-sig")
    for marker in ("E011AK_HOLDER_BEGIN","START_BEGIN","START_STATUS=Success","STOP_BEGIN","STOP_PASS valid_4k_handles=860","E011AK_HOLDER_END"):
        assert holder.count(marker)==1,marker
    assert "Detached" in raw and "quit:" in raw
    capture_prefix=raw.split("E011AK_REQ req=8",1)[0]
    assert not re.search(r"syntax error|memory access error|unable to|could not",capture_prefix,re.I)
    expected=set()
    for name,count in counts.items():
        own=[e for e in events if e[0]==name]
        assert [int(e[1]) for e in own]==list(range(1,count+1)),name
        if name in ("AEC","AWB","RS"):
            assert [int(e[2]) for e in own]==[1,1,2,3,4,5,6,7]
        for n in range(1,count+1):
            for label,size in sizes[name].items():
                filename=f"{name}{n:02}_{label}.bin"
                assert len(read(name,n,label))==size,filename
                expected.add(filename)
    assert {f.name for f in C.glob("*.bin")}==expected
    assert sum(f.stat().st_size for f in C.glob("*.bin"))==6464
    reference=Path(str(P)+"-generated")
    assert len(list(reference.glob("*.cmd")))==9
    assert all((P/f.name).read_bytes()==f.read_bytes() for f in reference.glob("*.cmd"))
    run=json.loads((P/"RUN-SAFE.json").read_text(encoding="utf-8-sig"))
    assert run["singleStart"] and run["cleanStop"] and run["taskRemoved"]
    assert run["detachObserved"] and run["debuggerExitCode"]==0
    assert run["valid4kHandles"]==860
    # These records contain semantic inputs/options, no optical payload.
    # OPT includes private pointers: never export any part of its raw record.
    for name in ("AEC","AWB"):
        for n in range(1,9):
            assert word(read(name,n,"GAIN"))==0x3f800000
            weights=struct.unpack_from("<3f",read(name,n,"REC"),0x30)
            assert all(0<=v<=1 for v in weights)
            assert word(read(name,n,"REC"),0x4c)<=1
    aec_weights=read("AEC",2,"REC")[0x30:0x3c]
    awb_quad=read("AWB",2,"REC")[0x4c:0x50]
    assert all(read("AECPRODUCE",n,"FRAME")[0x44:0x50]==aec_weights for n in range(1,9))
    assert all(read("AWBPRODUCE",n,"IO")[0x54:0x58]==awb_quad for n in range(1,9))
    assert all(read("AEC",n,"REC")[0x30:0x3c]==aec_weights for n in range(2,9))
    assert all(read("AWB",n,"REC")[0x4c:0x50]==awb_quad for n in range(2,9))
    assert all(read("AECPACK",n,"REC")[0x30:0x3c]==read("AEC",n,"REC")[0x30:0x3c] for n in (1,2))
    # The same AWB pack routine serves another BG client. Select the two
    # records by complete primary semantic identity, never by output registers.
    awb_indices=[]
    for n in (1,2):
        matches=[i for i in range(1,5) if read("AWBPACK",i,"REC")[:0x28]==read("AWB",n,"REC")[:0x28]]
        assert len(matches)==1
        awb_indices.append(matches[0])
    assert awb_indices==[1,3]
    assert all(read("AWBPACK",i,"REC")[0x4c:0x50]==read("AWB",n,"REC")[0x4c:0x50]
        for n,i in enumerate(awb_indices,1))
    bg=load("e011ak_bg",HERE.parent/"e011aj-rear-bg-geometry-threshold-integration/native-private.py")
    native=bg.Native()
    bg_cases=[]
    for name,rva,pack,indices in (("AEC",0xa06288,"AECPACK",[1,2]),("AWB",0x9fe120,"AWBPACK",awb_indices)):
        for i,j in enumerate(indices,1):
            rec=read(name,i,"REC")
            l,t,r,b=struct.unpack("<4I",read(name,i,"CROP"))
            inputs=[r-l+1,b-t+1,*struct.unpack_from("<10I",rec),word(rec,0x28),word(read(name,i,"GAIN"))]
            actual=native.produce(inputs,rva)
            packed=read(pack,j,"REC")
            offsets=(0,4,8,12,0x44,0x40,0x18,0x1c,0x20,0x24)
            assert actual==tuple(word(packed,o) for o in offsets)
            bg_cases.append({"client":name,"case":i,"geometry_threshold_fields_exact":10})
    # RS AdjustROI input dimensions are produced by CheckDependenceChange
    # from inclusive crop, pixel format, and input region counts.
    n=native.oracle;u=n.u;rs_cases=[]
    for i in range(1,4):
        rec=read("RS",i,"REC")
        l,t,r,b=struct.unpack("<4I",read("RS",i,"CROP"));w,h=r-l+1,b-t+1
        if word(read("RS",i,"FORMAT"))==1:w//=2
        assert word(rec)>0 and word(rec,4)>0
        u.mem_write(n.heap,bytes(0x30000));u.mem_write(n.stack,bytes(0x10000))
        u.mem_write(n.heap+0x60,rec)
        u.mem_write(n.heap+0x10c,struct.pack("<2I",w,h))
        u.mem_write(n.heap+0xe4,struct.pack("<2I",w//word(rec),h//word(rec,4)))
        for reg,value in ((UC_ARM64_REG_X0,n.heap),(UC_ARM64_REG_SP,n.stack+0xf000),(UC_ARM64_REG_LR,n.end)):
            u.reg_write(reg,value)
        u.emu_start(n.base+0xa0e538,n.end,count=100000)
        assert u.reg_read(UC_ARM64_REG_PC)==n.end
        actual=bytes(u.mem_read(n.heap+0x60,160));packed=read("RSPACK",i,"REC")
        offsets=(0,4,0x80,0x84,0x88,0x8c,0x90)
        assert all(word(actual,o)==word(packed,o) for o in offsets)
        rs_cases.append({"case":i,"counts_color_region_offset_fields_exact":7})
    assert read("RS",1,"REC")[4:]==read("RS",2,"REC")[4:]
    assert read("RS",2,"REC")[:4]==read("RS",3,"REC")[:4]
    assert read("RS",2,"REC")[8:]==read("RS",3,"REC")[8:]
    assert read("RS",1,"REC")[:4]!=read("RS",2,"REC")[:4]
    assert read("RS",2,"REC")[4:8]!=read("RS",3,"REC")[4:8]
    assert all(read("RS",i,"REC")==read("RS",3,"REC") for i in range(3,9))
    # Hash manifest remains private on the same SP11.
    (P/"VALIDATED-PRIVATE-MANIFEST.json").write_text(json.dumps({
        f.name:{"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()}
        for f in sorted([*C.glob("*.bin"),*P.glob("*.cmd"),P/"holder.ps1",P/"holder.log",P/"cdb-observer.raw",P/"RUN-SAFE.json"])},indent=2)+"\n")
    safe={"experiment":"E011AK","status":"PASS_BOUNDED_SOURCE_INPUT_CAPTURE_AND_PRIVATE_NATIVE_REPLAY",
        "attempt":ATTEMPT,"single_start":True,"valid_4k_handles":860,"clean_stop":True,
        "resolved_user_mode_probes":9,"capture_events":counts,"request_hook_ids":requests,
        "request_consumer_ids":[1,1,2,3,4,5,6,7],"private_files":106,"private_bytes":6464,
        "generated_scripts_byte_identical":True,"unity_gain_samples":16,
        "unity_gain_binding_closed_for_sampled_rear_startup":True,
        "normal_AEC_producer_weight_fields_identical":24,"normal_AWB_producer_quad_fields_identical":8,
        "producer_request_label":"last observed IFE hook, not independently tagged AEC/AWB ExecuteProcessRequest",
        "cold_weight_quad_initialization_origin_closed":False,
        "AWB_pack_cases_identified":[1,3],"other_BG_pack_cases_excluded":[2,4],
        "original_BG_geometry_threshold_replay":bg_cases,"original_RS_region_replay":rs_cases,
        "RS_input_transition":"horizontal count at second request-1 consumer, then vertical count at request2; holds through sampled request7",
        "RS_color_flag_is_module_enable":False,"RS_normal_count_policy_producer_closed":False,
        "RS_shift_field_native_replay_closed":False,
        "remaining_full_composer_differences":11,"full_composer_changed":False,
        "task_removed":True,"debugger_detached":True,"debugger_exit_code":0,
        "return_golden_boot_id":"b74c0760-83bb-421f-ac4d-1efa4e297294",
        "golden_kernel":"7.1.5-sp11-render-parity-v4+","saved_entry":"sp11-audio-fullio-v19c",
        "next_entry_empty":True,"camera_modules_nodes_processes_absent":True,"windows_ntfs_unmounted":True,
        "OEM_bytes_or_raw_logs_exported":False,"optical_pixels_saved":False,
        "kernel_debugging":False,"module_installed_or_loaded":False,
        "WM16_safe_retirement_closed":False,"native_rear_ISP_runtime_authorized":False}
    (HERE/"VALIDATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps(safe,indent=2))
if __name__=="__main__":main()
