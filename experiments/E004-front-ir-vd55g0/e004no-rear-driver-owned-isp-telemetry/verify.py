#!/usr/bin/env python3
"""E004no offline strict evidence gate. Never reads private ETL/NTFS/camera."""
import copy
import json
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GUID = "57e95397-c84e-4f53-9473-56207aaa5938"
SHA = "64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"

def verify(result, provider):
    assert result["experiment"] == provider["experiment"] == "E004no"
    assert result["same_SP11_Windows_11_OEM_rear"] == "OV13858_MSHW0491"
    assert result["selected_ISP_driver_SHA256"] == provider["driver_sha256"] == SHA
    assert result["driver_embedded_live_ETW_candidate_GUID"] == GUID
    assert result["Windows_live_GUID_and_exact_installed_PE_bytes_matched"] is True
    assert result["embedded_ETW_GUID_PE_file_offset_from_readonly_byte_scan"] == 289216
    assert provider["enum_trace_guids_ex_status"] == 0
    assert provider["GUID_alignment_matches"] == [{
        "alignment": 0,
        "embedded_and_runtime_matches": [GUID + " | PE_FILE_OFFSET=289216"],
    }]
    assert result["status"].startswith("PASS_REAL_WIN_REAR4K_QCISP_PE_MATCHED_REGISTERED_GUID")
    assert result["live_ETW_session_single_guid_start_and_stop_succeeded"] is True
    assert result["ETW_total_events"] == 12
    assert result["candidate_ETW_events"] == 11
    assert result["candidate_ETW_event_ids"] == [
        {"count": 2, "id": 2}, {"count": 8, "id": 61}, {"count": 1, "id": 62},
    ]
    assert result["candidate_ETW_processing_error_code"] == 15003
    assert result["candidate_ETW_event_payloads_present_but_UNDECODED"] is True
    assert 20 <= result["candidate_ETW_event_payload_hex_minimum_length"] < 160
    assert result["candidate_ETW_event_payload_hex_maximum_length"] == 160
    assert 0 <= result["candidate_ETW_burst_duration_ms"] <= 10
    assert result["candidate_ETW_first_event_ms_before_WinRT_rear4k_live_marker"] == 269
    first = datetime.fromisoformat(result["candidate_ETW_first_event"])
    last = datetime.fromisoformat(result["candidate_ETW_last_event"])
    assert first <= last and (last - first).total_seconds() < 0.05
    assert result["candidate_ETW_event_process_context_id_is_NOT_hardware_IFE_core"] is True
    assert result["Windows_manifest_provider_for_candidate_found"] is False
    assert result["candidate_ETW_event_fields_decoded_as_ISP_resources"] is False
    assert result["private_OEM_PDB_public_Microsoft_symbol_server_HEAD_status"] == "HTTP_404"
    assert result["Windows_PnP_qcISP_associated_IRQ_resource_count"] == 12
    assert result["Windows_PnP_associated_MMIO_memory_resources_via_WMI"] == 0
    assert result["Windows_PnP_associated_WMI_MMIO_absence_means_no_MMIO"] is False
    assert result["Windows_KD_driver_object_extension_read_fails_ObpInfoMaskToOffset"] is True
    assert result["Windows_prior_KD_direct_camera_MMIO_uniform_80000000_is_validated"] is False
    assert result["task_has_no_future_trigger_and_is_unregistered"] is True
    assert result["one_original_script_entry_permanent_atomic_consume_marker"] is True
    assert (result["original_WinRT_rear_record_NV12_width"],
            result["original_WinRT_rear_record_NV12_height"]) == (3840, 2160)
    assert result["original_WinRT_software_bitmap_handle_count"] == 350
    assert result["original_WinRT_source_timestamps_missing"] == 350
    assert result["original_WinRT_session_frame_ids_not_proven"] is True
    assert result["original_trace_stays_private_same_SP11"] is True
    assert result["raw_trace_file_bytes"] == 16384
    for key in (
        "registered_GUID_identified_as_qcISP_driver_owned",
        "active_rear_IFE_or_CSID0_resource_proven",
        "active_rear_VFE0_output_DMA_proven",
    ):
        assert provider[key] is False, key
    assert provider["no_ETW_session_started"] is True # preflight only
    assert provider["no_camera_opened"] is True # preflight only
    assert provider["original_driver_binary_exported"] is False
    for key in (
        "active_rear_CSID0_IPP_selected_IFE_core_proven",
        "active_rear_VFE0_FULL_WM_DMA_output_geometry_proven",
        "rear_Linux_native_hardware_ISP_4K_frame_proven",
        "original_driver_firmware_ETL_images_pixels_or_metadata_transcript_exported",
    ):
        assert result[key] is False, key
    return True

