#!/usr/bin/env python3
"""E004hk: original OEM PMIC -> SPMI interface and raw-write selector audit.

Pinned ORIGINAL Windows OEM qcpmic8380.sys/qcspmi8380.sys ARM64 image bytes.
No Windows/KD/PMIC/LED actions, no purported proof of a live SPMI transaction,
first write of timer 0x93, independent optical/electrical cutoff, or firmware
absence. Do not arm a live bus observer based on static address alone.
"""
from pathlib import Path
from hashlib import sha256
import json
import struct
import uuid
import capstone
import pefile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCH=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
BASE=0x140000000
HASHES={
    "qcpmic8380":"756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e",
    "qcspmi8380":"b6a5868ec2450e713b9a5ada7b4e1a4a77c77427fedf0806fe3eb6541099523c",
}
GUID="72c96e71-eb2d-48e3-99ac-9894a59f9c4c"
CALL_SITES=[0x23a04,0x2fc54,0x303b4,0x32c2c]

def need(ok,why):
    if not ok:raise AssertionError("E004HK_FAIL_CLOSED "+why)

def original(name):
    matches=list(ARCH.glob(name+".inf_*/"+name+".sys"))
    need(len(matches)==1,"ambiguous original OEM image "+name)
    raw=matches[0].read_bytes()
    need(sha256(raw).hexdigest()==HASHES[name],
         "original Windows ARM64 PE bytes changed "+name)
    pe=pefile.PE(data=raw)
    need(pe.FILE_HEADER.Machine==0xaa64 and
         pe.OPTIONAL_HEADER.ImageBase==BASE,"wrong original Windows ARM64 image")
    return pe

def ins(pe,rva):
    c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    items=list(c.disasm(pe.get_data(rva,4),BASE+rva))
    need(len(items)==1 and items[0].address==BASE+rva,
         "original instruction absent "+hex(rva))
    return items[0].mnemonic,items[0].op_str

def expect(pe,rva,mn,operands):
    need(ins(pe,rva)==(mn,operands),
         "original ARM64 interface/transport instruction changed "+hex(rva))

def direct_bl(pe,rva):
    c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    c.skipdata=True
    sites=[]
    for sec in pe.sections:
        if not sec.Characteristics&0x20000000:continue
        for i in c.disasm(sec.get_data(),BASE+sec.VirtualAddress):
            if (i.mnemonic=="bl" and i.op_str.startswith("#") and
                int(i.op_str[1:],16)==BASE+rva):
                sites.append(i.address-BASE)
    return sorted(sites)

def model_selector(bus,sid,address,count):
    """Original +0x23ed8/+0x23edc selector for already normalized bus/SID.

    A fake caller may pass wider register IDs; this fixture narrows the
    modeled inputs to the 16-bit PMIC address domain and 1..256 byte count.
    0xee3e..0xee41 is not necessarily in the same physical SID as Linux.
    """
    need(all(type(v) is int for v in (bus,sid,address,count)) and
         0<=bus<=1 and 0<=sid<=13 and 0<=address<=0xffff and
         1<=count<=256,"invalid normalized synthetic SPMI selector inputs")
    return (address | ((sid | (bus<<4))<<16))

