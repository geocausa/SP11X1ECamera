#!/usr/bin/env python3
"""SP11-only RS input/copy qualification. Raw records and packets stay private.
The metadata API, registry/settings, loader TLS and lock objects are owned
fixtures. This is NOT an implementation or proof of the upstream AFD algorithm.
"""
from pathlib import Path
import hashlib, importlib.util, json, random, struct, subprocess, tempfile
import pefile
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EX = HERE.parent
PRIVATE = ROOT.parent / "private"
IMAGE_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
READER_SHA = "904c4309b9ddae9adffdf2e5dacf92a84c829edc839921be18a56b226b5cc08e"
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def parent(tag, name):
    paths = list(EX.glob(tag + "-*/" + name))
    assert len(paths) == 1
    return paths[0]
def observed():
    capture = PRIVATE / "E011AK-20260930-1025A/capture"
    records, inputs, pins = [], [], []
    for index in range(1, 4):
        record = (capture / f"RS{index:02d}_REC.bin").read_bytes()
        crop = (capture / f"RS{index:02d}_CROP.bin").read_bytes()
        fmt = (capture / f"RS{index:02d}_FORMAT.bin").read_bytes()
        assert len(record) == 132 and len(crop) == 16 and len(fmt) == 4
        l,t,r,b = struct.unpack("<4I", crop)
        assert l == t == 0
        count = struct.unpack_from("<2I", record)
        assert struct.unpack_from("<2I", record, 8) == (0, 0)
        color = struct.unpack_from("<I", record, 128)[0]
        half = int(struct.unpack("<I",fmt)[0] == 1)
        records.append(record + crop + struct.pack("<I", half))
        inputs.append((r-l+1,b-t+1,*count,half,color))
        pins.append({"case":index,"record_sha256":hashlib.sha256(record).hexdigest(),
                     "crop_sha256":hashlib.sha256(crop).hexdigest(),
                     "format_sha256":hashlib.sha256(fmt).hexdigest()})
    previous = HERE / "SOURCE-SAFE.json"
    if previous.exists():
        assert json.loads(previous.read_text())["observed_fixture_pins"] == pins, "changed observed RS fixture"
    return records,inputs,pins

