#!/usr/bin/env python3
"""Validate exclusively scalar Windows E004nm oracle; no Windows/optical access."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

def check(result):
    assert result["schema"] == "sp11-e004nm-windows-rear-4k-video-scalar-only-v1"
    assert result["experiment"] == "E004nm"
    assert result["source"] == "actual_same_SP11_Windows_11_OEM_VideoRecord"
    assert result["sensor"] == "OV13858" and result["board"] == "MSHW0491"
    assert result["windows_task_completed_once"] is True
    assert result["windows_task_exit_code"] == 0
    assert result["winrt_start_status"] == "Success"
    assert result["winrt_output_subtype"] == "NV12"
    assert (result["winrt_output_width"], result["winrt_output_height"]) == (3840, 2160)
    assert result["software_bitmap_handles"] == 1650
    assert result["software_bitmap_NV12_3840x2160_count"] == result["software_bitmap_handles"]
    assert result["source_timestamps_missing"] == result["software_bitmap_handles"]
    assert 74000 <= result["original_observer_elapsed_ms"] <= 75000
    assert result["frames_distinct_new_sensor_frames_proven"] is False
    assert sorted(x["Name"] for x in result["camera_drivers"]) == [
        "CameraRearSensor", "qcCameraMipiCsi", "qcCameraPlatform", "qcISP"]
    assert all(x["State"] == "Running" and x["Started"] is True
               for x in result["camera_drivers"])
    assert result["sp7_KD_NET_session_reached_running_Windows_ARM64"] is True
    assert result["kd_physical_TLMM_readable"] is True
    assert result["kd_CSID0_VFE0_reads_uniform_80000000_not_proven_real_configuration"] is True
    for key in ("rear_IFE_resource_id_confirmed",
                "rear_native_VFE0_processed_output_format_confirmed",
                "OEM_HQ_photo_mode_tested",
                "windows_firmware_copied_to_Linux",
                "optical_pixel_photo_raw_thumbnail_or_hash_exported",
                "Linux_rear_native_hardware_ISP_4K_frame_proven"):
        assert result[key] is False, key
    import yaml
    state = yaml.safe_load((ROOT / "state/project.yaml").read_text())
    oracle = state["latest_windows_native_isp_oracle"]
    if oracle["identity"] != "E004nm":
        # Keep this historical Windows oracle independently verifiable after
        # E004nn (or any later source-backed Windows session) becomes latest.
        oracle = state["prior_windows_native_isp_oracle"]
    assert oracle["identity"] == "E004nm"
    assert oracle["dynamic_rear_VFE0_4k_isp_output_proven"] is False
    assert state["latest_native_isp_source_gate"]["identity"] == "E004nl"
    return ("PASS_E004NM_REAL_WINDOWS_REAR4K_NV12_HANDLES_1650_"
            "NO_NATIVE_VFE0_4K_OR_TIMESTAMP_OR_STILL_PROOF")

if __name__ == "__main__":
    print(check(json.loads((HERE / "RESULT.json").read_text())))
