#!/usr/bin/env python3
"""SP11-local *existing* four user-private RGB photos -> aggregate scalars.

No outbound photos/pixels/tiles/thumbnails/image hashes; zero camera
nodes, network, sensor control or Linux sleep. Run only on verified
protected Golden with its guarded idle camera graph. This reads and
analyzes ONLY four existing E004mv PNGs LOCAL to SP11. Nothing from the
actual image is displayed, saved or emitted except aggregate scalar
means/percentiles/parity-strength. Image-data buffers die after run.
The test target/camera FOV and spectral illumination are UNCALIBRATED.
"""
from __future__ import annotations
import json,math,os,stat
from pathlib import Path
from PIL import Image
import numpy as np

PRIVATE=Path("/home/geoca/Pictures/SP11-Camera-Private-E004mv")
EXACT_SIZES={"front":(1920,1080),"rear":(3840,2160)}
NO_CAPTURE_OR_TRANSPORT=True


def aggregate_RGB(rgb:np.ndarray)->dict:
    if rgb.dtype!=np.uint8 or rgb.ndim!=3 or rgb.shape[2]!=3 or        rgb.shape[0]<8 or rgb.shape[1]<8:
        raise ValueError("RGB8_GEOMETRY_REQUIRED")
    # A 4x row/column stride computes the same scalar sampling basis
    # for front and rear. No spatial feature arrays survive the call.
    s=rgb[::4,::4,:]
    arr=s.astype(np.float32)
    gray=np.rint(arr@np.asarray([.299,.587,.114],dtype=np.float32)).astype(np.uint8)
    mean_channels=[round(float(v),4) for v in arr.mean(axis=(0,1))]
    gr=np.percentile(gray,[1,50,99])
    parity=np.asarray([[float(rgb[ry::4,rx::4,1].mean())
                      for rx in (0,1)] for ry in (0,1)],dtype=np.float64)
    return {
       "4x_stride_sampled_pixels":int(gray.size),
       "display_gray_mean":round(float(gray.mean()),4),
       "display_gray_p01_p50_p99":[round(float(x),3) for x in gr],
       "display_fraction_below_25":round(float(np.mean(gray<25)),6),
       "fraction_RGB_any_channel_at_least_250":round(
                                        float(np.mean(s.max(axis=2)>=250)),6),
       "RGB_channel_means_R_G_B":mean_channels,
       "RGB_green_subpixel_parity_spread_only_scalar":round(
                                         float(parity.max()-parity.min()),4),
       "RGB_2x2_parity_is_not_sensor_dark_or_optical_detail_proof":True,
       "private_photo_pixels_frames_thumbnails_grid_or_hashes_in_result":False}


def run()->dict:
    p=PRIVATE
    if not p.is_dir() or p.is_symlink() or p.stat().st_uid!=1000 or        stat.S_IMODE(p.stat().st_mode)!=0o700:
        raise RuntimeError("SP11_ORIGINAL_PHOTO_DIRECTORY_MUST_BE_OWNER_PRIVATE")
    out={}
    for camera in ("front","rear"):
        for stage in ("baseline","gain"):
            name=f"{camera}-{stage}-private.png"
            f=p/name
            if not f.is_file() or f.is_symlink() or f.stat().st_uid!=1000 or                stat.S_IMODE(f.stat().st_mode)!=0o600:
                raise RuntimeError("PRIVATE_ORIGINAL_PHOTO_NOT_EXACT_OWNER_MODE")
            with Image.open(f) as image:
                if image.format!="PNG" or image.mode!="RGB" or                    image.size!=EXACT_SIZES[camera]:
                    raise RuntimeError("PRIVATE_RGB_PHOTO_FORMAT_GEOMETRY_NOT_VALID")
                result=aggregate_RGB(np.asarray(image,dtype=np.uint8))
            out[f"{camera}_{stage}"]=result
    return {
       "source":"read_only_SP11_local_private_E004mv_original_photos",
       "actual_image_or_colour_chart_target_recognized":False,
       "actual_neutral_gray_or_colour_temperature_reference_available":False,
       "front_vs_rear_lighting_FOV_and_sensor_readback_photo_time_matched":False,
       "RGB_channel_means_may_reflect_real_scene_or_uncalibrated_processing":True,
       "green_subpixel_parity_may_reflect_scene_sensor_or_demosaic_processing":True,
       "colour_calibration_sharpening_or_green_parity_fix_authorized":False,
       "user_default_RGB_camera_or_optical_files_modified":False,
       "pixels_images_tile_grids_thumbnails_photo_hashes_or_RAW_frames_exported":False,
       "cameras":out}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
