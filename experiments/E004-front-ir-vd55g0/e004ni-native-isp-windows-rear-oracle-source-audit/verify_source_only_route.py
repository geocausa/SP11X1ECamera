#!/usr/bin/python3
"""Camera-free native ISP pivot consistency test; no private photos or driver blobs."""
import json,sys
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent

def verify():
    strategy=yaml.safe_load((ROOT/"state/project.yaml").read_text())
    assert strategy["phase"]=="native-qualcomm-hardware-isp-windows-oem-rgb-image-quality-priority"
    opt=strategy["active_native_isp_priority"]
    assert opt["user_selected_second_previously_optional_windows_oem_isp_path"]
    assert opt["selected_real_rear_Windows_ACPI_subsystem"]=="MSHW0491"
    assert opt["selected_real_rear_sensor"]=="OV13858"
    assert opt["selected_real_rear_Windows_tuning_file"]=="com.surface.tuned.rfc_ov13858.bin"
    assert opt["selected_real_rear_Windows_tuning_sha256"]=="4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"
    assert opt["other_MSHW0561_tuning_is_NOT_selected_on_this_SP11"]
    assert opt["physical_FRONT_linux_VFE_PIX_QC10C_processed_frame_proven"]
    assert opt["actual_front_native_E003i_HY_27_hardware_frames_Golden_return_proven"]
    assert opt["actual_front_native_E003i_Z_six_generation_paired_AEC_BHist_AWB_stats_proven"]
    assert not opt["physical_REAR_linux_VFE_PIX_hardware_processed_4K_frame_proven"]
    assert not opt["Windows_Xtensa_ICP_firmware_compatible_Linux_loader_and_host_IPC_proven"]
    assert not opt["candidate_OPE_upstream_Agatti_shikra_code_directly_compatible_X1E_proven"]
    assert opt["selected_Windows_driver_package_read_only_mount_cleanly_unmounted"]
    assert opt["normal_default_Golden_camera_IR_tone_temporal_unchanged"]
    assert strategy["latest_rgb_experiment"]["identity"]=="E004nh"
    assert not strategy["latest_rgb_experiment"]["original_complete_physical_one_shot_runner_passed"]
    assert strategy["last_complete_full_native_rgb_trial"]["identity"]=="E004ne"
    assert strategy["last_complete_full_native_rgb_trial"]["original_full_one_shot_physical_runner_success"]
    assert strategy["strategy"]["active_rgb_backend_priority"]=="native_qualcomm_hardware_isp_with_same_SP11_Windows_OEM_reference"
    docs=[ROOT/"AGENTS.md",ROOT/"src/sp11-camera-stack/RGB-PHASED-ROADMAP.md",
          ROOT/"HANDOFF.md",ROOT/"CONTINUE.md",ROOT/"PROJECT_STATE.md",HERE/"README.md"]
    for f in docs:
        s=f.read_text()
        assert "Windows" in s and "ISP" in s and "Golden" in s,f
    a=(ROOT/"AGENTS.md").read_text()
    assert "SECOND route" in a and "SP11" in a
    assert not Path("/run/sp11-windows-isp-audit-20260923").exists()
    assert not Path("/var/lib/sp11-camera-e004ni").exists()
    assert not (HERE/"RESULT.json").exists()
    assert not (HERE/"evidence").exists()
    assert not any(x.suffix.lower() in (".png",".jpg",".jpeg",".raw",".nv12",
        ".webp",".bmp",".dll",".sys",".mbn",".elf",".bin") for x in HERE.rglob("*") if x.is_file())
    prior=(ROOT/"oracle/windows-e000-inventory.md").read_text()
    for value in (opt["selected_real_rear_Windows_tuning_file"],
                  opt["selected_real_rear_Windows_tuning_sha256"],"MSHW0491"):
        assert value in prior
    return {"status":"PASS_E004NI_SOURCE_ONLY_USER_SELECTED_WINDOWS_NATIVE_ISP_PRIORITY_SAME_SP11_REAR_MSHW0491_TUNING_LAST_RGB_FALLBACK_GOLDEN_NO_PROPRIETARY_PAYLOAD",
            "selected_rear_sensor":"OV13858","selected_board":"MSHW0491",
            "native_front_27frame_QC10C_hardware_output_proven":True,
            "Windows_parity_front_and_rear_native_4K_processed_frames_proven":False,
            "old_software_fallback_E004ne_preserved":True,
            "old_E004nh_original_full_runner_failed_preserved":True,
            "Windows_driverstore_readonly_partition_unmounted":True,
            "optical_photos_pixels_RAW_thumbnails_image_hashes_exported":False}

if __name__=="__main__":
    print(json.dumps(verify(),sort_keys=True))
