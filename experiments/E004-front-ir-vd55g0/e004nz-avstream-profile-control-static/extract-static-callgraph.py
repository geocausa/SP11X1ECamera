#!/usr/bin/env python3
"""E004nz read-only OEM SP11 AVStream orchestration graph (safe scalar only).

Input: SHA-pinned original Windows ARM64 camera AVStream binary and UTF-16 INF
on the SAME SP11. Output: small JSON of source-verified PE-relative RVAs,
selector values, component roles and strict unknowns. No driver bytes,
literal diagnostic text, Windows DMA addresses, optical data or KD creds.
"""
import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/"
          "surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342")
DRIVER=BASE/"surfacecamavs8380.sys"
INF=BASE/"surfacecamavs8380.inf"
DRIVER_SHA="b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed"
IMAGE_BASE=0x140000000

# name: exact original same-SP11 diagnostic substring, PE RVA and unique
# ADRP/ADD source reference RVAs. Prefixes only are held in the extractor;
# neither original diagnostics nor OEM code/binary are exported into result.
STRINGS={
 "engine_initialize":(b"CCameraEngine::OnInitialize(SensorID",0x2b190,0x1edc0,0x1edc4),
 "engine_start":(b" CCameraEngine::OnStart",0x2b290,0x1efe8,0x1efec),
 "engine_start_ack":(b"CCameraEngine:: Ack received for OnStart",0x2b2a8,0x1f09c,0x1f0a0),
 "engine_stop":(b" CCameraEngine::OnStop",0x2b348,0x1f148,0x1f14c),
 "engine_stop_isp_error":(b" CCameraEngine::OnStop - Stop IFE Failed",0x2b360,0x1f18c,0x1f190),
 "engine_stop_sensor_error":(b" CCameraEngine::OnStop - Stop Sensor Failed",0x2b3d0,0x1f228,0x1f22c),
 "configuration_from_user_mode":(b"{CCaptureFilter::SetDeviceConfiguration} Sensor Delay Info received from UMD",0x25a10,0x6914,0x691c),
 "profile_configuration_packet":(b"{CCaptureFilter::SetDeviceConfiguration}  profile id and processing type and config packet",0x25c10,0x6c2c,0x6c30),
 "profile_per_request_packet":(b"{CCaptureFilter::SendPacketInternal}  profile id and processing type and sending packet",0x27368,0xa0f4,0xa0f8),
 "create_topology":(b"{CCaptureFilter::CreateTopology} CCaptureFilter::CreateTopology: Camera core OnConfig() failed",0x9c400,0x7e3b0,0x7e3b4),
 "topology_activate_vcm":(b"{CCaptureFilter::CreateTopology} ActivateVcm",0x9c370,0x7e22c,0x7e230),
 "isp_worker_registration":(b"{CCaptureFilter::RegisterISPDataPathNotifierHandle} CCaptureFilter::AcquireFilterResources: StartIspWorkerThread",0x9cbf8,0x7ff60,0x7ff64),
 "single_filter_exclusivity":(b"{CCaptureFilter::AcquireFilterResources} Active filter already assigned",0x9cd18,0x7fc78,0x7fc7c),
 "filter_initialized":(b"{CCaptureFilter::AcquireFilterResources} CCaptureFilter::AcquireFilterResources: capture filter state changed",0x9ce00,0x7ff84,0x7ff88),
 "pin_state_transition":(b"{CPin::SetState} ENTERING",0xa2858,0x8bbcc,0x8bbd0),
 "privacy_shutter":(b"{CPin::SetState} Unable to send privacy shutter event",0xa2980,0x8be40,0x8be44),
 "still_photo_control":(b"{CCaptureFilter::SetExtendedPhotoMode} PhotoMode",0x9edb0,0x834cc,0x834d0),
 "isp_event_worker_callback":(b"{CDispatchHandler::OnIspNotification} Received RDI buffer",0x28110,0x17568,0x1756c),
 "preview_profile_handler":(b"{CCaptureFilter::ConfigurePreviewStreamInRun} Invalid use case",0x9c500,0x7ebbc,0x7ebc0),
 "still_profile_handler":(b"{CCaptureFilter::ConfigureStillStreamInRun} Invalid use case",0x9c828,0x7f030,0x7f034),
 "video_profile_handler":(b"{CCaptureFilter::ConfigureVideoStreamInRun} Invalid use case",0x9c8f8,0x7fa28,0x7fa2c),
 "stats_pin_factory":(b"{CCaptureFilter::CreateStatsPinFactory} KsFilterCreatePinFactory() failed",0x9e478,0x824f4,0x824f8),
 "pdaf_config_override":(b"{CCaptureFilter::CheckDisablePDAFRegistry} [CheckDisablePDAFRegistry] overwrite",0x9f600,0x846e8,0x846ec),
}
# Immediate value and a separate, shared indirect callback dispatch:
# DO NOT relabel these numeric selectors as stable IOCTL or sensor commands.
SELECTORS={
 "engine_start":((0x1f01c,0x804,0x1f020),
                 (0x1f058,0x804,0x1f05c),
                 (0x1f08c,0x005,0x1f090),
                 (0x1f0e8,0x017,0x1f0f0)),
 "engine_stop":((0x1f17c,0x805,0x1f180),
                (0x1f1e0,0x809,0x1f1e4),
                (0x1f218,0x805,0x1f21c),
                (0x1f278,0x018,0x1f280)),
}

