#!/usr/bin/python3
"""Read old optical photos ONLY on SP11, report global scalar colour facts.

The private E004ne user side-by-side holds PRIOR Windows E004wq
OEM preview and LATER Linux E004ne preview. No pixel arrays,
photo thumbnails, image hashes, spatial maps or filename content
are printed, committed, copied or transmitted. No physical camera
or SP7 screen change. Colour/illumination/time NOT matched.
"""
from pathlib import Path
import json,stat
import numpy as np
from PIL import Image

REPO=Path(__file__).resolve().parents[3]
EXPERIMENT=REPO/"experiments/E004-front-ir-vd55g0/e004ne-screen-rear-stable-window-guarded-one-shot"
PHOTOS=Path("/home/geoca/Pictures/SP11-Camera-Private-E004ne")
PANEL=PHOTOS/"PRIVATE-SP11-REAR-E004WQ-OEM-WINDOWS-vs-E004NE-LINUX.png"

def population(rgb,mask):
    p=rgb[mask].astype(np.float64)
    if p.shape[0]<1000:raise ValueError("INSUFFICIENT_MATCHED_SCENE_PIXELS")
    m=p.mean(axis=0)
    return {
      "sample_count":int(p.shape[0]),
      "channel_mean_R_G_B":[round(float(x),4) for x in m],
      "channel_p50_R_G_B":[round(float(x),4) for x in np.median(p,axis=0)],
      "R_divided_by_G":round(float(m[0]/max(m[1],1.)),6),
      "B_divided_by_G":round(float(m[2]/max(m[1],1.)),6),
      "fraction_B_greater_than_R":round(float(np.mean(p[:,2]>p[:,0])),6),
      "fraction_G_greater_than_R":round(float(np.mean(p[:,1]>p[:,0])),6),
    }

def audit():
    if (not PHOTOS.is_dir() or PHOTOS.is_symlink() or
        PHOTOS.stat().st_uid!=1000 or stat.S_IMODE(PHOTOS.stat().st_mode)!=0o700 or
        not PANEL.is_file() or PANEL.is_symlink() or
        PANEL.stat().st_uid!=1000 or stat.S_IMODE(PANEL.stat().st_mode)!=0o600):
        raise RuntimeError("ONLY_EXISTING_OWNER_PRIVATE_SP11_ORIGINALS_ALLOWED")
    with Image.open(PANEL) as im:
        if im.mode!="RGB" or im.format!="PNG" or im.size!=(1920,566):
            raise RuntimeError("PREVIOUS_WINDOWS_LINUX_PRIVATE_PANEL_GEOMETRY_MISMATCH")
        windows=np.asarray(im.crop((0,26,960,566)),dtype=np.uint8)[::2,::2,:].copy()
        linux=np.asarray(im.crop((960,26,1920,566)),dtype=np.uint8)[::2,::2,:].copy()
    if windows.shape!=linux.shape!=(270,480,3):
        raise RuntimeError("MATCHED_DISPLAY_GRID_GEOMETRY_INVALID")
    weights=np.asarray([.299,.587,.114],dtype=np.float32)
    wg=windows.astype(np.float32)@weights
    lg=linux.astype(np.float32)@weights
    masks={
      "entire_preview_each":(np.ones(wg.shape,bool),np.ones(lg.shape,bool)),
      "bright_Y_above_96_each":(wg>=96,lg>=96),
      "same_position_bright_Y_above_96_both":((wg>=96)&(lg>=96),
                                             (wg>=96)&(lg>=96)),
      "same_position_bright_Y_above_128_both":((wg>=128)&(lg>=128),
                                               (wg>=128)&(lg>=128))}
    pair={}
    for key,(wm,lm) in masks.items():
        pair[key]={"earlier_Windows_OEM":population(windows,wm),
                   "later_Linux":population(linux,lm)}
    p=EXPERIMENT/"evidence/RAW10-PROFILE-RESULT.json"
    raw=json.loads(p.read_text())["cameras"]["rear"]["channels_per_frame"]
    channels={}
    for frame in ("90","600","630"):
        channels[frame]={ch:{k:int(raw[frame][ch][k]) for k in
          ("p01","p50","p95","p99","max")} for ch in ("R","G0","G1","B")}
    if pair["same_position_bright_Y_above_96_both"]["earlier_Windows_OEM"]["channel_mean_R_G_B"][0]>15:
        raise ValueError("EARLIER_WIN_SCREEN_REGION_NO_LONGER_APPEARS_CYAN")
    return {
      "status":"E004NF_ONLY_PRIVATE_SP11_COLOR_CHANNELS_SHOW_CYAN_EARLIER_WINDOWS_VS_MAGENTA_LATER_LINUX",
      "same_capture_time_screen_content_light_or_autoexposure":False,
      "same_original_e004wq_OEM_earlier_vs_e004ne_Linux_later_side_by_side":True,
      "Windows_OEM_preview_RGB_conversion_and_Linux_BT601_fully_calibrated":False,
      "channel_population_scalar_only":pair,
      "actual_original_same_boot_native_rear_RAW10_per_CFA_site_global_quantiles":channels,
      "native_4_CFA_site_color_label_is_provisional_video_format_GRBG":True,
      "two_nominal_green_sites_have_strongly_different_gain_phase_high_quantiles":True,
      "BGGR_actual_sensor_vs_GRBG_assumed_by_converter_is_only_a_testable_hypothesis":True,
      "actual_Bayer_order_or_sensor_flip_proven":False,
      "source_SENSOR_blue_channel_absent_proven":False,
      "pixel_arrays_images_spatial_maps_thumbnails_RAW_or_photo_hashes_exported":False,
      "no_camera_no_sensor_control_no_boot_no_SP7_screen_change":True,
      "next":"Display known unchanging RGB/gray colour blocks on SP7 and use fresh source-locked rear native CFA-site ROI responses and private opt-in 4K app colour scalar readback before trying alternate Bayer map or white balance."}

if __name__=="__main__":
    print(json.dumps(audit(),sort_keys=True,indent=2))