def vm_check(image, payloads):
    native = image.Native()
    u = native.u
    u.mem_map(0x73000000,0x400000)
    u.mem_map(0x74000000,0x30000)
    blob = image.DLL.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == IMAGE_SHA
    pe = pefile.PE(data=blob)
    assert hashlib.sha256(pe.get_data(0x740e70,1792)).hexdigest() == READER_SHA
    code = next(s for s in pe.sections if s.Characteristics & 0x20000000)
    initial_code = bytes(u.mem_read(native.base+code.VirtualAddress,code.Misc_VirtualSize))
    heap_size=0x30000
    total_instructions=0
    modes={"present":0,"absent":0,"fallback":0}
    total_query_callbacks=0
    # The preserved-register ABI is checked independently of the copied data.
    saved_regs=[UC_ARM64_REG_X19+i for i in range(10)]+[UC_ARM64_REG_X29]
    for bias in (0,0x1000,0x2000,0x3000):
        for payload in payloads:
            assert len(payload) == 132
            for mode in modes:
                u.mem_write(native.heap,bytes(heap_size))
                u.mem_write(native.stack,bytes(0x10000))
                u.mem_write(0x73000000,bytes(0x400000))
                u.mem_write(0x74000000,bytes(0x30000))
                node=native.heap+bias
                dest=native.heap+0x10000+bias
                source=native.heap+0x20000
                registry=native.heap+0x8000
                context=native.heap+0x9000
                settings=0x73000000
                teb=0x74000000
                u.mem_write(settings+0x10,struct.pack("<Q",settings+0x1000))
                u.mem_write(settings+0x1010,struct.pack("<Q",settings+0x2000))
                u.mem_write(teb+0x58,struct.pack("<Q",teb+0x10000))
                u.mem_write(teb+0x10000,struct.pack("<Q",teb+0x20000))
                u.reg_write(UC_ARM64_REG_X18,teb)
                u.reg_write(UC_ARM64_REG_TPIDR_EL0,teb)
                u.mem_write(node+0x400,struct.pack("<Q",context))
                u.mem_write(node+0x33f4,struct.pack("<I",1))
                # Explicit owned runtime tag-vector fixture, not source-file BSS authority.
                u.mem_write(native.base+0x17a30e0,struct.pack("<7I",*range(0x1000,0x1007)))
                for k,off in enumerate((0xc0,0xd8,0x48,0x60,0x78,0x90,0xa8)):
                    u.mem_write(registry+off,struct.pack("<I",0x1000+k))
                prior=bytes((k*11+3)&255 for k in range(132))
                u.mem_write(dest+0x2c50,prior)
                u.mem_write(source,payload)
                before=bytes(u.mem_read(native.heap,heap_size))
                expected=bytearray(before)
                if mode != "absent":
                    off=dest+0x2c50-native.heap
                    expected[off:off+132]=payload
                sp=native.stack+0xf000
                canaries={reg:0x12340000+reg for reg in saved_regs}
                for reg,value in canaries.items():u.reg_write(reg,value)
                u.reg_write(UC_ARM64_REG_X0,node)
                u.reg_write(UC_ARM64_REG_X1,dest)
                u.reg_write(UC_ARM64_REG_SP,sp)
                u.reg_write(UC_ARM64_REG_LR,native.end)
                visits=[];queries=[];rs_queries=[];lock=[False];getters=[0]
                callbacks={0x5b80a8:"registry",0xce7ad8:"lock",
                           0xce7a48:"unlock",0x5bde08:"settings",0x5d4d30:"query"}
                def hook(uc,address,size,user):
                    if address == native.end:
                        uc.emu_stop()
                        return
                    rva=address-native.base
                    if rva in callbacks:
                        kind=callbacks[rva]
                        caller=uc.reg_read(UC_ARM64_REG_LR)-native.base
                        assert 0x740e70 <= caller < 0x741570
                        if kind == "registry":
                            getters[0]+=1
                            uc.reg_write(UC_ARM64_REG_X0,registry)
                        elif kind == "settings":
                            uc.reg_write(UC_ARM64_REG_X0,settings)
                        elif kind == "lock":
                            assert not lock[0];lock[0]=True
                        elif kind == "unlock":
                            assert lock[0];lock[0]=False
                        else:
                            args=[uc.reg_read(UC_ARM64_REG_X0+i) for i in range(8)]
                            assert args[0]==node
                            assert args[1]==native.base+0x17a30e0
                            assert struct.unpack("<7I",uc.mem_read(args[1],28))==tuple(range(0x1000,0x1007))
                            assert args[2]==sp-0xf0
                            assert 0<=args[3]<7
                            assert args[4] in (0,1)
                            assert args[5:8]==[0,0,1]
                            index=args[3];value=0
                            if index==5:
                                rs_queries.append(args[4])
                                if mode=="present" or (mode=="fallback" and len(rs_queries)==2):
                                    value=source
                            uc.mem_write(args[2]+index*8,struct.pack("<Q",value))
                            uc.reg_write(UC_ARM64_REG_X0,0)
                            queries.append(index)
                        uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
                        return
                    assert (0x740e70<=rva<0x741570) or (0x11d0<=rva<0x1220)
                    visits.append(rva)
                handle=u.hook_add(UC_HOOK_CODE,hook)
                try:
                    u.emu_start(native.base+0x740e70,native.end,count=20000)
                finally:
                    u.hook_del(handle)
                assert u.reg_read(UC_ARM64_REG_PC)==native.end
                assert u.reg_read(UC_ARM64_REG_SP)==sp
                assert all(u.reg_read(reg)==value for reg,value in canaries.items())
                assert not lock[0] and getters[0]==7
                assert rs_queries == ([0] if mode=="present" else [0,1])
                assert bytes(u.mem_read(native.heap,heap_size))==bytes(expected)
                assert bytes(u.mem_read(native.stack,0xec00))==bytes(0xec00)
                assert bytes(u.mem_read(sp,0x1000))==bytes(0x1000)
                modes[mode]+=1
                total_instructions+=len(visits)
                total_query_callbacks+=len(queries)
    assert bytes(u.mem_read(native.base+code.VirtualAddress,code.Misc_VirtualSize))==initial_code
    return {"cases":sum(modes.values()),"cases_by_record_state":modes,
            "original_instruction_visits_including_original_frame_helpers":total_instructions,
            "owned_metadata_query_callbacks":total_query_callbacks,
            "all132_RS_bytes_exact":True,"entire_owned_heap_unchanged_except_expected_RS_record":True,
            "source_records_immutable":True,"incoming_SP_and_callee_saved_registers_preserved":True,
            "stack_redzones_unchanged":True,"original_executable_bytes_unchanged":True,
            "API_registry_settings_TLS_lock_objects_are_owned_fixtures":True,
            "runtime_property_tag_vector_is_an_owned_fixture":True,
            "upstream_query_helper_registry_publication_AFD_policy_not_executed":True}