def must(t,message):
    if not t:raise AssertionError("E004NZ_FAIL_CLOSED "+message)

def secs(data):
    pe=struct.unpack_from("<I",data,0x3c)[0]
    must(data[pe:pe+4]==b"PE\0\0","missing PE")
    must(struct.unpack_from("<H",data,pe+4)[0]==0xaa64,"not ARM64 PE")
    n=struct.unpack_from("<H",data,pe+6)[0]
    sh=pe+24+struct.unpack_from("<H",data,pe+20)[0]
    out=[]
    for i in range(n):
        s=sh+40*i
        size,rva,raw_size,raw=struct.unpack_from("<IIII",data,s+8)
        out.append((rva,raw_size,raw))
    return out

def to_rva(sections,off):
    for va,size,raw in sections:
        if raw<=off<raw+size:return va+off-raw
    raise AssertionError("OEM diagnostic not mapped in PE section")

def disassemble():
    s=subprocess.check_output(["llvm-objdump","-d",str(DRIVER)],text=True)
    pat=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    return {int(m.group(1),16)-IMAGE_BASE:
            (m.group(2),m.group(3).split("//",1)[0].strip())
            for m in pat.finditer(s)}

def at(asm,rva,mn,ops):
    must(asm.get(rva)==(mn,ops),
         f"instruction RVA 0x{rva:x}: {asm.get(rva)} != {mn} {ops}")

def inf_check():
    x=INF.read_text(encoding="utf-16")
    active="\n".join(row.split(";",1)[0] for row in x.splitlines())
    must("AddService=QCCamAvs" in active,"no AVStream registered driver")
    must("surfacecamavs8380.sys" in active,"no AVStream service image")
    must("QcDeviceMFT8380.dll" in active,"OEM MFT registration absent")
    for desc in ("BackSensor.FriendlyName","FrontSensor.FriendlyName",
                 "AuxSensor.FriendlyName","PINNAME_VIDEO_PREVIEW",
                 "PINNAME_IMAGE","PINNAME_VIDEO_CAPTURE",
                 "BackSensor.RefGuid","FrontSensor.RefGuid","AuxSensor.RefGuid"):
        must(desc in active,"missing sensor/pin declaration "+desc)
    # INF has explanatory commented examples for profile registry assignments.
    # They must not be counted as active profile selection evidence.
    live=[row.strip() for row in x.splitlines()
          if row.strip() and not row.lstrip().startswith(";")
          and ("HKR" in row.upper() or "HKLM" in row.upper())
          and "OEMCameraProfiles" in row]
    must(len(live)==0,"unexpected active OEMCameraProfiles INF registry lines")
    return {"AVStream_kernel_service_registered":True,
            "three_sensor_identities":True,
            "preview_still_video_pin_names":True,
            "DeviceMFT_DLL_registered_not_session_observed":True,
            "camera_profile_registry_assignment_in_this_INF":False}

