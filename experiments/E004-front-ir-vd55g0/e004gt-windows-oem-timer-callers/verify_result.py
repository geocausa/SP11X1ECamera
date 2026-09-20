#!/usr/bin/env python3
"""E004gt: verify immutable original Windows normal-OEM and SP7 KD logs, offline.

Only a bounded OEM camera-control observation, NEVER an optical emission
measurement, early-boot call exclusion, native LED enable or face-auth test.
"""
from hashlib import sha256
from pathlib import Path
import json
import re
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ZIP=HERE/"evidence/ORIGINAL-WINDOWS-AND-SP7-KD-20260920.zip"
RESULT=HERE/"evidence/RESULT.json"
PREPARED=HERE/"evidence/PREPARED.json"
CAPTURE_SCRIPT=HERE/"capture-oem-timer-windows.ps1"
KD_HASH="e10a1bc0c51085ba94dcd4a870c4adf739100294b62f55306dfdaba23bd994a0"
CAP_HASH="aac4b8dfeb7df757623d7784cedf6b434272b45e72282ce80813febb17f48ec2"
SRC_HASH="e667bc41e9518e0d6d3e24597bf08c7675a6265f4ccb2a3f60aa4716d7f4902c"
TARGETS={
    "pmic_four_timer":(b"E004GT_TIMER4_HIT",b"qcpmic8380+0x26d50"),
    "pmic_single_timer":(b"E004GT_TIMER1_HIT",b"qcpmic8380+0x26f30"),
    "flash_timer_wrapper":(b"E004GT_FLASH_TIMER_HIT",b"qccamflash8380+0x4dd0"),
    "flash_config":(b"E004GT_FLASH_CONFIG_HIT",b"qccamflash8380+0x48c8"),
}

def require(cond,what):
    if not cond:
        raise AssertionError("E004GT_FAIL_CLOSED "+what)

