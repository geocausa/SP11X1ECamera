#!/usr/bin/env python3
"""E004nn offline scalar verifier: no Windows, camera, or private ETL access."""
import copy
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def validate(j):
    assert j["schema"]=="sp11-e004nn-rear-preview-4k-record-frameserver-scalar-v1"
    assert (j["experiment"],j["sensor"],j["board"]) == ("E004nn","OV13858","MSHW0491")
    assert j["actual_machine"]=="SP11_Windows_11_ARM64"
    assert j["original_windows_user_task_consumed_once"] is False
    assert j["windows_user_task_invocations_observed"]==2
    for k in ("windows_duplicate_scheduled_trigger_detected",
              "windows_duplicate_scheduled_task_unregistered",
              "windows_frame_server_ETW_covers_first_task_invocation_only",
              "Windows_ETW_first_run_vs_second_run_monotonic_timing_boundary_verified",
              "Windows_ETW_first_and_second_invocations_never_merged",
              "Windows_ETW_second_run_wall_clock_markers_overwrote_first_run_markers"):
        assert j[k] is True,k
    assert j["first_traced_winrt_metadata_file"].endswith("212206.json")
    assert j["second_untraced_winrt_metadata_file"].endswith("212305.json")
    from datetime import datetime
    t1=datetime.fromisoformat(j["Windows_first_traced_user_run_json_created"])
    t2=datetime.fromisoformat(j["Windows_second_untraced_user_run_json_created"])
    et=datetime.fromisoformat(j["Windows_traced_ETW_last_event_time"])
    assert et<t1<t2 and (t1-et).total_seconds()<3 and (t2-et).total_seconds()>30
    assert j["windows_original_task_last_observed_exit_code_before_unregistration"]==0
    assert j["Original_Windows_ETW_event_count"]==4314
    assert j["Windows_FrameServer_23_explicit_drop_events"]==0
    assert j["Windows_FrameServer_10_statistics_per_mode"] is True
    assert j["Windows_DeviceMFT_configured_auxiliary_input_pin_1_NV12_4076x2806_count"]==2
    assert j["Windows_FSProxy_configured_auxiliary_output_pin_1_NV12_3736x2802_count"]==1
    assert j["Windows_DeviceMFT_auxiliary_full_sensor_pin_1_shown_active"] is False
    assert j["Windows_device_MFT_media_type_sample_size_is_not_native_ISP_DMA_contract"] is True
    assert j["original_windows_ETL_is_private_on_same_SP11"] is True
    expected=[
        ("VideoPreview",0,1920,1080,246,9832,297,296,297,21,3342336),
        ("VideoRecord",2,3840,2160,254,9795,295,294,288,20,12503040),
    ]
    actual=j["Windows_rear_observed_streams"]
    assert len(actual)==2
    for r,(name,sid,w,h,handles,ms,fs_samples,edges,stat_out,stat_n,media_size) in zip(actual,expected):
        assert (r["stream"],r["Windows_FrameServer_sample_stream_id"])==(name,sid)
        assert (r["Windows_WinRT_NV12_app_width"],r["Windows_WinRT_NV12_app_height"])==(w,h)
        assert r["Windows_WinRT_CPU_bitmap_handles"]==handles
        assert r["Windows_WinRT_source_timestamps_missing"]==handles
        assert r["Windows_WinRT_polling_elapsed_ms"]==ms
        assert r["Windows_FrameServer_distinct_timestamped_client_samples"]==fs_samples
        assert r["Windows_FrameServer_timestamp_monotonic_edges"]==edges
        assert r["Windows_FrameServer_timestamp_duplicates_or_regressions"]==0
        assert r["Windows_FrameServer_timestamp_median_positive_delta_100ns"]==334730
        assert 330000<r["Windows_FrameServer_timestamp_min_positive_delta_100ns"]<=334730
        assert 334730<=r["Windows_FrameServer_timestamp_max_positive_delta_100ns"]<340000
        assert r["Windows_FrameServer_expected_interval_100ns"]==333333
        assert r["Windows_FrameServer_capture_statistics_snapshots"]==stat_n
        assert r["Windows_FrameServer_capture_statistics_last_input"]==stat_out
        assert r["Windows_FrameServer_capture_statistics_last_output"]==stat_out
        assert r["Windows_FrameServer_capture_statistics_drops"]==0
        assert r["Windows_DeviceMFT_matching_output_pin_selected_once"] is True
        assert r["Windows_DeviceMFT_output_pin_default_stride_metadata"]==w
        assert r["Windows_DeviceMFT_output_pin_sample_size_metadata_bytes"]==media_size
        assert r["Windows_DeviceMFT_output_pin_sample_size_metadata_is_NOT_VFE0_DMA_layout"] is True
    assert [x["Name"] for x in j["Windows_camera_drivers"]]==[
        "CameraRearSensor","qcCameraMipiCsi","qcCameraPlatform","qcISP"
    ]
    assert all(x["State"]=="Running" and x["Started"] is True for x in j["Windows_camera_drivers"])
    for k in ("Windows_rear_hardware_IFE_core_assignment_confirmed",
              "Windows_rear_native_VFE0_FULL_WM_DMA_output_geometry_confirmed",
              "Windows_rear_4k_softwarebitmap_equals_native_hardware_4k_surface_proven",
              "Windows_rear_sensor_hardware_frame_ids_measured",
              "Windows_high_quality_photo_mode_tested",
              "optical_pixels_images_RAW_thumbnails_or_hashes_exported",
              "Windows_firmware_tuning_or_proprietary_driver_copied_into_repo",
              "Linux_rear_native_hardware_ISP_4k_frame_proven"):
        assert j[k] is False,k
    assert j["SP7_broken_lower_LCD_excluded_from_image_quality_claims"] is True
    return True