def build():
    driver=DRIVER.read_bytes()
    must(len(driver)==547192 and hashlib.sha256(driver).hexdigest()==DRIVER_SHA,
         "exact same-SP11 private OEM AVStream driver identity")
    sections=secs(driver)
    asm=disassemble()
    evidence={}
    for name,(prefix,expect_rva,adrp,add) in STRINGS.items():
        off=driver.find(prefix)
        must(off>=0,"OEM diagnostic missing "+name)
        must(to_rva(sections,off)==expect_rva,"diagnostic PE RVA changed "+name)
        prefixva=IMAGE_BASE+expect_rva
        page=prefixva&~0xfff
        adr=asm.get(adrp)
        must(adr is not None and adr[0]=="adrp" and f"0x{page:x}" in adr[1],
             "ADR page reference changed "+name)
        m=re.match(r"(x\d+),\s*0x[0-9a-f]+",adr[1])
        must(m is not None,"ADR register parse "+name)
        reg=m.group(1)
        addrow=asm.get(add)
        must(addrow is not None and addrow[0]=="add" and
             re.fullmatch(r"x\d+,\s*"+reg+r",\s*#0x%x"%(prefixva-page),addrow[1]) is not None,
             "diagnostic ADD operand changed "+name)
        must(0<add-adrp<=12 and add % 4==0,"split ADRP/ADD changed "+name)
        evidence[name]={"OEM_diagnostic_RVA":f"0x{expect_rva:x}",
                        "PE_ADRP_RVA":f"0x{adrp:x}",
                        "PE_ADD_RVA":f"0x{add:x}"}
    selectors={}
    for phase,sequence in SELECTORS.items():
        steps=[]
        for mov,val,bl in sequence:
            at(asm,mov,"mov",f"w1, #0x{val:x}" if val>9 else f"w1, #0x{val:x}")
            at(asm,bl,"bl",f"0x{IMAGE_BASE+0x20da8:x} <.text+0x1fda8>")
            steps.append({"selector":f"0x{val:x}",
                          "selector_instruction_RVA":f"0x{mov:x}",
                          "shared_dispatch_call_RVA":f"0x{bl:x}"})
        selectors[phase]=steps
    # Call helper 0x20da8 checks its target object then branches into a
    # callback at x15. Numeric selector meaning is NOT established by this.
    at(asm,0x20de0,"ldr","x8, [x0]")
    at(asm,0x20df4,"blr","x15")
    at(asm,0x20e1c,"ldr","x1, [x9, #0x38]")
    at(asm,0x20e30,"blr","x15")
    # Check only presence of KS/NT imports: an import is not proof any given
    # device-control is routed to one specific backend driver.
    imports=subprocess.check_output(["llvm-readobj","--coff-imports",str(DRIVER)],text=True)
    for name in ("KsInitializeDriver","KsCreateFilterFactory",
                 "KsFilterCreatePinFactory","KsPinAttemptProcessing",
                 "IoBuildDeviceIoControlRequest","IofCallDriver"):
        must(f"Symbol: {name} (" in imports,"OEM AVStream imported interface changed "+name)
    return {
      "schema":"sp11-e004nz-same-machine-Windows-AVStream-static-control-slice-v1",
      "experiment":"E004nz",
      "parent_git_revision":"bf70ebaa7f01a509b511cd3869e5ea08eb9a7352",
      "OEM_private_same_SP11_AVStream_driver_sha256":DRIVER_SHA,
      "OEM_AVStream_driver_bytes":len(driver),
      "OEM_AVStream_ARM64_instructions_source_checked":len(evidence)*2+len(SELECTORS["engine_start"])*2+len(SELECTORS["engine_stop"])*2+4,
      "INF":inf_check(),
      "diagnostic_call_sites":evidence,
      "camera_engine_shared_indirect_dispatch_RVA":"0x20da8",
      "camera_engine_on_start_source_function_RVA":"0x1efd0",
      "camera_engine_on_stop_source_function_RVA":"0x1f130",
      "camera_engine_start_stop_numeric_selectors_UNDECODED":selectors,
      "configuration_receives_user_mode_sensor_timing_scalar":True,
      "profile_and_processing_type_are_present_in_configuration_and_per_request_packet_paths":True,
      "distinct_preview_still_video_and_stats_pin_logic_present":True,
      "isp_notification_worker_and_request_identity_path_statically_present":True,
      "actual_Windows_camera_session_selected_profile_identified":False,
      "registered_OEM_DeviceMFT_actually_loaded_in_recording_proven":False,
      "numeric_dispatch_selectors_mapped_to_specific_sensor_or_ISP_commands":False,
      "live_rear_BF_event_0x0f_observed":False,
      "Linux_rear_native_4k_ISP_optical_frame_proven":False,
      "no_Windows_binary_UMD_payload_or_optical_bytes_exported":True,
      "hardware_camera_or_Golden_changed":False,
    }

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--write-new",action="store_true",
                     help="create a new scalar result once; never overwrite")
    options=cli.parse_args()
    out=build()
    p=HERE/"RESULT.json"
    if options.write_new:
        must(not p.exists(),"scalar evidence already exists")
        p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    else:
        must(p.exists() and json.loads(p.read_text())==out,
             "saved scalar evidence differs from same-SP11 OEM static re-extraction")
    print("PASS_E004NZ_OEM_AVSTREAM_PIN_PROFILE_CONFIG_START_STOP_"
          "INDIRECT_DISPATCH_USERMODE_TIMING_ISR_STATIC_SOURCE_"
          f"{out['OEM_AVStream_ARM64_instructions_source_checked']}_INSTRUCTION_ANCHORS_"
          "MFT_RUNTIME_UNKNOWN_NATIVE_GOLDEN_UNTOUCHED")
