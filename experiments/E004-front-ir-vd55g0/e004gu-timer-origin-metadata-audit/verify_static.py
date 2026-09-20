#!/usr/bin/env python3
"""E004gu: original OEM PMIC timer provenance, CFG/unwind false-xref audit.

Read-only archive disassembly and metadata processing. Neither absence of
literal addresses nor lack of observed runtime hits proves no prior timer
programming, nor proves firmware reset defaults or hardware pulse behavior.
"""
from pathlib import Path
from hashlib import sha256
import json
import struct
import pefile
import capstone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCH=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
NAME="qcpmic8380.sys"
PE_HASHES={
    "qcpmic8380.sys":"756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e",
    "qcpmicapps8380.sys":"8418c2739e6d969a0c791d937a09f583eeeacd70e866126d9362b2f56d13cca7",
    "qcpmicglink8380.sys":"00a73e2b050d2299a33ee6823756dc94ce2a5f9e70948fc563a05938803cae2b",
    "qccamflash8380.sys":"6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b",
}
BASE=0x140000000
TIMER_BYTES=struct.pack("<4I",0xee3e,0xee3f,0xee40,0xee41)
PRIOR={
    "E004gt":("e004gt-windows-oem-timer-callers",
              "e7c7301f8b9ad39990815fbfc3a93854b971df252eb81e2b5528b20a04286e92"),
    "E004gs":("e004gs-windows-passive-timer-boot-trace",
              "49e9fb7d88c09bb5b98d21d6b6e2efe3923118647846a6353fe251ebad5f6b86"),
    "E004gb":("e004gb-windows-flash-enable-explicit-kd-predicate",
              "1e3858e30aa085d3c75b1681a2ff7e7d25f1711fb34b90e3e5474b9e30e0e783"),
    "E004fx":("e004fx-passive-golden-timer-read",
              "b2cbfeb4705937cca69609672fd1c4143135c82ee2aff8bcf82e33206daa093e"),
}

def require(ok,why):
    if not ok:raise AssertionError("E004GU_FAIL_CLOSED "+why)

def section(pe,rva):
    matches=[x.Name.rstrip(b"\0").decode() for x in pe.sections if x.contains_rva(rva)]
    require(len(matches)==1,"ambiguous PE section at "+hex(rva))
    return matches[0]

def audit_pmic_image(raw):
    require(sha256(raw).hexdigest()==PE_HASHES[NAME],"original PMIC PE SHA drift")
    pe=pefile.PE(data=raw)
    require(pe.OPTIONAL_HEADER.ImageBase==BASE and pe.FILE_HEADER.Machine==0xaa64,
            "not the original OEM Windows ARM64 image")
    require(pe.get_data(0x36d48,16)==TIMER_BYTES and
            section(pe,0x36d48)==".rdata","four-address timer table changed")
    require(raw.count(TIMER_BYTES)==1 and raw.find(TIMER_BYTES)==0x35948,
            "unique four-channel timer table file position changed")
    for offset,rva in ((0x39498,0x26d50),(0x394a0,0x26f30)):
        require(section(pe,offset)==".data" and
                struct.unpack("<Q",pe.get_data(offset,8))[0]==BASE+rva,
                "actual in-memory 64-bit runtime PMIC callback table changed")
    load=pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct
    require(load.GuardCFFunctionTable-BASE==0x36218 and
            load.GuardCFFunctionCount==438,
            "Windows PE CFG metadata table changed")
    for offset,rva in ((0x364c4,0x26d50),(0x364c8,0x26f30)):
        require(section(pe,offset)==".rdata" and
                0x36218 <= offset < 0x36218+load.GuardCFFunctionCount*4 and
                struct.unpack("<I",pe.get_data(offset,4))[0]==rva,
                "RVA-only Guard CF allowed-target metadata changed")
    for offset,rva in ((0x3faa0,0x26d50),(0x3faa8,0x26f30)):
        require(section(pe,offset)==".pdata" and
                struct.unpack("<I",pe.get_data(offset,4))[0]==rva,
                "PE xdata/unwind metadata changed")
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    def ins(rva):
        instructions=list(cs.disasm(pe.get_data(rva,4),BASE+rva))
        require(len(instructions)==1,"invalid original ARM64 instruction "+hex(rva))
        return instructions[0].mnemonic,instructions[0].op_str
    for rva,op,fragment in (
        (0x26e2c,"ldr","w2, [x26, x21, lsl #2]"),
        (0x26e60,"ldr","w2, [x26, x8, lsl #2]"),
        (0x27008,"adrp","0x140036000"),
        (0x2700c,"add","#0xd48"),
        (0x27010,"ldr","w2, [x8, w20, sxtw #2]"),
        (0x26e40,"bl","#0x140023968"),
        (0x27020,"bl","#0x140023968"),
    ):
        mnemonic,args=ins(rva)
        require(mnemonic==op and fragment in args,
                "original PMIC timer table read/masked-request path changed "+hex(rva))
    return {
        "pmic_timer_register_table_rva":"0x36d48",
        "pmic_timer_registers":["0xee3e","0xee3f","0xee40","0xee41"],
        "recognized_code_refs_to_timer_table":["0x26e2c","0x26e60","0x27010"],
        "actual_indirect_runtime_timer_callbacks":{
            "slot5_four_channel":"0x39498 -> 0x26d50",
            "slot6_single_channel":"0x394a0 -> 0x26f30",
        },
        "guardcf_allowed_target_table":{
            "rva":"0x36218","entries":438,
            "four_timer_entry":"0x364c4","single_timer_entry":"0x364c8",
            "runtime_callback_table":False,
        },
        "pdata_unwind_function_start_metadata":{
            "four_timer":"0x3faa0","single_timer":"0x3faa8",
            "runtime_callback_table":False,
        },
        "true_additional_timer_callback_dispatchers_from_cfg_pdata":False,
    }