def verify_source():
    provider = (HERE / "find-qcisp-live-etw-providers.ps1").read_text()
    capture = (HERE / "capture-rear4k-singleentry-provider-trial.ps1").read_text()
    reduce = (HERE / "extract-windows-scalar.ps1").read_text()
    assert "EnumerateTraceGuidsEx" in provider and "FindBytes" in provider
    assert 'qccamisp8380.sys' in provider and "64463b4d" in provider
    assert "[IO.FileMode]::CreateNew" in capture
    assert "E004NO-rear4k-driver-etw-single-entry.consumed" in capture
    assert "VideoRecord" in capture and "3840" in capture and "2160" in capture
    assert "SoftwareBitmap.LockBuffer" not in capture and "CopyToBuffer" not in capture
    assert "candidate_ETW_processing_error_code=15003" in reduce
    assert "candidate_ETW_event_fields_decoded_as_ISP_resources=$false" in reduce
    assert "active_rear_VFE0_FULL_WM_DMA_output_geometry_proven=$false" in reduce
    assert "Split-Path -Parent $MyInvocation.MyCommand.Path" in reduce
    return True

if __name__ == "__main__":
    r = json.loads((HERE / "RESULT.json").read_text())
    p = json.loads((HERE / "PROVIDER-PREFLIGHT.json").read_text())
    verify(r, p)
    verify_source()
    tests = [
        ("bad GUID",lambda x:x.__setitem__("driver_embedded_live_ETW_candidate_GUID","00000000-0000-0000-0000-000000000000")),
        ("wrong event count",lambda x:x.__setitem__("candidate_ETW_events",12)),
        ("decoded-but-unproven",lambda x:x.__setitem__("candidate_ETW_event_fields_decoded_as_ISP_resources",True)),
        ("missing WPP metadata falsely decoded",lambda x:x.__setitem__("candidate_ETW_processing_error_code",0)),
        ("false IFE assignment",lambda x:x.__setitem__("active_rear_CSID0_IPP_selected_IFE_core_proven",True)),
        ("false DMA proof",lambda x:x.__setitem__("active_rear_VFE0_FULL_WM_DMA_output_geometry_proven",True)),
        ("false Linux frame",lambda x:x.__setitem__("rear_Linux_native_hardware_ISP_4K_frame_proven",True)),
        ("false task single-use",lambda x:x.__setitem__("one_original_script_entry_permanent_atomic_consume_marker",False)),
        ("false memory exclusion",lambda x:x.__setitem__("Windows_PnP_associated_WMI_MMIO_absence_means_no_MMIO",True)),
        ("false image privacy",lambda x:x.__setitem__("original_driver_firmware_ETL_images_pixels_or_metadata_transcript_exported",True)),
    ]
    for name, mutate in tests:
        t=copy.deepcopy(r)
        mutate(t)
        try:
            verify(t,p)
        except AssertionError:
            pass
        else:
            raise SystemExit("FAIL E004no mutation test: " + name)
    import yaml
    state = yaml.safe_load((ROOT / "state/project.yaml").read_text())
    assert state["latest_windows_isp_resource_oracle"]["identity"] == "E004no"
    assert state["latest_windows_isp_resource_oracle"]["active_rear_VFE0_FULL_WM_DMA_output_geometry_proven"] is False
    assert state["latest_windows_native_isp_oracle"]["identity"] == "E004nn"
    print(f"PASS E004no exact OEM PE/runtime ETW GUID, 11 undecoded startup events, 350 real Windows rear4K app handles, {len(tests)} negative tests, Golden-return record; native rear Linux ISP 4K unproven")
