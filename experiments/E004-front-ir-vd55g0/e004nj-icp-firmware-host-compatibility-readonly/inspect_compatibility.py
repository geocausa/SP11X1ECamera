#!/usr/bin/env python3
"""Only parse installed ELF metadata and SOURCE of the running host.

No device open, I/O beyond metadata/header reads from read-only
Windows volume, no firmware upload, boot, modules or optical data.
The results are format/host-driver compatibility, not execution.
"""
from __future__ import annotations
import argparse
import json
import re
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
KERNEL=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src")
NAMES=("CAMERA_ICP.mbn","CAMERA_ICP_AAAAAA.elf")
ELF_MACHINES={94:"XTENSA",164:"HEXAGON",183:"AARCH64"}

def read_elf_metadata(p:Path)->dict:
    if not p.is_file() or p.is_symlink():
        raise ValueError("NOT_EXISTING_REGULAR_FIRMWARE")
    if p.stat().st_size<52:
        raise ValueError("TRUNCATED_ELF")
    with p.open("rb") as f: head=f.read(52)
    if head[:4]!=b"\x7fELF" or head[4]!=1 or head[5]!=1:
        raise ValueError("EXPECTED_ELF32_LITTLE_ENDIAN")
    machine=struct.unpack_from("<H",head,18)[0]
    if machine not in ELF_MACHINES:
        raise ValueError("UNRECOGNIZED_ELF_MACHINE_STOP_BEFORE_COMPATIBILITY_INFERENCE")
    phnum=struct.unpack_from("<H",head,44)[0]
    phoff=struct.unpack_from("<I",head,28)[0]
    if phnum<1 or phnum>2048 or phoff>p.stat().st_size:
        raise ValueError("INVALID_ELF_PROGRAM_HEADERS")
    return {"format":"ELF32 little-endian",
        "cpu_architecture":ELF_MACHINES[machine],
        "byte_count":p.stat().st_size,
        "program_header_count":phnum,
        "has_section_header":struct.unpack_from("<I",head,32)[0]!=0}

def firmware_packages(root:Path)->dict:
    driverstore=root/"Windows/System32/DriverStore/FileRepository"
    if not driverstore.is_dir():
        raise ValueError("MISSING_WINDOWS_DRIVERSTORE")
    packages=[p for p in driverstore.glob("qccamisp8380.inf_*") if p.is_dir()]
    if len(packages)!=1 or not packages[0].is_dir():
        raise ValueError("AMBIGUOUS_WINDOWS_ISP_PACKAGE")
    return {name:read_elf_metadata(packages[0]/name) for name in NAMES}

def remoteprocs(base:Path=Path("/sys/class/remoteproc"))->list[dict]:
    out=[]
    if not base.exists():return out
    for p in sorted(base.glob("remoteproc*")):
        if not p.is_dir():continue  # sysfs class entries are symlinks to real kernel devices
        out.append({"identity":p.name,
            "name":(p/"name").read_text().strip().lower(),
            "state":(p/"state").read_text().strip(),
            "firmware_basename":Path((p/"firmware").read_text().strip()).name})
    return out

def linux_camss_loader_boundary(k:Path=KERNEL)->dict:
    c=k/"drivers/media/platform/qcom/camss"
    if not c.is_dir():raise ValueError("LINUX_CAMSS_SOURCE_MISSING")
    texts={p.name:p.read_text(errors="replace") for p in c.glob("*.[ch]")}
    if not texts:raise ValueError("NO_CAMSS_CODE_TO_AUDIT")
    x="\n".join(texts.values())
    actual=[(name,body.count("request_firmware(")+body.count("request_firmware_direct("))
            for name,body in texts.items() if "request_firmware" in body]
    macro=re.findall(r'#define\s+(CAMSS_X1E_PIX_TRIGGER_FW(?:_R5)?)\s+"([^"]+)"',x)
    # Distinguish source-only IQ-host capsule ingestion from a real
    # camera firmware loader/remote processor. The supplied X1E
    # engineering driver can evolve, so refuse unexpected requests.
    names=sorted(set(v for _,v in macro))
    if not names or any(not n.startswith("sp11/e003h/E003H_PIX_ORACLE_CAPSULE") for n in names):
        raise ValueError("CAMSS_FIRMWARE_CALL_NO_LONGER_ONLY_KNOWN_IQ_CAPSULES")
    if "CAMERA_ICP" in x or "rproc_boot(" in x or "qcom_scm_pas_auth_and_reset(" in x:
        raise ValueError("CAMSS_CAMERA_ICP_OR_REMOTE_PROC_IMPLEMENTATION_REQUIRES_NEW_AUDIT")
    return {"source_file_count":len(texts),
        "firmware_read_call_sites":actual,
        "existing_firmware_requests_are_known_HOST_IQ_capsules_not_camera_ICP_boot":True,
        "known_capsule_names":names,
        "camera_ICP_startup_loader_in_this_source":False}

def audit(win:Path)->dict:
    pkg=firmware_packages(win)
    assert set(pkg)==set(NAMES)
    assert all(f["cpu_architecture"]=="XTENSA" for f in pkg.values())
    proc=remoteprocs()
    if not {"adsp","cdsp"}.issubset({p["name"] for p in proc}):
        raise ValueError("RUNNING_AUDIO_COMPUTE_REMOTEPROC_BASELINE_DIFFERENT")
    if any("camera" in p["name"] or "icp" in p["name"] or "ipe" in p["name"] for p in proc):
        raise ValueError("CAMERA_REMOTEPROC_EXISTENCE_CHANGED_NEEDS_DIRECT_ANALYSIS")
    source=linux_camss_loader_boundary()
    front=json.loads((ROOT/"experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hy-production-one-stream-r27/RESULT.json").read_text())
    z=json.loads((ROOT/"experiments/E003-front-imx681-cphy/e003i-front-native-productionization/z-live-3a-runtime/RESULT.json").read_text())
    rear=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ne-screen-rear-stable-window-guarded-one-shot/RESULT.json").read_text())
    assert front["status"].startswith("PASS_CAPTURE_HY") and front["frames"]==27 and front["golden_return"]=="PASS"
    assert z["status"]=="PASS" and z["paired_tlbg_stats3a_identity_exact"] and len(z["observed_sequences"])==6
    assert rear["original_complete_physical_one_shot_runner_passed"] and rear["identity"]=="E004ne"
    return {"status":"PASS_E004NJ_SP11_WINDOWS_CAMERA_ICP_XTENSA_FORMAT_VS_LINUX_HOST_LOADER_AND_FRONT_NATIVE_HW_EVIDENCE",
        "windows_installed_CAMERA_ICP_files_metadata_only":pkg,
        "current_Linux_remoteproc_names_and_non_camera_firmware_basenames":proc,
        "current_Linux_CAMSS_source_only_loader_boundary":source,
        "bounded_native_Linux_front_QC10C_27_hardware_frames_previously_passed":True,
        "bounded_native_Linux_front_real_3A_statistics_six_frames_previously_passed":True,
        "native_qualified_live_Windows_tuning_Linux_rear4K_image_parity_proven":False,
        "ICP_binary_loadability_and_host_IPC_on_Linux_proven":False,
        "existing_SP11_user_RGB_software_fallback_E004ne_passed":True,
        "camera_ICP_windows_blob_copied_to_Linux_Git_or_another_host":False,
        "hardware_camera_or_boot_modified_during_this_source_only_audit":False}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--read-only-windows-root",required=True,type=Path)
    args=p.parse_args()
    print(json.dumps(audit(args.read_only_windows_root),sort_keys=True,indent=2))
