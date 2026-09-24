#!/usr/bin/env python3
"""E004nz OEM AVStream static control handoff: read-only scalar verifier."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
EXTRACTOR=HERE/"extract-static-callgraph.py"
RESULT=HERE/"RESULT.json"
MAP=ROOT/"docs/CAMERA-STACK-PORT-MAP.md"
README=HERE/"README.md"
EXPECTED_AVS_SHA="b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed"
NAMES=(
 "engine_initialize","engine_start","engine_start_ack","engine_stop",
 "engine_stop_isp_error","engine_stop_sensor_error",
 "configuration_from_user_mode","profile_configuration_packet",
 "profile_per_request_packet","create_topology","topology_activate_vcm",
 "isp_worker_registration","single_filter_exclusivity","filter_initialized",
 "pin_state_transition","privacy_shutter","still_photo_control",
 "isp_event_worker_callback","preview_profile_handler","still_profile_handler",
 "video_profile_handler","stats_pin_factory","pdaf_config_override"
)
START=("0x804","0x804","0x5","0x17")
STOP=("0x805","0x809","0x805","0x18")

def verify_result(r):
    assert r["schema"]=="sp11-e004nz-same-machine-Windows-AVStream-static-control-slice-v1"
    assert r["experiment"]=="E004nz"
    assert r["parent_git_revision"]=="bf70ebaa7f01a509b511cd3869e5ea08eb9a7352"
    assert r["OEM_private_same_SP11_AVStream_driver_sha256"]==EXPECTED_AVS_SHA
    assert r["OEM_AVStream_driver_bytes"]==547192
    assert r["OEM_AVStream_ARM64_instructions_source_checked"]==66
    inf=r["INF"]
    assert set(inf)=={
       "AVStream_kernel_service_registered","three_sensor_identities",
       "preview_still_video_pin_names","DeviceMFT_DLL_registered_not_session_observed",
       "camera_profile_registry_assignment_in_this_INF"}
    for k in inf:
        assert inf[k] is (False if k=="camera_profile_registry_assignment_in_this_INF" else True)
    assert set(r["diagnostic_call_sites"])==set(NAMES)
    for name,row in r["diagnostic_call_sites"].items():
        assert set(row)=={"OEM_diagnostic_RVA","PE_ADRP_RVA","PE_ADD_RVA"}
        assert all(isinstance(row[k],str) and row[k].startswith("0x")
                   for k in row)
        a=int(row["PE_ADRP_RVA"],16)
        b=int(row["PE_ADD_RVA"],16)
        assert 0<b-a<=12 and b%4==0
    assert r["diagnostic_call_sites"]["engine_start"]["PE_ADRP_RVA"]=="0x1efe8"
    assert r["diagnostic_call_sites"]["engine_stop"]["PE_ADRP_RVA"]=="0x1f148"
    assert r["diagnostic_call_sites"]["configuration_from_user_mode"]["PE_ADRP_RVA"]=="0x6914"
    assert r["diagnostic_call_sites"]["profile_configuration_packet"]["PE_ADRP_RVA"]=="0x6c2c"
    assert r["diagnostic_call_sites"]["profile_per_request_packet"]["PE_ADRP_RVA"]=="0xa0f4"
    assert r["diagnostic_call_sites"]["isp_worker_registration"]["PE_ADRP_RVA"]=="0x7ff60"
    assert r["diagnostic_call_sites"]["stats_pin_factory"]["PE_ADRP_RVA"]=="0x824f4"
    assert r["camera_engine_shared_indirect_dispatch_RVA"]=="0x20da8"
    assert r["camera_engine_on_start_source_function_RVA"]=="0x1efd0"
    assert r["camera_engine_on_stop_source_function_RVA"]=="0x1f130"
    order=r["camera_engine_start_stop_numeric_selectors_UNDECODED"]
    assert set(order)=={"engine_start","engine_stop"}
    assert tuple(x["selector"] for x in order["engine_start"])==START
    assert tuple(x["selector"] for x in order["engine_stop"])==STOP
    assert tuple(x["shared_dispatch_call_RVA"] for x in order["engine_start"])==(
        "0x1f020","0x1f05c","0x1f090","0x1f0f0")
    assert tuple(x["shared_dispatch_call_RVA"] for x in order["engine_stop"])==(
        "0x1f180","0x1f1e4","0x1f21c","0x1f280")
    must_true=("configuration_receives_user_mode_sensor_timing_scalar",
               "profile_and_processing_type_are_present_in_configuration_and_per_request_packet_paths",
               "distinct_preview_still_video_and_stats_pin_logic_present",
               "isp_notification_worker_and_request_identity_path_statically_present",
               "no_Windows_binary_UMD_payload_or_optical_bytes_exported")
    must_false=("actual_Windows_camera_session_selected_profile_identified",
                "registered_OEM_DeviceMFT_actually_loaded_in_recording_proven",
                "numeric_dispatch_selectors_mapped_to_specific_sensor_or_ISP_commands",
                "live_rear_BF_event_0x0f_observed",
                "Linux_rear_native_4k_ISP_optical_frame_proven",
                "hardware_camera_or_Golden_changed")
    assert all(r[k] is True for k in must_true)
    assert all(r[k] is False for k in must_false)
    return True

if __name__=="__main__":
    spec=importlib.util.spec_from_file_location("e004nz_oracle",EXTRACTOR)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    observed=json.loads(RESULT.read_text())
    verify_result(observed)
    assert module.build()==observed,"original OEM static re-extraction differs from recorded scalar"
    assert hashlib.sha256(module.DRIVER.read_bytes()).hexdigest()==EXPECTED_AVS_SHA
    assert "CCameraEngine" in README.read_text()
    assert "MFT registration does not establish" in README.read_text()
    assert "numeric selector" in README.read_text().lower() or "selectors" in README.read_text().lower()
    arch=MAP.read_text()
    assert "E004nz" in arch
    assert "L1" in arch and "L2" in arch and "L3" in arch and "L4" in arch
    negative=(
      ("wrong_OEM_image",lambda x:x.__setitem__("OEM_private_same_SP11_AVStream_driver_sha256","0"*64)),
      ("wrong_ARM64_anchor_count",lambda x:x.__setitem__("OEM_AVStream_ARM64_instructions_source_checked",65)),
      ("fabricated_active_profile_from_comments",lambda x:x["INF"].__setitem__("camera_profile_registry_assignment_in_this_INF",True)),
      ("remove_rear_sensor_identity",lambda x:x["INF"].__setitem__("three_sensor_identities",False)),
      ("fabricated_MFT_execution",lambda x:x.__setitem__("registered_OEM_DeviceMFT_actually_loaded_in_recording_proven",True)),
      ("fabricated_camera_profile",lambda x:x.__setitem__("actual_Windows_camera_session_selected_profile_identified",True)),
      ("fake_selector_semantics",lambda x:x.__setitem__("numeric_dispatch_selectors_mapped_to_specific_sensor_or_ISP_commands",True)),
      ("wrong_shared_call_helper",lambda x:x.__setitem__("camera_engine_shared_indirect_dispatch_RVA","0x20db0")),
      ("wrong_start_first_selector",lambda x:x["camera_engine_start_stop_numeric_selectors_UNDECODED"]["engine_start"][0].__setitem__("selector","0x805")),
      ("wrong_stop_order",lambda x:x["camera_engine_start_stop_numeric_selectors_UNDECODED"]["engine_stop"][0].__setitem__("selector","0x18")),
      ("wrong_start_callsite",lambda x:x["camera_engine_start_stop_numeric_selectors_UNDECODED"]["engine_start"][2].__setitem__("shared_dispatch_call_RVA","0x1f094")),
      ("wrong_user_timing_anchor",lambda x:x["diagnostic_call_sites"]["configuration_from_user_mode"].__setitem__("PE_ADRP_RVA","0x6918")),
      ("missing_stats_pin",lambda x:x["diagnostic_call_sites"].pop("stats_pin_factory")),
      ("faked_BF_live",lambda x:x.__setitem__("live_rear_BF_event_0x0f_observed",True)),
      ("faked_native_rear4K",lambda x:x.__setitem__("Linux_rear_native_4k_ISP_optical_frame_proven",True)),
      ("faked_image_export",lambda x:x.__setitem__("no_Windows_binary_UMD_payload_or_optical_bytes_exported",False)),
      ("faked_Golden_change",lambda x:x.__setitem__("hardware_camera_or_Golden_changed",True)),
    )
    for name,change in negative:
        mutant=copy.deepcopy(observed)
        change(mutant)
        try:verify_result(mutant)
        except (AssertionError,KeyError,TypeError):
            continue
        raise SystemExit("FAIL_OPEN_E004NZ_NEGATIVE_MUTANT "+name)
    print("PASS_E004NZ_ORIGINAL_SAME_SP11_OEM_AVSTREAM_66_ARM64_INSTRUCTION_ANCHORS_"
          "3_PHYSICAL_CAMERA_IDENTITIES_3_LOGICAL_CAPTURE_PINS_"
          "STATIC_PROFILE_REQUEST_PACKET_ENGINE_START_STOP_"
          "17_FAIL_CLOSED_NEGATIVE_TESTS_MFT_LIVE_RUNTIME_UNPROVEN")
