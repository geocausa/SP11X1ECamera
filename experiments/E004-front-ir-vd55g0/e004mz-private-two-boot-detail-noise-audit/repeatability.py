#!/usr/bin/python3
"""SP11-ONLY non-exporting READ-ONLY camera IQ spatial repeatability probe.

Two different E004mx/E004my 1080p front / 4K rear local PRIVATE PNG
baseline/gain photographs are used solely for within-host scalar
summary. No image arrays, images, tiles, hashes, thumbnails or optical
pixels are printed/written/exfiltrated. No device/IR/reboot/network.
DO NOT claim a repeated spatial pattern is actual optical scene detail:
it may be sensor FPN, demosaic pattern, static dark scene, or
resampling. A low correlation may be genuine motion, tiny alignment
change, high temporal sensor noise or colour processing differences.
No controlled optical target, dark reference or matched lighting.
"""
from __future__ import annotations
import json,stat
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

HOME=Path("/home/geoca/Pictures")
RUNS=("E004mx","E004my")
CAMS={"front":(1920,1080),"rear":(3840,2160)}
PHASES=("baseline","gain")
STRIDE=4
SIGMA_LOW=8.
SIGMA_HIGH=2.

def corr(a:np.ndarray,b:np.ndarray)->float|None:
    if a.shape!=b.shape or a.ndim!=2 or a.size<32:
        raise ValueError("SCALAR_FRAME_GEOMETRY_MISMATCH")
    x=np.asarray(a,dtype=np.float64).ravel().copy()
    y=np.asarray(b,dtype=np.float64).ravel().copy()
    x-=x.mean();y-=y.mean()
    den=np.linalg.norm(x)*np.linalg.norm(y)
    if not np.isfinite(den) or den<=1e-7:
        return None
    return round(float((x@y)/den),6)

def image_components(y:np.ndarray)->tuple[np.ndarray,np.ndarray]:
    if y.ndim!=2 or min(y.shape)<32 or not np.all(np.isfinite(y)):
        raise ValueError("INVALID_PRIVATE_RGB_LUMA_SAMPLING")
    y=np.asarray(y,dtype=np.float32)
    return (gaussian_filter(y,SIGMA_LOW,mode="reflect"),
            y-gaussian_filter(y,SIGMA_HIGH,mode="reflect"))

def shifted_aggregate(a:np.ndarray,b:np.ndarray)->dict:
    if a.shape!=b.shape or min(a.shape)<16:raise ValueError("BAD_SAMPLE_GEOMETRY")
    h,w=a.shape;y0,y1=4,h-4;x0,x1=4,w-4
    scores=[]
    for dy in range(-2,3):
        for dx in range(-2,3):
            val=corr(a[y0:y1,x0:x1],b[y0+dy:y1+dy,x0+dx:x1+dx])
            if val is not None:scores.append((val,dy,dx))
    exact=corr(a[y0:y1,x0:x1],b[y0:y1,x0:x1])
    winner=max(scores) if scores else None
    return {"same_position_correlation":exact,
            "best_correlation_within_plusminus_eight_original_pixels":
                (winner[0] if winner else None),
            "best_shift_sample_y_x":
                ([int(winner[1]),int(winner[2])] if winner else None),
            "no_spatial_frequency_array_or_tile_grid_in_report":True}

def load_private(run:str,camera:str,phase:str)->np.ndarray:
    if run not in RUNS or camera not in CAMS or phase not in PHASES:
        raise ValueError("ONLY_EXACT_EXISTING_PRIVATE_RGB_RUNS")
    directory=HOME/("SP11-Camera-Private-"+run)
    p=directory/(camera+"-"+phase+"-private.png")
    if (not directory.is_dir() or directory.is_symlink()
        or directory.stat().st_uid!=1000
        or stat.S_IMODE(directory.stat().st_mode)!=0o700
        or not p.is_file() or p.is_symlink() or p.stat().st_uid!=1000
        or stat.S_IMODE(p.stat().st_mode)!=0o600):
        raise RuntimeError("PRIVATE_SP11_ORIGINAL_OWNERSHIP_MODE_OR_FILE_MISMATCH")
    with Image.open(p) as image:
        if (image.format!="PNG" or image.mode!="RGB"
            or image.size!=CAMS[camera]):
            raise RuntimeError("PRIVATE_RGB_ORIGINAL_GEOMETRY_UNEXPECTED")
        arr=np.asarray(image,dtype=np.uint8)[::STRIDE,::STRIDE,:].copy()
    rgb=arr.astype(np.float32)
    return rgb@np.asarray([.299,.587,.114],dtype=np.float32)

def measure()->dict:
    pictures={}
    for camera in CAMS:
        for phase in PHASES:
            for run in RUNS:
                pictures[(run,camera,phase)]=load_private(run,camera,phase)
    report={}
    for camera in CAMS:
        phases={}
        for phase in PHASES:
            xs=[pictures[(run,camera,phase)] for run in RUNS]
            parts=[image_components(y) for y in xs]
            lows=[part[0] for part in parts]
            highs=[part[1] for part in parts]
            shift=shifted_aggregate(*highs)
            phases[phase]={
                "earlier_and_later_rendered_gray_means":
                    [round(float(x.mean()),4) for x in xs],
                "earlier_and_later_coarse_lowpass_std":
                    [round(float(x.std()),4) for x in lows],
                "earlier_and_later_fine_highpass_std":
                    [round(float(x.std()),4) for x in highs],
                "two_separate_boot_luma_correlation":corr(*xs),
                "two_separate_boot_coarse_lowpass_correlation":corr(*lows),
                "two_separate_boot_fine_highpass":shift}
        baseline=[image_components(pictures[(run,camera,"baseline")])[1] for run in RUNS]
        gain=[image_components(pictures[(run,camera,"gain")])[1] for run in RUNS]
        report[camera]={"different_boots_same_control_profiles":phases,
                        "same_boot_baseline_vs_gain_highpass_correlations":
                            [corr(b,g) for b,g in zip(baseline,gain)]}
    return {
      "status":"SP11_LOCAL_PRIVATE_ORIGINAL_RGB_REPEATABILITY_SCALAR_ONLY",
      "actual_files":"exact_four_per_run_front_and_rear_baseline_and_gain",
      "optical_illumination_and_FOV_same_across_runs_verified":False,
      "fixed_lit_target_dedicated_dark_reference_or_colour_chart_verified":False,
      "pixel_resampling":"RGB_to_gray_on_every_fourth_original_row_and_column",
      "coarse_lowpass_sigma_downsampled_pixels":SIGMA_LOW,
      "fine_highpass_sigma_downsampled_pixels":SIGMA_HIGH,
      "shift_search_each_axis_downsampled_pixels":2,
      "repeated_fine_pattern_proves_recognizable_scene_detail":False,
      "unrepeated_fine_pattern_proves_sensor_noise":False,
      "no_image_arrays_pixels_tiles_thumbnails_or_image_hashes_exported":True,
      "no_sensor_control_IR_camera_boot_or_default_config_touched":True,
      "cameras":report}

if __name__=="__main__":
    print(json.dumps(measure(),sort_keys=True,indent=2))