def main():
    assert PRIVATE.is_dir()
    image=load("dk_image",parent("e011ai","native-private.py"))
    records,inputs,pins=observed()
    rng=random.Random(1104)
    synthetic=[]
    for index in range(5):
        wire=bytearray(rng.randbytes(132))
        struct.pack_into("<4I",wire,0,1+index,128+index,0,0)
        struct.pack_into("<I",wire,128,index%2)
        synthetic.append(bytes(wire))
    vm=vm_check(image,[record[:132] for record in records]+synthetic)
    original=load("dk_numeric_parent",parent("e011am","native-private.py")).Native()
    outputs=[original.produce(x) for x in inputs]
    compilers=[]
    with tempfile.TemporaryDirectory(prefix="e011dk-private-",dir=PRIVATE) as tmp:
        for cc in ("gcc","clang"):
            binary=Path(tmp)/cc
            build=subprocess.run([cc,"-std=c11","-Wall","-Wextra","-Werror",
                "-fsanitize=address,undefined","-g",str(HERE/"check.c"),"-o",str(binary)],
                capture_output=True)
            if build.returncode:
                (Path(tmp)/"build.private.log").write_bytes(build.stderr)
                raise RuntimeError("RS decoder build failed; diagnostic stays private")
            check=subprocess.run([str(binary),"--selfcheck"],capture_output=True)
            assert check.returncode==0 and not check.stderr
            negatives=json.loads(check.stdout)["atomic_negative_cases"]
            run=subprocess.run([str(binary)],input=b"".join(records),capture_output=True)
            assert run.returncode==0 and not run.stderr and len(run.stdout)==3*56
            for index,(inp,out) in enumerate(zip(inputs,outputs)):
                assert struct.unpack_from("<14I",run.stdout,index*56)==inp+out
            compilers.append({"compiler":cc,"atomic_negative_cases":negatives,
                              "observed_source_records_decoded":3,
                              "input_and_original_RS_output_fields_exact":42,
                              "ASan_UBSan_stderr_empty":True})
    report={"experiment":"E011DK","status":"PASS_BOUNDED_ORIGINAL_RS_METADATA_COPY_AND_C_INPUT_DECODER",
            "original_image_sha256":IMAGE_SHA,"original_reader_RVA":"0x740e70",
            "original_reader_bytes":1792,"original_reader_sha256":READER_SHA,
            "RS_query_slot":5,"source_property_table_RVA":"0x17a30e0",
            "destination_record_offset":"0x2c50","metadata_record_bytes":132,
            "reader":vm,"compiler_runs":compilers,"observed_fixture_pins":pins,
            "initial_RS_origin_reused":"E011M","RS_numerical_producer_reused":"E011AM",
            "upstream_AFD_normal_count_policy_closed":False,
            "metadata_query_helper_or_actual_runtime_registry_qualified":False,
            "runtime_property_tag_vector_initialization_qualified":False,
            "complete_deterministic_source_bootstrap_closed":False,
            "whole_frame_zero_offset_scope_only":True,
            "native_rear_runtime_allowed":False,"new_camera_starts":0,"new_reboots":0,
            "new_kernel_build":False,"private_bytes_exported":False,
            "sampled_unity_BG_gain_binding_already_closed":"E011AK, 16 samples; arbitrary gain unsupported"}
    (HERE/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":report["status"],"reader_cases":vm["cases"],
                     "instructions":vm["original_instruction_visits_including_original_frame_helpers"],
                     "compilers":compilers,"upstream_AFD_normal_count_policy_closed":False}),flush=True)

if __name__ == "__main__":
    main()
