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
    """Independently audit REQUEST, S_FMT return, G_FMT return + event.

    A bare raw zero is accepted ONLY with explicit SMPTE170M
    colorspace, NV12 geometry and exact Linux V4L2 default semantics.
    A fabricated effective tag without all three real-format records
    cannot pass. Actual UID1000 GST bt601 source AND consumer caps are
    separately required by validate(), not inferred here.
    """
    if camera not in GEOMETRY:raise ValueError("UNEXPECTED_RGB_CAMERA")
    records={}
    for line in log.splitlines():
        if not line.startswith("E004NC_COLOR_DIAG camera="):continue
        fields={}
        for item in line.split()[1:]:
            if "=" not in item:raise ValueError("INVALID_COLOR_DIAG_FIELD")
            name,value=item.split("=",1)
            if name in fields:raise ValueError("DUPLICATE_V4L2_FORMAT_FIELD")
            fields[name]=value
        if fields.pop("camera",None)!=camera:
            raise ValueError("FORMAT_CAMERA_MISMATCH")
        stage=fields.pop("stage",None)
        if stage not in ("request","S_FMT_return","G_FMT_return") or stage in records:
            raise ValueError("MISSING_DUPLICATE_OR_UNKNOWN_REAL_FORMAT_STAGE")
        try:records[stage]={k:int(v) for k,v in fields.items()}
        except ValueError as exc:raise ValueError("NONNUMERIC_REAL_COLOR_FORMAT") from exc
    if set(records)!={"request","S_FMT_return","G_FMT_return"}:
        raise ValueError("ALL_THREE_INDEPENDENT_V4L2_FORMAT_EVENTS_REQUIRED")
    expect_geometry={"width":GEOMETRY[camera][0],"height":GEOMETRY[camera][1],
                     "fourcc":842094158,"bytesperline":GEOMETRY[camera][0],
                     "sizeimage":GEOMETRY[camera][0]*GEOMETRY[camera][1]*3//2}
    req=records["request"]
    expect_requested={"colorspace":1,"ycbcr_enc":1,"quantization":2,"xfer_func":1}
    for k,v in dict(expect_geometry,**expect_requested).items():
        if req.get(k)!=v:raise ValueError("V4L2_REQUEST_NOT_PROVISIONAL_601_NV12")
    for stage in ("S_FMT_return","G_FMT_return"):
        row=records[stage]
        if row.get("rc")!=0 or row.get("errno")!=0:
            raise ValueError("V4L2_FORMAT_IOCTL_DID_NOT_SUCCEED")
        if any(row.get(k)!=v for k,v in expect_geometry.items()):
            raise ValueError("V4L2_NATIVE_GEOMETRY_OR_NV12_NOT_PRESERVED")
        if row.get("colorspace")!=1 or row.get("ycbcr_enc") not in (0,1) or            row.get("quantization") not in (0,2) or row.get("xfer_func") not in (0,1):
            raise ValueError("V4L2_COLOUR_DEFAULT_MAPPING_NOT_SAFE_601_LIMITED_709")
    sfmt={k:v for k,v in records["S_FMT_return"].items()
          if k not in ("rc","errno")}
    gfmt={k:v for k,v in records["G_FMT_return"].items()
          if k not in ("rc","errno")}
    if sfmt!=gfmt:raise ValueError("V4L2_G_FMT_DOES_NOT_ECHO_EFFECTIVE_S_FMT")
    events=[line for line in log.splitlines()
            if line.startswith("E004NC_REAL_V4L2_OUTPUT_COLORIMETRY camera=")]
    if len(events)!=1:raise ValueError("ONE_REAL_SOURCE_SUCCESS_EVENT_REQUIRED")
    fields={}
    for item in events[0].split()[1:]:
        if "=" not in item:raise ValueError("INVALID_REAL_COLOR_EVENT")
        k,v=item.split("=",1)
        if k in fields:raise ValueError("DUPLICATE_REAL_COLOR_EVENT_FIELD")
        fields[k]=v
    if fields.get("camera")!=camera or fields.get("effective_bt601")!="YES":
        raise ValueError("NO_EXPLICIT_E004NC_EFFECTIVE_601_MARKER")
    for k in ("width","height","colorspace","ycbcr_enc","quantization","xfer_func"):
        if fields.get(k)!=str(gfmt[k]):
            raise ValueError("CLAIMED_REAL_COLOR_TAG_DIFFERS_FROM_G_FMT")
    return {"original_V4L2_request":expect_requested,
            "actual_S_FMT_return_raw_color_fields":
                  {k:sfmt[k] for k in expect_requested},
            "actual_independent_G_FMT_return_raw_color_fields":
                  {k:gfmt[k] for k in expect_requested},
            "effective_V4L2_NV12_YCbCr601_limited_xfer709":True,
            "native_ordinary_GST_colorimetry_still_checked_separately":True}

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
        cams[camera]={"actual_physical_V4L2_loopback_S_FMT_G_FMT_effective_601_metadata":native,
                      "real_UID1000_source_and_consumer_colour_caps_by_phase":phases}
    return {
      "status":"PASS_E004NC_REAL_FRONT1080_REAR4K_EXPLICIT_BT601_V4L2_AND_UID1000_GSTREAMER_MATRIX_CONSISTENCY",
      "both_actual_cameras_and_both_native_gain_phases_checked":True,
      "ordinary_UID1000_NV12_source_and_I420_output_match_601":True,
      "real_source_RGB_matrix_and_original_sensor_colour_chart_calibrated":False,
      "sensor_primaries_gamma_white_balance_Bayer_CFA_true_noise_or_Windows_ISP_parity_proven":False,
      "no_private_optical_pixels_photos_RAW_frames_image_hashes_or_thumbnails_exported":True,
      "cameras":cams}

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("ACTUAL_TEXT_ONLY_OUTPUT_FOLDER_REQUIRED")
    print(json.dumps(validate(Path(sys.argv[1])),sort_keys=True,indent=2))
