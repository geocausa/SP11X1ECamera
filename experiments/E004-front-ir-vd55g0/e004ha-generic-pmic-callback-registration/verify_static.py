#!/usr/bin/env python3
"""Pin the OEM PMIC generic raw-write callback and its two descriptor producers.

Offline PE and ARM64 verification only. Callback registration is not evidence
that the callback executes, a register write completed, or a flash is bounded.
"""
from pathlib import Path
from hashlib import sha256
import json
import struct
import capstone
import pefile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCHIVE=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
OEM_SHA="756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e"
BASE=0x140000000
TABLE=(0x327c0,0x32920,0x329e0,0x32b70)
PRODUCERS={
    "general_descriptor":{"caller":0x20304,"function":0x2f918,
                          "adrp":0x2f9cc,"add":0x2f9d0,"store":0x2f9d8,
                          "table_head":0x3a4f8},
    "type_0x4a_descriptor":{"caller":0x2021c,"function":0x2fdd0,
                           "adrp":0x2fe5c,"add":0x2fe60,"store":0x2fe68,
                           "table_head":0x3a508},
}

def require(ok,why):
    if not ok:raise AssertionError("E004HA_FAIL_CLOSED "+why)

def original():
    files=list(ARCHIVE.glob("qcpmic8380.inf_*/qcpmic8380.sys"))
    require(len(files)==1,"ambiguous original OEM driver")
    raw=files[0].read_bytes()
    require(sha256(raw).hexdigest()==OEM_SHA,"original PMIC hash drift")
    pe=pefile.PE(data=raw)
    require(pe.OPTIONAL_HEADER.ImageBase==BASE and pe.FILE_HEADER.Machine==0xaa64,
            "not original Windows ARM64 PMIC")
    return pe

def instruction(pe,rva):
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    found=list(cs.disasm(pe.get_data(rva,4),BASE+rva))
    require(len(found)==1,"missing instruction "+hex(rva))
    return found[0].mnemonic,found[0].op_str

def expect(pe,rva,mnemonic,operands):
    require(instruction(pe,rva)==(mnemonic,operands),
            "original instruction changed at "+hex(rva))
    return True

def callers(pe,target):
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    cs.skipdata=True
    sites=[]
    for sec in pe.sections:
        if not sec.Characteristics&0x20000000:continue
        for i in cs.disasm(sec.get_data(),BASE+sec.VirtualAddress):
            if i.mnemonic=="bl" and i.op_str.startswith("#") and int(i.op_str[1:],16)==BASE+target:
                sites.append(i.address-BASE)
    return sorted(sites)

def verify(pe):
    for i,target in enumerate(TABLE):
        require(struct.unpack("<Q",pe.get_data(0x3a4f8+8*i,8))[0]==BASE+target,
                "true OEM PMIC callback table changed at slot "+str(i))
    require(struct.unpack("<Q",pe.get_data(0x3a518,8))[0]==1,
            "callback table trailing data changed")
    for name,desc in PRODUCERS.items():
        require(callers(pe,desc["function"])==[desc["caller"]],
                "registration function callers changed "+name)
        expect(pe,desc["caller"],"bl","#"+hex(BASE+desc["function"]))
        expect(pe,desc["adrp"],"adrp","x8, #0x14003a000")
        expect(pe,desc["add"],"add","x8, x8, #"+hex(desc["table_head"]-0x3a000))
        store="x8, [x11, x12]" if name=="general_descriptor" else "x8, [x11, x9]"
        expect(pe,desc["store"],"str",store)
    expect(pe,0x2fdf4,"ldr","w5, [x20, #4]")
    expect(pe,0x2fdf8,"cmp","w5, #0x4a")
    expect(pe,0x32b90,"uxth","w25, w1")
    expect(pe,0x32b94,"uxtb","w20, w2")
    expect(pe,0x32c20,"mov","w4, w20")
    expect(pe,0x32c24,"mov","w2, w25")
    expect(pe,0x32c28,"mov","x3, x23")
    expect(pe,0x32c2c,"bl","#0x140023dc8")
    require(callers(pe,0x32b70)==[],
            "generic wrapper unexpectedly gained a direct BL")
    return {
        "original_runtime_callback_table_rva":"0x3a4f8",
        "callback_targets_rva":[hex(x) for x in TABLE],
        "generic_write_callback_slot_rva":"0x3a510",
        "generic_write_callback_rva":"0x32b70",
        "general_descriptor_function_rva":"0x2f918",
        "general_descriptor_caller_rva":"0x20304",
        "general_descriptor_table_head_rva":"0x3a4f8",
        "type_0x4a_descriptor_function_rva":"0x2fdd0",
        "type_0x4a_descriptor_caller_rva":"0x2021c",
        "type_0x4a_descriptor_table_head_rva":"0x3a508",
        "type_0x4a_table_has_generic_writer_at_index":1,
        "generic_writer_register_address":"w1 truncated to u16",
        "generic_writer_byte_count":"w2 truncated to u8",
        "generic_writer_data_pointer":"x3",
        "generic_writer_calls_raw_write_rva":"0x23dc8",
        "descriptor_producer_is_runtime_callback_invocation_proven":False,
        "subtype_0x4a_represents_camera_or_emitter_proven":False,
    }

def prior_check():
    p=ROOT/"experiments/E004-front-ir-vd55g0/e004gz-raw-pmic-bypass-address-proof/evidence/RESULT.json"
    d=json.loads(p.read_text())
    require(d["status"]=="PASS_ORIGINAL_ARM64_PMIC_THREE_BYPASS_ADDRESS_RANGE_AUDIT",
            "previous checkpoint identity drift")
    require(d["static_address_proof"]["generic_wrapper_entry_rva"]=="0x32b70" and
            d["static_address_proof"]["generic_wrapper_actual_data_callback_table_rva"]=="0x3a510",
            "prior generic callback pointer drift")
    return sha256(p.read_bytes()).hexdigest()

def main():
    summary=verify(original())
    p={
        "experiment":"E004ha",
        "status":"PASS_ORIGINAL_OEM_GENERIC_WRITE_CALLBACK_AND_TWO_DESCRIPTOR_PRODUCERS_OFFLINE",
        "date":"2026-09-20",
        "baseline_commit":"5309ea3098881a1e7c7f168298d6385bf9627421",
        "original_oem_pmic_sha256":OEM_SHA,
        "prior_e004gz_result_sha256":prior_check(),
        "static_callback_proof":summary,
        "generic_write_callback_runtime_entry_hit_observed":False,
        "actual_register_timer_write_or_0x93_writer_identified":False,
        "physical_pulse_or_autonomous_cutoff_proven":False,
        "new_windows_kd_camera_or_pmic_device_activity":False,
        "native_linux_ir_enabled":False,
        "golden_modified":False,
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_static.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(p,indent=2)+"\n")
    print("E004HA_ORIGINAL_CALLBACK_POINTER_AND_TWO_DESCRIPTOR_PRODUCERS=PASS")
    print("E004HA_WRITER_RVA=0x32b70 EXPORTED_TABLE=0x3a4f8/0x3a508")
    print("E004HA_RUNTIME_CALL_AND_FIRST_TIMER_WRITER=UNKNOWN GOLDEN=UNCHANGED NATIVE_IR=OFF")

if __name__=="__main__":main()