def audit(pmic,spmi):
    guid=uuid.UUID(GUID).bytes_le
    need(pmic.get_data(0x37058,16)==guid and
         spmi.get_data(0xa1d8,16)==guid,
         "original PMIC/SPMI interface GUID bytes differ")
    # On PMIC initialization, original WDF indirect call uses this GUID
    # at x2 and provides output structure +0x3d010 via x3, size 0x70.
    # WDF indirect function-index +0x588 is NOT a raw register writer.
    for rva,mn,args in (
        (0x3938,"adrp","x8, #0x14003d000"),
        (0x393c,"add","x3, x8, #0x10"),
        (0x3944,"adrp","x8, #0x140037000"),
        (0x3948,"add","x2, x8, #0x58"),
        (0x3954,"mov","w5, #1"),
        (0x3958,"ldr","x8, [x9, #0x588]"),
        (0x395c,"mov","w4, #0x70"),
        (0x3964,"mov","x15, x8"),
        (0x3974,"blr","x15"),
    ):
        expect(pmic,rva,mn,args)
    # qcspmi8380 constructs an interface descriptor containing the
    # exact same GUID and passes it to its OWN indirect WDF +0x720 slot.
    # These static calls strongly show a compatible interface handshake,
    # not that Windows successfully bound it during this new offline audit.
    for rva,mn,args in (
        (0x3ef8,"adrp","x8, #0x14000a000"),
        (0x3efc,"add","x8, x8, #0x1d8"),
        (0x3f04,"ldr","x1, [sp]"),
        (0x3f0c,"add","x2, sp, #0x70"),
        (0x3f10,"stp","x9, x8, [sp, #0x78]"),
        (0x3f20,"ldr","x8, [x22, #0x338]"),
        (0x3f24,"ldr","x8, [x8, #0x720]"),
        (0x3f28,"mov","x15, x8"),
        (0x3f38,"blr","x15"),
    ):
        expect(spmi,rva,mn,args)
    # PMIC RAW write accepts (bus, sid, u16-ish register, src, len):
    # normalized 16-bit address OR (SID | bus<<4)<<16. Then it loads
    # the output-interface handle and vtable +0x30 callback and calls it.
    for rva,mn,args in (
        (0x23de8,"mov","w22, w0"),
        (0x23dec,"mov","w20, w1"),
        (0x23df0,"mov","w27, w2"),
        (0x23df4,"mov","x26, x3"),
        (0x23df8,"mov","w24, w4"),
        (0x23ec0,"adrp","x8, #0x14003d000"),
        (0x23ec4,"add","x25, x8, #0x10"),
        (0x23ec8,"ldr","x8, [x25, #0x20]"),
        (0x23ed0,"ldr","x8, [x25, #0x30]"),
        (0x23ed8,"orr","w8, w20, w22, lsl #4"),
        (0x23edc,"orr","w2, w27, w8, lsl #16"),
        (0x23ee0,"str","w2, [sp, #0x10]"),
        (0x23f14,"ldr","w2, [sp, #0x10]"),
        (0x23f18,"mov","w4, w24"),
        (0x23f1c,"ldr","x0, [x25, #0x20]"),
        (0x23f20,"mov","x3, x26"),
        (0x23f24,"ldr","x8, [x25, #0x30]"),
        (0x23f28,"mov","w1, #0"),
        (0x23f2c,"mov","x15, x8"),
        (0x23f3c,"blr","x15"),
    ):
        expect(pmic,rva,mn,args)
    need(direct_bl(pmic,0x23dc8)==CALL_SITES,
         "original four direct PMIC raw-write callers changed")
    need(direct_bl(pmic,0x32b70)==[],
         "original indirectly published PMIC generic writer gained direct caller")
    expected={0xee3e:0x0001ee3e,0xee3f:0x0001ee3f,
              0xee40:0x0001ee40,0xee41:0x0001ee41}
    need({address:model_selector(0,1,address,1) for address in expected}==expected,
         "synthetic normalized bus0 SID1 timer selectors changed")
    need(model_selector(1,1,0xee3e,1)==0x0011ee3e and
         model_selector(0,2,0xee3e,1)==0x0002ee3e,
         "SID/bus selector bit ownership changed")
    return {
        "common_original_interface_guid":GUID,
        "pmic_interface_guid_rva":"0x37058",
        "spmi_interface_guid_rva":"0xa1d8",
        "pmic_interface_query_call_rva":"0x3974",
        "spmi_interface_descriptor_publish_call_rva":"0x3f38",
        "pmic_interface_output_structure_rva":"0x3d010",
        "pmic_interface_output_structure_size_bytes":0x70,
        "raw_write_entry_rva":"0x23dc8",
        "raw_write_direct_callsite_rvas":[hex(x) for x in CALL_SITES],
        "raw_write_data_callback_handle_global_rva":"0x3d030",
        "raw_write_data_callback_ptr_global_rva":"0x3d040",
        "raw_write_selector_pack_rvas":["0x23ed8","0x23edc"],
        "raw_write_dispatch_indirect_call_rva":"0x23f3c",
        "sample_only_normalized_bus0_sid1_timer_selectors":
            {hex(address):hex(value) for address,value in expected.items()},
        "bus_sid_actual_live_values_for_flash_timer_in_this_stage":None,
        "spmi_provider_interface_bound_at_runtime_in_this_stage":False,
        "lower_indirect_function_is_specific_original_spmi_method_verified":False,
        "original_timer_0x93_first_writer_identified":False,
        "independent_physical_pulse_or_fault_off_verified":False,
    }

def prior():
    gy=ROOT/"experiments/E004-front-ir-vd55g0/e004gy-early-raw-pmic-write-hardware-kd/evidence/RESULT.json"
    ha=ROOT/"experiments/E004-front-ir-vd55g0/e004ha-generic-pmic-callback-registration/evidence/RESULT.json"
    a=json.loads(gy.read_text());b=json.loads(ha.read_text())
    need(a["raw_write_entry_spans_overlapping_ee3e_to_ee41"]==0 and
         b["generic_write_callback_runtime_entry_hit_observed"] is False,
         "original consumed PMIC KD/generic callback scope drift")
    return {"e004gy_original_kd_result_sha256":sha256(gy.read_bytes()).hexdigest(),
            "e004ha_original_generic_callback_result_sha256":sha256(ha.read_bytes()).hexdigest()}

def main():
    result={
        "experiment":"E004hk",
        "status":"PASS_ORIGINAL_OEM_PMIC_SPMI_SHARED_GUID_RAW_WRITE_SELECTOR_AND_INDIRECT_TRANSPORT_OFFLINE",
        "date":"2026-09-20",
        "baseline_commit":"cb1699bb28c59bbce1f86570eb95961b11b8c1ca",
        "original_windows_driver_sha256":HASHES,
        "prior_consumed_original_trace_result_sha256":prior(),
        "original_pmic_spmi_interface_and_selector":audit(original("qcpmic8380"),original("qcspmi8380")),
        "new_windows_kd_camera_pmic_spmi_led_or_login_activity":False,
        "native_ir_emitter_authorized":False,
        "golden_modified":False,
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_bus.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004HK_ORIGINAL_PMIC_TO_SPMI_INTERFACE_GUID_AND_PACKED_INDIRECT_BUS_WRITER=PASS")
    print("E004HK_TRUE_LIVE_SID_ORIGINAL_0X93_FIRST_WRITER=UNKNOWN GOLDEN=UNCHANGED NATIVE_IR=OFF")
if __name__=="__main__":main()
