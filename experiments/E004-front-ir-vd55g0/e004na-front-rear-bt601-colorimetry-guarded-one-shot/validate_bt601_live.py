#!/usr/bin/python3
"""Independent actual REAL uid1000 V4L2 -> GST front/rear BT.601 caps gate.

Only scalar text. No camera/device, optical pixels/images/RAW/thumb/hash,
sensor writes, boot, files other than reading preexisting scalar logs.
For full release the actual original physical candidate must run it
in the sealed one-shot BEFORE the final 119-edge native-neutral gate.
"""
from pathlib import Path
import json,re,sys

GEOMETRY={"front":(1920,1080),"rear":(3840,2160)}
PHASES=("DAYLIGHT","GAIN")
V4L2_TAG={"colorspace":1,"ycbcr_enc":1,"quantization":2,"xfer_func":1}


def parse_native_tag(log:str,camera:str)->dict:
    lines=[line for line in log.splitlines()
           if line.startswith("E004NA_REAL_V4L2_OUTPUT_COLORIMETRY camera=")]
    if len(lines)!=1:
        raise ValueError("EXPECTED_EXACTLY_ONE_NEW_REAL_NATIVE_S_FMT_COLOUR_TAG")
    words={}
    for entry in lines[0].split()[1:]:
        if "=" not in entry:raise ValueError("INVALID_REAL_V4L2_METADATA_EVENT")
        key,val=entry.split("=",1)
        if key in words:raise ValueError("DUPLICATE_NATIVE_COLOR_FIELD")
        words[key]=val
    if words.get("camera")!=camera or words.get("exact_bt601")!="YES":
        raise ValueError("WRONG_NATIVE_CAM_OR_NO_REAL_METADATA")
    expected=dict(V4L2_TAG,width=GEOMETRY[camera][0],
                  height=GEOMETRY[camera][1])
    for key,val in expected.items():
        if words.get(key)!=str(val):
            raise ValueError("REAL_V4L2_COLORSPACE_OR_GEOMETRY_RETURN_MISMATCH")
    return expected


def validate(out:Path)->dict:
    cams={}
    for camera in GEOMETRY:
        log=(out/(camera+"-SERVICE-STDERR.txt")).read_text()
        native=parse_native_tag(log,camera)
        phases={}
        for phase in PHASES:
            d=json.loads((out/(camera.upper()+"-"+phase+"-PROBE.json")).read_text())
            if (d.get("status")!="PASS" or d.get("camera")!=camera or
                d.get("frames")!=90 or d.get("effective_uid")!=1000 or
                d.get("real_v4l2src_NV12_colorimetry")!="bt601" or
                d.get("ordinary_UID1000_I420_consumer_colorimetry")!="bt601" or
                d.get("consumer_colorimetry_from_actual_real_video_not_synthetic") is not True or
                d.get("pixel_files_saved") is not False or
                d.get("camera_route_or_controls_changed") is not False):
                raise ValueError("REAL_UNPRIVILEGED_SOURCE_AND_APP_COLOR_CAPS_MISMATCH")
            phases[phase]={"real_UID1000_front_rear_app_frames":d["frames"],
                           "real_raw_NV12_output_colorimetry":"bt601",
                           "real_independent_I420_consumer_colorimetry":"bt601"}
        cams[camera]={"exact_physical_V4L2_loopback_S_FMT_metadata":native,
                      "real_UID1000_source_and_consumer_colour_caps_by_phase":phases}
    return {
      "status":"PASS_E004NA_REAL_FRONT1080_REAR4K_EXPLICIT_BT601_V4L2_AND_UID1000_GSTREAMER_MATRIX_CONSISTENCY",
      "both_actual_cameras_and_both_native_gain_phases_checked":True,
      "ordinary_UID1000_NV12_source_and_I420_output_match_601":True,
      "real_source_RGB_matrix_and_original_sensor_colour_chart_calibrated":False,
      "sensor_primaries_gamma_white_balance_Bayer_CFA_true_noise_or_Windows_ISP_parity_proven":False,
      "no_private_optical_pixels_photos_RAW_frames_image_hashes_or_thumbnails_exported":True,
      "cameras":cams}

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("ACTUAL_TEXT_ONLY_OUTPUT_FOLDER_REQUIRED")
    print(json.dumps(validate(Path(sys.argv[1])),sort_keys=True,indent=2))