def check_source():
    a=(HERE/"capture-rear-preview-vs-record.ps1").read_text()
    b=(HERE/"extract-windows-scalars.ps1").read_text()
    c=(HERE/"windows-atomic-consumed-guard.ps1").read_text()
    t=(HERE/"test-windows-atomic-consumed-guard.ps1").read_text()
    assert "Surface Camera Rear" in a and "VideoPreview" in a and "VideoRecord" in a
    assert "TryAcquireLatestFrame" in a and "SoftwareBitmap.LockBuffer" not in a
    assert "E004NN-rear-preview-vs-record-20260923-212206.json" in b
    assert "E004NN-rear-preview-vs-record-20260923-212305.json" in b
    assert "windows_user_task_invocations_observed=2" in b
    assert "$root=Split-Path -Parent $MyInvocation.MyCommand.Path" in b
    assert "C:\\Users\\" not in b
    assert "[System.IO.FileMode]::CreateNew" in c
    assert "WINDOWS_ORACLE_SINGLE_USE_ENTRY_REJECTED_OR_UNCERTAIN" in c
    assert "second entry altered existing marker" in t
    assert "Remove-Item -LiteralPath $dir" in t  # temporary selftest only
    return True

if __name__=="__main__":
    j=json.loads((HERE/"RESULT.json").read_text())
    validate(j)
    check_source()
    cases=[
        ("duplicate_window_uncounted",lambda x:x.__setitem__("windows_user_task_invocations_observed",1)),
        ("untraced_run_merged",lambda x:x.__setitem__("windows_frame_server_ETW_covers_first_task_invocation_only",False)),
        ("framecount_faked",lambda x:x["Windows_rear_observed_streams"][1].__setitem__("Windows_FrameServer_distinct_timestamped_client_samples",1650)),
        ("timestamp_regressed",lambda x:x["Windows_rear_observed_streams"][0].__setitem__("Windows_FrameServer_timestamp_duplicates_or_regressions",1)),
        ("sensor_frames_claimed",lambda x:x.__setitem__("Windows_rear_sensor_hardware_frame_ids_measured",True)),
        ("hardware_dma_claimed",lambda x:x.__setitem__("Windows_rear_native_VFE0_FULL_WM_DMA_output_geometry_confirmed",True)),
        ("optical_export_claimed",lambda x:x.__setitem__("optical_pixels_images_RAW_thumbnails_or_hashes_exported",True)),
        ("unobserved_photo_claimed",lambda x:x.__setitem__("Windows_high_quality_photo_mode_tested",True)),
    ]
    for name,mutate in cases:
        test=copy.deepcopy(j);mutate(test)
        try:
            validate(test)
        except AssertionError:
            pass
        else:
            raise SystemExit("FAIL negative test: "+name)
    print("PASS E004nn 2 modes, 4314 original first-run ETW events, 297/295 distinct "
          "FrameServer client timestamps, 2 Windows task invocations audited, "
          f"{len(cases)} negative tests; rear native VFE0 hardware 4K unproven")