def audit_archive(files):
    require(len(files)==102,"original DriverStore SYS inventory count changed")
    require(len(set(f.name for f in files))==101,
            "original driver name distribution changed")
    found=[]
    for file in files:
        raw=file.read_bytes()
        off=raw.find(TIMER_BYTES)
        if off>=0:
            require(raw.count(TIMER_BYTES)==1,
                    "additional four-register timer sequence occurrences")
            found.append((file.name,off))
    require(found==[(NAME,0x35948)],
            "four-register literal table found outside original PMIC driver")
    return len(files)

def audit_literal_sites(files):
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    cs.skipdata=True
    sites={}
    for name in PE_HASHES:
        items=[f for f in files if f.name==name]
        require(len(items)==1,"original named PE not unique "+name)
        raw=items[0].read_bytes()
        require(sha256(raw).hexdigest()==PE_HASHES[name],
                "original named PE hash drift "+name)
        pe=pefile.PE(data=raw)
        found=[]
        for section_obj in pe.sections:
            if not section_obj.Characteristics & 0x20000000:
                continue
            for i in cs.disasm(section_obj.get_data(),
                               pe.OPTIONAL_HEADER.ImageBase+section_obj.VirtualAddress):
                if (i.mnemonic in ("mov","movz","movk") and
                    i.op_str.rsplit(",",1)[-1].strip().lower()=="#0x93"):
                    found.append(hex(i.address-BASE))
        sites[name]=found
    require(sites["qcpmic8380.sys"]==[] and
            sites["qcpmicapps8380.sys"]==[] and
            sites["qccamflash8380.sys"]==[] and
            sites["qcpmicglink8380.sys"]==["0xc740"],
            "immediate-literal scan drift (not a whole-program data-flow proof)")
    return sites

def audit_prior():
    result={}
    for key,(folder,pinned) in PRIOR.items():
        path=ROOT/"experiments/E004-front-ir-vd55g0"/folder/"evidence/RESULT.json"
        require(sha256(path.read_bytes()).hexdigest()==pinned,
                key+" consumed original evidence drift")
        result[key]=json.loads(path.read_text())
    require(result["E004gt"]["kd_callback_hits_during_bounded_oem_session"]==
            {"pmic_four_timer":0,"pmic_single_timer":0,
             "flash_timer_wrapper":0,"flash_config":0} and
            result["E004gt"]["preboot_or_early_init_timer_programming_excluded"] is False,
            "normal preview does not exclude early init")
    require(result["E004gs"]["passive_idle_timer_breakpoint_hits"]==
            {"timer4":0,"timer1":0,"flash_timer_helper":0} and
            result["E004gs"]["first_windows_boot_init_timer_requests_excluded"] is False,
            "passive boot observation scope drift")
    require(result["E004gb"]["identity_consumed"] is True and
            result["E004gb"]["timer_register_access_observed_in_selected_helper"] is False,
            "original bounded Windows PMIC helper observation drift")
    require(result["E004fx"]["read_once_identity_consumed"] is True and
            set(result["E004fx"]["idle_timer_register_bytes"].values())=={"93"},
            "original consumed idle PMIC timer byte changed")
    return True

def main():
    files=sorted(ARCH.glob("*/*.sys"))
    count=audit_archive(files)
    image=next(f.read_bytes() for f in files if f.name==NAME)
    pmic=audit_pmic_image(image)
    literal_sites=audit_literal_sites(files)
    audit_prior()
    result={
        "experiment":"E004gu",
        "status":"PASS_ORIGINAL_OEM_PMIC_TIMER_TABLE_AND_METADATA_PROVENANCE_OFFLINE",
        "date":"2026-09-20",
        "baseline_commit":"e7954fd6b997036c821ca13452497446496764bc",
        "archived_windows_sys_files_scanned":count,
        "four_register_literal_sequence_unique_to_qcpmic8380":True,
        "original_pmic_sha256":PE_HASHES[NAME],
        "pinned_binary_sha256":PE_HASHES,
        "pmic_function_and_metadata_classification":pmic,
        "executable_immediate_0x93_sites":literal_sites,
        "no_literal_0x93_in_three_named_executable_drivers_proves_no_timer_writer":False,
        "four_register_literal_absence_in_other_sys_excludes_computed_or_indirect_writers":False,
        "alternative_windows_oem_early_init_or_uefi_firmware_timer_source_identified":False,
        "windows_preexisting_0x93_is_true_pmic_reset_default_proven":False,
        "normal_oem_preview_postboot_timer_entry_calls_observed":False,
        "golden_idle_0x93_physically_enforces_200ms":False,
        "new_windows_kd_camera_pmic_or_emitter_activity":False,
        "linux_native_ir_emitter_authorized":False,
        "golden_modified":False,
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_static.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004GU_ORIGINAL_DRIVER_SYS_102_SCAN=PASS TIMER_TABLE_UNIQUE_TO_QCPMIC")
    print("E004GU_TRUE_INDIRECT_TIMER_TABLE=0x39498/0x394a0 GUARD_CF_AND_PDATA=METADATA_ONLY")
    print("E004GU_ORIGINAL_PMIC_TIMER_DATA_REFS=2_CALLBACKS TRUE_EARLY_TIMER_INIT_SOURCE=UNKNOWN")
    print("NATIVE_IR_EMITTER=OFF PHYSICAL_TIMER_CUTOFF=UNPROVEN GOLDEN=UNCHANGED")
if __name__=="__main__":main()