def validate(kd,capture,result,prepared,source):
    require(len(kd)==9958 and sha256(kd).hexdigest()==KD_HASH,
            "original SP7 KD raw hash/length drift")
    require(len(capture)==1016 and sha256(capture).hexdigest()==CAP_HASH,
            "original Windows capture raw hash/length drift")
    require(sha256(source).hexdigest()==SRC_HASH,
            "bounded independently authored Windows capture script changed")
    require(re.search(rb"(?i)key=[A-Za-z0-9.]{8,}",kd) is None,
            "KD credential leaked into retained trace")
    for marker in (
        b"Connected to Windows 10 26100 ARM 64-bit",
        b"E004GT_FRESH_CODE_VERIFIED",
        b"E004GT_FOUR_ONESHOT_HOOKS_ARMED",
        b"E004GT_AFTER_OEM_PREVIEW_STOP",
        b"E004GT_ALL_FOUR_KD_HOOKS_DISARMED",
        b"fffff803`1b8a0000",b"fffff803`1f940000",
    ):
        require(marker in kd,"live KD module or closure marker missing "+marker.decode())
    for i, (name,(marker,source_rva)) in enumerate(TARGETS.items()):
        require(source_rva in kd and
                re.search(rb"(?m)^\s*"+str(i).encode()+
                          rb" e fffff803`[0-9a-f]+\s+/1",kd) is not None,
                "live one-shot hook not armed "+name)
        # Commands are echoed within bp definitions: only a marker at the
        # *start of a line* proves the callback actually executed.
        require(re.search(rb"(?m)^"+marker+rb"\s*$",kd) is None,
                "unexpected actual OEM lifecycle callback hit "+name)
    require(b"bc *; bl; .echo E004GT_ALL_FOUR_KD_HOOKS_DISARMED" in kd,
            "KD clear-all operation absent")
    require(capture.startswith(b"\xff\xfe"),"original Windows log BOM drift")
    s=capture.decode("utf-16")
    for marker in ("E004GT_BEGIN","E004GT_INITIALIZE_PASS",
                   "E004GT_SOURCE subtype=NV12 width=644 height=604 fps=60/1",
                   "E004GT_READER_STARTED","E004GT_ACQUIRED_METADATA_ONLY=8",
                   "E004GT_STOP_PASS","E004GT_END",
                   "E004GT_BOUNDED_OEM_PREVIEW_COMPLETE_NO_PIXEL_SAVE"):
        require(marker in s,"original OEM stop/metadata marker absent "+marker)
    require(len(re.findall(r"(?m)^E004GT_FRAME_METADATA n=[1-8]\s*$",s))==8,
            "exact eight bounded metadata frames missing")
    require(prepared["experiment"]=="E004gt" and
            prepared["normal_oem_preview_max_frames"]==8 and
            prepared["normal_oem_preview_max_seconds"]==4 and
            prepared["capture_script_sha256"]==SRC_HASH and
            prepared["prior_e004gb_and_e004gs_one_shot_repeated"] is False,
            "original fresh experiment preparation contract changed")
    require(result["experiment"]=="E004gt" and
            result["status"]=="PASS_NEW_BOUNDED_WINDOWS_OEM_TIMER_CALLER_ZERO_HITS_GOLDEN_RETURN",
            "completion metadata drift")
    require(result["new_windows_boots"]==1 and
            result["new_oem_normal_preview_sessions"]==1 and
            result["oem_preview_metadata_frames"]==8 and
            result["kd_one_shot_auto_continue_hooks_armed"]==4 and
            result["kd_callback_hits_during_bounded_oem_session"]==
               {key:0 for key in TARGETS},
            "completion scope, normal frame count or callback count drift")
    require(result["original_sp7_kd_sha256"]==KD_HASH and
            result["original_windows_capture_sha256"]==CAP_HASH and
            result["fresh_capture_source_sha256"]==SRC_HASH,
            "original evidence references changed")
    for tag in (
        "preboot_or_early_init_timer_programming_excluded",
        "other_firmware_or_pmic_timer_writers_excluded",
        "hardware_timer_active_or_autonomous_cutoff_proven",
        "oem_preview_pixels_read_or_persisted",
        "prior_e004gb_and_e004gs_identities_repeated",
        "linux_native_ir_emitter_enabled",
        "windows_oem_physical_current_irradiance_or_pulse_measured",
        "autonomous_led_fault_off_verified",
        "linux_login_or_pam_modified",
    ):
        require(result[tag] is False,"unverified hardware/security claim "+tag)
    for tag in (
        "oem_preview_stop_async_completed",
        "all_four_kd_hooks_explicitly_cleared_after_capture",
        "sp7_kd_closed_and_stopped",
        "uefi_bootorder_unchanged",
        "grub_next_entry_empty",
        "camera_nodes_modules_and_processes_idle_on_golden",
    ):
        require(result[tag] is True,"documented teardown/GOLDEN return claim "+tag)
    require(result["golden_return_boot_id"]==
            "6f958ff9-f46b-47c5-91ac-30a3a5b1aa47",
            "Golden return identity mismatch")

def main():
    result=json.loads(RESULT.read_text())
    prepared=json.loads(PREPARED.read_text())
    require(sha256(ZIP.read_bytes()).hexdigest()==result["archive_sha256"],
            "original zip changed")
    with zipfile.ZipFile(ZIP) as archive:
        require(archive.namelist()==[
            "ORIGINAL-SP7-KD.log","ORIGINAL-WINDOWS-CAPTURE-UTF16LE.log"],
            "unapproved archive members")
        kd=archive.read("ORIGINAL-SP7-KD.log")
        cap=archive.read("ORIGINAL-WINDOWS-CAPTURE-UTF16LE.log")
    validate(kd,cap,result,prepared,CAPTURE_SCRIPT.read_bytes())
    print("E004GT_ORIGINAL_WINDOWS_OEM_8_FRAME_CAPTURE_AND_SP7_KD=PASS")
    print("E004GT_FOUR_POSTBOOT_TIMER_AND_CONFIG_CALLBACK_HITS=0 ORIGINAL_LOGS_PINNED=YES")
    print("E004GT_GOLDEN_RETURN=PASS EARLY_TIMER_PROGRAMMING=NOT_EXCLUDED NATIVE_IR=OFF")

if __name__=="__main__":
    main()
